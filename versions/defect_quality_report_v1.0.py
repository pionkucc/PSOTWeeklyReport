"""
缺陷质量分析可视化报告生成器
生成清新UI风格的交互式HTML图表 (卡片平铺布局)

使用方法:
    python defect_quality_report.py

输出文件:
    缺陷质量分析报告.html
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ============ 配置区 ============

COLORS = {
    'pastel': ['#A8D8EA', '#AA96DA', '#FCBAD3', '#FFFFD2', '#C4E1C1', '#F9D5A7', '#B8E0D2', '#D6EADF'],
    'fresh': ['#7FB3D5', '#76D7C4', '#F7DC6F', '#F0B27A', '#E59866', '#AF7AC5', '#85C1E9', '#82E0AA'],
    'status': {'New': '#F7DC6F', 'Closed': '#82E0AA', 'ReOpen': '#F0B27A'},
    'priority': {'优先': '#E74C3C', '高': '#F39C12', '中': '#3498DB', '低': '#27AE60'},
    'severity': {'严重': '#E74C3C', '一般': '#F39C12', '轻微': '#3498DB', '建议': '#27AE60'}
}

INPUT_FILE = '缺陷明细.xlsx'
OUTPUT_FILE = '缺陷质量分析报告.html'
TITLE = '缺陷质量分析报告'
SUBTITLE = '2026-05-18 ~ 2026-05-22'

# ============ 数据读取 ============

df = pd.read_excel(INPUT_FILE)
total = len(df)

# ============ 图表生成函数 ============

def create_pie_chart(data, title, hole=0.4, colors=None, height=300):
    """创建饼图"""
    counts = data.value_counts()
    marker_colors = colors if colors else COLORS['pastel'][:len(counts)]

    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values,
        hole=hole, marker_colors=marker_colors,
        textinfo='label+percent', textposition='outside',
        textfont={'size': 13, 'color': '#34495e', 'family': 'Microsoft YaHei'},
        hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text=title, x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
        paper_bgcolor='white',
        margin=dict(t=50, l=20, r=20, b=20),
        height=height,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5, font={'size': 11})
    )
    return fig

def create_bar_chart(data, title, orientation='v', colors=None, height=300, x_label='', y_label='数量'):
    """创建柱状图"""
    counts = data.value_counts()

    if orientation == 'v':
        fig = go.Figure(go.Bar(
            x=counts.index, y=counts.values,
            marker_color=colors[:len(counts)] if colors else COLORS['fresh'][:len(counts)],
            marker_line_color='white', marker_line_width=2,
            text=counts.values, textposition='outside',
            textfont={'size': 13, 'color': '#34495e', 'family': 'Microsoft YaHei'},
            hovertemplate='<b>%{x}</b><br>数量: %{y}个<extra></extra>',
            opacity=0.85
        ))
        fig.update_xaxes(tickfont={'size': 11, 'family': 'Microsoft YaHei'})
    else:
        fig = go.Figure(go.Bar(
            x=counts.values, y=counts.index, orientation='h',
            marker_color=colors[:len(counts)] if colors else COLORS['fresh'][:len(counts)],
            marker_line_color='white', marker_line_width=2,
            text=counts.values, textposition='outside',
            textfont={'size': 12, 'color': '#34495e', 'family': 'Microsoft YaHei'},
            hovertemplate='<b>%{y}</b><br>数量: %{x}个<extra></extra>',
            opacity=0.85
        ))
        fig.update_yaxes(tickfont={'size': 10, 'family': 'Microsoft YaHei'})

    fig.update_layout(
        title=dict(text=title, x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
        paper_bgcolor='white',
        plot_bgcolor='#fafafa',
        margin=dict(t=50, l=60, r=30, b=50),
        height=height,
        xaxis_title=x_label, yaxis_title=y_label
    )
    fig.update_yaxes(gridcolor='#e8e8e8', griddash='dot')
    return fig

def create_histogram(data, title, height=300):
    """创建直方图"""
    fig = go.Figure()

    if len(data) > 0:
        fig.add_trace(go.Histogram(
            x=data, nbinsx=int(data.max()) + 1,
            marker_color='#7FB3D5', marker_line_color='white', marker_line_width=2,
            opacity=0.85,
            hovertemplate='修复周期: %{x}天<br>数量: %{y}个<extra></extra>'
        ))

        mean_val = data.mean()
        fig.add_annotation(
            x=mean_val, y=1.05,
            text=f'平均 {mean_val:.1f}天',
            showarrow=False,
            font=dict(size=12, color='#E74C3C', family='Microsoft YaHei'),
            xref='x domain', yref='y domain'
        )

    fig.update_layout(
        title=dict(text=title, x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
        paper_bgcolor='white',
        plot_bgcolor='#fafafa',
        margin=dict(t=50, l=60, r=30, b=50),
        height=height,
        xaxis_title='修复周期(天)', yaxis_title='数量'
    )
    fig.update_yaxes(gridcolor='#e8e8e8', griddash='dot')
    return fig

def create_metrics_table(title, height=280):
    """创建指标表格"""
    closed = len(df[df['缺陷状态'] == 'Closed'])
    new = len(df[df['缺陷状态'] == 'New'])
    reopen = len(df[df['缺陷状态'] == 'ReOpen'])
    close_rate = closed / total * 100 if total > 0 else 0

    metrics = [
        ('总缺陷数', str(total), '#5DADE2'),
        ('已关闭', str(closed), '#58D68D'),
        ('待处理', str(new), '#F7DC6F'),
        ('重打开', str(reopen), '#F0B27A'),
        ('关闭率', f'{close_rate:.1f}%', '#AF7AC5')
    ]

    fig = go.Figure(go.Table(
        header=dict(
            values=['<b>指标名称</b>', '<b>数值</b>'],
            fill_color='#e8f4f8',
            font=dict(color='#2c3e50', size=14, family='Microsoft YaHei'),
            line_color='white', height=40, align='center'
        ),
        cells=dict(
            values=[[f'<span style="color:{m[2]}">{m[0]}</span>' for m in metrics],
                    [f'<b>{m[1]}</b>' for m in metrics]],
            fill_color=[['#f8fffe'] * 5, ['#f0f8f7'] * 5],
            font=dict(color='#34495e', size=16, family='Microsoft YaHei'),
            line_color='#e8e8e8', height=40, align=['left', 'center']
        )
    ))

    fig.update_layout(
        title=dict(text=title, x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
        paper_bgcolor='white',
        margin=dict(t=50, l=20, r=20, b=20),
        height=height
    )
    return fig

# ============ 生成HTML ============

# 图表配置
config = {
    'displayModeBar': True,
    'scrollZoom': False,
    'displaylogo': False,
    'responsive': True,
    'toImageButtonOptions': {'format': 'png', 'filename': TITLE, 'height': 300, 'width': 400, 'scale': 2}
}

# 生成各个图表的HTML
charts_html = []

# 1. 缺陷状态分布
status_counts = df['缺陷状态'].value_counts()
fig = create_pie_chart(
    df['缺陷状态'], '缺陷状态分布', hole=0.4,
    colors=[COLORS['status'].get(s, '#A8D8EA') for s in status_counts.index]
)
charts_html.append(fig.to_html(full_html=False, config=config))

# 2. 缺陷优先级分布
priority_counts = df['优先级'].value_counts()
priority_order = ['优先', '高', '中', '低']
priority_counts = priority_counts.reindex([p for p in priority_order if p in priority_counts.index])
fig = go.Figure(go.Bar(
    x=priority_counts.index, y=priority_counts.values,
    marker_color=[COLORS['priority'].get(p, '#A8D8EA') for p in priority_counts.index],
    marker_line_color='white', marker_line_width=2,
    text=priority_counts.values, textposition='outside',
    textfont={'size': 14, 'color': '#34495e', 'family': 'Microsoft YaHei'},
    hovertemplate='<b>%{x}</b>优先级<br>数量: %{y}个<extra></extra>',
    opacity=0.85
))
fig.update_layout(
    title=dict(text='缺陷优先级分布', x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
    paper_bgcolor='white', plot_bgcolor='#fafafa',
    margin=dict(t=50, l=50, r=30, b=50), height=300, yaxis_title='数量'
)
fig.update_yaxes(gridcolor='#e8e8e8', griddash='dot')
charts_html.append(fig.to_html(full_html=False, config=config))

# 3. 缺陷严重程度分布
fig = create_bar_chart(df['严重程度'], '缺陷严重程度分布', orientation='h',
                        colors=[COLORS['severity'].get(s, '#A8D8EA') for s in df['严重程度'].value_counts().index])
charts_html.append(fig.to_html(full_html=False, config=config))

# 4. 处理人员缺陷统计
fig = create_bar_chart(df['处理人员'], '处理人员缺陷统计', colors=COLORS['fresh'])
fig.update_xaxes(tickangle=15)
charts_html.append(fig.to_html(full_html=False, config=config))

# 5. 关联任务项统计
fig = create_bar_chart(df['关联任务项'], '关联任务项统计', orientation='h', colors=COLORS['fresh'])
charts_html.append(fig.to_html(full_html=False, config=config))

# 6. 缺陷类型分布
fig = create_pie_chart(df['缺陷类型'], '缺陷类型分布', hole=0.55, colors=COLORS['pastel'])
charts_html.append(fig.to_html(full_html=False, config=config))

# 7. 缺陷发现阶段分布
fig = create_bar_chart(df['发现阶段'], '缺陷发现阶段分布', orientation='h', colors=COLORS['pastel'])
charts_html.append(fig.to_html(full_html=False, config=config))

# 8. 缺陷引入阶段分布
fig = create_bar_chart(df['引入阶段'].dropna(), '缺陷引入阶段分布', orientation='h', colors=COLORS['fresh'])
charts_html.append(fig.to_html(full_html=False, config=config))

# 9. 缺陷修复周期分布
fix_period = df['缺陷修复周期(天)'].replace('/', np.nan)
fix_period = pd.to_numeric(fix_period, errors='coerce').dropna()
fig = create_histogram(fix_period, '缺陷修复周期分布')
charts_html.append(fig.to_html(full_html=False, config=config))

# 10. 缺陷引入原因分析
fig = create_bar_chart(df['引入原因'].dropna(), '缺陷引入原因分析', orientation='h', colors=COLORS['pastel'])
charts_html.append(fig.to_html(full_html=False, config=config))

# 11. 缺陷返工情况
rework_counts = df['返工次数'].value_counts()
rework_labels = [f'返工{i}次' if i > 0 else '无返工' for i in rework_counts.index]
fig = go.Figure(go.Pie(
    labels=rework_labels, values=rework_counts.values,
    hole=0.45, marker_colors=['#82E0AA', '#F7DC6F', '#F0B27A'][:len(rework_counts)],
    textinfo='label+percent', textposition='outside',
    textfont={'size': 13, 'color': '#34495e', 'family': 'Microsoft YaHei'},
    hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
))
fig.update_layout(
    title=dict(text='缺陷返工情况', x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
    paper_bgcolor='white',
    margin=dict(t=50, l=20, r=20, b=20), height=300,
    showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5)
)
charts_html.append(fig.to_html(full_html=False, config=config))

# 12. 质量指标概览
fig = create_metrics_table('质量指标概览')
charts_html.append(fig.to_html(full_html=False, config=config))

# ============ 组装完整HTML ============

html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TITLE}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }}

        .header h1 {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}

        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}

        .card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 20px;
            transition: all 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}

        .plotly-graph-div {{
            width: 100% !important;
        }}

        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}

            .header h1 {{
                font-size: 28px;
            }}
        }}

        /* 工具栏美化 */
        .js-toolbar-btn {{
            background-color: rgba(255,255,255,0.9) !important;
            border-radius: 8px !important;
            margin: 2px !important;
            transition: all 0.2s ease;
        }}

        .js-toolbar-btn:hover {{
            background-color: #e8f4f8 !important;
            transform: scale(1.1);
        }}

        /* 表格hover效果 */
        .plotly-table tbody tr:hover td {{
            background-color: #e8f8f5 !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{TITLE}</h1>
            <p>{SUBTITLE} | 共 {total} 条缺陷数据</p>
        </div>

        <div class="grid">
            {''.join([f'<div class="card">{html}</div>' for html in charts_html])}
        </div>
    </div>
</body>
</html>
'''

# 保存文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f'报告已生成: {OUTPUT_FILE}')
print(f'共 {total} 条缺陷数据')