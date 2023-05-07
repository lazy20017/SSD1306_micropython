#MicroPython SSD1306 OLED driver, I2C and SPI interfaces created by Adafruit

import time
import framebuf
import math

# register definitions
SET_CONTRAST        = 0x81
SET_ENTIRE_ON       = 0xa4
SET_NORM_INV        = 0xa6
SET_DISP            = 0xae
SET_MEM_ADDR        = 0x20
SET_COL_ADDR        = 0x21
SET_PAGE_ADDR       = 0x22
SET_DISP_START_LINE = 0x40
SET_SEG_REMAP       = 0xa0
SET_MUX_RATIO       = 0xa8
SET_COM_OUT_DIR     = 0xc0
SET_DISP_OFFSET     = 0xd3
SET_COM_PIN_CFG     = 0xda
SET_DISP_CLK_DIV    = 0xd5
SET_PRECHARGE       = 0xd9
SET_VCOM_DESEL      = 0xdb
SET_CHARGE_PUMP     = 0x8d


class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        # Note the subclass must initialize self.framebuf to a framebuffer.
        # This is necessary because the underlying data buffer is different
        # between I2C and SPI implementations (I2C needs an extra byte).


        self.poweron()
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00, # off
            # address setting
            SET_MEM_ADDR, 0x00, # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL, 0x30, # 0.83*Vcc
            # display
            SET_CONTRAST, 0xff, # maximum
            SET_ENTIRE_ON, # output follows RAM contents
            SET_NORM_INV, # not inverted
            # charge pump
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_framebuf()

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)

    def light_dot(self, x, y):
        self.pixel(x, y, 1)

    def draw_line(self, x1, y1, x2, y2, isRectangle=0):
        '''
        绘制线段
        :param: x1 y1 x2 y2 线段两端
        :param: isRetangle 是否为矩形
        :return: None
        '''
        if (x1 == x2):
            step = 1
            if (y1 > y2):
                step *= -1
            while (y1 != y2):
                self.light_dot(x1, y1)
                y1 = y1 + step
            self.light_dot(x2, y2)
        else:
            # y = kx+a
            k = (y2 - y1) / (x2 - x1)
            a = y1 - (k * x1)
            step = 1
            if (x1 > x2):
                step *= -1
            while (x1 != x2):
                self.light_dot(x1, round(k * x1 + a))
                x1 += step
            self.light_dot(x2, y2)
        if not isRectangle:
            self.show()

    def draw_rectangle(self, x, y, length, width, isFill=0):
        '''
        绘制矩形
        :param: x y 矩形左上角
        :param: length width 长和宽
        :isFill: 是否填充 0 否 1 是
        :return: None
        '''
        point_upper_left = (x, y)
        point_upper_right = (x + length, y)
        point_bottom_left = (x, y + width)
        point_bottom_right = (x + length, y + width)

        self.draw_line(point_upper_left[0], point_upper_left[1],point_upper_right[0], point_upper_right[1], 1)
        self.draw_line(point_upper_left[0], point_upper_left[1],point_bottom_left[0], point_bottom_left[1], 1)
        self.draw_line(point_bottom_left[0], point_bottom_left[1],point_bottom_right[0], point_bottom_right[1], 1)
        self.draw_line(point_upper_right[0], point_upper_right[1],point_bottom_right[0], point_bottom_right[1], 1)

        if isFill:
            for xx in range(x, x + length + 1):
                self.draw_line(xx, y, xx, y + width, 1)

        self.show()

    def draw_diamond(self, x, y, side_length, angle):
        '''
        绘制菱形
        有点BUG -_- 勉强能用
        :param: x y 菱形顶点
        :param: side_length 边长
        :angle: 顶角 [0,90]
        :return: None
        '''
        xx = abs(round(math.sin(angle / 2) * side_length))
        yy = abs(round(math.cos(angle / 2) * side_length))

        point_upper = (x, y)
        point_left = (x - xx, y + yy)
        point_right = (x + xx, y + yy)
        point_bottom = (x, y + yy * 2)

        self.draw_line(point_upper[0], point_upper[1], point_left[0], point_left[1])
        self.draw_line(point_upper[0], point_upper[1], point_right[0], point_right[1])
        self.draw_line(point_bottom[0], point_bottom[1], point_left[0], point_left[1])
        self.draw_line(point_bottom[0], point_bottom[1], point_right[0], point_right[1])

    def draw_circular_arc(self,x, y, r, start_angle, end_angle, isCircular=0):
        '''
        绘制圆弧
        :x,y 圆心坐标
        :r 半径
        :start_angle,end_angle 角度范围
        :isCircular 是否为圆 未使用abs(start_angle-end_angle)>360,因为与使用者自由。
        '''
        # 0度的位置有点怪，顺时针转了90度。+90度作为补偿。
        angleList = [math.radians(i + 90) for i in range(start_angle, end_angle + 1)]
        for i in angleList:
            self.light_dot(x + round(math.sin(i) * r), y + round(math.cos(i) * r))
        if not isCircular:
            self.show()

    def draw_circular(self,x, y, r, fill=0):
        '''
        绘制圆，并决定是否填充
        :x,y 圆心坐标
        :r 半径
        :fill 是否填充 0 否 1 是
        '''
        self.draw_circular_arc(x, y, r, 0, 360, isCircular=1)
        if fill:
            powR = math.pow(r, 2)
            for xx in range(x - r, x + r):
                for yy in range(y - r, y + r):
                    if ((math.pow(xx - x, 2) + math.pow(yy - y, 2)) < powR):
                        self.light_dot(xx, yy)
        self.show()

    #下面函数为添加的功能，根据pyboard板子厂商提供的例程修改
    #显示汉字
    def show_hanzi(self, row, col, charlist1):
        data = bytearray(charlist1)
        fbuf = framebuf.FrameBuffer(data, 16, 16, framebuf.MONO_VLSB)
        self.blit(fbuf,col,(row-1)*16)
        del fbuf
    #显示图形
    def show_image(self, data,row, col):
        #data = bytearray(image_list) #data为字节串
        fbuf = framebuf.FrameBuffer(data, col, row, framebuf.MONO_HMSB)
        self.blit(fbuf, 0, 0)
        del fbuf

