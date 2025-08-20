"""
HTML报告生成器 - 将分析结果转换为美观的HTML报告
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from jinja2 import Template


class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def generate_report(self, analysis_result: Dict[str, Any], 
                       title: str = "数据分析报告") -> str:
        """
        生成HTML报告
        
        Args:
            analysis_result: Agent分析结果
            title: 报告标题
            
        Returns:
            HTML报告内容
        """
        # 准备报告数据
        report_data = self._prepare_report_data(analysis_result, title)
        
        # 渲染模板
        template = Template(self.template)
        html_content = template.render(**report_data)
        
        return html_content
    
    def save_report(self, html_content: str, file_path: str) -> str:
        """
        保存HTML报告到文件
        
        Args:
            html_content: HTML内容
            file_path: 保存路径
            
        Returns:
            实际保存的文件路径
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    def _prepare_report_data(self, analysis_result: Dict[str, Any], title: str) -> Dict[str, Any]:
        """准备报告数据"""
        
        # 基础信息
        report_data = {
            'title': title,
            'timestamp': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
            'query': analysis_result.get('query', ''),
            'insights': analysis_result.get('insights', ''),
            'has_data': False,
            'sections': []
        }
        
        # 处理执行结果
        execution = analysis_result.get('execution', {})
        
        # 数据概览部分
        data_section = self._create_data_overview_section(execution)
        if data_section:
            report_data['sections'].append(data_section)
            report_data['has_data'] = True
        
        # 统计分析部分
        stats_section = self._create_stats_section(execution)
        if stats_section:
            report_data['sections'].append(stats_section)
        
        # 可视化部分
        viz_section = self._create_visualization_section(execution)
        if viz_section:
            report_data['sections'].append(viz_section)
        
        # 异常值分析部分
        outliers_section = self._create_outliers_section(execution)
        if outliers_section:
            report_data['sections'].append(outliers_section)
        
        # 趋势分析部分
        trend_section = self._create_trend_section(execution)
        if trend_section:
            report_data['sections'].append(trend_section)
        
        # 聚类分析部分
        clustering_section = self._create_clustering_section(execution)
        if clustering_section:
            report_data['sections'].append(clustering_section)
        
        # 执行日志部分
        log_section = self._create_log_section(analysis_result.get('execution_log', []))
        if log_section:
            report_data['sections'].append(log_section)
        
        return report_data
    
    def _create_data_overview_section(self, execution: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建数据概览部分"""
        for step_key, step_data in execution.items():
            if step_data.get('action') == 'read_file' and step_data.get('success'):
                result = step_data.get('result', {})
                file_info = result.get('file_info', {})
                
                return {
                    'title': '数据概览',
                    'type': 'data_overview',
                    'content': {
                        'file_name': file_info.get('file_name', '未知'),
                        'file_type': file_info.get('file_type', '未知'),
                        'file_size': self._format_size(file_info.get('file_size', 0)),
                        'shape': file_info.get('shape', '未知'),
                        'columns': file_info.get('columns', []),
                        'data_summary': result.get('data_summary', '')
                    }
                }
        return None
    
    def _create_stats_section(self, execution: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建统计分析部分"""
        for step_key, step_data in execution.items():
            if step_data.get('action') == 'analyze_basic_stats' and step_data.get('success'):
                result = step_data.get('result', {}).get('results', {})
                
                return {
                    'title': '统计分析',
                    'type': 'statistics',
                    'content': {
                        'basic_info': result.get('basic_info', {}),
                        'numeric_summary': result.get('numeric_summary', {}),
                        'categorical_summary': result.get('categorical_summary', {}),
                        'missing_analysis': result.get('missing_analysis', {})
                    }
                }
        return None
    
    def _create_visualization_section(self, execution: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建可视化部分"""
        for step_key, step_data in execution.items():
            if step_data.get('action') == 'create_visualizations' and step_data.get('success'):
                charts = step_data.get('result', {}).get('results', {})
                
                if charts:
                    return {
                        'title': '数据可视化',
                        'type': 'visualizations',
                        'content': {
                            'charts': charts
                        }
                    }
        return None
    
    def _create_outliers_section(self, execution: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建异常值分析部分"""
        for step_key, step_data in execution.items():
            if step_data.get('action') == 'detect_outliers' and step_data.get('success'):
                outliers = step_data.get('result', {}).get('results', {})
                
                return {
                    'title': '异常值检测',
                    'type': 'outliers',
                    'content': outliers
                }
        return None
    
    def _create_trend_section(self, execution: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建趋势分析部分"""
        for step_key, step_data in execution.items():
            if step_data.get('action') == 'trend_analysis' and step_data.get('success'):
                trends = step_data.get('result', {}).get('results', {})
                
                if 'error' not in trends:
                    return {
                        'title': '趋势分析',
                        'type': 'trends',
                        'content': trends
                    }
        return None
    
    def _create_clustering_section(self, execution: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建聚类分析部分"""
        for step_key, step_data in execution.items():
            if step_data.get('action') == 'clustering_analysis' and step_data.get('success'):
                clustering = step_data.get('result', {}).get('results', {})
                
                if 'error' not in clustering:
                    return {
                        'title': '聚类分析',
                        'type': 'clustering',
                        'content': clustering
                    }
        return None
    
    def _create_log_section(self, execution_log: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """创建执行日志部分"""
        if execution_log:
            return {
                'title': '📝 执行日志',
                'type': 'execution_log',
                'content': {
                    'logs': execution_log
                }
            }
        return None
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _get_html_template(self) -> str:
        """获取HTML模板"""
        return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .timestamp {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .query-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .query-section h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .query-text {
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            font-style: italic;
        }
        
        .section {
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section-header {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .section-header h2 {
            color: #495057;
            font-size: 1.4em;
        }
        
        .section-content {
            padding: 25px;
        }
        
        .data-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .info-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        
        .info-card h4 {
            color: #28a745;
            margin-bottom: 10px;
        }
        
        .stats-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        .stats-table th,
        .stats-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        .stats-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        .stats-table tr:hover {
            background-color: #f8f9fa;
        }
        
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        
        .insights-section {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .insights-section h2 {
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .insights-content {
            font-size: 1.1em;
            line-height: 1.8;
            white-space: pre-line;
        }
        
        .log-entry {
            background: #f8f9fa;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        .log-timestamp {
            color: #6c757d;
            font-size: 0.8em;
        }
        
        .error {
            color: #dc3545;
        }
        
        .success {
            color: #28a745;
        }
        
        .warning {
            color: #ffc107;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .data-info {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>{{ title }}</h1>
            <div class="timestamp">生成时间: {{ timestamp }}</div>
        </div>
        
        <!-- 查询部分 -->
        {% if query %}
        <div class="query-section">
            <h2>分析目标</h2>
            <div class="query-text">{{ query }}</div>
        </div>
        {% endif %}
        
        <!-- 各个分析部分 -->
        {% for section in sections %}
        <div class="section">
            <div class="section-header">
                <h2>{{ section.title }}</h2>
            </div>
            <div class="section-content">
                
                <!-- 数据概览 -->
                {% if section.type == 'data_overview' %}
                <div class="data-info">
                    <div class="info-card">
                        <h4>文件信息</h4>
                        <p><strong>文件名:</strong> {{ section.content.file_name }}</p>
                        <p><strong>类型:</strong> {{ section.content.file_type }}</p>
                        <p><strong>大小:</strong> {{ section.content.file_size }}</p>
                        {% if section.content.shape %}
                        <p><strong>形状:</strong> {{ section.content.shape[0] }} 行 × {{ section.content.shape[1] }} 列</p>
                        {% endif %}
                    </div>
                    <div class="info-card">
                        <h4>数据摘要</h4>
                        <pre style="white-space: pre-line;">{{ section.content.data_summary }}</pre>
                    </div>
                </div>
                {% endif %}
                
                <!-- 统计分析 -->
                {% if section.type == 'statistics' %}
                {% if section.content.numeric_summary %}
                <h4>数值变量统计</h4>
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>变量</th>
                            <th>均值</th>
                            <th>标准差</th>
                            <th>最小值</th>
                            <th>最大值</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for col, stats in section.content.numeric_summary.items() %}
                        <tr>
                            <td><strong>{{ col }}</strong></td>
                            <td>{{ "%.2f"|format(stats.mean) }}</td>
                            <td>{{ "%.2f"|format(stats.std) }}</td>
                            <td>{{ "%.2f"|format(stats.min) }}</td>
                            <td>{{ "%.2f"|format(stats.max) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
                
                {% if section.content.missing_analysis %}
                <h4>缺失值分析</h4>
                <p><strong>完整记录:</strong> {{ section.content.missing_analysis.complete_rows }} 行</p>
                <p><strong>有缺失值的记录:</strong> {{ section.content.missing_analysis.rows_with_missing }} 行</p>
                {% endif %}
                {% endif %}
                
                <!-- 可视化 -->
                {% if section.type == 'visualizations' %}
                {% for chart_name, chart_html in section.content.charts.items() %}
                <div class="chart-container">
                    <h4>{{ chart_name }}</h4>
                    {{ chart_html|safe }}
                </div>
                {% endfor %}
                {% endif %}
                
                <!-- 异常值检测 -->
                {% if section.type == 'outliers' %}
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>变量</th>
                            <th>IQR方法异常值</th>
                            <th>Z-score方法异常值</th>
                            <th>异常值比例</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for col, outlier_info in section.content.items() %}
                        <tr>
                            <td><strong>{{ col }}</strong></td>
                            <td>{{ outlier_info.iqr_method.count }}</td>
                            <td>{{ outlier_info.zscore_method.count }}</td>
                            <td>{{ "%.1f%%"|format(outlier_info.iqr_method.percentage) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
                
                <!-- 趋势分析 -->
                {% if section.type == 'trends' %}
                <div class="data-info">
                    <div class="info-card">
                        <h4>时间范围</h4>
                        <p><strong>开始时间:</strong> {{ section.content.time_range.start }}</p>
                        <p><strong>结束时间:</strong> {{ section.content.time_range.end }}</p>
                        <p><strong>时间跨度:</strong> {{ section.content.time_range.duration_days }} 天</p>
                    </div>
                </div>
                
                {% if section.content.trends %}
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>变量</th>
                            <th>趋势方向</th>
                            <th>相关强度</th>
                            <th>显著性</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for col, trend_info in section.content.trends.items() %}
                        <tr>
                            <td><strong>{{ col }}</strong></td>
                            <td>{{ trend_info.trend_direction }}</td>
                            <td>{{ trend_info.strength }}</td>
                            <td>{{ "%.4f"|format(trend_info.p_value) if trend_info.p_value else 'N/A' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
                {% endif %}
                
                <!-- 聚类分析 -->
                {% if section.type == 'clustering' %}
                <div class="data-info">
                    <div class="info-card">
                        <h4>聚类信息</h4>
                        <p><strong>聚类数量:</strong> {{ section.content.n_clusters }}</p>
                        <p><strong>使用特征:</strong> {{ ", ".join(section.content.features_used) }}</p>
                        <p><strong>聚类质量:</strong> {{ "%.2f"|format(section.content.inertia) }}</p>
                    </div>
                </div>
                
                {% if section.content.cluster_statistics %}
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>聚类</th>
                            <th>样本数量</th>
                            <th>占比</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cluster_name, cluster_info in section.content.cluster_statistics.items() %}
                        <tr>
                            <td><strong>{{ cluster_name }}</strong></td>
                            <td>{{ cluster_info.size }}</td>
                            <td>{{ "%.1f%%"|format(cluster_info.percentage) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
                {% endif %}
                
                <!-- 执行日志 -->
                {% if section.type == 'execution_log' %}
                {% for log in section.content.logs %}
                <div class="log-entry">
                    <span class="log-timestamp">{{ log.timestamp }}</span> - 
                    <strong>{{ log.action }}</strong>
                    {% if log.details %}
                    <br><small>{{ log.details }}</small>
                    {% endif %}
                </div>
                {% endfor %}
                {% endif %}
                
            </div>
        </div>
        {% endfor %}
        
        <!-- 洞察部分 -->
        {% if insights %}
        <div class="insights-section">
            <h2>智能洞察</h2>
            <div class="insights-content">{{ insights }}</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
        '''