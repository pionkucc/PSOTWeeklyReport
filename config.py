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
SUBTITLE = '2026-05-18 ~ 2026-05-22'

# 文件路径
INPUT_FILE = '缺陷明细.xlsx'

# 动态生成输出文件名：PSOT_Weekly_Report_日期范围.html
def generate_output_filename():
    """根据SUBTITLE日期范围生成文件名"""
    # SUBTITLE格式: "2026-05-18 ~ 2026-05-22"
    dates = SUBTITLE.replace(' ~ ', '-').replace('-', '.')
    return f'PSOT_Weekly_Report_{dates}.html'

OUTPUT_FILE = generate_output_filename()

# Tooltip样式：圆角+阴影+padding
TOOLTIP_CSS = "border-radius: 8px; padding: 8px 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.12);"

# 公共面板配置
PANEL_SHEET_INDEX = 2  # sheet3索引
PANEL_HEADER_COLOR = '#5DADE2'  # 面板标题背景色