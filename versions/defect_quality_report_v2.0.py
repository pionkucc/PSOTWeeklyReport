"""
缺陷质量分析可视化报告生成器
生成清新UI风格的交互式HTML图表 (卡片平铺布局)
使用ECharts渲染图表，支持hover tooltip圆角+阴影+padding

使用方法:
    python defect_quality_report.py

输出文件:
    缺陷质量分析报告.html
"""

import pandas as pd
import numpy as np
import re
from pyecharts.charts import Pie, Bar, Line
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode

# ============ 配置区 ============

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

INPUT_FILE = '缺陷明细.xlsx'
OUTPUT_FILE = '缺陷质量分析报告.html'
TITLE = 'POST-产品标准化运营工具-质量周报'
SUBTITLE = '2026-05-18 ~ 2026-05-22'

# Tooltip样式：圆角+阴影+padding
TOOLTIP_CSS = "border-radius: 8px; padding: 8px 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.12);"

# ============ 数据读取 ============

df = pd.read_excel(INPUT_FILE)
total = len(df)

# 从sheet2读取任务项统计
df_sheet2 = pd.read_excel(INPUT_FILE, sheet_name=1)
# 任务项数量（排除合计行）
task_count = len(df_sheet2) - 1  # 排除最后一行合计
# 子任务项数量（从合计行的第4列获取：关联任务项（子任务））
subtask_count = df_sheet2.iloc[-1, 4] if len(df_sheet2) > 0 else 0

# ============ 图表生成函数 ============

def create_pie_chart(data, title, hole=0.4, colors=None, height="350px"):
    """创建饼图/环形图 - ECharts版本"""
    counts = data.value_counts()

    if len(counts) == 0:
        pie = Pie(init_opts=opts.InitOpts(height=height))
        pie.add("", [("暂无数据", 1)])
        pie.set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left="center"))
        return pie

    data_pair = [(str(k), int(v)) for k, v in counts.items()]

    if colors is None:
        colors = COLORS['pastel'][:len(counts)]

    pie = Pie(init_opts=opts.InitOpts(height=height))
    pie.add(
        series_name="",
        data_pair=data_pair,
        radius=[f"{hole*100}%", "70%"],
        label_opts=opts.LabelOpts(
            formatter="{d}%",
            font_size=14,
            color="#34495e",
            font_family="Microsoft YaHei"
        )
    )

    color_js = f"""
    function(params) {{
        var colors = {colors};
        return colors[params.dataIndex];
    }}
    """
    pie.set_series_opts(
        itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_js))
    )

    pie.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            pos_left="center",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=16, color="#2c3e50", font_family="Microsoft YaHei"
            )
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item",
            extra_css_text=TOOLTIP_CSS
        ),
        legend_opts=opts.LegendOpts(
            is_show=True,
            orient="horizontal",
            pos_top="bottom",
            pos_left="center",
            item_width=25,
            item_height=14,
            textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei", font_size=11)
        )
    )

    return pie


