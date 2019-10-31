import server_socket
import time
import socket

class Steer(object):

    def __init__(self, client):
        self.client = client
        self.ultrasonic = 9999
        self.microphone = 'NONE'
        self.line = 'NONE'
        self.obj_list = []
        self.stopline = False
        self.state = 'NONE'
        self.speed = '0'
        self.light_signal = 'NONE'
        self.obs = 'NO'
        self.stoptime = 0

    def Set_Line(self, line):
        self.line = line

    def Set_Stopline(self, result):
        self.stopline = result

    def Set_ObjectDetection(self, obj):
        self.obj_list = obj

    def ultrasonic_process(self, ultra):
        if ultra < 30:
            return 's'
        else:
            return 'w'

    def mic_process(self, speech):
        if (speech == '정지') or (speech == '멈춰') or (speech == '멈추라고'):
            return 's'
        elif (speech == '가') or (speech == '가라고') or (speech == '출발'):
            return 'w'
        else:
            return ''

    def Control(self):
        mic_comm = self.mic_process(self.microphone)
        us_comm = self.ultrasonic_process(self.ultrasonic)

        # os.system('clear')
        print('속도 : ', self.speed)
        print('상태 : ', self.state)
        print('전방 거리 : ', self.ultrasonic)
        print('신호 명령 : ', self.light_signal)
        print('음성 명령 : ', self.microphone)
        print('정지 명령 : ', self.stopline)
        print('장애물 : ', self.obs)

        # speed limit
        if not self.obj_list:
            if self.state != 'STOP':
                self.state = 'DRIVE'
                if self.line == 2:
                    self.client.send('w'.encode())
                    print("FORWARD")
                elif self.line == 0:
                    self.client.send('a'.encode())
                    print("LEFT")
                elif self.line == 1:
                    self.client.send('d'.encode())
                    print("RIGHT")
                else:
                    print("WAIT..")

        else:
            if 'speed_limit' in self.obj_list:
                if self.speed != '30':
                    self.client.send('30'.encode())
                    self.speed = '30'
                else:
                    if self.line == 2:
                        self.client.send('w'.encode())
                        print("FORWARD")
                    elif self.line == 0:
                        self.client.send('a'.encode())
                        print("LEFT")
                    elif self.line == 1:
                        self.client.send('d'.encode())
                        print("RIGHT")
                    else:
                        print("WAIT..")

            elif self.state == 'STOP':
                self.client.send('ls'.encode())

            else:
                self.client.send(self.speed.encode())

            if 'red_light' in self.obj_list:
                if self.light_signal != 'LIGHT_STOP':
                    self.client.send('s'.encode())
                    self.light_signal = 'LIGHT_STOP'
                    self.state = 'STOP'
                    print('RED LIGHT')

            elif ('green_light' in self.obj_list):
                self.light_signal = 'DRIVE'
                self.state = 'DRIVE'
                self.client.send('lw'.encode())
                self.speed = '0'

            elif self.state == 'STOP':
                self.client.send('s'.encode())

