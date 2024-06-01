# -*- coding: utf-8 -*-
import re
import time
import threading
from huaweicloud_sis.client.rtts_client import RttsClient
from huaweicloud_sis.bean.rtts_request import RttsRequest
from huaweicloud_sis.bean.callback import RttsCallBack
from huaweicloud_sis.bean.sis_config import SisConfig
from huaweicloud_sis.client.rasr_client import RasrClient
from huaweicloud_sis.bean.rasr_request import RasrRequest
from huaweicloud_sis.bean.callback import RasrCallBack
from huaweicloud_sis.bean.sis_config import SisConfig
import json
import os

import socket

# 鉴权参数
# 认证用的ak和sk硬编码到代码中或者明文存储都有很大的安全风险，建议在配置文件或者环境变量中密文存放，使用时解密，确保安全； 
# 本示例以ak和sk保存在环境变量中来实现身份验证为例，运行本示例前请先在本地环境中设置环境变量HUAWEICLOUD_SIS_AK/HUAWEICLOUD_SIS_SK/HUAWEICLOUD_SIS_PROJECT_ID。
ak = 'N8HKRYSYGU4UWYRDIE4Z'  # 从环境变量获取ak 参考https://support.huaweicloud.com/sdkreference-sis/sis_05_0003.html
# assert ak is not None, "Please add ak in your develop environment"
sk = 'qqPUovlJ2sxUWaIKoDtLrl8oTw2LD37sswhVddby'  # 从环境变量获取sk 参考https://support.huaweicloud.com/sdkreference-sis/sis_05_0003.html
# assert sk is not None, "Please add sk in your develop environment"
project_id = "d055a81adc1b472dba736cdd781a57a1"  # project id 同region一一对应，参考https://support.huaweicloud.com/api-sis/sis_03_0008.html
region = 'cn-north-4'  # region，如cn-north-4

"""
    todo 请正确填写音频格式和模型属性字符串
    1. 音频格式一定要相匹配.
         例如音频是pcm格式，并且采样率为8k，则格式填写pcm8k16bit。
         如果返回audio_format is invalid 说明该文件格式不支持。具体支持哪些音频格式，需要参考一些api文档。

    2. 音频采样率要与属性字符串的采样率要匹配。
         例如格式选择pcm16k16bit，属性字符串却选择chinese_8k_common, 则会返回'audio_format' is not match model
"""

# 实时语音识别参数
path = ''  # 需要发送音频路径，如D:/test.pcm, 同时sdk也支持byte流发送数据。
audio_format = 'pcm16k16bit'  # 音频支持格式，如pcm16k16bit，详见api文档
property = 'chinese_16k_general'  # 属性字符串，language_sampleRate_domain, 如chinese_16k_general, 采样率要和音频一致。详见api文档

import pyaudio

# 设置录音参数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 采样率，根据你的需求调整
CHUNK = 1024  # 每次读取的音频帧数

#DEVICE_ID = 4

global sign
sign = 1

# 初始化录音对象
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                #input_device_index=DEVICE_ID,
                frames_per_buffer=CHUNK)
stream_output = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)


class MyCallback(RasrCallBack):
    """ 回调类，用户需要在对应方法中实现自己的逻辑，其中on_response必须重写 """

    def on_open(self):
        """ websocket连接成功会回调此函数 """
        print('语音识别连接成功')

    def on_start(self, message):
        """
            websocket 开始识别回调此函数
        :param message: 传入信息
        :return: -
        """
        print('语音识别开始 %s' % message)

    ###########################################################################################
    #主函数，1.语音识别到结果后打印，2.将结果发给模型，得到回复后打印，3.语音合成 4.创建新的语音合成对象
    ###########################################################################################
    def on_response(self, message):
        global rasr_client
        global sign
        global history

        sign = 0
        #1.
        result = message["segments"][0]["result"]["text"]
        print('语音识别结果：', result)

        ########## 发送问诊结果,在显示屏显示出来
        global client_socket_display

        # 发送问诊结果数据
        client_socket_display.send(result[:-1].encode('utf-8'))
        print("发送语音识别结果成功")

        data["query"] = result[:-1]

        print(data)
        #2.
        #response = requests.post(url, headers=headers, json=data)
        #print("response=---:",response)
        response = requests.post(url, json=data)
        resp = response.json()["answer"]

        #print("response:",resp)
        #print(response.json())
        # 提取answer中的内容
        #start_index = response.text.find('"answer": "') + len('"answer": "')
        #end_index = response.text.find('", "docs')
        #answer_content = response.text[start_index+3:end_index]

        answer_content = resp.replace("n", "")
        answer_content = answer_content.replace("\\", "")
        answer_content = re.sub("<[^>]*>", "", answer_content)

        #answer_content = resp
        print("answer:", answer_content)

        ### 发送问诊结果
        client_socket_display.send(answer_content.encode('utf-8'))
        print("发送问诊结果成功")

        data_user = {
            "role": "user",
            "content": result
        }

        data_ai = {
            "role": "assistant",
            "content": answer_content
        }
        history.append(data_user)
        history.append(data_ai)

        #3.
        global rtts_client
        rtts_example(answer_content, rtts_client)

        global end_sign
        end_sign = 1

        global communication_sign
        communication_sign = 0
        # rasr_client.send_end()
        # rasr_client.close()

        """
            websockert返回响应结果会回调此函数
        :param message: json格式
        :return: -
        """

    def on_end(self, message):
        """
            websocket 结束识别回调此函数
        :param message: 传入信息
        :return: -
        """
        print('语音识别结束 %s' % message)

    def on_close(self):
        """ websocket关闭会回调此函数 """
        print('语音识别关闭')

    def on_error(self, error):
        """
            websocket出错回调此函数
        :param error: 错误信息
        :return: -
        """
        print('语音识别：websocket meets error, the error is %s' % error)

    def on_event(self, event):
        """
            出现事件的回调
        :param event: 事件名称
        :return: -
        """
        print('语音识别：receive event %s' % event)


