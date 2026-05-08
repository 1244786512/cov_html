# cov_html

`cov_html` 是一个面向 **Go 语言覆盖率数据** 的 HTML 报告生成工具。  
它将 `.cov` 覆盖率文件解析为可视化页面，支持按目录、文件、函数维度查看覆盖情况，并可在源码视图中高亮覆盖行，便于快速定位薄弱测试区域。

## 功能特性

- 解析 Go 覆盖率文件（如 `coverage.cov`）
- 统计并展示行覆盖率与函数覆盖率
- 生成目录级、文件级汇总页面
- 支持源码逐行展示与覆盖高亮
- 生成纯静态 HTML 报告，可离线查看

## 环境要求

- Python 3
- 依赖包见 `requirements.txt`

## 安装

1. 克隆仓库

```bash
git clone https://github.com/1244786512/cov_html.git
cd cov_html
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 构建可执行文件

```bash
python setup.py
```

构建完成后可在 `dist/` 目录看到 `cov-html` 可执行文件。  
如需全局使用，可自行将其加入系统 PATH（Linux 可复制到 `/usr/local/bin`）。

## 使用方式

```bash
cov-html -f coverage.cov -o report
```

### 参数说明

- `-f`, `--file`：覆盖率文件路径（必填）
- `-o`, `--output`：报告输出目录（可选，默认 `report`）
- `-v`, `--version`：查看版本信息

## 输入与输出

- 输入：Go 覆盖率文件（`.cov`）
- 输出：HTML 报告目录（默认 `report/`），包含：
  - 目录与文件覆盖率总览页
  - 文件源码覆盖详情页
  - 报告静态资源（CSS/JS/图标）

## 项目结构

```text
cov_html/
├── main.py                 # 命令行入口
├── coverDataFile.py        # 覆盖率数据解析与统计
├── coverHtmlFile.py        # HTML 报告渲染与输出
├── templates/              # Jinja2 模板
├── static/                 # 前端静态资源
├── requirements.txt        # Python 依赖
└── setup.py                # 可执行文件构建脚本
```

## 常见说明

- 本工具用于覆盖率结果可视化，不负责执行测试本身。
- 建议先通过 Go 测试流程生成覆盖率文件，再用本工具转换为 HTML。
- 使用 `cov-html --help` 可查看命令帮助。
