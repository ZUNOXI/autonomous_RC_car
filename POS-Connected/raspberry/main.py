# 필요한 library import
import server_connect
import rasp_serial
import Camera
import threading
# import ultrasonic
# import mic
import time


def run():
    # 연결할 server의 host와 연결 port설정
    HOST = '141.223.140.22'
    PORT = 8001

    # socket create for camera
    server_socket = server_connect.Connect(HOST, PORT)
    time.sleep(1)

    # create raspberrypi object
    serial = rasp_serial.Serial()
    print("serial")

    # if connected to server..start thread and send camera frame
    camera = Camera.Camera(server_socket.Get_Socket())
    camera_thread = threading.Thread(target=camera.run, args=())  # target은 thread를 사용할 함수
    camera_thread.start()
    print("camera")

    print('start')

    while True:
        # server로부터 데이터를 받아옴
        data = server_socket.Get_Data()

        print("data:", data)
        if data == 'q':
            break
        serial.steer(data)  # 받아온 데이터 신호에 따라 steering


if __name__ == "__main__":
    run()
