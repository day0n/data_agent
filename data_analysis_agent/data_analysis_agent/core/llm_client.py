"""
阿里云百炼大模型API客户端
使用OpenAI兼容接口调用通义千问模型
"""
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
import json


class AliyunLLMClient:
    def __init__(self, api_key: str = None, init_client: bool = True):
        """
        初始化阿里云大模型客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量获取
            init_client: 是否初始化客户端，测试时可设为False
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY", "sk-8f735e8d4a944cc7a0d00f9c2062fbde")
        self.client = None
        self.model = "qwen-plus"
        
        if init_client:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                )
            except Exception as e:
                print(f"LLM客户端初始化失败: {str(e)}")
                self.client = None
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        """
        发送聊天消息到大模型
        
        Args:
            messages: 消息列表，格式为[{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数，控制输出随机性
            max_tokens: 最大输出token数
        
        Returns:
            模型的回复文本
        """
        if self.client is None:
            return "LLM客户端未初始化"
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"API调用失败: {str(e)}"
    
    def analyze_data(self, data_description: str, analysis_request: str) -> str:
        """
        让大模型分析数据并提供洞察
        
        Args:
            data_description: 数据的描述信息
            analysis_request: 用户的分析需求
        
        Returns:
            分析结果和建议
        """
        system_prompt = """你是一个专业的数据分析师。你需要：
1. 理解用户的数据和分析需求
2. 提供专业的数据分析建议
3. 建议合适的分析方法和可视化方案
4. 用中文回复，语言简洁专业"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"数据描述：{data_description}\n分析需求：{analysis_request}"}
        ]
        
        return self.chat(messages)
    
    def plan_analysis_steps(self, data_info: Dict[str, Any], user_goal: str) -> List[str]:
        """
        让大模型规划分析步骤
        
        Args:
            data_info: 数据信息字典
            user_goal: 用户目标
        
        Returns:
            分析步骤列表
        """
        system_prompt = """你是一个数据分析规划师。根据数据特征和用户目标，制定详细的分析计划。
请返回一个JSON格式的步骤列表，每个步骤包含：
- step_name: 步骤名称
- description: 步骤描述
- tools_needed: 需要的工具
例如：[{"step_name": "数据清洗", "description": "处理缺失值", "tools_needed": ["pandas"]}]"""
        
        data_summary = f"""
数据类型: {data_info.get('file_type', '未知')}
数据形状: {data_info.get('shape', '未知')}
列名: {data_info.get('columns', [])}
数据类型: {data_info.get('dtypes', {})}
缺失值: {data_info.get('missing_values', {})}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"数据信息：{data_summary}\n用户目标：{user_goal}\n请制定分析计划："}
        ]
        
        response = self.chat(messages, temperature=0.3)
        
        try:
            # 尝试解析JSON格式的回复
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                steps_data = json.loads(json_match.group())
                return [f"{step['step_name']}: {step['description']}" for step in steps_data]
            else:
                # 如果不是JSON格式，按行分割
                return [line.strip() for line in response.split('\n') if line.strip()]
        except:
            # 解析失败时返回原始文本按行分割
            return [line.strip() for line in response.split('\n') if line.strip()]
    
    def generate_insights(self, analysis_results: Dict[str, Any]) -> str:
        """
        基于分析结果生成洞察
        
        Args:
            analysis_results: 分析结果字典
        
        Returns:
            洞察和建议文本
        """
        system_prompt = """你是一个资深数据科学家。根据分析结果，提供深入的业务洞察和建议。
请用中文回复，包含：
1. 关键发现
2. 趋势分析
3. 异常或特殊情况
4. 业务建议"""
        
        results_text = json.dumps(analysis_results, ensure_ascii=False, indent=2)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"分析结果：{results_text}\n请提供洞察："}
        ]
        
        return self.chat(messages)