def create_bar_chart(data, title, orientation='v', colors=None, height="350px", show_legend=False, order=None):
    """创建柱状图 - ECharts版本"""
    counts = data.value_counts()

    if order is not None and show_legend:
        full_counts = {}
        for o in order:
            full_counts[o] = counts.get(o, 0)
        counts = pd.Series(full_counts)
    elif order is not None:
        counts = counts.reindex([o for o in order if o in counts.index])

    if len(counts) == 0:
        bar = Bar(init_opts=opts.InitOpts(height=height))
        bar.add_xaxis(["暂无数据"])
        bar.add_yaxis("", [0])
        bar.set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left="center"))
        return bar

    if colors is None:
        colors = COLORS['fresh'][:len(counts)]

    bar = Bar(init_opts=opts.InitOpts(height=height))

    x_data = [str(x) for x in counts.index.tolist()]
    y_data = counts.values.tolist()

    if show_legend:
        # 多系列：每个类别单独一个系列，支持图例
        bar.add_xaxis(x_data)
        for i, (label, value) in enumerate(zip(x_data, y_data)):
            series_data = [None] * len(x_data)
            series_data[i] = value
            bar.add_yaxis(
                label,
                series_data,
                color=colors[i] if i < len(colors) else colors[-1],
                label_opts=opts.LabelOpts(
                    is_show=True if value > 0 else False,
                    position="top" if orientation == 'v' else "right",
                    font_family="Microsoft YaHei",
                    font_size=12
                ),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=colors[i] if i < len(colors) else colors[-1],
                    border_color="white",
                    border_width=2,
                    opacity=0.85 if value > 0 else 0.3
                )
            )
        if orientation == 'h':
            bar.reversal_axis()
        bar.set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=16, color="#2c3e50", font_family="Microsoft YaHei"
                )
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                axis_pointer_type="shadow",
                extra_css_text=TOOLTIP_CSS
            ),
            xaxis_opts=opts.AxisOpts(
                name="数量" if orientation == 'h' else "",
                splitline_opts=opts.SplitLineOpts(
                    is_show=True if orientation == 'h' else False,
                    linestyle_opts=opts.LineStyleOpts(type_="dashed")
                ),
                axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
            ),
            yaxis_opts=opts.AxisOpts(
                name="" if orientation == 'h' else "数量",
                splitline_opts=opts.SplitLineOpts(
                    is_show=False if orientation == 'h' else True,
                    linestyle_opts=opts.LineStyleOpts(type_="dashed")
                ),
                axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
            ),
            legend_opts=opts.LegendOpts(
                is_show=True,
                orient="horizontal",
                pos_top="bottom",
                pos_left="center",
                item_width=25,
                item_height=14,
                textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei", font_size=11)
            )
        )
    else:
        # 单系列：所有柱子在一个系列中
        bar.add_xaxis(x_data)
        bar.add_yaxis(
            "数量",
            y_data,
            label_opts=opts.LabelOpts(
                is_show=True,
                position="top" if orientation == 'v' else "right",
                font_family="Microsoft YaHei",
                font_size=12
            )
        )

        color_js = f"""
        function(params) {{
            var colors = {colors};
            return colors[params.dataIndex % colors.length];
        }}
        """
        bar.set_series_opts(
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(color_js),
                border_color="white",
                border_width=2,
                opacity=0.85
            )
        )

        if orientation == 'h':
            bar.reversal_axis()

        bar.set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=16, color="#2c3e50", font_family="Microsoft YaHei"
                )
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="shadow",
                extra_css_text=TOOLTIP_CSS
            ),
            xaxis_opts=opts.AxisOpts(
                name="数量" if orientation == 'h' else "",
                splitline_opts=opts.SplitLineOpts(
                    is_show=True if orientation == 'h' else False,
                    linestyle_opts=opts.LineStyleOpts(type_="dashed")
                ),
                axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
            ),
            yaxis_opts=opts.AxisOpts(
                name="" if orientation == 'h' else "数量",
                splitline_opts=opts.SplitLineOpts(
                    is_show=False if orientation == 'h' else True,
                    linestyle_opts=opts.LineStyleOpts(type_="dashed")
                ),
                axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )

    return bar


