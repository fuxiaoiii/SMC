import socket

def main():
    # 创建一个套接字对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 设置服务器地址和端口
    host = '127.0.0.1'
    port = 8086

    # 连接服务器
    client_socket.connect((host, port))

    # 发送数据
    message = "Hello, this is a test message from the client!"
    client_socket.send(message.encode('utf-8'))
    print("发送数据成功")

    # 接收服务器发送的确认消息
    confirmation = client_socket.recv(1024)
    print(f"收到确认消息：{confirmation.decode('utf-8')}")


    # 关闭连接
    # client_socket.close()


if __name__ == "__main__":
    a = 2
    main()
