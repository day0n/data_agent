"""
数据分析Agent - 基于大语言模型的智能数据分析工具
"""

from .agent import DataAnalysisAgent
from .interactive_agent import InteractiveDataAgent

__version__ = "1.0.0"
__all__ = ["DataAnalysisAgent", "InteractiveDataAgent"]