def create_histogram(data, title, height="300px"):
    """创建直方图 - ECharts版本（单系列模式）"""
    if len(data) == 0:
        bar = Bar(init_opts=opts.InitOpts(height=height))
        bar.add_xaxis(["暂无数据"])
        bar.add_yaxis("", [0])
        bar.set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left="center"))
        return bar

    max_val = int(data.max())
    bins = list(range(0, max_val + 2))
    hist, bin_edges = np.histogram(data, bins=bins)

    x_labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(hist))]
    non_empty = [(x, h) for x, h in zip(x_labels, hist) if h > 0]
    if non_empty:
        x_labels, hist = zip(*non_empty)
        x_labels = list(x_labels)
        hist = list(hist)
    else:
        x_labels = ["0"]
        hist = [0]

    mean_val = data.mean()

    bar = Bar(init_opts=opts.InitOpts(height=height))
    bar.add_xaxis(x_labels)
    bar.add_yaxis(
        "数量",
        list(hist),
        label_opts=opts.LabelOpts(
            is_show=True,
            position="top",
            font_family="Microsoft YaHei",
            font_size=12
        )
    )

    bar.set_series_opts(
        itemstyle_opts=opts.ItemStyleOpts(
            color="#7FB3D5",
            border_color="white",
            border_width=2,
            opacity=0.85
        )
    )

    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            pos_left="center",
            subtitle=f"平均 {mean_val:.1f}天",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=16, color="#2c3e50", font_family="Microsoft YaHei"
            ),
            subtitle_textstyle_opts=opts.TextStyleOpts(
                font_size=12, color="#E74C3C", font_family="Microsoft YaHei"
            )
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            axis_pointer_type="shadow",
            extra_css_text=TOOLTIP_CSS
        ),
        xaxis_opts=opts.AxisOpts(
            name="修复周期(天)",
            axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=10)
        ),
        yaxis_opts=opts.AxisOpts(
            name="数量",
            splitline_opts=opts.SplitLineOpts(
                is_show=True,
                linestyle_opts=opts.LineStyleOpts(type_="dashed")
            ),
            axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei")
        ),
        legend_opts=opts.LegendOpts(is_show=False)
    )

    return bar


def create_metrics_cards_html():
    """创建质量指标卡片HTML (5个小卡片平铺)"""
    global task_count, subtask_count

    closed = len(df[df['缺陷状态'] == 'Closed'])
    legacy_count = len(df[df['缺陷状态'] != 'Closed'])  # 遗留缺陷：非Closed状态
    close_rate = closed / total * 100 if total > 0 else 0

    # 基本流占比（发现阶段包含"基本流"的缺陷）
    df['发现阶段'] = df['发现阶段'].str.strip()
    basic_flow = len(df[df['发现阶段'].str.contains('基本流', na=False)])
    basic_flow_rate = basic_flow / total * 100 if total > 0 else 0

    # 返工率（返工次数>0的缺陷）
    rework = len(df[df['返工次数'] > 0])
    rework_rate = rework / total * 100 if total > 0 else 0

    # 平均修复时长（天）
    fix_period = df['缺陷修复周期(天)'].replace('/', np.nan)
    fix_period = pd.to_numeric(fix_period, errors='coerce')
    avg_fix_time = fix_period.mean()
    max_fix_time = fix_period.max()
    min_fix_time = fix_period.min()
    avg_fix_time_str = f'{avg_fix_time:.2f}天' if avg_fix_time > 0 else '--'
    max_fix_time_str = f'{max_fix_time:.0f}天' if max_fix_time > 0 else '--'
    min_fix_time_str = f'{min_fix_time:.0f}天' if min_fix_time > 0 else '--'

    cards = [
        ('任务项', f'{task_count}个', 'linear-gradient(135deg, #A8D8EA 0%, #B8E0D2 100%)', 'icon-task', f'子任务项{subtask_count}个'),
        ('平均修复时长', avg_fix_time_str, 'linear-gradient(135deg, #F7DC6F 0%, #F9D5A7 100%)', 'icon-clock', f'最大{max_fix_time_str}<br>最小{min_fix_time_str}'),
        ('遗留缺陷', f'{legacy_count}个', 'linear-gradient(135deg, #82E0AA 0%, #A8E8EA 100%)', 'icon-bug', f'关闭率{close_rate:.1f}%'),
        ('基本流占比', f'{basic_flow_rate:.1f}%', 'linear-gradient(135deg, #F0B27A 0%, #FCBAD3 100%)', 'icon-chart', f'{basic_flow}/{total}个'),
        ('返工率', f'{rework_rate:.1f}%', 'linear-gradient(135deg, #AA96DA 0%, #D6EADF 100%)', 'icon-refresh', f'{rework}/{total}个')
    ]

    cards_html = ''.join([
        f'<div class="metric-card" style="background:{c[2]}">'
        f'<div class="metric-header">'
        f'<span class="metric-name">{c[0]}</span>'
        f'<div class="metric-icon {c[3]}"></div>'
        f'</div>'
        f'<div class="metric-value">{c[1]}</div>'
        f'<div class="metric-subtitle">{c[4]}</div>'
        f'</div>'
        for c in cards
    ])

    return f'<div class="metrics-container"><div class="metrics-title">质量指标概览</div><div class="metrics-row">{cards_html}</div></div>'


