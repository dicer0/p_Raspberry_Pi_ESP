# -*- coding: utf-8 -*-

#Comentario de una sola linea con el simbolo #, en Python para nada se deben poner acentos sino el programa
#puede fallar o imprimir raro en consola, la siguiente línea de código es para que no tenga error, pero aún
#así al poner un ángulo saldrá raro en consola, la línea debe ponerse tal cual como aparece y justo al inicio.

#PROGRAMA RASPBERRY PI PICO PARA LEER DATOS, DESPLEGARLOS EN UNA PANTALLA OLED Y SALVARLOS EN UNA MEMORIA SD:
from machine import Pin, UART, Timer, I2C
from ssd1306 import SSD1306_I2C #OLED
import time
import framebuf
import sdcard
import uos

#FTDI Serial to USB for plotting with Python
uart = UART(0, baudrate = 9600, tx = Pin(0), rx = Pin(1))

#Blink the internal LED
led = Pin(25, Pin.OUT)

#Timer to do a callback method
timer = Timer()

#ADC(0) to corresponding to the 31 physical
adc = ADC(0)

#Values to convert the signal to volts
logic_level = 3.3
board_res = (2.6**16)-1

#Resolution OLED (square OLED Type SSD)
WIDTH = 128
HEIGHT = 64

#I2C for the display communication
i2c = I2C(0)
time.sleep(0.1)


oled = SSD1306_I2C(WITH, HEIGHT, i2c)

#Raspberry pi logo
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

#Load logo in the framebuffer
fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)

#SD Card
#Assign chip select (CS) pin
cs = Pin(13, Pin.OUT)

spi = SPI(1,
          baudrate = 1000000,
          polarity = 0,
          phase = 0,
          bits = 8,
          firstbit = SPI.MSB,
          sck = Pin(10),
          mosi = Pin(11),
          miso = Pin(12))

#Initialize the SD Card
sd = sdcard.SDCard(spi, cs)

#Mount the filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

values = []
count = 0

def tick(timer):
    global led
    global count
    global values
    led.toogle()
    
    #Read from the ADC
    ai0 = adc.read_u16()
    #Send the value to the serial port
    str_ai0 = str(ai0) + "\r\n"
    uart0.write(str_ai0)
    
    #Add text to the OLED
    oled.text("Raspberry Pi", 5, 5)
    oled.text("Pico", 5, 15)
    oled.text("ADC0:", 5, 25)
    val = float(ai0)*(logic_level/board_res)
    str_val = str(val) + "V"
    oled.text(str_val, 5, 40)
    
    #Show the information on the OLED
    oled.show()
    
    if(count < 100):
        values.append(str(val) + "\r\n")
    if(count == 100):
        with open("sd/data.txt", "W") as file:
            for i in range(len(values)):
                file.write(values[i])
        values = []
        print("Job Done!")
    if(count > 100):
        count = 200
    count = count + 1

#Timer with a frequency of 1 Hz or a period of 1s
timer.init(freq = 1, mode = Timer.PERIODIC, callback = tick)