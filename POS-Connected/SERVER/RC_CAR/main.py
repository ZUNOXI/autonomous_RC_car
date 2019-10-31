import server_video
# import server_ultra
# import server_microphone
import server_steer
import server_socket

import threading

if __name__ == '__main__':
    # host, port
    host, port = "141.223.140.22", 8001

    client = server_socket.Server(host, port)

    steer = server_steer.Steer(client.Get_Client())

    # loop
    video_object = server_video.CollectTrainingData(client.Get_Client(), steer)
    video_object.collect()
