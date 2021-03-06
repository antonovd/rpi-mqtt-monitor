# Rapsberry Pi MQTT monitor
Python script to check the cpu load, cpu temperature, free space, voltage and system clock speed
on a Raspberry Pi computer and publish the data to a MQTT server.

I wrote this so I can monitor my raspberries at home with [home assistant](https://www.home-assistant.io/). The script was written and tested on Python 2 but it should work fine on Python 3.
The script if very light, it takes 4 seconds as there are 4 one second sleeps in the code - due to mqtt haveing problems if I shoot the messages with no delay.

Each value measured by the script is send via a separate message for easier craetion of home assistant sensors.

Example message topic:
```
masoko/rpi4/cpuload
```
- first part (masoko) is the main topic configurable via the congig.py file
- second part (pi4) is the host name of the raspberry which is automatically pulled by the script, so you don't have to configure it for each installation (in case you have many raspberries like me)
- third part (cpuload) is the name of the value (these are all values published via MQTT - cpuload, cputemp, diskusage, voltage, sys_clock_speed)

# Installation:

If you don't have pip installed:
```bash
$ sudo apt install python-pip
```
Then install this module needed for the script:
```bash
$ pip install paho-mqtt
```

Copy rpi-cpu2mqtt.py and config.py.example to a folder of your choise (I am using ```/home/pi/scripts/``` ).

Rename ```config.py.example``` to ```config.py``` and populate the needed variables (MQTT host, user, password and main topic).

Test the script.
```bash
$ /usr/bin/python /home/pi/scripts/rpi-cpu2mqtt.py
```
Once you test the script there will be no output if it run OK but you should get 5 messages via the configured MQTT server.

Create a cron entry like this (you might need to update the path in the cron entry below, depending on where you put the script files):
```
*/2 * * * * /usr/bin/python /home/pi/scripts/rpi-cpu2mqtt.py
```
# Home Assistant Integration:

![Rapsberry Pi MQTT monitor in Home Assistant](images/rpi-cpu2mqtt-hass.jpg)

Once you installed the script on your raspberry you need to create some sensors in home assistant.

This is the sensors configuration assuming your sensors are separated in ```sensors.yaml``` file.
```yaml
  - platform: mqtt
    state_topic: "masoko/rpi4/cpuload"
    name: rpi 4 cpu load
    unit_of_measurement: "%"

  - platform: mqtt
    state_topic: "masoko/rpi4/cputemp"
    name: rpi 4 cpu temp
    unit_of_measurement: "°C"

  - platform: mqtt
    state_topic: "masoko/rpi4/diskusage"
    name: rpi 4 diskusage
    unit_of_measurement: "%"

  - platform: mqtt
    state_topic: "masoko/rpi4/voltage"
    name: rpi 4 voltage
    unit_of_measurement: "V"

  - platform: mqtt
    state_topic: "masoko/rpi4/sys_clock_speed"
    name: rpi 4 sys clock speed
    unit_of_measurement: "hz"
```

After that you need to create entities list via the home assistant GUI.
You can use this code or compose it via the GUI.

```yaml
type: entities
title: Rapsberry Pi MQTT monitor
entities:
  - entity: sensor.rpi4_cpu_load
  - entity: sensor.rpi4_cpu_temp
  - entity: sensor.rpi4_diskusage
  - entity: sensor.rpi_4_voltage
  - entity: sensor.rpi_4_sys_clock_speed
```