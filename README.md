# Open Hardware Monitor Python library
Python module that gives you most of the info of your pc over the network!

![screenshot](images/lcd.gif?raw=true)

## How does it work?

The Python script uses Open Hardware Monitor's built-in web server to get the following information:

* CPU name, load and core temperatures
* GPU name, load, core temperature, available and used memory
* GPU fan speed percentage and RPM
* GPU core and memory clock
* RAM name, load, temperature, usage and available
LCD library provided in: https://www.recantha.co.uk/blog/?p=4849 (has to be named as "I2C_LCD_driver.py")

### Making it run on startup
Set these options in Open Hardware Monitor:

![screenshot](images/ohm_options.png?raw=true)

![screenshot](images/OHWserver.png?raw=true)

check "Run" in the "Remote Web Server" submenu.
