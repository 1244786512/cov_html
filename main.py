# -*- coding: utf-8 -*-
import argparse
import os
import sys
from coverDataFile import CoverDataFileMethod
from coverHtmlFile import CoverHtmlFileMethod

# author = wxf


def get_version():
    """获取版本信息"""
    current_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(current_path)
    version_file = os.path.join(parent_path, 'version')
    
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        return content
    except FileNotFoundError:
        return "Unknown version"
    except Exception as e:
        print(f"Error reading version file: {e}", file=sys.stderr)
        return "Unknown version"


def validate_coverage_file(file_path):
    """验证覆盖率文件是否存在且可读"""
    if not os.path.exists(file_path):
        print(f"Error: Coverage file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isfile(file_path):
        print(f"Error: Path is not a file: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    if not os.access(file_path, os.R_OK):
        print(f"Error: Cannot read file: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    return True


def create_parser():
    """创建并配置命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='cov-html',
        description='Coverage reporting tool for The Golang Programming Language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: cov-html -f coverage.cov -o report'
    )
    
    parser.add_argument(
        '-f', '--file',
        dest='coverage_file',
        required=True,
        metavar='<file_path>',
        help='Specify the coverage .cov file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='report_path',
        default='report',
        metavar='<report_path>',
        help='Output report file path (default: report)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {get_version()}',
        help='Print the cov_html version information'
    )
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 验证覆盖率文件
    validate_coverage_file(args.coverage_file)
    
    # 处理覆盖率数据
    data_processor = CoverDataFileMethod(args.coverage_file)
    coverage_data, root_file_name, coverage_time = data_processor.getContentBefore()
    processed_data = data_processor.getIsCovRowsList(coverage_data)
    final_cov_data = data_processor.updateParentIsCovLines(processed_data)[6]
    
    # 生成HTML报告
    html_generator = CoverHtmlFileMethod(args.report_path)
    html_generator.covHtmlRun(final_cov_data, root_file_name, coverage_time)
    
    print(f"Coverage report generated successfully: {args.report_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
