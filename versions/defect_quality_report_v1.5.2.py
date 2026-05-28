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
    'status': {'New': '#F7DC6F', 'Closed': '#82E0AA', 'ReOpen': '#F0B27A', 'Pending': '#85C1E9', 'Fixed': '#76D7C4'},
    'priority': {'优先': '#E57373', '高': '#FFB74D', '中': '#64B5F6', '低': '#81C784'},
    'severity': {'严重': '#E57373', '一般': '#FFB74D', '轻微': '#64B5F6', '建议': '#81C784'},
    'stage_find': {
        '2.1-系统测试【基本流】': '#A8D8EA',
        '2.2-系统测试【备选流】': '#AA96DA',
        '4.1-回归测试【基本流】': '#FCBAD3',
        '4.2-回归测试【备选流】': '#FFFFD2'
    }
}

INPUT_FILE = '缺陷明细.xlsx'
OUTPUT_FILE = '缺陷质量分析报告.html'
TITLE = '缺陷质量分析报告'
SUBTITLE = '2026-05-18 ~ 2026-05-22'

# ============ 数据读取 ============

df = pd.read_excel(INPUT_FILE)
total = len(df)

# ============ 图表生成函数 ============

def create_pie_chart(data, title, hole=0.4, colors=None, height=350, legend_y=-0.2):
    """创建饼图"""
    counts = data.value_counts()

    if len(counts) == 0:
        fig = go.Figure()
        fig.add_annotation(text='暂无数据', x=0.5, y=0.5, showarrow=False,
                          font={'size': 16, 'color': '#999', 'family': 'Microsoft YaHei'})
    else:
        marker_colors = colors if colors else COLORS['pastel'][:len(counts)]
        fig = go.Figure(go.Pie(
            labels=counts.index, values=counts.values,
            hole=hole, marker_colors=marker_colors,
            textinfo='percent', textposition='inside',
            textfont={'size': 14, 'color': '#34495e', 'family': 'Microsoft YaHei'},
            hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>',
            showlegend=True
        ))

    fig.update_layout(
        title=dict(text=title, x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
        paper_bgcolor='white',
        margin=dict(t=50, l=20, r=20, b=60),
        height=height,
        showlegend=True if len(counts) > 0 else False,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=legend_y,
            xanchor='center',
            x=0.5,
            font={'size': 12, 'family': 'Microsoft YaHei'},
            itemwidth=30,
            itemsizing='constant'
        )
    )
    return fig

def create_bar_chart(data, title, orientation='v', colors=None, height=350, x_label='', y_label='数量', show_legend=False, order=None, legend_y=-0.45):
    """创建柱状图"""
    counts = data.value_counts()

    # 如果指定了顺序，使用预定义顺序（支持预留图例）
    if order is not None and show_legend:
        # 创建完整顺序，包含预留项（值为0）
        full_counts = {}
        for o in order:
            full_counts[o] = counts.get(o, 0)
        counts = pd.Series(full_counts)
    elif order is not None:
        # 无图例版本，只显示有数据的项
        counts = counts.reindex([o for o in order if o in counts.index])

    fig = go.Figure()

    if len(counts) == 0:
        fig.add_annotation(text='暂无数据', x=0.5, y=0.5, showarrow=False,
                          font={'size': 16, 'color': '#999', 'family': 'Microsoft YaHei'})
    elif show_legend:
        # 添加图例版本：每个类别单独一个trace，颜色按counts.index顺序对应
        chart_colors = colors[:len(counts)] if colors else COLORS['fresh'][:len(counts)]

        for i, (label, value) in enumerate(zip(counts.index, counts.values)):
            if orientation == 'v':
                fig.add_trace(go.Bar(
                    x=[label], y=[value],
                    name=label,
                    marker_color=chart_colors[i],
                    marker_line_color='white', marker_line_width=2,
                    text=[value] if value > 0 else None, textposition='outside',
                    textfont={'size': 13, 'color': '#34495e', 'family': 'Microsoft YaHei'},
                    hovertemplate=f'<b>{label}</b><br>数量: {value}个<extra></extra>',
                    opacity=0.85 if value > 0 else 0.3,
                    showlegend=True
                ))
            else:
                fig.add_trace(go.Bar(
                    x=[value], y=[label], orientation='h',
                    name=label,
                    marker_color=chart_colors[i],
                    marker_line_color='white', marker_line_width=2,
                    text=[value] if value > 0 else None, textposition='outside',
                    textfont={'size': 12, 'color': '#34495e', 'family': 'Microsoft YaHei'},
                    hovertemplate=f'<b>{label}</b><br>数量: {value}个<extra></extra>',
                    opacity=0.85 if value > 0 else 0.3,
                    showlegend=True
                ))

        if orientation == 'v':
            fig.update_xaxes(tickfont={'size': 11, 'family': 'Microsoft YaHei'})
        else:
            fig.update_yaxes(tickfont={'size': 10, 'family': 'Microsoft YaHei'})
    else:
        # 无图例版本
        if orientation == 'v':
            fig.add_trace(go.Bar(
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
            fig.add_trace(go.Bar(
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
        margin=dict(t=50, l=20, r=20, b=100),
        height=height + 50 if show_legend else height,
        xaxis_title=x_label, yaxis_title=y_label,
        barmode='group' if show_legend else 'relative',
        showlegend=show_legend if len(counts) > 0 else False,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=legend_y,
            xanchor='center',
            x=0.5,
            font={'size': 10, 'family': 'Microsoft YaHei'},
            itemwidth=30,
            itemsizing='constant',
            tracegroupgap=0,
            valign='middle',
            itemclick=False,
            itemdoubleclick=False
        ) if show_legend else None
    )
    fig.update_yaxes(gridcolor='#e8e8e8', griddash='dot')
    return fig

def create_histogram(data, title, height=300):
    """创建直方图"""
    fig = go.Figure()

    if len(data) == 0:
        fig.add_annotation(text='暂无数据', x=0.5, y=0.5, showarrow=False,
                          font={'size': 16, 'color': '#999', 'family': 'Microsoft YaHei'})
    else:
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

# 图表配置 (隐藏工具栏)
config = {
    'displayModeBar': False,
    'scrollZoom': False,
    'displaylogo': False,
    'responsive': True
}

# 生成各个图表的HTML (按用户指定顺序)
charts_html = []

# 1. 质量指标概览 (表格)
fig = create_metrics_table('质量指标概览')
charts_html.append(fig.to_html(full_html=False, config=config))

# 2. 处理人员缺陷统计 (柱状图)
fig = create_bar_chart(df['处理人员'], '处理人员缺陷统计', colors=COLORS['fresh'], show_legend=True)
fig.update_xaxes(tickangle=15)
charts_html.append(fig.to_html(full_html=False, config=config))

# 3. 缺陷状态分布 (饼图)
status_counts = df['缺陷状态'].value_counts()
fig = create_pie_chart(
    df['缺陷状态'], '缺陷状态分布', hole=0.4,
    colors=[COLORS['status'].get(s, '#A8D8EA') for s in status_counts.index]
)
charts_html.append(fig.to_html(full_html=False, config=config))

# 4. 关联任务项统计 (横向柱状图)
fig = create_bar_chart(df['关联任务项'], '关联任务项统计', orientation='h', colors=COLORS['fresh'], show_legend=True, legend_y=-0.3)
charts_html.append(fig.to_html(full_html=False, config=config))

# 5. 缺陷修复周期分布 (直方图)
fix_period = df['缺陷修复周期(天)'].replace('/', np.nan)
fix_period = pd.to_numeric(fix_period, errors='coerce').dropna()
fig = create_histogram(fix_period, '缺陷修复周期分布')
charts_html.append(fig.to_html(full_html=False, config=config))

# 6. 缺陷返工情况 (饼图)
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
    showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5)
)
charts_html.append(fig.to_html(full_html=False, config=config))

