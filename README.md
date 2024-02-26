# libcamera-imx477-speed-ramping
Simple example of changing fps and/or shutter speed with libcamera and the Raspberry Pi HQ camera.

### Background

From the Raspberry Pi camera documentation (https://www.raspberrypi.com/documentation/accessories/camera.html#synchronous-captures):

---
*Both the HQ Camera and the Global Shutter Camera, have support for synchronous captures. Making use of the XVS pin (Vertical Sync) allows one camera to pulse when a frame capture is initiated. The other camera can then listen for this sync pulse, and capture a frame at the same time as the other camera.*

---

By simulating this trigger pulse using Raspberry Pi hardware PWM we can achieve control of both camera frame rate and shutter angle.

<img width="739" alt="Skärmavbild 2023-12-18 kl  19 23 46" src="https://github.com/Tiramisioux/libcamera-imx477-speed-ramping/assets/74836180/ff55513a-7279-47ca-aa9e-657fbac99608">

Note that the trigger pulse is reverse to a normal PWM pulse, starting low (dictating the exposure time) and then going high (time until next frame)

### Hardware setup

1) Connect the camera XVS line to RPi GPIO 18 (hardware PWM) via a voltage divider (using 10k resistors).
2) Connect a rotary encoder to 3.3v, GND, GPIO 21 (CLK) and GPIO 20 (DT)

<img width="1296" alt="Skärmavbild 2024-02-26 kl  20 56 06" src="https://github.com/Tiramisioux/libcamera-imx477-speed-ramping/assets/74836180/47f6b23c-5f32-42d2-9391-103efde7b7f4">

### Software setup

install the pigpio hardware pwm and pigpio-encoder libraries

```pip3 install pigpio pigpio-encoder ```

clone example script

```git https://www.github.com/tiramisioux/libcamera-imx477-speed-ramping```

start the pigpio daemon

```sudo pigpiod```

go to the test script folder 

```cd libcamera-imx477-speed-ramping```

run the code

```sudo python3 pwm_test.py```

open a new terminal window and run the libcamera app:

```libcamera-vid -t 1000```

The rotary encoder should now modify frame rate.

### Known issues

When run in trigger mode 2, the sensor sometimes show some unexpected behavior. Looking into these issues. Please let me know if you have any ideas on these (or other) issues! 

- In the example script, shutter angle is set to 180 degrees (duty cycle 50%). Theoretically, this could be adjusted so that shutter angle is synced with frame rate, resulting in a fixed exposure. However, in my experiments the exposure time still varies, even with this compensation.

- Running the sensor in Trigger mode 2, and with frame capture being dictated by a PWM pulse, sometimes the image freezes, or the preview gets squeezed into a thin line on the display. I have also noticed the image becoming cropped, when adjusting shutter angle.



