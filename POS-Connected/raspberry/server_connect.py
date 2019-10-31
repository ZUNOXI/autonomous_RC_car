# host, port 설정 후 server와 연결
import socket


class Connect(object):
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.connect((self.host, self.port))
        print('Connected')

    def Get_Data(self):
        return self.server_socket.recv(2).decode()

    def Get_Socket(self):
        return self.server_socket

    def Send_Data(self, data):
        self.server_socket.send(data)

    def __del__(self):
        self.server_socket.close()
