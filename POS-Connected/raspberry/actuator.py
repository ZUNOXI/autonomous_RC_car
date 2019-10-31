# donkey 코드의 steering 및 throttle 조정 함수 코드를 가져와 사용할 수 있도록 수정
import busio
import board

i2c = busio.I2C(board.SCL, board.SDA)

import time


def map_range(x, X_min, X_max, Y_min, Y_max):
    """
    Linear mapping between two ranges of values
    """
    X_range = X_max - X_min
    Y_range = Y_max - Y_min
    XY_ratio = X_range / Y_range

    y = ((x - X_min) / XY_ratio + Y_min) // 1

    return int(y)


# pca를 사용하기 때문에 pca관련 library를 이용한다.
class PCA9685:
    """
    PWM motor controler using PCA9685 boards.
    This is used for most RC Carsf
    """

    def __init__(self, channel, frequency=60):
        import Adafruit_PCA9685
        # Initialise the PCA9685 using the default address (0x40).
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(frequency)
        self.channel = channel

    def set_pulse(self, pulse):
        try:
            self.pwm.set_pwm(self.channel, 0, pulse)
        except OSError as err:
            print("Unexpected issue setting PWM (check wires to motor board): {0}".format(err))

    def run(self, pulse):
        self.set_pulse(pulse)


# rc car의 throttle control 함수
class PWMThrottle:
    """
    Wrapper over a PWM motor cotnroller to convert -1 to 1 throttle
    values to PWM pulses.
    """
    MIN_THROTTLE = -1
    MAX_THROTTLE = 1

    # throttle_controller = PCA9685(0)

    def __init__(self,
                 controller=None,
                 max_pulse=300,
                 min_pulse=490,
                 zero_pulse=350):

        self.controller = PCA9685(0)
        self.max_pulse = max_pulse
        self.min_pulse = min_pulse
        self.zero_pulse = zero_pulse

        # send zero pulse to calibrate ESC
        self.controller.set_pulse(self.zero_pulse)
        time.sleep(1)

    def run(self, throttle):
        if throttle > 0:
            pulse = map_range(throttle,
                              0, self.MAX_THROTTLE,
                              self.zero_pulse, self.max_pulse)
            print(pulse)
        else:
            pulse = map_range(throttle,
                              self.MIN_THROTTLE, 0,
                              self.min_pulse, self.zero_pulse)

        self.controller.set_pulse(pulse)
        print('throttle pulse:', pulse)

    def shutdown(self):
        self.run(0)  # stop vehicle


# rc car 의 steering control 함수
class PWMSteering:
    """
    Wrapper over a PWM motor cotnroller to convert angles to PWM pulses.
    """
    LEFT_ANGLE = -1
    RIGHT_ANGLE = 1

    def __init__(self, controller=None,
                 left_pulse=150, right_pulse=640):
        self.controller = PCA9685(1)
        self.left_pulse = left_pulse
        self.right_pulse = right_pulse

    def run(self, angle):
        # map absolute angle to angle that vehicle can implement.
        pulse = map_range(
            angle,
            self.LEFT_ANGLE, self.RIGHT_ANGLE,
            self.left_pulse, self.right_pulse
        )

        self.controller.set_pulse(pulse)
        print('steering pulse:', pulse)

    def shutdown(self):
        self.run(0)  # set steering straight
