import pyaudio
import wave
import time

# 设置录音参数
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000  # 根据需要调整采样率
CHUNK = 1024
RECORD_SECONDS = 5

# 初始化录音对象
p = pyaudio.PyAudio()

try:
    # 打开音频流
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    # 录制音频
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording done.")

finally:
    # 停止录音
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 保存录制的音频
    wf = wave.open("recorded_audio.wav", "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()
    print("Audio saved as recorded_audio.wav")
