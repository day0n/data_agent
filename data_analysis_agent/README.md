# 数据分析Agent - MVP版本

一个基于阿里云通义千问大模型的智能数据分析助手，支持自动分析数据并生成HTML报告。

## 核心功能

- **多格式支持**: CSV、Excel文件自动读取
- **智能分析**: 基于大模型的数据洞察生成
- **可视化**: 自动生成分布图、相关性图等
- **HTML报告**: 美观的分析报告，支持图表展示
- **半自主模式**: Agent建议分析，用户选择执行

## 快速开始

### 1. 安装依赖

```bash
# 使用uv管理项目（推荐）
uv sync

# 或者使用pip安装
pip install -e .
```

### 2. 设置API密钥

方式一：环境变量
```bash
export DASHSCOPE_API_KEY="sk-8f735e8d4a944cc7a0d00f9c2062fbde"
```

方式二：代码中直接使用（已配置默认密钥）

### 3. 开始分析

**简单模式（全自动）:**
```bash
uv run data-agent examples/simple_test_data.csv --goal "分析产品销售数据"
```

**交互模式（半自主）:**
```bash
uv run data-agent examples/simple_test_data.csv --interactive
```

**生成更多示例数据:**
```bash
uv run python examples/create_sample_data.py
```

## 使用示例

### 简单模式示例

```python
from data_analysis_agent import DataAnalysisAgent

# 创建Agent
agent = DataAnalysisAgent()

# 分析数据文件
report_path = agent.analyze_file("data.csv", "分析销售数据的主要趋势")

print(f"报告已生成: {report_path}")
```

### 交互模式示例

```python
from data_analysis_agent import InteractiveDataAgent

# 创建交互式Agent
agent = InteractiveDataAgent()

# 开始交互式分析
agent.start_analysis("customer_data.csv")
```

## Agent特性

### 简单模式 (DataAnalysisAgent)
- **全自动**: 加载数据 -> 分析 -> 生成报告
- **快速**: 一键生成完整分析报告
- **适合**: 快速数据探索和报告生成

### 交互模式 (InteractiveDataAgent) 
- **半自主**: Agent提供建议，用户选择分析
- **灵活**: 可选择执行特定分析类型
- **对话**: 支持多轮对话和问答
- **适合**: 深入探索和定制化分析

## 支持的分析类型

1. **基础统计分析** - 数据概览、均值、标准差等
2. **缺失值分析** - 数据完整性检查
3. **数据分布分析** - 直方图、分布特征
4. **相关性分析** - 变量间关系、热图
5. **异常值检测** - IQR方法检测异常值
6. **趋势分析** - 时间序列趋势识别
7. **分类变量分析** - 频次分析、饼图

## 报告展示

生成的HTML报告包含：
- 数据概览和基本信息
- 交互式图表（基于Plotly）
- AI生成的洞察和建议
- 详细的分析结果
- 执行日志和过程记录

## 项目结构

```
data_analysis_agent/
├── data_analysis_agent/       # 主包
│   ├── __init__.py           # 包初始化
│   ├── main.py               # 命令行入口
│   ├── agent.py              # 简单模式Agent
│   ├── interactive_agent.py  # 交互模式Agent
│   ├── core/                 # 核心模块
│   │   ├── llm_client.py     # 阿里云大模型API客户端
│   │   └── report_generator.py # HTML报告生成器
│   └── tools/                # 工具库
│       ├── document_processor.py # 文档处理工具
│       └── data_analyzer.py  # 数据分析工具
├── examples/                 # 示例和测试
│   ├── create_sample_data.py # 生成示例数据
│   └── simple_test_data.csv  # 测试数据
├── pyproject.toml           # 项目配置（uv/pip）
├── uv.lock                  # 依赖锁定文件
└── README.md               # 说明文档
```

## 配置说明

### API配置
默认使用阿里云百炼平台的通义千问模型，支持：
- API密钥: `sk-8f735e8d4a944cc7a0d00f9c2062fbde` (已配置)
- 模型: `qwen-plus`
- 基础URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`

### 文件支持
- CSV文件 (支持多种编码：UTF-8, GBK, GB2312)
- Excel文件 (.xlsx, .xls)
- PDF, Word文档 (完整版支持)

## 扩展功能TODO

### 高优先级
- [ ] **Web界面** - Streamlit/Flask简单UI
- [ ] **更多文件格式** - PDF、Word、JSON支持
- [ ] **时间序列预测** - 基于历史数据预测
- [ ] **导出功能** - PDF/Excel/PowerPoint报告导出

### 技术优化
- [ ] **缓存机制** - 分析结果缓存
- [ ] **异步处理** - 大文件异步分析
- [ ] **错误恢复** - 更好的异常处理
- [ ] **性能优化** - 内存和速度优化

## 已知限制

1. **文件大小**: 建议小于100MB的文件
2. **中文支持**: CSV文件编码可能需要调整
3. **图表样式**: 目前使用默认Plotly样式
4. **LLM依赖**: 需要稳定的网络连接到阿里云

