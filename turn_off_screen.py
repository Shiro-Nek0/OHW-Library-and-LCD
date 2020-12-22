import I2C_LCD_driver 
import time
from subprocess import call

mylcd = I2C_LCD_driver.lcd()

call('pgrep -f "example.py"', shell=True)
call('pkill -9 -f "example.py"', shell=True)

mylcd.lcd_clear()
mylcd.backlight(0)