# ============ 生成图表 ============

charts_html = []

def chart_to_html(chart, chart_id):
    """将ECharts图表转换为内嵌HTML（不依赖CDN）"""
    options = chart.dump_options()
    return f'''
<div id="{chart_id}" style="width:100%;height:{chart.height if hasattr(chart, 'height') else '350px'}"></div>
<script>
echarts.init(document.getElementById('{chart_id}')).setOption({options});
</script>
'''

# 1. 质量指标概览 (5个小卡片) - 直接生成HTML
metrics_html = create_metrics_cards_html()

# 2. 处理人员缺陷统计 (复合图表: 堆叠柱状图 + 折线图双Y轴)
status_list = ['Closed', 'Fixed', 'New', 'Pending', 'ReOpen']
handler_status_counts = df.groupby(['处理人员', '缺陷状态']).size().unstack(fill_value=0)

for status in status_list:
    if status not in handler_status_counts.columns:
        handler_status_counts[status] = 0

handler_status_counts = handler_status_counts[status_list]
handler_totals = handler_status_counts.sum(axis=1)
handler_status_counts = handler_status_counts.loc[handler_totals.sort_values(ascending=False).index]

handlers = handler_status_counts.index.tolist()

# 计算平均修复时长
df['缺陷修复周期(天)'] = pd.to_numeric(df['缺陷修复周期(天)'].replace('/', np.nan), errors='coerce')
avg_fix_time = df.groupby('处理人员')['缺陷修复周期(天)'].mean()
avg_fix_time = avg_fix_time.reindex(handlers).fillna(0)

# 创建柱状图
bar = Bar(init_opts=opts.InitOpts(height="400px"))
bar.add_xaxis(handlers)

# 添加堆叠柱状图
for status in status_list:
    bar.add_yaxis(
        status,
        handler_status_counts[status].tolist(),
        stack="total",
        color=COLORS['status_soft'].get(status, '#A8D8EA'),
        label_opts=opts.LabelOpts(is_show=False)
    )

bar.set_global_opts(
    title_opts=opts.TitleOpts(
        title="处理人员缺陷统计",
        pos_left="center",
        title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#2c3e50", font_family="Microsoft YaHei")
    ),
    tooltip_opts=opts.TooltipOpts(
        trigger="axis",
        axis_pointer_type="shadow",
        extra_css_text=TOOLTIP_CSS
    ),
    xaxis_opts=opts.AxisOpts(
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11, rotate=15)
    ),
    yaxis_opts=opts.AxisOpts(
        name="数量",
        splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(type_="dashed")),
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei")
    ),
    legend_opts=opts.LegendOpts(is_show=False)
)

# 创建折线图
line = Line()
line.add_xaxis(handlers)
line.add_yaxis(
    "平均修复时长(天)",
    avg_fix_time.values.tolist(),
    yaxis_index=1,
    is_smooth=True,
    color="#F5C4D0",
    linestyle_opts=opts.LineStyleOpts(width=2.5),
    symbol="circle",
    symbol_size=8,
    label_opts=opts.LabelOpts(
        is_show=True,
        position="top",
        formatter=JsCode("function(p){return p.value > 0 ? p.value.toFixed(2) : ''}"),
        font_family="Microsoft YaHei",
        color="#2c3e50"
    )
)

# 使用 overlap 组合
bar.overlap(line)

