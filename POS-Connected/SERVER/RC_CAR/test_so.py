import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
# init : (1000, 2000)
# 5000mAh battery
# full-charging state
# kit.continuous_servo[0].set_pulse_width_range(750, 1971)

kit.continuous_servo[0].set_pulse_width_range(750, 1960)

# kit.continuous_servo[0].set_pulse_width_range(750, 2007)

print("kit")


class Serial(object):
    def __init__(self):
        self.speed = 0.2
        # default speed
        kit.continuous_servo[0].throttle = 0
        self.new_data = 85
        self.left_command = 130
        self.right_command = 40

        print("init")

    def steer(self, data):
        print(self.new_data)
        print(data)

        if (data == '60') or (data == '30'):
            kit.continuous_servo[0].throttle = self.speed

        elif (data == 'w') or (data == 'lw') or (data == 'ww') or (data == 'sb'):
            # front
                kit.servo[1].angle = self.new_data
            # back
            kit.continuous_servo[0].throttle = self.speed

        elif (data == 's') or (data == 'us') or (data == 'ls') or (data == 'ss'):
            kit.servo[1].angle = self.new_data
            kit.continuous_servo[0].throttle = 0 * self.speed

        elif data == 'a':
            kit.servo[1].angle = self.left_command
            kit.continuous_servo[0].throttle = self.speed * 0.999

        elif (data == 'd') or (data == 'td'):
            kit.servo[1].angle = self.right_command
            kit.continuous_servo[0].throttle = self.speed * 0.999

        if data != 's':
            if self.new_data == 'w':
                self.new_data = self.new_data
            elif self.new_data == 'a':
                self.new_data = self.right_command
            elif self.new_data == 'd':
                self.new_data = self.left_command
        else:
            pass