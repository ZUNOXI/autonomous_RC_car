import numpy as np
import threading

import Object
import StopLine
import time
from model import NeuralNetwork

import struct
import io
from PIL import Image
import cv2 as cv

from binarization_utils import binarize


class CollectTrainingData(object):

    def __init__(self, client, steer):

        self.client = client
        self.steer = steer

        self.stopline = StopLine.Stop()
        self.objDetect = Object.Object_Detection(self.steer) # class - load object detection model

        # model create
        print("Load VGGNet")
        self.model = NeuralNetwork()
        self.model.load_model(path='../model_data/posicar_binary_v11.h5') # self-driving model
        print("Complete")

    def collect(self):

        print("Start video stream")

        stream_bytes = b' '
        # connection = self.client.makefile('rb')
        data_name = 0
        while True:
            stream_bytes += self.client.recv(1024)
            first = stream_bytes.find(b'\xff\xd8')
            last = stream_bytes.find(b'\xff\xd9')

            if first != -1 and last != -1:
                try:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]

                    imgBGR = cv.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv.IMREAD_COLOR)
                    #imgGRAY = cv.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv.IMREAD_GRAYSCALE)

                    imgBINARY = binarize(img=imgBGR, verbose=True)

                    data_name += 1

                    roiGRAY = imgBINARY[120:240, :]

                    cv.imwrite("../data/picamera/img.jpg", imgBGR)


                    #cv.imshow('Origin', imgBGR)

                    # cv.imshow('GRAY', imgGRAY)
                    #print("roi")
                    cv.imshow('roi', roiGRAY)
                    #print("roi show")
                    # reshape the roi image into a vector
                    image_array = np.reshape(roiGRAY, (-1, 120, 320, 1))

                    # neural network makes prediction
                    self.steer.Set_Line(self.model.predict(image_array))
                    # self.steer.Set_Stopline(self.stopline.GetStopLine(roiGRAY))
                    #print("detecting...")
                    self.objDetect.Detection()
                    #print("detection complete")
                    self.steer.Control()
                except:
                    continue

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break


            # image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            # # print(image_len)
            # # image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            #
            # if not image_len:
            #     break
            #
            # # Construct a stream to hold the image data and read the image
            # # data from the connection
            #
            # image_stream = io.BytesIO()
            # image_stream.write(connection.read(image_len))
            # # Rewind the stream, open it as an image with PIL and do some
            # # processing on it
            # image_stream.seek(0)
            # # image = Image.open(image_stream)
            # # print('Image is %dx%d' % image.size)
            # # image.verify()
            # # print('Image is verified')

            ###############################################################

            # imgBGR = cv.imdecode(np.fromstring(image_stream.read(), np.uint8), cv.IMREAD_COLOR)
            # # imageRGB = cv.cvtColor(imageBGR, cv.COLOR_BGR2RGB)
            # imgBINARY = binarize(img=imgBGR, verbose=True)
            # imgROI = imgBINARY[120:240, :]
            #
            # image_array = np.reshape(imgROI, (-1, 120, 320, 1))
            #
            # cv.imwrite("../data/picamera/img.jpg", imgBGR)
            #
            # self.steer.Set_Line(self.model.predict(image_array))
            # print("set complete!")
            # self.objDetect.Detection()
            #
            # self.steer.Control()


























