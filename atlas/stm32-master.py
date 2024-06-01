import serial

# 配置串口参数
serial_port = '/dev/ttyUSB0'  # 串口设备文件，根据实际情况修改
baud_rate = 115200            # 波特率，根据实际情况修改

# 打开串口
ser = serial.Serial(serial_port, baud_rate)
# 确保串口已经打开
if ser.is_open:
    print(f"串口 {serial_port} 已打开，波特率 {baud_rate}")

    try:
        #while True:
            # 从键盘获取用户输入的1到2位16进制数据
            #user_input = input("请输入1到2位的16进制数据（例如 0A 或 1F）：")
            user_input="05"
            # 检查用户输入是否为有效的1到2位16进制数据
            if len(user_input) <= 2 and all(c in '0123456789ABCDEFabcdef' for c in user_input):
                user_input = user_input
                # 将16进制字符串转换为字节类型并发送
                data_to_send = int(user_input, 16).to_bytes(1, 'big')
                ser.write(data_to_send)
                ser.write(b'\x0d')
                ser.write(b'\x0a')
                print(f"发送数据: {data_to_send}")
            else:
                print("无效的16进制数据，请输入1到2位的十六进制数。")
    except KeyboardInterrupt:
        # 当按下Ctrl+C时退出循环
        print("程序被用户中断")

# 关闭串口
ser.close()
print("串口已关闭")