# 添加右侧Y轴
bar.extend_axis(
    yaxis=opts.AxisOpts(
        name="平均修复时长(天)",
        position="right",
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei"),
        splitline_opts=opts.SplitLineOpts(is_show=False)
    )
)

charts_html.append(chart_to_html(bar, "chart_handler"))

# 3. 缺陷状态分布 (饼图)
pie = create_pie_chart(
    df['缺陷状态'], '缺陷状态分布', hole=0.4,
    colors=[COLORS['status'].get(s, '#A8D8EA') for s in df['缺陷状态'].value_counts().index]
)
charts_html.append(chart_to_html(pie, "chart_status"))

# 4. 关联任务项统计 (横向柱状图，带底部自定义图例，点击图例同步隐藏Y轴标签)
task_data = df['关联任务项'].value_counts()
task_categories = [str(x) for x in task_data.index.tolist()]
task_values = task_data.values.tolist()
task_colors = COLORS['fresh'][:len(task_data)]

bar_task = Bar(init_opts=opts.InitOpts(height="350px"))
bar_task.add_xaxis(task_categories)
bar_task.add_yaxis(
    "数量",
    task_values,
    label_opts=opts.LabelOpts(
        is_show=True,
        position="right",
        font_family="Microsoft YaHei",
        font_size=12
    )
)

bar_task.set_series_opts(
    itemstyle_opts=opts.ItemStyleOpts(
        color=JsCode(f"function(params) {{ var colors = {task_colors}; return colors[params.dataIndex]; }}"),
        border_color="white",
        border_width=2,
        opacity=0.85
    )
)

bar_task.reversal_axis()
bar_task.set_global_opts(
    title_opts=opts.TitleOpts(
        title='关联任务项统计',
        pos_left="center",
        title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#2c3e50", font_family="Microsoft YaHei")
    ),
    tooltip_opts=opts.TooltipOpts(
        trigger="axis",
        axis_pointer_type="shadow",
        extra_css_text=TOOLTIP_CSS
    ),
    xaxis_opts=opts.AxisOpts(
        name="数量",
        splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(type_="dashed")),
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
    ),
    yaxis_opts=opts.AxisOpts(
        splitline_opts=opts.SplitLineOpts(is_show=False),
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
    ),
    legend_opts=opts.LegendOpts(is_show=False)
)

# 生成自定义图例HTML
task_options = bar_task.dump_options()
legend_items = ''.join([
    f'<span class="legend-item" data-index="{i}" style="cursor:pointer;display:inline-block;margin:0 8px;"><span style="display:inline-block;width:14px;height:14px;background:{task_colors[i]};border-radius:2px;margin-right:4px;"></span><span style="font-family:Microsoft YaHei;font-size:11px;color:#333;">{cat}</span></span>'
    for i, cat in enumerate(task_categories)
])

task_cat_json = str(task_categories)
task_val_json = str(task_values)

charts_html.append(f'''
<div id="chart_task" style="width:100%;height:350px"></div>
<div class="custom-legend" style="text-align:center;margin-top:5px;">{legend_items}</div>
<script>
(function() {{
    var categories = {task_cat_json};
    var values = {task_val_json};
    var selected = {{}};
    for (var i = 0; i < categories.length; i++) selected[i] = true;

    function updateChart() {{
        var newCat = [], newVal = [];
        for (var i = 0; i < categories.length; i++) {{
            if (selected[i]) {{
                newCat.push(categories[i]);
                newVal.push(values[i]);
            }}
        }}
        chart.setOption({{yAxis: {{data: newCat}}, series: {{data: newVal}}}});
    }}

    var chart = echarts.init(document.getElementById('chart_task'));
    chart.setOption({task_options});

    var legendItems = document.querySelectorAll('#chart_task + .custom-legend .legend-item');
    legendItems.forEach(function(item) {{
        item.addEventListener('click', function() {{
            var idx = parseInt(this.getAttribute('data-index'));
            selected[idx] = !selected[idx];
            this.style.opacity = selected[idx] ? 1 : 0.3;
            updateChart();
        }});
    }});
}})();
</script>
''')

