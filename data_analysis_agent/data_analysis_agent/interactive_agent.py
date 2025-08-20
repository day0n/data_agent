"""
半自主数据分析Agent - 交互式版本
Agent提供建议，用户做决策
"""
import pandas as pd
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from .core.llm_client import AliyunLLMClient
from .core.report_generator import HTMLReportGenerator


class InteractiveDataAgent:
    """
    半自主数据分析Agent
    
    特点：
    1. Agent分析数据并提供建议
    2. 用户选择要执行的分析
    3. Agent执行选定的分析
    4. 支持多轮对话
    """
    
    def __init__(self, api_key: str = None):
        """初始化Agent"""
        self.llm = AliyunLLMClient(api_key)
        self.report_generator = HTMLReportGenerator()
        
        # 当前状态
        self.current_data = None
        self.current_file_info = {}
        self.analysis_results = {}
        self.conversation_history = []
        
        # 可选分析类型
        self.available_analyses = {
            '1': {'name': '基础统计分析', 'desc': '数据概览、均值、标准差等基础统计'},
            '2': {'name': '缺失值分析', 'desc': '检查数据完整性和缺失值分布'},
            '3': {'name': '数据分布分析', 'desc': '查看各变量的分布情况'},
            '4': {'name': '相关性分析', 'desc': '分析变量之间的相关关系'},
            '5': {'name': '异常值检测', 'desc': '识别数据中的异常值'},
            '6': {'name': '简单趋势分析', 'desc': '时间序列数据的趋势分析'},
            '7': {'name': '分类变量分析', 'desc': '分类变量的频次和分布'},
            'all': {'name': '完整分析', 'desc': '执行所有适用的分析'}
        }
    
    def start_analysis(self, file_path: str) -> None:
        """开始交互式分析流程"""
        print("🤖 你好！我是数据分析Agent，我将帮助你分析数据。")
        print("=" * 60)
        
        # 步骤1: 加载数据
        if not self._load_data(file_path):
            return
        
        # 步骤2: 数据初步检查和建议
        suggestions = self._analyze_and_suggest()
        
        # 步骤3: 用户选择分析
        selected_analyses = self._user_select_analyses(suggestions)
        
        # 步骤4: 执行分析
        self._execute_analyses(selected_analyses)
        
        # 步骤5: 生成报告
        self._generate_final_report()
        
        # 步骤6: 继续对话
        self._continue_conversation()
    
    def _load_data(self, file_path: str) -> bool:
        """加载并检查数据"""
        print(f"📂 正在加载文件: {os.path.basename(file_path)}")
        
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                encodings = ['utf-8', 'gbk', 'gb2312']
                for encoding in encodings:
                    try:
                        self.current_data = pd.read_csv(file_path, encoding=encoding)
                        print(f"✅ 使用{encoding}编码成功读取CSV文件")
                        break
                    except UnicodeDecodeError:
                        continue
                if self.current_data is None:
                    print("❌ 无法读取CSV文件，请检查文件编码")
                    return False
                    
            elif file_ext in ['.xlsx', '.xls']:
                self.current_data = pd.read_excel(file_path)
                print("✅ 成功读取Excel文件")
            else:
                print(f"❌ 不支持的文件格式: {file_ext}")
                print("支持的格式: .csv, .xlsx, .xls")
                return False
            
            # 保存文件信息
            self.current_file_info = {
                'file_name': os.path.basename(file_path),
                'shape': self.current_data.shape,
                'columns': self.current_data.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in self.current_data.dtypes.items()}
            }
            
            # 显示基本信息
            print(f"📊 数据基本信息:")
            print(f"   • 行数: {self.current_data.shape[0]}")
            print(f"   • 列数: {self.current_data.shape[1]}")
            print(f"   • 列名: {', '.join(self.current_data.columns[:5])}")
            if len(self.current_data.columns) > 5:
                print(f"         (还有{len(self.current_data.columns)-5}列...)")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ 读取文件失败: {str(e)}")
            return False
    
    def _analyze_and_suggest(self) -> List[str]:
        """分析数据特征并提供建议"""
        print("🧠 正在分析数据特征...")
        
        df = self.current_data
        suggestions = []
        
        # 分析数据类型
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        datetime_cols = []
        
        # 检查可能的时间列
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', '时间', '日期']):
                try:
                    pd.to_datetime(df[col])
                    datetime_cols.append(col)
                except:
                    pass
        
        # 基于数据特征给出建议
        print("💡 基于你的数据特征，我建议进行以下分析:")
        print()
        
        # 必要的基础分析
        suggestions.append('1')  # 基础统计
        print("🔹 基础统计分析 - 必须进行，了解数据基本特征")
        
        # 缺失值检查
        if df.isnull().sum().sum() > 0:
            suggestions.append('2')
            print("🔸 缺失值分析 - 发现缺失数据，建议检查")
        
        # 数值型变量分析
        if len(numeric_cols) > 0:
            suggestions.append('3')
            print(f"🔹 数据分布分析 - 发现{len(numeric_cols)}个数值型变量")
            
            if len(numeric_cols) >= 2:
                suggestions.append('4')
                print("🔹 相关性分析 - 多个数值变量，可分析相关性")
        
        # 分类变量分析
        if len(categorical_cols) > 0:
            suggestions.append('7')
            print(f"🔹 分类变量分析 - 发现{len(categorical_cols)}个分类变量")
        
        # 时间序列分析
        if len(datetime_cols) > 0:
            suggestions.append('6')
            print(f"🔹 趋势分析 - 发现时间列: {', '.join(datetime_cols)}")
        
        print()
        return suggestions
    
    def _user_select_analyses(self, suggestions: List[str]) -> List[str]:
        """用户选择要执行的分析"""
        print("请选择要执行的分析 (可多选，用空格分隔):")
        print()
        
        # 显示所有可用分析
        for key, info in self.available_analyses.items():
            if key == 'all':
                continue
            status = "✅ 推荐" if key in suggestions else "⚪ 可选"
            print(f"{key}. {info['name']} - {info['desc']} {status}")
        
        print("all. 完整分析 - 执行所有适用的分析")
        print()
        print("💡 我的建议: " + " ".join(suggestions))
        print()
        
        while True:
            user_input = input("请选择分析类型 (例如: 1 3 4 或 all): ").strip()
            
            if not user_input:
                print("❌ 请输入选择")
                continue
            
            if user_input.lower() == 'all':
                # 选择所有推荐的分析
                return suggestions + ['4', '5']  # 添加一些额外分析
            
            # 解析用户输入
            choices = user_input.split()
            valid_choices = []
            
            for choice in choices:
                if choice in self.available_analyses and choice != 'all':
                    valid_choices.append(choice)
                else:
                    print(f"⚠️  无效选择: {choice}")
            
            if valid_choices:
                print(f"✅ 将执行以下分析: {', '.join([self.available_analyses[c]['name'] for c in valid_choices])}")
                return valid_choices
            else:
                print("❌ 没有有效的选择，请重新输入")
    
    def _execute_analyses(self, selected_analyses: List[str]) -> None:
        """执行选定的分析"""
        print()
        print("🔬 开始执行分析...")
        print("=" * 50)
        
        for analysis_id in selected_analyses:
            analysis_name = self.available_analyses[analysis_id]['name']
            print(f"📊 正在执行: {analysis_name}")
            
            if analysis_id == '1':
                self._basic_statistics()
            elif analysis_id == '2':
                self._missing_value_analysis()
            elif analysis_id == '3':
                self._distribution_analysis()
            elif analysis_id == '4':
                self._correlation_analysis()
            elif analysis_id == '5':
                self._outlier_detection()
            elif analysis_id == '6':
                self._trend_analysis()
            elif analysis_id == '7':
                self._categorical_analysis()
            
            print(f"✅ 完成: {analysis_name}")
            print()
    
    def _basic_statistics(self) -> None:
        """基础统计分析"""
        df = self.current_data
        
        basic_info = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'duplicated_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            numeric_summary = df[numeric_cols].describe().to_dict()
        else:
            numeric_summary = {}
        
        self.analysis_results['basic_statistics'] = {
            'basic_info': basic_info,
            'numeric_summary': numeric_summary
        }
        
        # 显示关键信息
        print(f"   • 数据行数: {basic_info['total_rows']}")
        print(f"   • 重复行数: {basic_info['duplicated_rows']}")
        if numeric_summary:
            print(f"   • 数值型变量: {len(numeric_cols)}个")
    
    def _missing_value_analysis(self) -> None:
        """缺失值分析"""
        df = self.current_data
        missing_data = df.isnull().sum()
        
        missing_info = {
            'missing_counts': missing_data[missing_data > 0].to_dict(),
            'missing_percentage': (missing_data / len(df) * 100)[missing_data > 0].to_dict(),
            'complete_rows': len(df.dropna()),
            'rows_with_missing': len(df) - len(df.dropna())
        }
        
        self.analysis_results['missing_analysis'] = missing_info
        
        if missing_info['rows_with_missing'] > 0:
            print(f"   ⚠️  发现缺失值: {missing_info['rows_with_missing']}行受影响")
            for col, count in list(missing_info['missing_counts'].items())[:3]:
                print(f"     • {col}: {count}个缺失值 ({missing_info['missing_percentage'][col]:.1f}%)")
        else:
            print("   ✅ 无缺失值")
    
    def _distribution_analysis(self) -> None:
        """分布分析和可视化"""
        try:
            import plotly.express as px
            
            df = self.current_data
            numeric_cols = df.select_dtypes(include=['number']).columns
            charts = {}
            
            if len(numeric_cols) > 0:
                # 第一个数值列的分布图
                col = numeric_cols[0]
                fig = px.histogram(df, x=col, title=f'{col} 分布图')
                charts['distribution'] = fig.to_html(include_plotlyjs='cdn')
                print(f"   📈 已生成 {col} 的分布图")
                
            self.analysis_results['visualizations'] = charts
            
        except ImportError:
            print("   ⚠️  未安装plotly，跳过可视化")
        except Exception as e:
            print(f"   ⚠️  可视化失败: {str(e)}")
    
    def _correlation_analysis(self) -> None:
        """相关性分析"""
        try:
            import plotly.express as px
            
            df = self.current_data
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                
                # 找出最强相关性
                corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        corr_val = corr_matrix.iloc[i, j]
                        corr_pairs.append((col1, col2, abs(corr_val), corr_val))
                
                # 按相关性强度排序
                corr_pairs.sort(key=lambda x: x[2], reverse=True)
                
                self.analysis_results['correlation'] = {
                    'correlation_matrix': corr_matrix.to_dict(),
                    'top_correlations': corr_pairs[:5]
                }
                
                # 生成热图
                fig = px.imshow(corr_matrix, title='相关性热图', 
                               color_continuous_scale='RdBu_r', text_auto=True)
                
                if 'visualizations' not in self.analysis_results:
                    self.analysis_results['visualizations'] = {}
                self.analysis_results['visualizations']['correlation_heatmap'] = fig.to_html(include_plotlyjs='cdn')
                
                # 显示最强相关性
                if corr_pairs:
                    col1, col2, abs_corr, corr = corr_pairs[0]
                    print(f"   🔗 最强相关性: {col1} ↔ {col2} (r={corr:.3f})")
                    
        except Exception as e:
            print(f"   ⚠️  相关性分析失败: {str(e)}")
    
    def _outlier_detection(self) -> None:
        """异常值检测"""
        df = self.current_data
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        outlier_info = {}
        total_outliers = 0
        
        for col in numeric_cols[:3]:  # 限制检测的列数
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            outlier_count = len(outliers)
            total_outliers += outlier_count
            
            outlier_info[col] = {
                'count': outlier_count,
                'percentage': outlier_count / len(df) * 100,
                'bounds': [lower_bound, upper_bound]
            }
        
        self.analysis_results['outliers'] = outlier_info
        print(f"   🎯 检测到 {total_outliers} 个异常值")
    
    def _trend_analysis(self) -> None:
        """简单趋势分析"""
        print("   📈 尝试识别时间相关列进行趋势分析")
        # 简化实现，实际可以更复杂
        self.analysis_results['trends'] = {'message': '需要明确的时间列才能进行趋势分析'}
    
    def _categorical_analysis(self) -> None:
        """分类变量分析"""
        try:
            import plotly.express as px
            
            df = self.current_data
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            
            if len(categorical_cols) > 0:
                col = categorical_cols[0]
                value_counts = df[col].value_counts().head(8)
                
                # 生成饼图
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                           title=f'{col} 分布饼图')
                
                if 'visualizations' not in self.analysis_results:
                    self.analysis_results['visualizations'] = {}
                self.analysis_results['visualizations']['category_pie'] = fig.to_html(include_plotlyjs='cdn')
                
                print(f"   📊 已分析 {col}，发现 {df[col].nunique()} 个不同类别")
                
        except Exception as e:
            print(f"   ⚠️  分类分析失败: {str(e)}")
    
    def _generate_final_report(self) -> None:
        """生成最终报告"""
        print("📄 正在生成分析报告...")
        
        # 构造分析结果
        mock_result = {
            'query': '交互式数据分析',
            'insights': self._get_ai_insights(),
            'execution': self._format_results_for_report(),
            'execution_log': []
        }
        
        # 生成HTML报告
        html_content = self.report_generator.generate_report(
            mock_result,
            title=f"交互式分析报告 - {self.current_file_info['file_name']}"
        )
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"interactive_report_{timestamp}.html"
        self.report_generator.save_report(html_content, report_path)
        
        print(f"✅ 报告已生成: {report_path}")
        
        # 询问是否打开报告
        open_report = input("是否要在浏览器中查看报告? (y/n): ").strip().lower()
        if open_report in ['y', 'yes', '是']:
            import webbrowser
            webbrowser.open(f'file://{os.path.abspath(report_path)}')
    
    def _get_ai_insights(self) -> str:
        """获取AI生成的洞察"""
        try:
            # 准备分析结果摘要
            summary = f"数据包含{self.current_file_info['shape'][0]}行{self.current_file_info['shape'][1]}列。"
            if 'basic_statistics' in self.analysis_results:
                basic = self.analysis_results['basic_statistics']['basic_info']
                if basic['duplicated_rows'] > 0:
                    summary += f"发现{basic['duplicated_rows']}行重复数据。"
            
            insights = self.llm.analyze_data(summary, "综合分析数据特征并给出业务建议")
            return insights
        except:
            return "基于分析结果，数据质量总体良好。建议根据具体业务需求进行深入分析。"
    
    def _format_results_for_report(self) -> Dict[str, Any]:
        """格式化结果用于报告"""
        execution = {}
        
        if 'basic_statistics' in self.analysis_results:
            execution['step_stats'] = {
                'action': 'analyze_basic_stats',
                'success': True,
                'result': {'results': self.analysis_results['basic_statistics']}
            }
        
        if 'visualizations' in self.analysis_results:
            execution['step_viz'] = {
                'action': 'create_visualizations',
                'success': True,
                'result': {'results': self.analysis_results['visualizations']}
            }
        
        return execution
    
    def _continue_conversation(self) -> None:
        """继续对话"""
        print()
        print("💬 还有什么问题吗？输入 'quit' 退出")
        
        while True:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 简单回复
            response = self.llm.chat([
                {"role": "system", "content": "你是一个数据分析助手，刚刚完成了数据分析。请简洁回答用户问题。"},
                {"role": "user", "content": user_input}
            ])
            
            print(f"🤖: {response}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python interactive_agent.py <文件路径>")
        print("示例: python interactive_agent.py data.csv")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    # 启动交互式分析
    agent = InteractiveDataAgent()
    agent.start_analysis(file_path)