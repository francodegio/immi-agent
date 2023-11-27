import os

import yaml

from langchain.embeddings import HuggingFaceEmbeddings
from omegaconf import OmegaConf


CONFIG = OmegaConf.create(
    yaml.load(open("app/config/model.yaml"), Loader=yaml.FullLoader)
)
LLM = CONFIG.llm.download_args
VS = CONFIG.vectorstore.model

## Download LLAMA model
os.system(
    f"huggingface-cli download {LLM.size} "
    + f"{LLM.name} "
    + "--local-dir . "
    + "--local-dir-use-symlinks False"
)
os.system(f"mv {LLM.name} llm.gguf")


## Download HuggingFace model
_ = HuggingFaceEmbeddings(model_name=VS.model_name)