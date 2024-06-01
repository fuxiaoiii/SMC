# coding=utf-8
import json
import requests
import os
from apig_sdk import signer

#########################################################调用1
url = 'http://x.x.x.x/knowledge_base/search_docs'

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

data = {
    "query": "头疼",
    "knowledge_base_name": "", #medicine
    "top_k": 3,
    "score_threshold": 1
}


def call_ecs(query,history,knowledge_base_name):
    if knowledge_base_name == 'medicines':
        knowledge_base_name = 'medicine'
    data['knowledge_base_name'] = knowledge_base_name
    
    # 将对话记录加入到 query中
    texts = [item["content"] for item in history] + [query]
    text_combined = "。".join(texts)
    
    data['query'] = text_combined 
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("知识库成功获取响应:")
        page_contents = response.json()
        #print(page_contents)
    else:
        print("知识库获取失败！！！！！！")

    merged_content = ''
    i = 1
    for item in page_contents:
        merged_content += '\n知识库信息' + str(i) + '：'
        page_content = item['page_content']
        merged_content += page_content.strip().replace('\n', '').replace(' ', '')
        i = i + 1

    global query_backup
    prompt = '<问题>{{ question }}</问题>\n<本地知识库>{以下信息为知识库中的知识，并非用户信息，请谨慎使用：{{ context }}</本地知识库>。'
    prompt = prompt.replace('{{ question }}', query)
    prompt = prompt.replace('{{ context }}', merged_content)
    print('知识库获取信息如下：',prompt)
    return prompt


#####################################################调用2
# Config url, ak, sk and file path.
url2 = ""
# 认证用的ak和sk硬编码到代码中或者明文存储都有很大的安全风险,建议在配置文件或者环境变量中密文存放,使用时解密,确保安全;
# 本示例以ak和sk保存在环境变量中来实现身份验证为例,运行本示例前请先在本地环境中设置环境变量HUAWEICLOUD_SDK_AK和HUAWEICLOUD_SDK_SK。
ak = ""
sk = ""

# Create request, set method, url, headers and body.
method = 'POST'
headers2 = {
    'Content-Type': 'application/json'
}

body = [
        {"text": 'prompt'},
        {"history": [
            {
              "role":"system",
              "content":"你是医院医师，必须通过至少两轮对话来仔细询问患者病情，每次回复给出一个<回答>即可，且不超过50字,禁止建议咨询医生、前往医院,若本地知识库中的信息与本次问题无关，则请忽视知识库的信息。"

            }
            # {
            #   "role":"user",
            #   "content":"nihao"
            # },
            # {
            #   "role":"assistant",
            #   "content":"你好呀，有什么需要帮助的吗？"
            # }
        ]}
    ]


# Create sign, set the AK/SK to sign and authenticate the request.
sig = signer.Signer()
sig.Key = ak
sig.Secret = sk


def call_modelarts(prompt,history):
    body[0]['text'] = prompt
    default_history = body[1]['history']
    body[1]['history'] = body[1]['history']+history
    #print(body)
    request = signer.HttpRequest(method, url2, headers2, json.dumps(body))
    global sig
    sig.Sign(request)
    # Send request
    resp = requests.request(request.method, request.scheme + "://" + request.host + request.uri,
                            headers=request.headers,
                            data=request.body)
    print('模型输出完毕！')
    body[1]['history'] = default_history
    return resp.text

from flask import Flask, request
import re
# 导入你的调用函数
def call(query,history,knowledge_base_name):
    prompt=call_ecs(query,history,knowledge_base_name)  # 假设 call_ecs 是你调用 ECS 的函数
    answer=call_modelarts(prompt,history)  # 假设 call_modelarts 是你调用 ModelArts 的函数
    assistant_index = answer.rfind("<|assistant|>")  # 找到 assistant 的索引位置
    #print(answer[assistant_index])
    result = answer[assistant_index + 17:]
    result= result[:-2]
    #result= re.search(r'<回答>(.*?)</回答>', result).group(1)
    #start_pos = result.find('<回答>')
    #end_pos = result.find('</回答>') + len('</回答>')
    #result = result[start_pos:end_pos]
    print('大模型回复:',result)
    #clean_answer = re.sub(r'<[^>]*>', '', answer)
    return result
app = Flask(__name__)

@app.route("/", methods=["POST"])
def handle_request():
    data = request.json
    knowledge_base_name = data['knowledge_base_name']
    query = data["query"]
    history = data["history"]
    response = call(query,history,knowledge_base_name)
    return {"answer": response}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9876)


call('我肚子好痛，该怎么办')
