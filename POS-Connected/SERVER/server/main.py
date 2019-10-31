import io
import socket
import struct
from PIL import Image

import time
import cv2 as cv
import numpy as np


# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]


# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        drawPred(classIds[i], confidences[i], left, top, left + width, top + height)


# Draw the predicted bounding box
def drawPred(classId, conf, left, top, right, bottom):
    # Draw a bounding box.
    cv.rectangle(frame, (left, top), (right, bottom), (0, 0, 255))

    label = '%.2f' % conf

    # Get the label for the class name and its confidence
    if classes:
        assert (classId < len(classes))
        label = '%s:%s' % (classes[classId], label)

    # Display the label at the top of the bounding box
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))


# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('141.223.140.22', 8003))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')
try:

    while True:

        start = time.time()
        print('Start')

        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        # image = Image.open(image_stream)
        # print('Image is %dx%d' % image.size)
        # image.verify()
        # print('Image is verified')


        ###############################################################3

        # Initialize the parameters
        confThreshold = 0.5  # Confidence threshold
        nmsThreshold = 0.4  # Non-maximum suppression threshold
        inpWidth = 416  # Width of network's input image
        inpHeight = 416  # Height of network's input image

        outputFile = "yolo_out_py.avi"

        # Load names of classes
        classesFile = "./coco.names";
        classes = None
        with open(classesFile, 'rt') as f:
            classes = f.read().rstrip('\n').split('\n')

        # Give the configuration and weight files for the model and load the network using them.
        modelConfiguration = "./yolov3.cfg";
        modelWeights = "./yolov3.weights";

        net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
        net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        # net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
        net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)

        print('OpenCV DNN~~~~~~~~~~~~~~~~~~~~~~~~~~~~')



        frame = cv.imdecode(np.fromstring(image_stream.read(), np.uint8), 1)

        blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)

        # Sets the input to the network
        net.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = net.forward(getOutputsNames(net))

        # Remove the bounding boxes with low confidence
        postprocess(frame, outs)

        # Put efficiency information. The function getPerfProfile returns the
        # overall time for inference(t) and the timings for each of the layers(in layersTimes)
        t, _ = net.getPerfProfile()
        label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
        cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        # Write the frame with the detection boxes
        # if (args.image):
        # cv.imwrite(outputFile, frame.astype(np.uint8))

        cv.imshow('result', frame)
        cv.waitKey(1)


        end = time.time()

        print('end', end-start)
finally:
    connection.close()
    server_socket.close()