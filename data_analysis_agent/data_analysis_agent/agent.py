"""
简化版数据分析Agent
专注于核心功能：读取数据、分析、生成报告
"""
import pandas as pd
import os
from typing import Dict, Any, Optional
from datetime import datetime

from .core.llm_client import AliyunLLMClient
from .core.report_generator import HTMLReportGenerator


class DataAnalysisAgent:
    """
    数据分析Agent
    """
    
    def __init__(self, api_key: str = None, test_mode: bool = False):
        self.llm = AliyunLLMClient(api_key, init_client=not test_mode)
        self.report_generator = HTMLReportGenerator()
        self.test_mode = test_mode
        
        self.current_data = None
        self.current_file_info = {}
        self.analysis_results = {}
    
    def analyze_file(self, file_path: str, analysis_goal: str = "分析数据") -> str:
        """
        分析文件并生成报告
        """
        print(f"开始分析文件: {os.path.basename(file_path)}")
        
        # 读取数据
        if not self._load_data(file_path):
            return None
        
        # 执行分析
        print("正在进行数据分析...")
        self._perform_analysis()
        
        # 生成AI洞察
        print("正在生成分析洞察...")
        insights = self._generate_insights(analysis_goal)
        
        # 生成报告
        print("正在生成HTML报告...")
        report_path = self._generate_report(analysis_goal, insights)
        
        print(f"分析完成，报告已保存到: {report_path}")
        return report_path
    
    def _load_data(self, file_path: str) -> bool:
        """加载数据文件"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                encodings = ['utf-8', 'gbk', 'gb2312']
                for encoding in encodings:
                    try:
                        self.current_data = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            elif file_ext in ['.xlsx', '.xls']:
                self.current_data = pd.read_excel(file_path)
            else:
                print(f"不支持的文件格式: {file_ext}")
                return False
            
            self.current_file_info = {
                'file_name': os.path.basename(file_path),
                'file_path': file_path,
                'file_type': file_ext,
                'file_size': os.path.getsize(file_path),
                'shape': self.current_data.shape,
                'columns': self.current_data.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in self.current_data.dtypes.items()}
            }
            
            print(f"文件已加载: {self.current_data.shape[0]}行 x {self.current_data.shape[1]}列")
            return True
            
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return False
    
    def _perform_analysis(self) -> None:
        """执行核心数据分析"""
        df = self.current_data
        
        # 基础统计信息
        self.analysis_results['basic_info'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'duplicated_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        # 数值型列分析
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            self.analysis_results['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # 分类型列分析
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            cat_summary = {}
            for col in categorical_cols[:5]:
                cat_summary[col] = {
                    'unique_count': df[col].nunique(),
                    'top_values': df[col].value_counts().head(3).to_dict(),
                    'missing_count': df[col].isnull().sum()
                }
            self.analysis_results['categorical_summary'] = cat_summary
        
        # 缺失值分析
        missing_data = df.isnull().sum()
        self.analysis_results['missing_analysis'] = {
            'missing_counts': missing_data[missing_data > 0].to_dict(),
            'missing_percentage': (missing_data / len(df) * 100)[missing_data > 0].to_dict(),
            'complete_rows': len(df.dropna()),
            'rows_with_missing': len(df) - len(df.dropna())
        }
        
        # 创建可视化
        self._create_visualizations()
    
    def _create_visualizations(self) -> None:
        """创建可视化图表"""
        try:
            import plotly.express as px
            
            charts = {}
            df = self.current_data
            
            # 数值型列的分布图
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                fig = px.histogram(df, x=col, title=f'{col} 分布图')
                charts['distribution'] = fig.to_html(include_plotlyjs='cdn')
                
                # 相关性热图
                if len(numeric_cols) >= 2:
                    corr_matrix = df[numeric_cols].corr()
                    fig = px.imshow(corr_matrix, title='变量相关性热图',
                                  color_continuous_scale='RdBu_r', text_auto=True)
                    charts['correlation'] = fig.to_html(include_plotlyjs='cdn')
            
            # 分类型列的饼图
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                col = categorical_cols[0]
                value_counts = df[col].value_counts().head(8)
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                           title=f'{col} 分布饼图')
                charts['category_pie'] = fig.to_html(include_plotlyjs='cdn')
            
            self.analysis_results['visualizations'] = charts
            
        except Exception as e:
            print(f"可视化生成失败: {str(e)}")
            self.analysis_results['visualizations'] = {}
    
    def _generate_insights(self, analysis_goal: str) -> str:
        """使用LLM生成分析洞察"""
        data_desc = f"""
