"""
创建示例数据用于测试Agent
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def create_sales_data(filename: str = "sales_data.csv") -> str:
    """创建销售数据示例"""
    np.random.seed(42)
    
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    data = []
    products = ['笔记本电脑', '台式电脑', '显示器', '键盘', '鼠标']
    regions = ['华北', '华南', '华东', '华西']
    
    for i, date in enumerate(dates):
        daily_records = np.random.randint(1, 5)
        for _ in range(daily_records):
            record = {
                'date': date.strftime('%Y-%m-%d'),
                'product': np.random.choice(products),
                'region': np.random.choice(regions),
                'sales_amount': np.random.normal(5000, 1500),
                'quantity': np.random.randint(1, 10),
                'discount_rate': np.random.uniform(0, 0.3)
            }
            
            # 添加异常值
            if np.random.random() < 0.02:
                record['sales_amount'] *= 5
            
            # 添加缺失值
            if np.random.random() < 0.05:
                record['discount_rate'] = np.nan
            
            data.append(record)
    
    df = pd.DataFrame(data)
    df['sales_amount'] = df['sales_amount'].round(2)
    df.to_csv(filename, index=False, encoding='utf-8')
    
    return filename


def create_customer_data(filename: str = "customer_data.csv") -> str:
    """创建客户数据示例"""
    np.random.seed(123)
    
    n_customers = 1000
    
    data = {
        'customer_id': [f'C{i:04d}' for i in range(1, n_customers + 1)],
        'age': np.random.normal(35, 12, n_customers).round().astype(int),
        'gender': np.random.choice(['男', '女'], n_customers),
        'city': np.random.choice(['北京', '上海', '广州', '深圳', '杭州', '成都'], n_customers),
        'annual_income': np.random.normal(80000, 25000, n_customers).round(2),
        'purchase_frequency': np.random.poisson(3, n_customers),
        'total_spent': np.random.exponential(5000, n_customers).round(2),
        'satisfaction_score': np.random.uniform(1, 5, n_customers).round(1)
    }
    
    df = pd.DataFrame(data)
    
    # 数据清理
    df['age'] = df['age'].clip(18, 80)
    df['annual_income'] = df['annual_income'].clip(20000, None)
    
    # 添加缺失值
    missing_indices = np.random.choice(df.index, size=int(0.03 * len(df)), replace=False)
    df.loc[missing_indices, 'satisfaction_score'] = np.nan
    
    df.to_csv(filename, index=False, encoding='utf-8')
    return filename


def create_stock_data(filename: str = "stock_data.csv") -> str:
    """创建股票价格数据示例"""
    np.random.seed(456)
    
    start_date = datetime(2023, 1, 1)
    dates = pd.bdate_range(start=start_date, periods=250)
    
    initial_price = 100
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = [initial_price]
    
    for return_rate in returns[1:]:
        new_price = prices[-1] * (1 + return_rate)
        prices.append(new_price)
    
    data = {
        'date': dates.strftime('%Y-%m-%d'),
        'open_price': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high_price': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low_price': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close_price': prices,
        'volume': np.random.lognormal(15, 0.5, len(dates)).astype(int),
        'market_cap': [p * 1000000 for p in prices]
    }
    
    df = pd.DataFrame(data)
    df = df.round(2)
    df['volume'] = df['volume'].astype(int)
    df['market_cap'] = df['market_cap'].astype(int)
    
    df.to_csv(filename, index=False, encoding='utf-8')
    return filename


if __name__ == "__main__":
    print("正在生成示例数据...")
    
    os.makedirs("examples", exist_ok=True)
    
    sales_file = create_sales_data("examples/sales_data.csv")
    customer_file = create_customer_data("examples/customer_data.csv")
    stock_file = create_stock_data("examples/stock_data.csv")
    
    print("示例数据已生成:")
    print(f"   销售数据: {sales_file}")
    print(f"   客户数据: {customer_file}")
    print(f"   股票数据: {stock_file}")
    print()
    print("使用方法:")
    print("   python simple_clean_agent.py examples/sales_data.csv '分析销售趋势'")
    print("   python interactive_agent.py examples/customer_data.csv")