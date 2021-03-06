# Python 2 script to check cpu load, cpu temperature and free space,
# on a Raspberry Pi computer and publish the data to a MQTT server.
# RUN pip install paho-mqtt
# RUN sudo apt-get install python-pip

from __future__ import division
import subprocess, time, socket, os
import paho.mqtt.client as paho
import config

#get device host name - used in mqtt topic
hostname = socket.gethostname()

#mqtt server configuration
mqtt_host = config.mqtt_host
mqtt_user = config.mqtt_user
mqtt_password = config.mqtt_password
mqtt_port = config.mqtt_port
mqtt_topic_prefix = config.mqtt_topic_prefix

def check_used_space(path):
		st = os.statvfs(path)
		free_space = st.f_bavail * st.f_frsize
		total_space = st.f_blocks * st.f_frsize
		used_space = int(100 - ((free_space / total_space) * 100))
		return used_space

def check_cpu_load():
		#bash command to get cpu load from uptime command
		p = subprocess.Popen("uptime", shell=True, stdout=subprocess.PIPE).communicate()[0]
		cpu_load = p.split("average:")[1].split(",")[0].replace(' ', '')
		return cpu_load
		
def check_voltage():
		full_cmd = "vcgencmd measure_volts | cut -f2 -d= | sed 's/000//'"
		voltage = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
		voltage = voltage.strip()[:-1]
		return voltage

def check_cpu_temp():
		full_cmd = "/opt/vc/bin/vcgencmd measure_temp"
		p = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
		cpu_temp = p.replace('\n', ' ').replace('\r', '').split("=")[1].split("'")[0]
		return cpu_temp
		
def check_sys_clock_speed():
		full_cmd = "awk '{printf (\"%0.0f\",$1/1000); }' </sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
		return subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
		
def publish_to_mqtt (cpu_load, cpu_temp, used_space, voltage, sys_clock_speed):
		#connect to mqtt server
		client = paho.Client()
		client.username_pw_set(mqtt_user, mqtt_password)
		client.connect(mqtt_host, mqtt_port)

		#publish monitored values to MQTT
		client.publish(mqtt_topic_prefix+"/"+hostname+"/cpuload", cpu_load, qos=1)
		time.sleep(1)
		client.publish(mqtt_topic_prefix+"/"+hostname+"/cputemp", cpu_temp, qos=1)
		time.sleep(1)
		client.publish(mqtt_topic_prefix+"/"+hostname+"/diskusage", used_space, qos=1)
		time.sleep(1)
		client.publish(mqtt_topic_prefix+"/"+hostname+"/voltage", voltage, qos=1)
		time.sleep(1)
		client.publish(mqtt_topic_prefix+"/"+hostname+"/sys_clock_speed", sys_clock_speed, qos=1)
		#disconect from mqtt server
		client.disconnect()

if __name__ == '__main__':
		#collect the monitored values
		cpu_load = check_cpu_load()
		cpu_temp = check_cpu_temp()
		used_space = check_used_space('/')
		voltage = check_voltage() 
		sys_clock_speed = check_sys_clock_speed()
		print(voltage)
		#Publish messages to MQTT
		publish_to_mqtt(cpu_load, cpu_temp, used_space, voltage, sys_clock_speed)
