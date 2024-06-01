from mindformers import AutoConfig, AutoModel, AutoTokenizer, AutoProcessor
from model_service.model_service import SingleNodeService
from mindspore import context
import mindspore as ms

context.set_context(max_device_memory='28GB', mode=ms.GRAPH_MODE, device_target="Ascend", device_id=0)


class GLM3Service(SingleNodeService):
    def __init__(self, model_name, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained("glm3_6b")
        self.config = AutoConfig.from_pretrained('glm3_6b')
        self.config.use_past = True  # 此处修改默认配置，开启增量推理能够加速推理性能
        self.config.seq_length = 2048
        self.config.checkpoint_name_or_path = 'glm3_6b'
        self.model = AutoModel.from_config(self.config)  # 从自定义配置项中实例化模型

    def _preprocess(self, data):
        query = data[0]['text']
        history = data[1]['history']
        inputs = self.tokenizer.build_chat_input(query, history=history, role="user")
        inputs = inputs['input_ids']
        return inputs

    def _inference(self, inputs):
        outputs = self.model.generate(inputs, do_sample=False, top_k=1, max_length=self.config.seq_length)
        response = self.tokenizer.decode(outputs)
        return response

    def _postprocess(self, data):
        return data