class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        # Add an extra byte to the data buffer to hold an I2C data/command byte
        # to use hardware-compatible I2C transactions.  A memoryview of the
        # buffer is used to mask this byte from the framebuffer operations
        # (without a major memory hit as memoryview doesn't copy to a separate
        # buffer).
        self.buffer = bytearray(((height // 8) * width) + 1)
        self.buffer[0] = 0x40  # Set first byte of data buffer to Co=0, D/C=1
        self.framebuf = framebuf.FrameBuffer1(memoryview(self.buffer)[1:], width, height)
        self.blit = self.framebuf.blit

        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_framebuf(self):
        # Blast out the frame buffer using a single I2C transaction to support
        # hardware I2C interfaces.
        self.i2c.writeto(self.addr, self.buffer)

    def poweron(self):
        pass


class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.buffer = bytearray((height // 8) * width)
        self.framebuf = framebuf.FrameBuffer1(self.buffer, width, height)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.high()
        self.dc.low()
        self.cs.low()
        self.spi.write(bytearray([cmd]))
        self.cs.high()

    def write_framebuf(self):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.high()
        self.dc.high()
        self.cs.low()
        self.spi.write(self.buffer)
        self.cs.high()

    def poweron(self):
        self.res.high()
        time.sleep_ms(1)
        self.res.low()
        time.sleep_ms(10)
        self.res.high()


if __name__== "__main__" :
    from machine import Pin,I2C

    # ESP32 Pin assignment
    i2c = I2C(0, scl=Pin(14), sda=Pin(12))  # 硬件I2C

    myaddress = i2c.scan()
    print("i2c地址:{},{:02X}".format(type(myaddress), myaddress[0]))
    oled_width = 128
    oled_height = 64
    oled = SSD1306_I2C(oled_width, oled_height, i2c)

    oled.fill(0)  # 清屏
    oled.text('Hello, Wokwi!', 10, 10)
    oled.show()
    time.sleep(1)

    oled.fill(0)  # 清屏
    oled.draw_line(1, 1, 8, 8)
    oled.draw_rectangle(10, 10, 30, 20)
    oled.draw_rectangle(10, 40, 60, 20, 1)
    oled.draw_diamond(90, 10, 30, 45)
    time.sleep(1)

    oled.fill(0)  # 清屏
    oled.draw_circular_arc(25, 25, 12, 20, 160)
    oled.draw_circular_arc(50, 25, 12, 20, 160)
    oled.draw_circular_arc(38, 35, 15, 200, 340)
    oled.draw_circular(90, 25, 20, 1)
