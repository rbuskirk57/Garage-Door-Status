# Garage-Door-Status
Code for Raspberry Pi and PRi Pico

This project contains files for a garage door status reporting system. It contains micropython code for the Raspberry Pi Pico W. The system consists of two Pico Ws, one is a MQTT publisher and the other the MQTT subscriber. The publisher monitors the open or close status of two garage doors. The subscriber receives the published messages and uses LEDs to indicate the status. There is a Raspberry Pi on the network that acts as MQTT broker.
