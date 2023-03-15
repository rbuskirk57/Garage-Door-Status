import network
import secrets
import mqtt_pub_params
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led, Button
from machine import Pin
import utime
import machine
from umqttsimple import MQTTClient

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # set static IP - put this in the secrets file for future)
    wlan.ifconfig(('192.168.2.185', '255.255.255.0', '192.168.2.1', '8.8.8.8'))
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    led.toggle()
    utime.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def mqtt_serve(door):
    client = mqtt_connect()
    client.publish(mqtt_pub_params.topic_pub, msg=door)
    utime.sleep(3)
        
def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=30)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reset_pico():
   print('Failed to connect to the MQTT Broker. Bailing out with a machine reset...')
   utime.sleep(5)
   machine.reset()

led = Pin(15, Pin.OUT)
sd_btn1 = Button(2)
sd_btn2 = Button(3)
ld_btn1 = Button(4)
ld_btn2 = Button(5)
btn_reset = Button(17)
led.low()
client_id = mqtt_pub_params.client_id
mqtt_server = mqtt_pub_params.mqtt_server
user_t = mqtt_pub_params.user_t
password_t = mqtt_pub_params.password_t

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

ip = connect()

while True:
    try:
        client = mqtt_connect()
    except OSError as e:
        reset_pico()
    while True:
        # kill it
        if btn_reset.is_pressed:
            reset_pico()

        # Small Garage Door
        if sd_btn1.is_pressed:
            sdoor = 'SD_OPEN'
        elif sd_btn2.is_pressed:
            sdoor = 'SD_CLOSED'
        else:
            sdoor = 'SD_IN MOTION'

        # Large Garage Door
        if ld_btn1.is_pressed:
            ldoor = 'LD_OPEN'
        elif ld_btn2.is_pressed:
            ldoor = 'LD_CLOSED'
        else:
            ldoor = 'LD_IN MOTION'
            
        reading = sensor_temp.read_u16() * conversion_factor 
        temperature_c = 27 - (reading - 0.706)/0.001721
        fahrenheit_degrees = temperature_c * (9 / 5) + 32
        Temp_F = "Temp: " + str(round(fahrenheit_degrees,2)) + " *F"

        try:
            client.publish(mqtt_pub_params.topic_pub, msg=sdoor)
            client.publish(mqtt_pub_params.topic_pub, msg=ldoor)
            client.publish(mqtt_pub_params.topic_pub, msg=Temp_F)
            utime.sleep(1)
        except:
            print("Client publish failed, executing a machine reset")
            reset_pico()
            pass
    print("client disconnect")
    client.disconnect()
    





