import socket


def main():
    # 创建一个套接字对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 设置服务器地址和端口
    host = '127.0.0.1'  # 将 IP 地址更改为你的本机 IP
    port = 8086

    # 绑定 IP 地址和端口
    server_socket.bind((host, port))

    # 设置最大连接数
    server_socket.listen(5)

    print(f"等待连接在 {host} 的 {port} 端口...")

    while True:
        # 等待客户端连接
        client_socket, addr = server_socket.accept()
        print(f"连接来自：{addr}")

        # 接收客户端发送的数据
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"接收到的数据：{data.decode('utf-8')}")

        # 可以在这里添加逻辑处理接收到的数据

        # 发送确认消息给客户端
        client_socket.send("消息已收到".encode('utf-8'))

        # 关闭与客户端的连接
        client_socket.close()

    print(1)
    # 关闭服务器套接字
    server_socket.close()
    print(2)


if __name__ == "__main__":
    main()
