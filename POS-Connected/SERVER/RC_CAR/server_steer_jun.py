import server_socket
import threading
import os
import time

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
        self.sign = 0
        self.green = 0

    def Set_UltraSonic(self, ultra) :
        if int(ultra) > 1000 :
            return
        self.ultrasonic = int(ultra)

    def Set_Microphone(self, mic) :
        self.microphone = mic

    def Set_Line(self, line) :
        self.line = line

    def Set_Stopline(self, result):
        self.stopline = result

    def Set_ObjectDetection(self, obj) :
        self.obj_list = obj

    def ultrasonic_process(self, ultra) :
        if ultra < 30 :
            return 's'
        else :
            return 'w'

    # def mic_process(self, speech) :
    #     if (speech == '정지') or (speech == '멈춰') or (speech == '멈추라고') :
    #         return 's'
    #     elif (speech == '가') or (speech == '가라고') or (speech == '출발') :
    #         return 'w'
    #     else :
    #         return ''

    def Control(self) :
#        mic_comm = self.mic_process(self.microphone)
#        us_comm = self.ultrasonic_process(self.ultrasonic)

        #os.system('clear')
        print('속도 : ', self.speed)
        print('상태 : ', self.state)
        print('전방 거리 : ', self.ultrasonic)
        print('신호 명령 : ', self.light_signal)
        print('음성 명령 : ', self.microphone)
        print('정지 명령 : ', self.stopline)
        print('장애물 : ', self.obs)
# ------------------------------------------------------------------------------------
        # speed limit
        if ('speed_limit' in self.obj_list) and (self.sign == 0):
            if self.speed != '50' :
                self.client.send('30'.encode())
                self.speed = '30'
                self.sign = 1
                self.green = 0

        elif 'limit60' in self.obj_list :
            print('limit 60')
            if self.speed != '60' :
                self.client.send('60'.encode())
                self.speed = '60'


# ------------------------------------------------------------------------------------
        # stop
        # it's only for different sound..
        if (self.stopline == True) and self.stoptime == 0 :
            if self.state != 'STOP_LINE' :
                self.stoptime = time.time()
                self.client.send('ss'.encode())
                self.state = 'STOP_LINE'
                print('STOP LINE')
                time.sleep(2)
# ------------------------------------------------------------------------------------

        if self.stopline == True and (time.time() - self.stoptime) > 10 :
            self.stoptime = 0
# ------------------------------------------------------------------------------------
        if ('red_light' in self.obj_list) :
            if (self.light_signal != 'LIGHT_STOP') or (mic_comm == 'w') :
                self.client.send('ls'.encode())
                self.light_signal = 'LIGHT_STOP'
                self.state = 'STOP'
                print('RED LIGHT')
                self.sign = 0

        # elif (mic_comm == 'w') :
        #     if self.state == 'STOP' and self.obs != 'YES' :
        #         self.client.send('lw'.encode())
        #         self.state = 'DRIVE'
        #
        # elif (mic_comm == 's') :
        #     if self.state != 'STOP' :
        #         self.client.send('s'.encode())
        #         self.state = 'STOP'
        #         print('STOP')
        #
        # elif (us_comm == 's') :
        #     if self.obs != 'YES' :
        #         self.client.send('us'.encode())
        #         self.obs = 'YES'
        #         self.state = 'STOP'
        #         print('STOP')
        # elif (us_comm == 'w') :
        #     if self.light_signal != 'LIGHT_STOP' and self.obs != 'NO' :
        #         self.obs = 'NO'
        #         self.state = 'DRIVE'
        #         self.client.send('w'.encode())
# ------------------------------------------------------------------------------------
        if ('green_light' in self.obj_list) and self.green == 0 :
            self.light_signal = 'DRIVE'
            self.state = 'DRIVE'
            self.client.send('lw'.encode())
            self.sign = 0
            self.green = 1


# ------------------------------------------------------------------------------------
        # driving
        if (self.light_signal != 'LIGHT_STOP') :
            if ('green_light' in self.obj_list) and self.green == 0:
                self.green = 1
                self.client.send('lw'.encode())
                self.light_signal = "DRIVE"

            if self.state != 'STOP' :
                self.state = 'DRIVE'
                if 'turn_right_yes' in self.obj_list :
                    self.client.send('td'.encode())
                    print("RIGHT")
                elif self.line == 2:
                    self.client.send('w'.encode())
                    print("FORWARD")
                elif self.line == 0:
                    self.client.send('a'.encode())
                    print("LEFT")
                elif self.line == 1:
                    self.client.send('d'.encode())
                    print("RIGHT")
                else :
                    print("WAIT..")
# ------------------------------------------------------------------------------------
        self.microphone = ''
        print("Sign:",self.sign, "green", self.green, "state:", self.state)

