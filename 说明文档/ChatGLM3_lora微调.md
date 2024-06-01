同目录下的 dev.json 和 train.json为微调示例文件，实际获取的数据为70w条，实际使用的微调文件为2w条，因chatglm3微调数据多时，模型输出重复，且未找到解决方法

	lora微调生成的文件很小，P-TuningV2 微调产生的文件有12G，本文只讲lora微调，不过lora和P-TuningV2 微调的环境一样，只是在微调结束后模型的合并/使用方面不同



# 环境

注：1. python>=3.10

​	2. LORA 微调: 1张显卡，占用 `14082MiB` 显存

- 克隆ChatGLM3仓库
- ```cd  finetune_demo ```
- ```pip install -r requirements.txt```

# 数据

将训练集和测试集（验证集，如果有的话）放在指定目录

- 训练集：train.json
- 测试集 & 验证集：dev.json

注：如果训练集和测试集（验证集）的名字和上述不符，需要修改configs/lora.yaml中相应的参数

# 微调

- ```cd  finetune_demo ```

- ```py
  python finetune_hf.py  指定data目录  指定模型文件目录  configs/lora.yaml
  ```

- 恭喜你！要进入环境纠正环节啦！报错会一个一个来的，解决方法参考文末

- 微调成功后进行测试 ```python inference_hf.py your_finetune_path --prompt your prompt```  eg:```python inference_hf.py output/checkpoint3000 --prompt "孩子发烧老不好，怎么办？"```  如果正常输出则没问题，大概率是成功不了的，报错解决参考文末

# 合并模型

- ```python merge.py lora文件夹路径   --out_dir  合并后模型的导出路径``` 参考：https://zhuanlan.zhihu.com/p/683583816#showWechatShareTip?utm_source=wechat_session&utm_medium=social&s_r=0

如果想导出为 .bin模型而不是 .sametensor模型，将merge.py的最后部分注释，并加上如下代码：

```py
from typing import Annotated
import typer
import transformers

def main(
        model_dir: Annotated[str, typer.Argument(help='')],
        out_dir: Annotated[str, typer.Option(help='')],
):
    model, tokenizer = load_model_and_tokenizer(model_dir)

    # 把加载原模型和lora模型后做合并，并保存
    merged_model = model.merge_and_unload()
    # 保存配置文件和权重，不保存张量
    merged_model.save_pretrained(out_dir, to_save="config")
    tokenizer.save_pretrained(out_dir)

    # 将权重保存为二进制文件
    merged_model.save_weights_to(os.path.join(out_dir, "pytorch_model.bin"))

if __name__ == '__main__':
    app()

```

- 查看合并后模型的config.json

  ![image-20240301211105566](https://raw.githubusercontent.com/fuxiaoiii/Pictures/main/202403012111664.png)

  需修改该路径为合并后模型路径 或 "THUDM/chatglm3-6b" ，或者直接把hugging face上的config.json文件覆盖过来（有佬让把hugging face上除了 .bin .index .josn 的文件都覆盖)

- 运行合并后的模型```python finetune_hf.py  合并后模型的导出路径  --prompt  "孩子发烧老不好，怎么办？"```















附录：环境报错的解决方案


  | 微调前后 | 问题                                                         | 解决方法                                                     |
  | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
  | 前       | [```TypeError: Accelerator.__init__() got an unexpected keyword argument 'use_seedable_sampler'```](https://github.com/hiyouga/LLaMA-Factory/issues/2552) | pip install accelerate --upgrade<br />pip install transformer --upgrade |
  | 前       | Failed to build mpi4py ERROR: Could not build wheels for mpi4py, which is required to install pyproject.toml-based projects | sudo apt-get install mpich sudo apt-get install libmpich-dev |
  | 后       | [tokenizer = AutoTokenizer.from_pretrained(model_file_path, trust_remote_code=True)<br/>AttributeError: can't set attribute 'eos_token'](https://github.com/hiyouga/LLaMA-Factory/issues/1340) | 1.把生成的lora文件目录下tokenizer_config.json文件里的几个*_token删掉<br />2.手动修改 tokenizer_config.json 里面的 padding side 为 left<br />3. 把源目录除了 bin 和 pytorch_model.bin.index.json 以外的文件全部复制到导出目录中覆盖 |
  | 后       | [File "/root/miniconda3/lib/python3.10/site-packages/transformers/modeling_utils.py", line 1612, in set_input_embeddings<br/>raise NotImplementedError<br/>NotImplementedError](https://github.com/THUDM/ChatGLM3/issues/809) | 直接注释modeling_utils的1609那4行  (即最后一个报错所在的if else 四行代码) |

  如果死活都不行，可以复刻我的python依赖

```
root@a7ed31cc7d9a4cbaafe789edfebf52cf-task0-0:/# pip list
Package                   Version
------------------------- ---------------
accelerate                0.27.2
aiofiles                  23.2.1
aiohttp                   3.9.3
aiosignal                 1.3.1
altair                    5.2.0
annotated-types           0.6.0
anyio                     3.7.1
argon2-cffi               23.1.0
argon2-cffi-bindings      21.2.0
arrow                     1.3.0
asttokens                 2.4.0
async-lru                 2.0.4
async-timeout             4.0.3
attrs                     23.1.0
Babel                     2.13.0
backcall                  0.2.0
beautifulsoup4            4.12.2
bleach                    6.0.0
blinker                   1.7.0
c2net                     0.1.8
cachetools                5.3.2
certifi                   2023.7.22
cffi                      1.16.0
charset-normalizer        3.2.0
click                     8.1.7
cmake                     3.27.4.1
comm                      0.1.4
contourpy                 1.2.0
cpm-kernels               1.0.11
cycler                    0.12.1
datasets                  2.17.1
debugpy                   1.8.0
decorator                 5.1.1
deepspeed                 0.13.4
defusedxml                0.7.1
dill                      0.3.8
exceptiongroup            1.1.3
executing                 2.0.0
fastapi                   0.104.1
fastjsonschema            2.18.1
ffmpy                     0.3.1
filelock                  3.12.3
fonttools                 4.45.1
fqdn                      1.5.1
frozenlist                1.4.1
fsspec                    2023.10.0
gitdb                     4.0.11
GitPython                 3.1.40
gradio                    3.50.2
gradio_client             0.6.1
h11                       0.14.0
hjson                     3.1.0
httpcore                  1.0.2
httpx                     0.25.2
huggingface-hub           0.17.3
idna                      3.4
importlib-metadata        6.8.0
```

