# 5. 缺陷趋势分析 (面积折线图)
date_range_match = re.search(r'(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})', SUBTITLE)
if date_range_match:
    start_date = pd.to_datetime(date_range_match.group(1))
    end_date = pd.to_datetime(date_range_match.group(2))
else:
    start_date = pd.to_datetime('2026-05-18')
    end_date = pd.to_datetime('2026-05-22')

date_range = pd.date_range(start=start_date, end=end_date, freq='D')
all_dates = [d.strftime('%m-%d') for d in date_range]

register_time_col = df.columns[11]
close_time_col = df.columns[13]

df['登记日期'] = pd.to_datetime(df[register_time_col]).dt.strftime('%m-%d')
df['关闭日期'] = pd.to_datetime(df[close_time_col]).dt.strftime('%m-%d')

new_counts = df[df['缺陷状态'] == 'New'].groupby('登记日期').size()
closed_counts = df[df['缺陷状态'] == 'Closed'].groupby('关闭日期').size()
legacy_df = df[df['缺陷状态'].isin(['New', 'ReOpen', 'Pending', 'Fixed'])]
legacy_counts = legacy_df.groupby('登记日期').size()

new_data = [int(new_counts.get(d, 0)) for d in all_dates]
closed_data = [int(closed_counts.get(d, 0)) for d in all_dates]
legacy_data = [int(legacy_counts.get(d, 0)) for d in all_dates]

line_chart = Line(init_opts=opts.InitOpts(height="350px"))
line_chart.add_xaxis(all_dates)

line_chart.add_yaxis(
    "新增缺陷",
    new_data,
    is_smooth=True,
    color="#A0E7E5",
    symbol="circle",
    symbol_size=8,
    areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
    label_opts=opts.LabelOpts(is_show=False)
)

line_chart.add_yaxis(
    "遗留缺陷",
    legacy_data,
    is_smooth=True,
    color="#FFD69B",
    symbol="circle",
    symbol_size=8,
    areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
    label_opts=opts.LabelOpts(is_show=False)
)

line_chart.add_yaxis(
    "关闭缺陷",
    closed_data,
    is_smooth=True,
    color="#F5C4D0",
    symbol="circle",
    symbol_size=8,
    areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
    label_opts=opts.LabelOpts(is_show=False)
)

line_chart.set_global_opts(
    title_opts=opts.TitleOpts(
        title="缺陷趋势分析",
        pos_left="center",
        title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#2c3e50", font_family="Microsoft YaHei")
    ),
    tooltip_opts=opts.TooltipOpts(
        trigger="axis",
        extra_css_text=TOOLTIP_CSS
    ),
    xaxis_opts=opts.AxisOpts(
        name="日期",
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
    ),
    yaxis_opts=opts.AxisOpts(
        name="缺陷数量",
        splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(type_="dashed")),
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei")
    ),
    legend_opts=opts.LegendOpts(is_show=False)
)

trend_chart_html = chart_to_html(line_chart, "chart_trend")

# 6. 缺陷修复周期分布 (直方图)
fix_period = df['缺陷修复周期(天)'].replace('/', np.nan)
fix_period = pd.to_numeric(fix_period, errors='coerce').dropna()
hist_chart = create_histogram(fix_period, '缺陷修复周期分布')
charts_html.append(chart_to_html(hist_chart, "chart_histogram"))

# 7. 缺陷返工情况 (饼图)
rework_counts = df['返工次数'].value_counts()
rework_labels = [f'返工{i}次' if i > 0 else '无返工' for i in rework_counts.index]
rework_data = [(rework_labels[i], int(rework_counts.values[i])) for i in range(len(rework_counts))]

