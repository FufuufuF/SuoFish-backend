"""
Prompt 模板集中管理

所有与 LLM 交互的 prompt 模板都应该放在这个模块中，
方便统一维护和调整。
"""

from .chat import (
    SYSTEM_PROMPT_WITH_RAG,
    SYSTEM_PROMPT_WITH_SUMMARY,
    SYSTEM_PROMPT_BASE,
    build_system_prompt,
)
from .summary import SUMMARY_PROMPT
from .rag import format_rag_context, format_file_list

__all__ = [
    # Chat prompts
    "SYSTEM_PROMPT_WITH_RAG",
    "SYSTEM_PROMPT_WITH_SUMMARY", 
    "SYSTEM_PROMPT_BASE",
    "build_system_prompt",
    # Summary prompts
    "SUMMARY_PROMPT",
    # RAG prompts
    "format_rag_context",
    "format_file_list",
]

