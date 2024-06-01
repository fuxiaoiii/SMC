# 导入代码依赖
import cv2
import numpy as np
import ipywidgets as widgets
import torch
from ais_bench.infer.interface import InferSession
import time
from det_utils import letterbox, scale_coords, nms

import os
import threading
import requests
import base64
from frs import *

def preprocess_image(image, cfg, bgr2rgb=True):
    """图片预处理"""
    img, scale_ratio, pad_size = letterbox(image, new_shape=cfg['input_shape'])
    if bgr2rgb:
        img = img[:, :, ::-1]
    img = img.transpose(2, 0, 1)  # HWC2CHW
    img = np.ascontiguousarray(img, dtype=np.float32)
    return img, scale_ratio, pad_size

def draw_bbox(bbox, img0, color, wt, names):
    """在图片上画预测框"""
    det_result_str = ''
    for idx, class_id in enumerate(bbox[:, 5]):
        if float(bbox[idx][4] < float(0.05)):
            continue
        img0 = cv2.rectangle(img0, (int(bbox[idx][0]), int(bbox[idx][1])), (int(bbox[idx][2]), int(bbox[idx][3])),
                             color, wt)
        img0 = cv2.putText(img0, str(idx) + ' ' + names[int(class_id)], (int(bbox[idx][0]), int(bbox[idx][1] + 16)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        # print(names[int(class_id)])
        # confidences = int(bbox[:, 4])
        # print(names[confidences])
        img0 = cv2.putText(img0, '{:.4f}'.format(bbox[idx][4]), (int(bbox[idx][0]), int(bbox[idx][1] + 32)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        det_result_str += '{} {} {} {} {} {}\n'.format(
            names[bbox[idx][5]], str(bbox[idx][4]), bbox[idx][0], bbox[idx][1], bbox[idx][2], bbox[idx][3])
    return img0

def get_labels_from_txt(path):
    """从txt文件获取图片标签"""
    labels_dict = dict()
    with open(path) as f:
        for cat_id, label in enumerate(f.readlines()):
            labels_dict[cat_id] = label.strip()
    return labels_dict

def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=False, scaleFill=False, scaleup=True):
    # Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, 64), np.mod(dh, 64)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)




# 上传指定文件到服务器
def upload_video_to_server(video_file):
    global is_upload
    # 设置服务器上传URL
    server_upload_url = 'http://121.36.203.63:5000/upload_endpoint'

    # 创建一个文件对象
    files = {'file': (video_file, open(video_file, 'rb'))}

    # 发送文件到服务器
    response = requests.post(server_upload_url, files=files)

    if response.status_code == 200:
        print(f"Uploaded {video_file} to server successfully.")
        is_upload = False
        # 上传成功后，删除本地文件
        os.remove(video_file)
    else:
        print(f"当前网络正常：Failed to upload {video_file}. Status code: {response.status_code}")

#线程函数，每半分钟检查一次is_upload的值是否为True，如果是，则代表有写好的视频文件需要上传到服务器
def upload_thread():
    global is_upload
    while True:
        if not is_upload:
            time.sleep(5) # 等待半分钟后再次检查,因为便于调试，设置为五秒
            continue
        try:
            # 获取当前目录下的所有文件
            files = os.listdir()

            # 过滤出视频文件，例如扩展名为 .avi 的文件
            video_files = [file for file in files if file.endswith('.avi')]

            if video_files:
                # 如果有新的视频文件，执行上传到服务器的操作
                for video_file in video_files:
                    upload_video_to_server(video_file)
            else:
                print("No new video to upload.")
                is_upload = False
        except requests.exceptions.ConnectionError as e:
            print("当前网络连接有误，上传视频失败:", str(e))

#当值为True时，代表有文件需要上传；当值为False时，代表没有视频要上传
is_upload = False

# 创建一个新线程并运行检查函数
upload_thread = threading.Thread(target=upload_thread)
upload_thread.start()

def get_unique_video_filename():
    current_time = time.strftime("%Y.%m.%d.%H.%M.%S", time.localtime())
    return f"{current_time}.avi"

def infer_frame_with_vis(image, model, labels_dict, cfg, bgr2rgb=True):
    global recording
    # 数据预处理
    img, scale_ratio, pad_size = preprocess_image(image, cfg, bgr2rgb)
    # 模型推理
    output = model.infer([img])[0]

    output = torch.tensor(output)
    # 非极大值抑制后处理
    boxout = nms(output, conf_thres=cfg["conf_thres"], iou_thres=cfg["iou_thres"])
    pred_all = boxout[0].numpy()
    # 预测坐标转换
    scale_coords(cfg['input_shape'], pred_all[:, :4], image.shape, ratio_pad=(scale_ratio, pad_size))
    # 图片预测结果可视化
    img_vis = draw_bbox(pred_all, image, (0, 255, 0), 2, labels_dict)
    labels = [labels_dict[int(confidence)] for confidence in pred_all[:, 5]]

    global is_upload
    global start_time

    if recording == False and 'person' in labels:
        global img_frame

        # 将图像帧转换为 base64 格式
        retval, buffer = cv2.imencode('.jpg', img_frame)
        img_frame_base64 = base64.b64encode(buffer).decode('utf-8')

        result = detect(img_frame_base64)
        if(result):
            print("目标识别成功，你好",result)
        else:
            print("很抱歉，未检索到您的信息")


        # 添加保存视频的相关设置
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_filename = get_unique_video_filename()
        # cap = cv2.VideoCapture(0)
        # fps = cap.get(cv2.CAP_PROP_FPS)
        global video_writer
        video_writer = cv2.VideoWriter(output_filename, fourcc, 30, (640, 480))
        # cap.release()

        print("Recording started.")
        start_time = time.time()
        recording = True

    if recording:
        video_writer.write(img_vis)

    if recording and (time.time() - start_time >= 30):
        if 'person' in labels:
            start_time = time.time()
            print("Continuing record")
        else:
            if time.time() - start_time >= 35:
                recording = False
                video_writer.release()   #已经完成了对视频写入对象的使用，已经写入完所有的帧，并希望释放相关资源
                is_upload = True         #只有该种情况下才会设置为True并且视频写完毕
                print("Recording finished")

    return img_vis


def img2bytes(image):
    """将图片转换为字节码"""
    return bytes(cv2.imencode('.jpg', image)[1])


# def infer_video(video_path, model, labels_dict, cfg):
#     """视频推理"""
#     image_widget = widgets.Image(format='jpeg', width=800, height=600)
#     display(image_widget)
#
#     # 读入视频
#     cap = cv2.VideoCapture(video_path)
#     while True:
#         ret, img_frame = cap.read()
#         if not ret:
#             break
#         # 对视频帧进行推理
#         image_pred = infer_frame_with_vis(img_frame, model, labels_dict, cfg, bgr2rgb=True)
#         image_widget.value = img2bytes(image_pred)

#调用该函数
def infer_camera(model, labels_dict, cfg):
    """外设摄像头实时推理"""

    #当新接摄像头或换摄像头的时候，如果不知道摄像头的索引号或者索引号一直变 （非常不推荐用这个函数！！！！）
    def find_camera_index():
        max_index_to_check = 10  # Maximum index to check for camera
        for index in range(max_index_to_check):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                cap.release()
                return index
        # If no camera is found
        raise ValueError("No camera found.")

    # 获取摄像头
    #camera_index = find_camera_index()
    cap = cv2.VideoCapture(0)
    # 初始化可视化对象
    # image_widget = widgets.Image(format='jpeg', width=1280, height=720)
    #display(image_widget)
    print(1)
    n=0
    while True:
    	# 对摄像头每帧进行推理和可视化
    	global img_frame
    	ret, img_frame = cap.read()
    	if not ret:
            continue

    	infer_frame_with_vis(img_frame, model, labels_dict, cfg)
    	time.sleep(0.3)
        # image_pred = infer_frame_with_vis(img_frame, model, labels_dict, cfg)
        # image_widget.value = img2bytes(image_pred)



cfg = {
    'conf_thres': 0.6,  # 模型置信度阈值，阈值越低，得到的预测框越多
    'iou_thres': 0.5,  # IOU阈值，高于这个阈值的重叠预测框会被过滤掉
    'input_shape': [640, 640],  # 模型输入尺寸
}

model_path = 'yolo.om'
label_path = './coco_names.txt'

# 初始化推理模型
model = InferSession(0, model_path)

labels_dict = get_labels_from_txt(label_path)
recording = False
start_time = time.time()  # 初始化 start_time 变量

infer_camera(model, labels_dict, cfg)


