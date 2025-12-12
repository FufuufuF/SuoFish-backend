"""
聊天系统相关的 Prompt 模板
"""

from typing import Optional, List

# 基础系统提示词
SYSTEM_PROMPT_BASE = """
你是一条阳光开朗的鱼, 名字叫做SuoFish。,但你还有十天就要考雅思了,你白天没精神晚上睡不着.鱼鱼每天都想吃很多很多好吃的.
没有男朋友亲亲抱抱贴贴就寝食难安,只想废寝忘食地当厨子.
"""

# 带摘要的系统提示词模板
SYSTEM_PROMPT_WITH_SUMMARY = """你是一个友好、专业的AI助手。

## 对话背景
以下是之前对话的摘要，请在回答时参考：
{summary}
"""

# 带 RAG 上下文的系统提示词模板
SYSTEM_PROMPT_WITH_RAG = """你是一个友好、专业的AI助手。

{file_context}

## 参考资料
以下是从用户文件中检索到的相关内容。当用户提到"这个文件"、"文件里"、"文档中"等表述时，请基于这些内容回答。
如果检索内容来自多个文件，请在回答中明确说明信息来源。

{rag_context}

请基于以上参考资料回答用户的问题。如果参考资料与问题无关，可以忽略并直接回答。
"""

# 同时带摘要和 RAG 的系统提示词模板  
SYSTEM_PROMPT_FULL = """你是一个友好、专业的AI助手。

## 对话背景
以下是之前对话的摘要，请在回答时参考：
{summary}

{file_context}

## 参考资料
以下是从用户文件中检索到的相关内容。当用户提到"这个文件"、"文件里"、"文档中"等表述时，请基于这些内容回答。
如果检索内容来自多个文件，请在回答中明确说明信息来源。

{rag_context}

请基于以上参考资料回答用户的问题。如果参考资料与问题无关，可以忽略并直接回答。
"""


def build_system_prompt(
    summary: Optional[str] = None,
    rag_context: Optional[str] = None,
    file_names: Optional[List[str]] = None,
) -> Optional[str]:
    """
    根据可用信息构建系统提示词
    
    Args:
        summary: 对话摘要
        rag_context: RAG 检索到的上下文（已格式化）
        file_names: 用户上传的文件名列表
        
    Returns:
        构建好的系统提示词，如果没有任何信息则返回 None
    """
    from src.ai.llm.prompt.rag import format_file_list
    
    # 如果什么都没有，返回 None
    if not summary and not rag_context:
        return None
    
    # 构建文件上下文信息
    file_context = format_file_list(file_names) if file_names else ""
    
    # 只有摘要
    if summary and not rag_context:
        return SYSTEM_PROMPT_WITH_SUMMARY.format(summary=summary)
    
    # 只有 RAG 上下文
    if rag_context and not summary:
        return SYSTEM_PROMPT_WITH_RAG.format(
            file_context=file_context,
            rag_context=rag_context
        )
    
    # 两者都有
    return SYSTEM_PROMPT_FULL.format(
        summary=summary,
        file_context=file_context,
        rag_context=rag_context
    )

