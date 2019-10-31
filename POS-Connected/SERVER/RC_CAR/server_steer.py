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
        self.speed = '60'
        self.light_signal = False
        self.obs = 'NO'
        self.stoptime = 0

    def Set_Line(self, line):
        self.line = line

    def Set_Stopline(self, result):
        self.stopline = result

    def Set_ObjectDetection(self, obj):
        self.obj_list = obj

    def steering(self):
        if self.line == 2:
            self.client.send('w'.encode())
            print("Command : FORWARD")
        elif self.line == 0:
            self.client.send('a'.encode())
            print("Command : LEFT")
        elif self.line == 1:
            self.client.send('d'.encode())
            print("Command : RIGHT")

    def Control(self):
        print('속도 : ', self.speed)
        print('상태 : ', self.state)
        #print('장애물 : ', self.obs)



        # speed limit
        if not self.obj_list:
            if self.state != 'STOP':
                self.light_signal = False
                self.steering()
                # if self.line == 2:
                #     self.client.send('w'.encode())
                #     print("FORWARD")
                # elif self.line == 0:
                #     self.client.send('a'.encode())
                #     print("LEFT")
                # elif self.line == 1:
                #     self.client.send('d'.encode())
                #     print("RIGHT")
                # else:
                #     print("WAIT..")

        else:
            if 'speed_limit' in self.obj_list:
                self.light_signal = False
                if self.speed != '30':
                    self.client.send('30'.encode())
                    self.speed = '30'
                else:
                    self.steering()
                    #else:
                        #self.client.send(self.speed.encode())

            #elif self.state == 'STOP':
                 #self.client.send('ls'.encode())



            elif 'red_light' in self.obj_list:
                self.light_signal = False
                if self.state != 'STOP':  # self.light_signal = 'STOP'
                    self.client.send('ls'.encode())
                    self.state = 'STOP'
                    self.speed = '0'
                    print('Command : STOP')

            elif 'green_light' in self.obj_list:
                if self.state == 'STOP':
                    self.state = 'DRIVE'
                    self.speed = '60'
                    self.client.send('lw'.encode())


                elif self.state == 'DRIVE' and self.light_signal == False:
                    self.speed = '60'
                    self.client.send('lw'.encode())
                    self.light_signal = True

                else:
                    self.steering()




            #elif self.state == 'STOP':
                #self.client.send('s'.encode())
        #self.client.send(self.speed.encode())