def rasr_example():
    """ 实时语音识别demo """
    # step1 初始化RasrClient, 暂不支持使用代理
    my_callback = MyCallback()
    config = SisConfig()
    # 设置连接超时,默认是10
    config.set_connect_timeout(1000)
    # 设置读取超时, 默认是10
    config.set_read_timeout(1000)
    # 设置connect lost超时，一般在普通并发下，不需要设置此值。默认是10
    config.set_connect_lost_timeout(1000)
    global rasr_client
    # websocket暂时不支持使用代理
    rasr_client = RasrClient(ak=ak, sk=sk, use_aksk=True, region=region, project_id=project_id, callback=my_callback,
                             config=config)
    try:
        # step2 构造请求
        request = RasrRequest(audio_format, property)
        # 所有参数均可不设置，使用默认值
        request.set_add_punc('yes')  # 设置是否添加标点， yes or no， 默认no
        request.set_vad_head(10000)  # 设置有效头部， [0, 60000], 默认10000
        request.set_vad_tail(500)  # 设置有效尾部，[0, 3000]， 默认500
        request.set_max_seconds(60)  # 设置一句话最大长度，[1, 60], 默认30
        request.set_interim_results('no')  # 设置是否返回中间结果，yes or no，默认no
        request.set_digit_norm('no')  # 设置是否将语音中数字转写为阿拉伯数字，yes or no，默认yes
        # request.set_vocabulary_id('')     # 设置热词表id，若不存在则不填写，否则会报错
        request.set_need_word_info('no')  # 设置是否需要word_info，yes or no, 默认no

        # step3 选择连接模式
        #rasr_client.short_stream_connect(request)       # 流式一句话模式

        rasr_client.sentence_stream_connect(request)  # 实时语音识别单句模式
        #rasr_client.continue_stream_connect(request)  # 实时语音识别连续模式

        # step4 发送音频前需要发送一些头部数据
        rasr_client.send_start()

        # 连续模式下，可多次发送音频，发送格式为byte数组
        # 实现一直接收音频并发送
        global sign
        global end_sign
        global communication_sign
        while 1:
            if sign == 1 and communication_sign == 1:
                print('oookkkk')
                data = stream.read(CHUNK, exception_on_overflow=False)  #exception_on_overflow=False
                rasr_client.send_audio(data)
                #print('23232323')
            elif sign == 0:
                # 4.创建下一轮的语音合成所需要的对象
                global rtts_client
                global sign_rasr
                rtts_client = create_rtts_client()
                while 1:
                    if end_sign == 1:
                        sign_rasr = 1
                        rasr_client.close()
                        break
                break
            else:
                time.sleep(0.5)
    except Exception as e:
        print('语音识别：', e)
    # finally:
    #     # step5 关闭客户端，使用完毕后一定要关闭，否则服务端20s内没收到数据会报错并主动断开。
    #     rasr_client.close()


################################################################################
###             第二部分：问诊api
################################################################################

import requests

history = []

url = "http://121.36.203.63:9876"

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

data = {
    "query": "",
    "history": history,
    'knowledge_base_name':'medicine'
}


