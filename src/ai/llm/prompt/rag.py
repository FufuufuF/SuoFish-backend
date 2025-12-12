"""
RAG 检索结果格式化相关的 Prompt 模板与函数
"""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.ai.rag.retriever import RetrievalResult


def format_file_chunk(
    content: str,
    file_name: Optional[str] = None,
    page: Optional[int] = None,
    chunk_index: Optional[int] = None,
) -> str:
    """
    格式化单个文件片段
    
    Args:
        content: 片段内容
        file_name: 文件名
        page: 页码（如果有）
        chunk_index: 片段索引
    
    Returns:
        格式化后的片段文本
    """
    # 构建来源标识
    source_parts = []
    if file_name:
        source_parts.append(f"文件: {file_name}")
    if page is not None:
        source_parts.append(f"第{page}页")
    
    if source_parts:
        source_label = " - ".join(source_parts)
        return f"[{source_label}]\n{content}"
    else:
        return f"[文档片段]\n{content}"


def format_rag_context(
    results: List["RetrievalResult"],
    separator: str = "\n\n---\n\n"
) -> str:
    """
    将检索结果格式化为上下文字符串，供 LLM 使用
    
    格式示例：
    [文件: 实验指导书.docx - 第3页]
    这是文件内容...
    
    ---
    
    [文件: 实验指导书.docx - 第4页]  
    更多内容...
    
    Args:
        results: 检索结果列表
        separator: 片段之间的分隔符
        
    Returns:
        格式化后的上下文字符串
    """
    if not results:
        return ""
    
    formatted_chunks = []
    for result in results:
        metadata = result.metadata
        chunk_text = format_file_chunk(
            content=result.content,
            file_name=metadata.get("file_name"),
            page=metadata.get("page"),
            chunk_index=metadata.get("chunk_index"),
        )
        formatted_chunks.append(chunk_text)
    
    return separator.join(formatted_chunks)


def format_file_list(file_names: List[str]) -> str:
    """
    格式化文件列表，用于在系统提示词中告知 LLM 用户上传了哪些文件
    
    Args:
        file_names: 文件名列表
        
    Returns:
        格式化的文件列表字符串
    """
    if not file_names:
        return ""
    
    if len(file_names) == 1:
        return f"用户在当前会话中上传了文件：{file_names[0]}"
    
    file_list = "\n".join([f"  - {name}" for name in file_names])
    return f"用户在当前会话中上传了以下文件：\n{file_list}"