# 7. 缺陷发现阶段分布 (横向柱状图)
df['发现阶段'] = df['发现阶段'].str.strip()  # 清除前导空格
stage_order = ['2.1-系统测试【基本流】', '2.2-系统测试【备选流】', '4.1-回归测试【基本流】', '4.2-回归测试【备选流】']
stage_colors = [COLORS['stage_find'].get(s, '#C4E1C1') for s in stage_order]
fig = create_bar_chart(df['发现阶段'], '缺陷发现阶段分布', orientation='h', colors=stage_colors, show_legend=True, order=stage_order)
charts_html.append(fig.to_html(full_html=False, config=config))

# 8. 缺陷类型分布 (环形图)
fig = create_pie_chart(df['缺陷类型'], '缺陷类型分布', hole=0.55, colors=COLORS['pastel'], legend_y=-0.5)
charts_html.append(fig.to_html(full_html=False, config=config))

# 9. 缺陷引入原因分析 (横向柱状图)
fig = create_bar_chart(df['引入原因'].dropna(), '缺陷引入原因分析', orientation='h', colors=COLORS['pastel'])
charts_html.append(fig.to_html(full_html=False, config=config))

# 10. 缺陷优先级分布 (柱状图)
priority_order = ['优先', '高', '中', '低']
fig = create_bar_chart(
    df['优先级'], '缺陷优先级分布', orientation='v',
    colors=[COLORS['priority'].get(p, '#A8D8EA') for p in priority_order],
    show_legend=True,
    order=priority_order,
    legend_y=-0.2
)
charts_html.append(fig.to_html(full_html=False, config=config))

# 11. 缺陷严重程度分布 (横向柱状图)
severity_order = ['严重', '一般', '轻微', '建议']
fig = create_bar_chart(
    df['严重程度'], '缺陷严重程度分布', orientation='h',
    colors=[COLORS['severity'].get(s, '#A8D8EA') for s in severity_order],
    show_legend=True,
    order=severity_order,
    legend_y=-0.2
)
charts_html.append(fig.to_html(full_html=False, config=config))

# 12. 缺陷引入阶段分布 (横向柱状图)
fig = create_bar_chart(df['引入阶段'].dropna(), '缺陷引入阶段分布', orientation='h', colors=COLORS['fresh'], show_legend=True, legend_y=-0.2)
charts_html.append(fig.to_html(full_html=False, config=config))

# ============ 组装完整HTML ============

html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TITLE}</title>
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