rework_colors = ['#82E0AA', '#F7DC6F', '#F0B27A'][:len(rework_counts)]
pie_rework = Pie(init_opts=opts.InitOpts(height="300px"))
pie_rework.add(
    "",
    rework_data,
    radius=["45%", "70%"],
    label_opts=opts.LabelOpts(
        formatter="{b}: {d}%",
        font_family="Microsoft YaHei"
    )
)
# 设置颜色
rework_color_js = f"""
function(params) {{
    var colors = {rework_colors};
    return colors[params.dataIndex];
}}
"""
pie_rework.set_series_opts(
    itemstyle_opts=opts.ItemStyleOpts(color=JsCode(rework_color_js))
)
pie_rework.set_global_opts(
    title_opts=opts.TitleOpts(
        title="缺陷返工情况",
        pos_left="center",
        title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#2c3e50", font_family="Microsoft YaHei")
    ),
    tooltip_opts=opts.TooltipOpts(
        trigger="item",
        extra_css_text=TOOLTIP_CSS
    ),
    legend_opts=opts.LegendOpts(
        is_show=True,
        orient="horizontal",
        pos_top="bottom",
        pos_left="center",
        item_width=25,
        item_height=14,
        textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei", font_size=11)
    )
)
charts_html.append(chart_to_html(pie_rework, "chart_rework"))

# 8. 缺陷发现阶段分布 (横向柱状图)
stage_order = ['2.1-系统测试【基本流】', '2.2-系统测试【备选流】', '4.1-回归测试【基本流】', '4.2-回归测试【备选流】']
stage_colors = [COLORS['stage_find'].get(s, '#C4E1C1') for s in stage_order]
bar_stage = create_bar_chart(df['发现阶段'], '缺陷发现阶段分布', orientation='h', colors=stage_colors, order=stage_order)
charts_html.append(chart_to_html(bar_stage, "chart_stage"))

# 9. 缺陷类型分布 (环形图)
pie_type = create_pie_chart(df['缺陷类型'], '缺陷类型分布', hole=0.55, colors=COLORS['pastel'])
charts_html.append(chart_to_html(pie_type, "chart_type"))

# 10. 缺陷引入原因分析 (横向柱状图)
bar_cause = create_bar_chart(df['引入原因'].dropna(), '缺陷引入原因分析', orientation='h', colors=COLORS['pastel'])
charts_html.append(chart_to_html(bar_cause, "chart_cause"))

# 11. 缺陷优先级分布 (柱状图)
priority_order = ['优先', '高', '中', '低']
bar_priority = create_bar_chart(
    df['优先级'], '缺陷优先级分布', orientation='v',
    colors=[COLORS['priority'].get(p, '#A8D8EA') for p in priority_order],
    order=priority_order
)
charts_html.append(chart_to_html(bar_priority, "chart_priority"))

# 12. 缺陷严重程度分布 (横向柱状图)
severity_order = ['严重', '一般', '轻微', '建议']
bar_severity = create_bar_chart(
    df['严重程度'], '缺陷严重程度分布', orientation='h',
    colors=[COLORS['severity'].get(s, '#A8D8EA') for s in severity_order],
    order=severity_order
)
charts_html.append(chart_to_html(bar_severity, "chart_severity"))

# 13. 缺陷引入阶段分布 (横向柱状图)
bar_intro = create_bar_chart(df['引入阶段'].dropna(), '缺陷引入阶段分布', orientation='h', colors=COLORS['fresh'])
charts_html.append(chart_to_html(bar_intro, "chart_intro"))

# ============ 组装完整HTML ============

