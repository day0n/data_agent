"""
数据分析工具 - 提供各种数据分析和统计功能
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from typing import Dict, Any, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DataAnalyzer:
    """数据分析工具类"""
    
    def __init__(self):
        self.results = {}
    
    def basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        基础统计分析
        
        Args:
            df: 数据框
            
        Returns:
            统计结果字典
        """
        results = {
            'shape': df.shape,
            'basic_info': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'duplicated_rows': df.duplicated().sum()
            }
        }
        
        # 数值型列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            results['numeric_summary'] = df[numeric_cols].describe().to_dict()
            results['correlation_matrix'] = df[numeric_cols].corr().to_dict()
        
        # 分类型列统计  
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            cat_summary = {}
            for col in categorical_cols[:10]:  # 限制列数
                cat_summary[col] = {
                    'unique_count': df[col].nunique(),
                    'top_values': df[col].value_counts().head().to_dict(),
                    'missing_count': df[col].isnull().sum()
                }
            results['categorical_summary'] = cat_summary
        
        # 缺失值分析
        missing_data = df.isnull().sum()
        results['missing_analysis'] = {
            'missing_counts': missing_data.to_dict(),
            'missing_percentage': (missing_data / len(df) * 100).to_dict(),
            'complete_rows': len(df.dropna()),
            'rows_with_missing': len(df) - len(df.dropna())
        }
        
        return results
    
    def detect_outliers(self, df: pd.DataFrame, columns: List[str] = None) -> Dict[str, Any]:
        """
        异常值检测
        
        Args:
            df: 数据框
            columns: 要检测的列名列表，默认检测所有数值列
            
        Returns:
            异常值检测结果
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        outliers_info = {}
        
        for col in columns:
            if col not in df.columns or df[col].dtype not in [np.int64, np.float64]:
                continue
                
            # IQR方法
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_iqr = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            # Z-score方法
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers_zscore = df[z_scores > 3]
            
            outliers_info[col] = {
                'iqr_method': {
                    'count': len(outliers_iqr),
                    'percentage': len(outliers_iqr) / len(df) * 100,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound
                },
                'zscore_method': {
                    'count': len(outliers_zscore),
                    'percentage': len(outliers_zscore) / len(df) * 100
                },
                'statistics': {
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max()
                }
            }
        
        return outliers_info
    
    def trend_analysis(self, df: pd.DataFrame, time_col: str = None, 
                      value_cols: List[str] = None) -> Dict[str, Any]:
        """
        趋势分析
        
        Args:
            df: 数据框
            time_col: 时间列名
            value_cols: 数值列名列表
            
        Returns:
            趋势分析结果
        """
        # 自动检测时间列
        if time_col is None:
            date_cols = df.select_dtypes(include=['datetime64', 'object']).columns
            for col in date_cols:
                try:
                    pd.to_datetime(df[col])
                    time_col = col
                    break
                except:
                    continue
        
        if time_col is None:
            return {"error": "未找到时间列，无法进行趋势分析"}
        
        # 转换时间列
        try:
            df[time_col] = pd.to_datetime(df[time_col])
        except:
            return {"error": f"无法将列 {time_col} 转换为时间格式"}
        
        # 自动选择数值列
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {
            'time_column': time_col,
            'time_range': {
                'start': df[time_col].min().strftime('%Y-%m-%d'),
                'end': df[time_col].max().strftime('%Y-%m-%d'),
                'duration_days': (df[time_col].max() - df[time_col].min()).days
            },
            'trends': {}
        }
        
        # 按时间排序
        df_sorted = df.sort_values(time_col)
        
        for col in value_cols[:5]:  # 限制分析的列数
            if col == time_col:
                continue
                
            # 计算趋势
            x = np.arange(len(df_sorted))
            y = df_sorted[col].fillna(df_sorted[col].mean())
            
            try:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                results['trends'][col] = {
                    'slope': slope,
                    'correlation': r_value,
                    'p_value': p_value,
                    'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.3 else 'weak'
                }
            except:
                results['trends'][col] = {'error': '无法计算趋势'}
        
        return results
    
    def clustering_analysis(self, df: pd.DataFrame, n_clusters: int = 3,
                          features: List[str] = None) -> Dict[str, Any]:
        """
        聚类分析
        
        Args:
            df: 数据框
            n_clusters: 聚类数量
            features: 用于聚类的特征列
            
        Returns:
            聚类分析结果
        """
        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(features) < 2:
            return {"error": "需要至少2个数值特征进行聚类分析"}
        
        # 准备数据
        data = df[features].fillna(df[features].mean())
        
        # 标准化
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        
        # K-means聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(data_scaled)
        
        # PCA降维用于可视化
        pca = PCA(n_components=2)
        data_pca = pca.fit_transform(data_scaled)
        
        results = {
            'n_clusters': n_clusters,
            'features_used': features,
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'inertia': kmeans.inertia_,
            'pca_explained_variance': pca.explained_variance_ratio_.tolist(),
            'cluster_distribution': pd.Series(clusters).value_counts().to_dict(),
            'pca_coordinates': data_pca.tolist(),
            'cluster_labels': clusters.tolist()
        }
        
        # 每个聚类的统计信息
        df_with_clusters = df[features].copy()
        df_with_clusters['cluster'] = clusters
        
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_data = df_with_clusters[df_with_clusters['cluster'] == i]
            cluster_stats[f'cluster_{i}'] = {
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(df) * 100,
                'mean_values': cluster_data[features].mean().to_dict()
            }
        
        results['cluster_statistics'] = cluster_stats
        
        return results
    
    def create_visualizations(self, df: pd.DataFrame, analysis_type: str = 'overview') -> Dict[str, Any]:
        """
        创建可视化图表
        
        Args:
            df: 数据框
            analysis_type: 分析类型 ('overview', 'correlation', 'distribution')
            
        Returns:
            包含图表HTML的字典
        """
        charts = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if analysis_type == 'overview' or analysis_type == 'all':
            # 数据概览图表
            if len(numeric_cols) > 0:
                # 直方图
                fig = px.histogram(df, x=numeric_cols[0], title=f'{numeric_cols[0]} 分布图')
                charts['histogram'] = fig.to_html(include_plotlyjs='cdn')
                
                # 箱线图
                if len(numeric_cols) > 1:
                    fig = px.box(df, y=numeric_cols[:4], title='数值变量箱线图')
                    charts['boxplot'] = fig.to_html(include_plotlyjs='cdn')
            
            # 饼图（分类变量）
            if len(categorical_cols) > 0:
                col = categorical_cols[0]
                value_counts = df[col].value_counts().head(10)
                fig = px.pie(values=value_counts.values, names=value_counts.index, 
                           title=f'{col} 分布饼图')
                charts['pie_chart'] = fig.to_html(include_plotlyjs='cdn')
        
        if analysis_type == 'correlation' or analysis_type == 'all':
            # 相关性热图
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                fig = px.imshow(corr_matrix, 
                              title='相关性热图',
                              color_continuous_scale='RdBu_r',
                              aspect='auto')
                charts['correlation_heatmap'] = fig.to_html(include_plotlyjs='cdn')
        
        if analysis_type == 'distribution' or analysis_type == 'all':
            # 分布对比图
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                               title=f'{numeric_cols[0]} vs {numeric_cols[1]} 散点图')
                charts['scatter_plot'] = fig.to_html(include_plotlyjs='cdn')
        
        return charts
    
    def generate_summary_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            df: 数据框
            
        Returns:
            综合分析结果
        """
        report = {
            'basic_stats': self.basic_statistics(df),
            'outliers': self.detect_outliers(df),
            'visualizations': self.create_visualizations(df, 'all')
        }
        
        # 尝试趋势分析
        try:
            trends = self.trend_analysis(df)
            if 'error' not in trends:
                report['trends'] = trends
        except:
            pass
        
        # 尝试聚类分析
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                clustering = self.clustering_analysis(df)
                if 'error' not in clustering:
                    report['clustering'] = clustering
        except:
            pass
        
        return report