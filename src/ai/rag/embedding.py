from typing import List, Optional
from openai import OpenAI

from src.core.config import embedding as embedding_config


class Embedding():
    """文本嵌入服务"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        初始化嵌入服务
        
        Args:
            api_key: API 密钥，如果未提供则从环境变量读取
            base_url: API 基础 URL，如果未提供则从环境变量读取
            model_name: 模型名称，如果未提供则从环境变量读取
        """
        # 优先使用传入的参数，否则使用环境变量配置
        effective_api_key = api_key or embedding_config.api_key
        effective_base_url = base_url or embedding_config.base_url
        effective_model_name = model_name or embedding_config.model_name
        
        self.client = OpenAI(
            api_key=effective_api_key,
            base_url=effective_base_url,
        )
        self.mode_name = effective_model_name

    def embed_text(self, chunk: str) -> List[float]:
        completion = self.client.embeddings.create(
            model=self.mode_name,
            input=chunk,
        )
        return completion.data[0].embedding

    def embed_texts(self, chunks: List[str]) -> List[List[float]]:
        return [self.embed_text(chunk) for chunk in chunks]
