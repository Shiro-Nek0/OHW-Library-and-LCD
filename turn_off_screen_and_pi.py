import I2C_LCD_driver 
import time
from subprocess import call

mylcd = I2C_LCD_driver.lcd()

call('pgrep -f "example.py"', shell=True)
call('pkill -9 -f "example.py"', shell=True)

time.sleep(2)
mylcd.lcd_clear()
mylcd.backlight(0)
time.sleep(1)
call('sudo poweroff', shell=True)
