# coding: utf-8
# last modified:20231031

# 导入所需的模块
import time
import serial
import re

# 初始化变量，用于存储 GPS 数据
utctime = ''   # UTC 时间
lat = ''       # 纬度
ulat = ''      # 纬度单位
lon = ''       # 经度
ulon = ''      # 经度单位
numSv = ''     # 卫星数量
msl = ''       # 海拔高度
cogt = ''      # 真北航向
cogm = ''      # 磁北航向
sog = ''       # 对地速度（海里/小时）
kph = ''       # 对地速度（公里/小时）
gps_t = 0      # GPS 状态标志


# 初始化串口对象，根据 Windows 环境下的串口编号进行设置
ser = serial.Serial("COM5", 9600)
# ser = serial.Serial("/dev/wheeltec_gps", 9600)

# 检查串口是否成功打开，并输出相应的提示信息
if ser.isOpen():
    print("GPS Serial Opened! Baudrate=9600")
else:
    print("GPS Serial Open Failed!")


# 将度分格式的经纬度转换为度格式的函数
def Convert_to_degrees(in_data1, in_data2):
    len_data1 = len(in_data1)
    str_data2 = "%05d" % int(in_data2)
    temp_data = int(in_data1)
    symbol = 1
    if temp_data < 0:
        symbol = -1
    degree = int(temp_data / 100.0)
    str_decimal = str(in_data1[len_data1-2]) + str(in_data1[len_data1-1]) + str(str_data2)
    f_degree = int(str_decimal)/60.0/100000.0
    if symbol > 0:
        result = degree + f_degree
    else:
        result = degree - f_degree
    return result


# 读取 GPS 数据并解析的函数
def GPS_read():
    global utctime
    global lat
    global ulat
    global lon
    global ulon
    global numSv
    global msl
    global cogt
    global cogm
    global sog
    global kph
    global gps_t
    if ser.inWaiting():
        if ser.read(1) == b'G':
            time.sleep(.05)
            if ser.inWaiting():
                if ser.read(1) == b'N':
                    if ser.inWaiting():
                        choice = ser.read(1)
                        if choice == b'G':
                            if ser.inWaiting():
                                if ser.read(1) == b'G':
                                    if ser.inWaiting():
                                        if ser.read(1) == b'A':
                                            GGA = ser.read(70)
                                            GGA_g = re.findall(r"\w+(?=,)|(?<=,)\w+", str(GGA))
                                            if len(GGA_g) < 13:
                                                print("GPS no found")
                                                gps_t = 0
                                                return 0
                                            else:
                                                utctime = GGA_g[0]
                                                lat = "%.8f" % Convert_to_degrees(str(GGA_g[2]), str(GGA_g[3]))
                                                ulat = GGA_g[4]
                                                lon = "%.8f" % Convert_to_degrees(str(GGA_g[5]), str(GGA_g[6]))
                                                ulon = GGA_g[7]
                                                numSv = GGA_g[9]
                                                msl = GGA_g[12]+'.'+GGA_g[13]+GGA_g[14]
                                                gps_t = 1
                                                return 1
                        elif choice == b'V':
                            if ser.inWaiting():
                                if ser.read(1) == b'T':
                                    if ser.inWaiting():
                                        if ser.read(1) == b'G':
                                            if gps_t == 1:
                                                VTG = ser.read(40)
                                                VTG_g = re.findall(r"\w+(?=,)|(?<=,)\w+", str(VTG))
                                                cogt = VTG_g[0]+'.'+VTG_g[1]+'T'
                                                if VTG_g[3] == 'M':
                                                    cogm = '0.00'
                                                    sog = VTG_g[4]+'.'+VTG_g[5]
                                                    kph = VTG_g[7]+'.'+VTG_g[8]
                                                elif VTG_g[3] != 'M':
                                                    cogm = VTG_g[3]+'.'+VTG_g[4]
                                                    sog = VTG_g[6]+'.'+VTG_g[7]
                                                    kph = VTG_g[9]+'.'+VTG_g[10]
def gps_get():
    try:
        # 无限循环，读取并输出 GPS 数据
        while True:
            if GPS_read():
                print("*********************")
                print('UTC Time:'+utctime)
                print('Latitude:'+lat+ulat)
                print('Longitude:'+lon+ulon)
                print('Number of satellites:'+numSv)
                print('Altitude:'+msl)
                print('True north heading:'+cogt+'°')
                print('Magnetic north heading:'+cogm+'°')
                print('Ground speed:'+sog+'Kn')
                print('Ground speed:'+kph+'Km/h')
                print("*********************")
    except KeyboardInterrupt:
        # 捕获键盘中断异常，关闭串口
        ser.close()
        print("GPS serial Close!")
