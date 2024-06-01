# coding: utf-8
import os
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkfrs.v2.region.frs_region import FrsRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkfrs.v2 import *

# The AK and SK used for authentication are hard-coded or stored in plaintext, which has great security risks. It is recommended that the AK and SK be stored in ciphertext in configuration files or environment variables and decrypted during use to ensure security.
# In this example, AK and SK are stored in environment variables for authentication. Before running this example, set environment variables CLOUD_SDK_AK and CLOUD_SDK_SK in the local environment
ak = ''
sk = ''

credentials = BasicCredentials(ak, sk)

client = FrsClient.new_builder() \
    .with_credentials(credentials) \
    .with_region(FrsRegion.value_of("cn-north-4")) \
    .build()



#官方可能有的函数是：SearchFaceByBase64
def  SearchFace_ByBase64(base64_image):
    request_search = SearchFaceByBase64Request()
    request_search.face_set_name = "smc"
    request_search.body = FaceSearchBase64Req(
        threshold=0.93,
        image_base64=base64_image
    )

    #request_search.body.image_base64 = base64_image

    try:
        response = client.search_face_by_base64(request_search)

        #{"faces": [{"bounding_box": {"width": 80, "top_left_y": 19, "top_left_x": 100, "height": 117}, "similarity": 0.96466804,
        # "external_image_id": "baideng", "face_id": "BSBKIB2J"}], "X-Request-Id": "ee4a3674d339ca93868f5edd1f549d50"}

        # 因为response的类型<class 'huaweicloudsdkfrs.v2.model.search_face_by_base64_response.SearchFaceByBase64Response'> 是自定义的，并不是简单的字典，所以转换成字典以便于获取检测结果
        response = response.to_dict()
        print(response)
        if len(response['faces'])>0:
            return response["faces"][0]["external_image_id"]
        else:
            return False
        
    except exceptions.ClientRequestException as e:
        # print(e.status_code)
        # print(e.request_id)
        # print(e.error_code)
        #print(e.error_msg)              #没有匹配到人脸库中人脸的错误原因，可以保存到数据库

        #ClientRequestException - {status_code:400,request_id:fcfdcbeb95de91e18c248f108fa5c04f,error_code:FRS.0304,error_msg:Detect no face, can not search,encoded_authorization_message:None }
        #print(e)
        return False


#静默活体检测
def DetectLiveFace_ByBase64(base64_image):

    try:
        request = DetectLiveFaceByBase64Request()
        request.body = LiveDetectFaceBase64Req(
            image_base64=base64_image
        )
        response = client.detect_live_face_by_base64(request)
        response = response.to_dict()
        return response["result"]["alive"]

    except exceptions.ClientRequestException as e:
        # print(e.status_code)
        # print(e.request_id)
        # print(e.error_code)
        # print(e.error_msg)
        return False

def detect(base64_image):
    print("正在从人脸库中检索 ---")
    #先看是否能匹配到人脸库中的人,如果能则result就是人的名字，否则为False
    result = SearchFace_ByBase64(base64_image)

    if(result):
        #如果能就进行静默活体检测
        alive = DetectLiveFace_ByBase64(base64_image)
        if(alive):
            print("peoson name:", result)
            return result

        else:

            print("FBI warning:the picture is a picture of picture!!!")
            print("FBI warning:the picture is a picture of picture!!!")
            print("FBI warning:the picture is a picture of picture!!!")
            return False

    else:

        #没有在人脸库匹配到
        print("no such people in the database")
        return False