#################################################################################
####   第三部分：语音合成和播放
#################################################################################
class MyCallback1(RttsCallBack):
    """ 回调类，用户需要在对应方法中实现自己的逻辑，其中on_response必须重写 """

    #def __init__(self,):

    def on_open(self):
        """ websocket连接成功会回调此函数 """
        print('语音合成连接成功')

    def on_start(self, message):
        """
            websocket 开始识别回调此函数
        :param message: 传入信息
        :return: -
        """
        print('语音合成开始 %s' % message)

    def on_response(self, data):
        """
            回调返回的音频合成数据，byte数组格式
        :param data byte数组，合成的音频数据
        :return: -
        """
        print('语音合成成功')
        stream_output.write(data)

        #stream_output.stop_stream()
        #self._f.write(data)

    def on_end(self, message):
        """
            websocket 结束识别回调此函数
        :param message: 传入信息
        :return: -
        """
        print('语音合成结束： %s' % message)
        time.sleep(0.3)
        # global sign
        # sign=1

    def on_error(self, error):
        print('语音合成报错： %s' % error)


def create_rtts_client():
    # step1 初始化RttsClient, 暂不支持使用代理
    my_callback = MyCallback1()
    config = SisConfig()
    # 设置连接超时,默认是10
    config.set_connect_timeout(100)
    # 设置读取超时, 默认是10
    config.set_read_timeout(100)
    # 设置websocket等待时间
    config.set_websocket_wait_time(200)
    # websocket暂时不支持使用代理
    rtts_client = RttsClient(ak=ak, sk=sk, use_aksk=True, region=region, project_id=project_id, callback=my_callback,
                             config=config)
    return rtts_client


def rtts_example(text, rtts_client):
    """ 
        实时语音合成demo
        1. RttsClient 只能发送一次文本，如果需要多次发送文本，需要新建多个RttsClient 和 callback
        2. 识别完成后服务端会返回end响应。
        3. 当识别出现问题时，会触发on_error回调，同时会关闭websocket。
        4. 实时语音合成会多次返回结果，demo的处理方式是将多次返回结果集合在一个音频文件里。
    """

    # step2 构造请求
    rtts_request = RttsRequest(text)
    # 设置属性字符串， language_speaker_domain, 默认chinese_xiaoyan_common, 参考api文档
    rtts_request.set_property('chinese_huaxiaofei_common')
    # 设置音频格式为pcm
    rtts_request.set_audio_format('pcm')
    # 设置采样率，8000 or 16000, 默认8000
    rtts_request.set_sample_rate('8000')
    # 设置音量，[0, 100]，默认50
    rtts_request.set_volume(10)
    # 设置音高, [-500, 500], 默认0
    rtts_request.set_pitch(0)
    # 设置音速, [-500, 500], 默认0
    rtts_request.set_speed(-400)

    # step3 合成
    rtts_client.synthesis(rtts_request)


def create_rasr():
    global sign_rasr
    global sign
    global communication_sign
    global communication_sign_help

    while 1:
        if sign_rasr == 1 and communication_sign == 1 and communication_sign_help == 1:
            sign = 1
            rasr_example()
        else:
            time.sleep(1)


# 通信函数，和触摸屏交互
# 1.将得到的问诊结果发送给显示屏（8085）端口
# 2.接收到的 data 为1时，communication_sign 置1，不再阻塞语音识别
#             2时，history = [] ,清空历史对话
def communication():
    ##################################### 发送 问诊 result 的client_server,发送到 8085 端口
    global client_socket_display
    # 创建一个套接字对象
    client_socket_display = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ##################################### 接收 communication_sign 的 server_socket，监听 18080 端口
    # 创建一个套接字对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置服务器地址和端口
    host = '0.0.0.0'
    port = 18080
    # 绑定 IP 地址和端口
    server_socket.bind((host, port))
    # 设置最大连接数
    server_socket.listen(5)

    # 等待客户端连接
    client_socket_display, addr = server_socket.accept()
    print(f"连接来自：{addr}")
    global history
    global communication_sign
    global data

    try:
        while True:
            # 接收客户端发送的数据
            data_recv = client_socket_display.recv(1024)
            if not data:
                continue
            print(f"接收到的数据：{data_recv.decode('utf-8')}")

            data_recv = data_recv.decode('utf-8')
            if data_recv == '1':
                communication_sign = 1
            elif data_recv == '2':
                history = []
                data["history"] = history

            while communication_sign == 1:
                time.sleep(0.5)
    finally:
        # 关闭连接
        print("关闭连接")
        client_socket_display.close()
        server_socket.close()


if __name__ == '__main__':
    communication_sign = 0
    # 创建一个线程对象，target参数设置为你要运行的函数名，args参数是函数的参数（如果有的话）
    thread1 = threading.Thread(target=communication)
    # 启动线程
    thread1.start()

    # 先创建对象，防止运行时影响速度
    rtts_client = create_rtts_client()
    # history = []   在第二部分定义过了

    num = 0

    sign_rasr = 0
    end_sign = 0
    # 创建线程并指定要执行的函数
    thread = threading.Thread(target=create_rasr)
    # 启动线程
    thread.start()

    communication_sign_help = 0
    while True:
        if communication_sign == 1:
            communication_sign_help = 1
            # 主函数
            rasr_example()
            break
