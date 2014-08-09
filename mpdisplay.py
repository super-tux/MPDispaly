#!/usr/bin/python
#
# HD44780 LCD Test Script for
# Raspberry Pi
#
# Author : Matt Hawkins
# Site   : http://www.raspberrypi-spy.co.uk
# 
# Date   : 26/07/2012
#

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time
import os

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 25
LCD_D4 = 8 
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

# Defomte GPIO for control buttons
NEXT = 10
PREV = 22
VOL_UP = 11
VOL_DOWN = 9
PLAY = 27
STOP = 17

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line 

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005

# arguments for mpc
arg = "-q -h 10.42.0.94 -P password"

def main():
  # Main program block
  
  GPIO.setwarnings(False)
  
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
    
  GPIO.setup(NEXT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Next button
  GPIO.setup(PREV, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Previous button
  GPIO.setup(PLAY, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # play/pause button
  GPIO.setup(STOP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # stop button
  GPIO.setup(VOL_UP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # volume up button
  GPIO.setup(VOL_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # volume down button



  #some variables
  i1 = 0
  i0 = 0
  timer = 0
  line0 = 0
  line1 = 0

  NEXT_alt = False
  PREV_alt = False
  VOL_UP_alt = False
  VOL_DOWN_alt = False
  PLAY_alt = False
  STOP_alt = False

 
  # Initialise display
  lcd_init()
  # Send some test
  lcd_byte(LCD_LINE_1, LCD_CMD)
  lcd_string("Raspberry Pi",2)
  lcd_byte(LCD_LINE_2, LCD_CMD)
  lcd_string("MPD Display",2)

  time.sleep(1) 
  os.system("mpc "+arg+"  play")

  os.system("echo \"runnung\"")
  
  while 1:
    # check if buttons are pressed and send the commands to mpd

    if GPIO.input(NEXT) == True and NEXT_alt == False:
      os.system("mpc "+arg+" next")

    if GPIO.input(PREV) == True and PREV_alt == False:
      os.system("mpc "+arg+" prev")

    if GPIO.input(VOL_UP) == True and VOL_UP_alt == False:
      os.system("mpc "+arg+" volume +5")

    if GPIO.input(VOL_DOWN) == True and VOL_DOWN_alt == False:
      os.system("mpc "+arg+" volume -5")

    if GPIO.input(PLAY) == True and PLAY_alt == False:
      os.system("mpc "+arg+" toggle")

    if GPIO.input(STOP) == True and STOP_alt == False:
      os.system("mpc "+arg+" stop")

    NEXT_alt = GPIO.input(NEXT)
    PREV_alt = GPIO.input(PREV)
    VOL_UP_alt = GPIO.input(VOL_UP)
    VOL_DOWN_alt = GPIO.input(VOL_DOWN)
    PLAY_alt = GPIO.input(PLAY)
    STOP_alt = GPIO.input(STOP)

    if timer == 0:
      #gathers information and displays it
      f=os.popen("mpc "+arg+" current")
      text = ""
      for i in f.readlines():
        text += i

      if text == "":
        lcd_byte(LCD_LINE_1, LCD_CMD)
        lcd_string("Raspberry Pi",2)
        lcd_byte(LCD_LINE_2, LCD_CMD)
        lcd_string("MPD Display",2)
        i0 = 0
        i2 = 0
      else:
        text = text[:len(text)-1]
        lines = text.split(" - ")

        # Send the gathered text 
        lcd_byte(LCD_LINE_1, LCD_CMD)
        lcd_string(lines[0][i0:i0+16],1)
        lcd_byte(LCD_LINE_2, LCD_CMD)
        lcd_string(lines[1][i1:i1+16],1)

        #if the text for each line is longer than 16 than scroll trouch the text
        if i0 >= len(lines[0])-16: i0 = 0
        else: i0 += 1
        if i1 >= len(lines[1])-16: i1 = 0
        else: i1 += 1       
    

    if timer == 100:
      timer = 0
    else:
      timer += 1

    time.sleep(0.01)      




def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD)
  lcd_byte(0x32,LCD_CMD)
  lcd_byte(0x28,LCD_CMD)
  lcd_byte(0x0C,LCD_CMD)  
  lcd_byte(0x06,LCD_CMD)
  lcd_byte(0x01,LCD_CMD)  

def lcd_string(message,style):
  # Send string to display
  # style=1 Left justified
  # style=2 Centred
  # style=3 Right justified
  
  if style==1:
    message = message.ljust(LCD_WIDTH," ")  
  elif style==2:
    message = message.center(LCD_WIDTH," ")
  elif style==3:
    message = message.rjust(LCD_WIDTH," ")
  
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR) 

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)      

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)   

if __name__ == '__main__':
  main()

