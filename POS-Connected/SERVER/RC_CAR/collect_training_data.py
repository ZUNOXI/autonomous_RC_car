import numpy as np
import cv2
#import serial
import pygame
from pygame.locals import *
import socket
import time
import os
from binarization_utils import binarize
from scipy.misc import toimage

class CollectTrainingData(object):
    
    def __init__(self, host, port, input_size):



        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((host, port))

        self.server_socket.listen(1)

        # accept a single connection
        #self.connection = self.server_socket.accept()[0].makefile('rb')


        self.connection = self.server_socket.accept()[0]
        self.send_inst = True

        self.input_size = input_size

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1

        pygame.init()
        pygame.display.set_mode((250, 250))
        pygame.key.set_repeat(True)

    def collect(self):

        saved_frame = 0
        total_frame = 0

        now_saved_frame = 0
        now_total_frame = 0

        cnt2 = 0

        # collect images for training
        print("Start collecting images...")
        print("Press 'q' or 'x' to finish...")
        start = cv2.getTickCount()

        X = np.empty((0, self.input_size))
        y = np.empty((0, 4))

        now_forward_data = 0
        now_left_data = 0
        now_right_data = 0

        num_forward_data = 0
        num_left_data = 0
        num_right_data = 0

        user_input = ""

        #direction = 17
        # stream video frames one by one
        try:
            print("2")
            stream_bytes = b' '
            frame = 1
            cnt = 0
            while self.send_inst:
                #stream_bytes += self.connection.read(1024)
                stream_bytes += self.connection.recv(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    #image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    #image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.COLOR_BGR2HSV)
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    #image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

                    # select lower half of the image
                    height, width = image.shape

                    #roi = image[int(height/2):height, :]
                    #img = binarize(img=image, verbose=True)
                    roi = image[120:240, :]

                    cv2.imshow('roi', roi)
                    #cv2.imshow('origin', image)
                    #cv2.imwrite('training_data/{}.jpg'.format(cnt), roi)

                    cnt += 1
                    # reshape the roi image into a vector
                    #temp_array = roi.reshape(1, int(240/2) * 320 * rgb).astype(np.float32)

                    temp_array = roi.reshape(1, 120 * width).astype(np.float32)

                    frame += 1
                    total_frame += 1

                    # get input from human driver
                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            key_input = pygame.key.get_pressed()

                            #complex orders
                            #if key_input[pygame.K_UP] and key_input[pygame.K_LEFT] and direction == 14:
                            if key_input[pygame.K_UP] and key_input[pygame.K_RIGHT]:
                               print("Forward Right")
                               X = np.vstack((X, temp_array))
                               y = np.vstack((y, self.k[1]))
                               now_right_data += 1
                               now_saved_frame += 1
                               self.connection.send('d'.encode())

                            elif (not key_input[pygame.K_UP]) and key_input[pygame.K_LEFT] and key_input[pygame.K_RIGHT]:
                                print("reset")
                                X = np.empty((0, self.input_size))
                                y = np.empty((0, 4))

                            elif key_input[pygame.K_UP] and key_input[pygame.K_LEFT]:
                               print("Forward Left")
                               X = np.vstack((X, temp_array))
                               y = np.vstack((y, self.k[0]))
                               now_left_data += 1
                               now_saved_frame += 1
                               self.connection.send('a'.encode())

                            elif key_input[pygame.K_UP] and key_input[pygame.K_DOWN]:
                               print("exit")
                               self.send_inst = False
                               self.connection.send('q'.encode())
                               self.connection.close()
                               break


                           # simple orders
                            if key_input[pygame.K_UP] and (not key_input[pygame.K_LEFT]) and (not key_input[pygame.K_RIGHT]):
                               print("Forward")
                               now_forward_data += 1
                               now_saved_frame += 1
                               X = np.vstack((X, temp_array))
                               y = np.vstack((y, self.k[2]))
                               self.connection.send('w'.encode())

                            # elif key_input[pygame.K_RIGHT]:
                            #     print("Right")
                            #     X = np.vstack((X, temp_array))
                            #     y = np.vstack((y, self.k[1]))
                            #     saved_frame += 1
                            #     self.connection.send('d'.encode())
                            #
                            # elif key_input[pygame.K_LEFT]:
                            #     print("Left")
                            #     X = np.vstack((X, temp_array))
                            #     y = np.vstack((y, self.k[0]))
                            #     saved_frame += 1
                            #     self.connection.send('a'.encode())


                            elif key_input[pygame.K_q]:
                                print("exit")
                                self.send_inst = False
                                self.connection.send('q'.encode())
                                self.connection.close()
                                break


                            elif key_input[pygame.K_DOWN]:
                                cnt2 += 1

                                saved_frame += now_saved_frame
                                total_frame += now_total_frame

                                num_forward_data += now_forward_data
                                num_left_data += now_left_data
                                num_right_data += now_right_data

                                print("stop")
                                self.connection.send('s'.encode())

                                # save
                                file_name = str(int(time.time()))
                                directory = "training_data"

                                if not os.path.exists(directory):
                                    os.makedirs(directory)
                                try:
                                    if X.shape[0]:
                                        # save or reset(save = y, reset = n)?
                                        user_input = input("Enter y or n : ").lower()

                                        if user_input == 'y':
                                            np.savez(directory + '/' + file_name + '.npz', train=X, train_labels=y)

                                            print("now Total frame(" + str(cnt2) + "): ", now_total_frame)
                                            print("now Saved frame(" + str(cnt2) + "): ", now_saved_frame)
                                            print(
                                            "now Dropped frame(" + str(cnt2) + "): ", now_total_frame - now_saved_frame)
                                            print("----------------------------------------")
                                            print("now datas - (1) 앞 : %d (2) 좌 : %d (3) 우 : %d" % (
                                                now_forward_data, now_left_data, now_right_data))
                                            print("----------------------------------------")
                                            print("Total datas - (1) 앞 : %d (2) 좌 : %d (3) 우 : %d" % (
                                                num_forward_data, num_left_data, num_right_data))
                                            print("----------------------------------------")
                                        else:

                                            saved_frame -= now_saved_frame
                                            num_forward_data -= now_forward_data
                                            num_left_data -= now_left_data
                                            num_right_data -= now_right_data

                                            print("now Total frame(" + str(cnt2) + "): ", total_frame)
                                            print("now Saved frame(" + str(cnt2) + "): ", saved_frame)
                                            print("now Dropped frame(" + str(cnt2) + "): ", total_frame - saved_frame)
                                            print("----------------------------------------")
                                            print("now datas - (1) 앞 : %d (2) 좌 : %d (3) 우 : %d" % (
                                                num_forward_data, num_left_data, num_right_data))
                                            print("----------------------------------------")

                                    else:
                                        pass
                                except IOError as e:
                                    print(e)

                                X = np.empty((0, self.input_size))
                                y = np.empty((0, 4))

                                now_total_frame = 0
                                now_saved_frame = 0

                                now_forward_data = 0
                                now_left_data = 0
                                now_right_data = 0

                            elif key_input[pygame.K_s]:
                                print("stop")


                                self.connection.send('s'.encode())

                            elif key_input[pygame.K_f]:
                                print("reset")
                                X = np.empty((0, self.input_size))
                                y = np.empty((0, 4))


                        else : # key up
                            pass
                            #self.connection.send('s'.encode())

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

            if X.shape[0]:

                # save data as a numpy file
                file_name = str(int(time.time()))
                directory = "training_data"

                if not os.path.exists(directory):
                    os.makedirs(directory)
                try:
                    np.savez(directory + '/' + file_name + '.npz', train=X, train_labels=y)
                except IOError as e:
                    print(e)

            else:
                end = cv2.getTickCount()
                # calculate streaming duration
                print("Streaming duration: , %.2fs" % ((end - start) / cv2.getTickFrequency()))

                # print(X.shape)
                # print(y.shape)
                print("Total frame: ", total_frame)
                print("Saved frame: ", saved_frame)
                print("Dropped frame: ", total_frame - saved_frame)
                print("----------------------------------------")
                print("Total datas - (1) 앞 : %d (2) 좌 : %d (3) 우 : %d" % (
                num_forward_data, num_left_data, num_right_data))

        finally:
            self.connection.close()
            self.server_socket.close()


if __name__ == '__main__':
    # host, port
    h, p = "192.168.0.5", 8001

    # serial port
    #sp = "/dev/tty.usbmodem1421"

    # vector size, half of the image
    s = 120 * 320
    print("1")
    ctd = CollectTrainingData(h, p, s)
    ctd.collect()