html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TITLE}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
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

        .card-full {{
            grid-column: 1 / -1;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 20px 30px;
            transition: all 0.3s ease;
        }}

        .card-wide {{
            grid-column: span 2;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 20px;
            transition: all 0.3s ease;
        }}

        .metrics-container {{
            width: 100%;
        }}

        .metrics-title {{
            text-align: center;
            font-size: 16px;
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 20px;
            font-family: 'Microsoft YaHei';
        }}

        .metrics-row {{
            display: flex;
            gap: 20px;
            justify-content: stretch;
            width: 100%;
        }}

        .metric-card {{
            flex: 1;
            height: 120px;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            align-items: stretch;
            justify-content: center;
            transition: all 0.3s ease;
            cursor: default;
            padding: 15px 18px;
            position: relative;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .metric-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .metric-name {{
            font-size: 15px;
            color: #5a6c7d;
            font-family: 'Microsoft YaHei';
            font-weight: bold;
        }}

        .metric-icon {{
            width: 22px;
            height: 22px;
            opacity: 0.7;
            position: relative;
        }}

        .icon-task {{
            width: 20px;
            height: 22px;
            border: 2px solid #fff;
            border-radius: 4px;
            position: relative;
        }}
        .icon-task::before {{
            content: '';
            position: absolute;
            top: 5px;
            left: 4px;
            width: 10px;
            height: 2px;
            background: #fff;
            border-radius: 1px;
        }}
        .icon-task::after {{
            content: '';
            position: absolute;
            top: 10px;
            left: 4px;
            width: 7px;
            height: 2px;
            background: #fff;
            border-radius: 1px;
        }}

        .icon-bug {{
            width: 20px;
            height: 20px;
            position: relative;
        }}
        .icon-bug::before {{
            content: '';
            position: absolute;
            top: 3px;
            left: 5px;
            width: 10px;
            height: 14px;
            border: 2px solid #fff;
            border-radius: 50% 50% 45% 45%;
        }}
        .icon-bug::after {{
            content: '';
            position: absolute;
            top: 7px;
            left: 1px;
            width: 4px;
            height: 2px;
            background: #fff;
            box-shadow: 12px 0 0 #fff, 6px 6px 0 #fff, 6px 10px 0 #fff;
        }}

        .icon-chart {{
            width: 22px;
            height: 22px;
            position: relative;
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
        }}
        .icon-chart::before {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 5px;
            height: 14px;
            background: #fff;
            border-radius: 2px 2px 0 0;
        }}
        .icon-chart::after {{
            content: '';
            position: absolute;
            bottom: 0;
            right: 0;
            width: 5px;
            height: 8px;
            background: #fff;
            border-radius: 2px 2px 0 0;
        }}

        .icon-refresh {{
            width: 20px;
            height: 20px;
            position: relative;
        }}
        .icon-refresh::before {{
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 16px;
            height: 16px;
            border: 2px solid #fff;
            border-radius: 50%;
            border-top-color: transparent;
            border-left-color: transparent;
            transform: rotate(-45deg);
        }}
        .icon-refresh::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 3px;
            width: 6px;
            height: 6px;
            border-top: 2px solid #fff;
            border-right: 2px solid #fff;
            transform: rotate(45deg);
        }}

        .icon-clock {{
            width: 20px;
            height: 20px;
            border: 2px solid #fff;
            border-radius: 50%;
            position: relative;
        }}
        .icon-clock::before {{
            content: '';
            position: absolute;
            top: 3px;
            left: 7px;
            width: 2px;
            height: 6px;
            background: #fff;
            border-radius: 1px;
        }}
        .icon-clock::after {{
            content: '';
            position: absolute;
            top: 7px;
            left: 7px;
            width: 5px;
            height: 2px;
            background: #fff;
            border-radius: 1px;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            font-family: 'Microsoft YaHei';
            margin-top: 12px;
        }}

        .metric-subtitle {{
            font-size: 11px;
            color: #aaa;
            font-family: 'Microsoft YaHei';
            position: absolute;
            bottom: 8px;
            right: 15px;
            line-height: 1.4;
            text-align: right;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}

        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}

            .header h1 {{
                font-size: 28px;
            }}
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
            <div class="card-full">{metrics_html}</div>
            <div class="card-wide">{charts_html[0]}</div>
            <div class="card">{charts_html[1]}</div>
            <div class="card">{charts_html[2]}</div>
            <div class="card-wide">{trend_chart_html}</div>
            {''.join([f'<div class="card">{html}</div>' for html in charts_html[3:]])}
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
