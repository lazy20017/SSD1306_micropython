import random
import time
from machine import Pin, I2C
import ssd1306
import machine
import math
from math import cos, sin
import framebuf, sys
import imgfile

# ESP32 Pin assignment
i2c = I2C(0, scl=Pin(14), sda=Pin(12))  # 硬件I2C

myaddress = i2c.scan()
print("i2c地址:{},{:02X}".format(type(myaddress), myaddress[0]))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.fill(0)  # 清屏
oled.text('Hello, Wokwi!', 10, 10)
oled.show()
time.sleep(1)

oled.fill(0)  # 清屏
oled.draw_line(1, 1, 60, 1)
oled.draw_rectangle(10, 10, 30, 20)
oled.draw_rectangle(10, 40, 60, 20, 1)
oled.draw_diamond(90, 10, 30, 45)

oled.fill(0)  # 清屏
oled.draw_circular_arc(25, 25, 12, 20, 160)
oled.draw_circular_arc(50, 25, 12, 20, 160)
oled.draw_circular_arc(38, 35, 15, 200, 340)
oled.draw_circular(90, 25, 20, 1)

print("显示图片")
#===================
buffer,img_res = imgfile.get_img() # get the image byte array
# frame buff types: GS2_HMSB, GS4_HMSB, GS8, MONO_HLSB, MONO_VLSB, MONO_HMSB, MVLSB, RGB565
fb = framebuf.FrameBuffer(buffer, img_res[0], img_res[1], framebuf.MONO_HMSB) # MONO_HLSB, MONO_VLSB, MONO_HMSB
oled.fill(0) # clear the OLED
oled.blit(fb, 0, 0)
oled.show()
time.sleep(3)

oled.fill(0) # clear the OLED
oled.text('picture2', 10, 10)
oled.show()
time.sleep(1)


oled.fill(0) # clear the OLED
oled.show_image(fb,64,64)
oled.show()
time.sleep(1)


#=============
oled.fill(0) # clear the OLED
oled.text('hanzi', 10, 10)
oled.show()
time.sleep(1)


char1=[0x20,0x10,0x08,0xFC,0x03,0x20,0x20,0x10,0x7F,0x88,0x88,0x84,0x82,0xE0,0x00,0x00,
0x04,0x04,0x04,0x05,0x04,0x04,0x04,0xFF,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x00] #华

char2=[0x00,0x20,0x20,0x20,0x20,0xFF,0x00,0x00,0x00,0xFF,0x40,0x20,0x10,0x08,0x00,0x00,
0x20,0x60,0x20,0x10,0x10,0xFF,0x00,0x00,0x00,0x3F,0x40,0x40,0x40,0x40,0x78,0x00] #北

char3=[0x24,0x24,0xA4,0xFE,0xA3,0x22,0x00,0x22,0xCC,0x00,0x00,0xFF,0x00,0x00,0x00,0x00,
0x08,0x06,0x01,0xFF,0x00,0x01,0x04,0x04,0x04,0x04,0x04,0xFF,0x02,0x02,0x02,0x00] #科

char4=[0x10,0x10,0x10,0xFF,0x10,0x90,0x08,0x88,0x88,0x88,0xFF,0x88,0x88,0x88,0x08,0x00,
0x04,0x44,0x82,0x7F,0x01,0x80,0x80,0x40,0x43,0x2C,0x10,0x28,0x46,0x81,0x80,0x00] #技

char5=[0x40,0x30,0x11,0x96,0x90,0x90,0x91,0x96,0x90,0x90,0x98,0x14,0x13,0x50,0x30,0x00,
0x04,0x04,0x04,0x04,0x04,0x44,0x84,0x7E,0x06,0x05,0x04,0x04,0x04,0x04,0x04,0x00] #学

char6=[0x00,0xFE,0x22,0x5A,0x86,0x10,0x0C,0x24,0x24,0x25,0x26,0x24,0x24,0x14,0x0C,0x00,
0x00,0xFF,0x04,0x08,0x07,0x80,0x41,0x31,0x0F,0x01,0x01,0x3F,0x41,0x41,0x71,0x00] #院

oled.fill(0)
startpos = 0
oled.show_hanzi(1, startpos, char1)  # 显示汉字1  row=0,col=0
oled.show_hanzi(1, startpos + 16, char2)  # 显示汉字2  row=0,col=16
oled.show_hanzi(1, startpos + 32, char3)  # 显示汉字3  row=0,col=32
oled.show_hanzi(1, startpos + 48, char4)  # 显示汉字4  row=0,col=48
oled.show_hanzi(1, startpos + 64, char5)  # 显示汉字5  row=0,col=64
oled.show_hanzi(1, startpos + 80, char6)  # 显示汉字6  row=0,col=80
oled.show()
#=============
print("显示3D")
cube = [[-15, -15, -15], [-15, 15, -15], [15, 15, -15], [15, -15, -15], [-15, -15, 15], [-15, 15, 15], [15, 15, 15],
        [15, -15, 15]]
lineid = [1, 2, 2, 3, 3, 4, 4, 1, 5, 6, 6, 7, 7, 8, 8, 5, 8, 4, 7, 3, 6, 2, 5, 1]
pi = math.pi


def matconv(a, matrix):
    res = [0, 0, 0]
    for i in range(0, 3):
        res[i] = matrix[i][0] * a[0] + matrix[i][1] * a[1] + matrix[i][2] * a[2]
    for i in range(0, 3):
        a[i] = res[i]
    return a


def rotate(obj, x, y, z):
    x = x / pi
    y = y / pi
    z = z / pi
    rz = [[cos(z), -sin(z), 0], [sin(z), cos(z), 0], [0, 0, 1]]
    ry = [[1, 0, 0], [0, cos(y), -sin(y)], [0, sin(y), cos(y)]]
    rx = [[cos(x), 0, sin(x)], [0, 1, 0], [-sin(x), 0, cos(x)]]
    matconv(matconv(matconv(obj, rz), ry), rx)


def drawcube(x, y, z):
    oled.fill(0)
    for i in range(0, 8):
        rotate(cube[i], x, y, z)
    for i in range(0, 24, 2):
        x1 = int(64 + cube[lineid[i] - 1][0])
        y1 = int(32 + cube[lineid[i] - 1][1])
        x2 = int(64 + cube[lineid[i + 1] - 1][0])
        y2 = int(32 + cube[lineid[i + 1] - 1][1])
        oled.draw_line(x1, y1, x2, y2, 1)
        # print(64+cube[lineid[i]-1][0],32+cube[lineid[i]-1][1],64+cube[lineid[i+1]-1][0],32+cube[lineid[i+1]-1][1])
    oled.show()


while True:
    drawcube(0.1, 0.2, 0.3)

# i=0
# while True:
#     i=random.random()

#     time.sleep(0.5)
#     oled.fill(0) #清屏
#     myoffset=8 #每个字母高8个像素点
#     oled.text('N1={:6f}'.format(i), 0, 0*myoffset)
#     oled.text('N2={:6f}'.format(i), 0, 1*myoffset)
#     oled.text('S1={:6f}'.format(i), 0, 2*myoffset)
#     oled.text('S2={:6f}'.format(i), 0, 3 * myoffset)
#     oled.text('W1={:6f}'.format(i), 0, 4*myoffset)
#     oled.text('W2={:6f}'.format(i), 0, 5*myoffset)
#     oled.text('E1={:6f}'.format(i), 0, 6*myoffset)
#     oled.text('E2={:6f}'.format(i), 0, 7 * myoffset)
#     oled.show()