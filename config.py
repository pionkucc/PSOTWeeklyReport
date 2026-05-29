"""
配置常量模块
定义颜色方案、文件路径、标题等常量
"""

# 颜色配置
COLORS = {
    'pastel': ['#A8D8EA', '#AA96DA', '#FCBAD3', '#FFFFD2', '#C4E1C1', '#F9D5A7', '#B8E0D2', '#D6EADF'],
    'fresh': ['#7FB3D5', '#76D7C4', '#F7DC6F', '#F0B27A', '#E59866', '#AF7AC5', '#85C1E9', '#82E0AA'],
    'status': {'New': '#F7DC6F', 'Closed': '#82E0AA', 'ReOpen': '#F0B27A', 'Pending': '#85C1E9', 'Fixed': '#76D7C4'},
    'status_soft': {'Closed': '#B8E0D2', 'Fixed': '#D6EADF', 'New': '#A8D8EA', 'Pending': '#AA96DA', 'ReOpen': '#F9D5A7'},
    'priority': {'优先': '#E57373', '高': '#FFB74D', '中': '#64B5F6', '低': '#81C784'},
    'severity': {'严重': '#E57373', '一般': '#FFB74D', '轻微': '#64B5F6', '建议': '#81C784'},
    'stage_find': {
        '2.1-系统测试【基本流】': '#A8D8EA',
        '2.2-系统测试【备选流】': '#AA96DA',
        '4.1-回归测试【基本流】': '#FCBAD3',
        '4.2-回归测试【备选流】': '#FFFFD2'
    }
}

# 报告标题
TITLE = 'POST-产品标准化运营工具-质量周报'
SUBTITLE = '报告周期：2026年05月25日-2026年05月29日'

# 文件路径
INPUT_FILE = '缺陷明细.xlsx'

# 动态生成输出文件名：PSOT_Weekly_Report_日期范围.html
def generate_output_filename():
    """根据SUBTITLE日期范围生成文件名"""
    import re
    # 支持两种格式：
    # 1. "2026-05-18 ~ 2026-05-22"
    # 2. "报告周期：2026年05月25日-2026年05月29日"

    # 格式2：提取"2026年05月25日-2026年05月29日"
    match = re.search(r'(\d{4})年(\d{2})月(\d{2})日-(\d{4})年(\d{2})月(\d{2})日', SUBTITLE)
    if match:
        start_date = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
        end_date = f"{match.group(4)}.{match.group(5)}.{match.group(6)}"
        return f'PSOT_Weekly_Report_{start_date}-{end_date}.html'

    # 格式1：提取"2026-05-18 ~ 2026-05-22"
    match = re.search(r'(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})', SUBTITLE)
    if match:
        start_date = match.group(1).replace('-', '.')
        end_date = match.group(2).replace('-', '.')
        return f'PSOT_Weekly_Report_{start_date}-{end_date}.html'

    # 无法解析时使用默认文件名
    return 'PSOT_Weekly_Report.html'

OUTPUT_FILE = generate_output_filename()

# Tooltip样式：圆角+阴影+padding
TOOLTIP_CSS = "border-radius: 8px; padding: 8px 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.12);"

# 公共面板配置
PANEL_SHEET_INDEX = 2  # sheet3索引
PANEL_HEADER_COLOR = '#5DADE2'  # 面板标题背景色

# 缺陷预警阈值配置
OVERDUE_DAYS = 1        # 超期天数阈值（>=此值为超期）
REWORK_THRESHOLD = 1    # 返工次数阈值（>=此值为返工预警）