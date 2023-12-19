#!/usr/bin/env python

import pigpio
import time
from pigpio_encoder.rotary import Rotary
from signal import pause
import subprocess

# Variables
gpio_pin = 19
shutter_angle = 180
pwm_freq = 24
pi = pigpio.pi()  

def set_trigger_mode(value):
    if value not in [0, 1, 2]:
        raise ValueError("Invalid argument: must be 0, 1, or 2")
    
    command = f'echo {value} > /sys/module/imx477/parameters/trigger_mode'
    full_command = ['sudo', 'su', '-c', command]
    subprocess.run(full_command, check=True)
    print(f"Trigger mode set to {value}")

# Set duty cycle
def set_duty_cycle(shutter_angle, pwm_freq):
    frame_interval = 1.0 / pwm_freq  # Frame interval in seconds
    shutter_time = (shutter_angle / 360.0) * frame_interval  # Shutter open time in seconds
    shutter_time_microseconds = shutter_time * 1_000_000  # Convert shutter time to microseconds
    frame_length_microseconds = frame_interval * 1_000_000  # Convert frame interval to microseconds
    duty_cycle = int((1 - ((shutter_time_microseconds - 14) / frame_length_microseconds)) * 1_000_000) #Invert PWM signal
    duty_cycle = max(min(duty_cycle, 1_000_000), 0)  # Ensure duty cycle is within 0-1M
    return duty_cycle

# Initial duty cycle calculation
duty_cycle = set_duty_cycle(shutter_angle, pwm_freq)
pi.hardware_PWM(gpio_pin, pwm_freq, duty_cycle)  # Start PWM on the specified pin

# Rotary callback function to update the PWM frequency
def rotary_callback(counter):
    global pwm_freq  # Access the global variable
    pwm_freq = counter  # Update the PWM frequency based on the rotary counter
    frame_interval = 1.0 / pwm_freq
    remaining_time = frame_interval - (time.time() % frame_interval)
    time.sleep(remaining_time)  # Wait for the current cycle to complete
    duty_cycle = set_duty_cycle(shutter_angle, pwm_freq)  # Recalculate duty cycle
    pi.hardware_PWM(gpio_pin, pwm_freq, duty_cycle)  # Update the PWM
    print("PWM Frequency: ", pwm_freq)

# Other callback functions
def sw_short():
    print("Switch short press")

def sw_long():
    print("Switch long press")

# Rotary setup
my_rotary = Rotary(clk_gpio=21, dt_gpio=20, sw_gpio=16)
my_rotary.setup_rotary(min=1, max=50, scale=1, debounce=200, rotary_callback=rotary_callback)
my_rotary.setup_switch(debounce=200, long_press=True, sw_short_callback=sw_short, sw_long_callback=sw_long)

try:
    set_trigger_mode(2)
    pause()  # Wait for events
except KeyboardInterrupt:
    set_trigger_mode(0)
    pi.hardware_PWM(gpio_pin, 0, 0)  # Stop the PWM
    pi.stop() 
