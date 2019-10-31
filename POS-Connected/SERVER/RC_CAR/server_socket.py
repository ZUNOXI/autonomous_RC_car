import socket


class Server(object):

    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print("%d 포트로 연결을 기다리는중" % (port))

        self.connection = self.server_socket.accept()[0]
        print("%d 포트로 연결 완료" % (port))

    def Get_Client(self):
        return self.connection

    def __del__(self):
        # print("del call")
        self.connection.close()
        self.server_socket.close()
