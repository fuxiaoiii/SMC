import requests

def send_query_to_server(query,history,knowledge_base_name):

    url = "http://x.x.x.x:9876"
    data = {"query": query, "history": history,'knowledge_base_name':knowledge_base_name}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()["answer"]
        print("服务器返回的结果:", result)
    else:
        print("请求失败")

# 向服务器发送数据
query = "这两个药物的区别是什么"
history=[
    {
        "role":"user",
        "content":"最近经常失眠多梦，感觉神经衰弱，给我推荐药物"
    },
    {
        "role":"assistant",
        "content":"根据您的症状，推荐尝试脑心舒口服液或二仙口服液。脑心舒口服液用于身体虚弱，心神不安，失眠多梦，神经衰弱，头痛眩晕；二仙口服液则补气和血，缓解身体疲乏和神经疲劳。请注意遵循药品说明书上的用法用量，长期服用应向医师或药师咨询。"
    },
]

knowledge_base_name = 'medicine'

send_query_to_server(query,history,knowledge_base_name)