文件名: {self.current_file_info['file_name']}
数据形状: {self.current_file_info['shape'][0]}行 x {self.current_file_info['shape'][1]}列
列名: {', '.join(self.current_file_info['columns'][:10])}

基础统计:
- 总记录数: {self.analysis_results['basic_info']['total_rows']}
- 重复记录数: {self.analysis_results['basic_info']['duplicated_rows']}
- 缺失记录数: {self.analysis_results['missing_analysis']['rows_with_missing']}
"""
        
        if 'numeric_summary' in self.analysis_results:
            data_desc += "\n数值型变量摘要:\n"
            for col, stats in list(self.analysis_results['numeric_summary'].items())[:5]:
                data_desc += f"- {col}: 均值={stats['mean']:.2f}, 标准差={stats['std']:.2f}\n"
        
        try:
            insights = self.llm.analyze_data(data_desc, analysis_goal)
            return insights
        except Exception as e:
            return f"AI洞察生成失败: {str(e)}\n\n基于分析结果，这是一个包含{self.current_file_info['shape'][0]}条记录的数据集。"
    
    def _generate_report(self, analysis_goal: str, insights: str) -> str:
        """生成HTML报告"""
        mock_analysis_result = {
            'query': analysis_goal,
            'insights': insights,
            'execution': {
                'step_1': {
                    'action': 'read_file',
                    'success': True,
                    'result': {
                        'file_info': self.current_file_info,
                        'data_summary': f"数据包含{self.current_file_info['shape'][0]}行和{self.current_file_info['shape'][1]}列"
                    }
                },
                'step_2': {
                    'action': 'analyze_basic_stats',
                    'success': True,
                    'result': {
                        'results': {
                            'basic_info': self.analysis_results['basic_info'],
                            'numeric_summary': self.analysis_results.get('numeric_summary', {}),
                            'categorical_summary': self.analysis_results.get('categorical_summary', {}),
                            'missing_analysis': self.analysis_results['missing_analysis']
                        }
                    }
                }
            },
            'execution_log': [
                {'timestamp': datetime.now().isoformat(), 'action': '读取数据', 'details': {}},
                {'timestamp': datetime.now().isoformat(), 'action': '执行分析', 'details': {}},
                {'timestamp': datetime.now().isoformat(), 'action': '生成洞察', 'details': {}}
            ]
        }
        
        if 'visualizations' in self.analysis_results:
            mock_analysis_result['execution']['step_3'] = {
                'action': 'create_visualizations',
                'success': True,
                'result': {
                    'results': self.analysis_results['visualizations']
                }
            }
        
        html_content = self.report_generator.generate_report(
            mock_analysis_result, 
            title=f"数据分析报告 - {self.current_file_info['file_name']}"
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"analysis_report_{timestamp}.html"
        report_path = os.path.join(os.getcwd(), file_name)
        
        self.report_generator.save_report(html_content, report_path)
        return report_path


def analyze_data(file_path: str, goal: str = "分析数据", api_key: str = None) -> str:
    """
    快速分析数据文件
    """
    agent = DataAnalysisAgent(api_key)
    return agent.analyze_file(file_path, goal)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python simple_clean_agent.py <文件路径> [分析目标]")
        print("示例: python simple_clean_agent.py data.csv '分析销售趋势'")
        sys.exit(1)
    
    file_path = sys.argv[1]
    goal = sys.argv[2] if len(sys.argv) > 2 else "分析数据"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    report_path = analyze_data(file_path, goal)
    if report_path:
        print(f"分析完成，请打开报告: {report_path}")
    else:
        print("分析失败")
        sys.exit(1)