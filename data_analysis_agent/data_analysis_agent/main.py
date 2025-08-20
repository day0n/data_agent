"""
数据分析Agent主程序入口
"""
import sys
import os
import argparse
from .agent import DataAnalysisAgent
from .interactive_agent import InteractiveDataAgent


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='数据分析Agent')
    parser.add_argument('file_path', help='数据文件路径')
    parser.add_argument('--goal', '-g', default='分析数据', help='分析目标')
    parser.add_argument('--interactive', '-i', action='store_true', help='使用交互模式')
    parser.add_argument('--api-key', help='阿里云API密钥')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"错误: 文件不存在 {args.file_path}")
        sys.exit(1)
    
    try:
        if args.interactive:
            # 交互模式
            agent = InteractiveDataAgent(args.api_key)
            agent.start_analysis(args.file_path)
        else:
            # 简单模式
            agent = DataAnalysisAgent(args.api_key)
            report_path = agent.analyze_file(args.file_path, args.goal)
            if report_path:
                print(f"分析完成，报告已生成: {report_path}")
            else:
                print("分析失败")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n分析已中断")
        sys.exit(0)
    except Exception as e:
        print(f"运行错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()