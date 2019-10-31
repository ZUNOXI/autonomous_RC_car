import io
import struct
import time
import picamera

class Camera(object):
    def __init__(self, server):
        self.server = server.makefile('wb')

    def run(self):
        with picamera.PiCamera() as camera :
            camera.resolution = (320, 240) # camera output 이미지 크기 설정
            camera.framerate = 20 # server에 송신할 초당 frame 수
            #camera.rotation = 180 # 만약 카메라가 뒤집어져 있다면 rotation시킬 수 있다.
            time.sleep(2)
            start = time.time()
            stream = io.BytesIO()

            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port = True) :
                self.server.write(struct.pack('<L', stream.tell()))
                self.server.flush()
                stream.seek(0)
                self.server.write(stream.read())
                if time.time() - start > 6000 : # server로 송신할 시간(연결시간) 설정
                    break
                stream.seek(0)
                stream.truncate()
        self.server.write(struct.pack('<L', 0))
