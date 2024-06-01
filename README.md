# 寻医有道——基于MindSpore的智能问诊医药系统



# 打印材料

包含所有用到过的打印材料

# server

包含服务器（不含APP后端）的所有代码

- newest_langchain：源自开源项目[chatchat](https://github.com/chatchat-space/Langchain-Chatchat)，附录代码中没有模型文件，需自行下载，或使用我提供的服务器镜像；请注意，项目使用的embedding model经过微调。由于chatchat项目不适用于Ascend平台，如果需要部署至NPU上，建议利用LangChain框架手搓底层源码，经测试难度适中。
- modelart_ecs  ：该文件夹为所有API的集成中心，核心文件为app.py。可通过request.py调用app.py服务，与RAG大模型对话

# atlas

包含药柜侧的语音交互、人脸绑定和使用北斗GPS双定位模块定位的代码

- frs.py为被import的文件，video_final.py为实现人脸识别的文件
- audio文件夹，rasr_demo.py为实现语音交互的文件
- iot_upload.py为使用定位模块上传定位信息至华为云IOT云的文件

