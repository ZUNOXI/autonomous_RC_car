# sudo pip3 install adafruit-circuitpython-PCA9685
# sudo pip3 install Adafruit_PCA9685

import time
from actuator import PCA9685, PWMSteering, PWMThrottle # actuator.py에 있는 class들
import config as cfg

# rc_car의 pwm 설정 및 calibration
throttle_cont = PWMThrottle(max_pulse=410, zero_pulse=360,
                            min_pulse=310)

steering = PWMSteering(
    left_pulse=cfg.STEERING_LEFT_PWM,
    right_pulse=cfg.STEERING_RIGHT_PWM)

throttle = PWMThrottle(
    max_pulse=cfg.THROTTLE_FORWARD_PWM,
    zero_pulse=cfg.THROTTLE_STOPPED_PWM,
    min_pulse=cfg.THROTTLE_REVERSE_PWM)

start_time = time.time()
print("kit")


class Serial(object):
    def __init__(self):

        self.new_data = 0  # 이전에 들어온 data로 이전 streeing 값, 정지 시 바퀴 방향을 유지하기 위함
        self.forward_command = 0  # 직진 steering신호 값
        self.left_command = -1.7  # 좌회전 steering 신호 값
        self.right_command = 1.7  # 우회전 steering 신호 값
        # init:        self.my_throttle = 0.65
        self.my_throttle = 0.68  # 자동차의 throttle 값
        throttle.run(self.my_throttle)  # 자동차가 달리기 시작 : 차를 들고있길 바람.
        print("init")

    def steer(self, data):
        print(self.new_data)
        print(data)

        # server에서 전송하는 data에 따라 rc car가 움직임
        if data == '30':
            print('limit 30')

            throttle.run(self.my_throttle - 0.001)  # 속도를 약간 줄임
            steering.run(self.new_data)


        elif (data == 'w') or (data == 'lw') or (data == 'ww') or (data == 'sb'):
            if data == 'lw':
                steering.run(self.new_data)
                throttle.run(self.my_throttle + 0.002)  # 속도를 약간 늘림
            else:
                steering.run(self.forward_command)
            # throttle.run(self.my_throttle)





        elif (data == 's') or (data == 'us') or (data == 'ls') or (data == 'ss'):
            if data == 'ls':
                print("redlight")

            steering.run(self.new_data)
            throttle.shutdown()  # rc car 정지

            print('final throttle: ', self.my_throttle)


        elif data == 'a':
            steering.run(self.left_command)
        # throttle.run(self.my_throttle)

        elif (data == 'd') or (data == 'td'):
            steering.run(self.right_command)
        # throttle.run(self.my_throttle)

        # self.new_data에 이전 data값 저장
        if data != 's':
            if self.new_data == 'w':
                self.new_data = self.new_data
            elif self.new_data == 'a':
                self.new_data = self.right_command
            elif self.new_data == 'd':
                self.new_data = self.left_command
        else:
            pass

        print("speed: ", self.my_throttle)


