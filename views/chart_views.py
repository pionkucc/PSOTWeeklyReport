"""
图表视图模块
包含饼图、柱状图、直方图等图表生成函数
"""

import pandas as pd
import numpy as np
import re
import json
from pyecharts.charts import Pie, Bar, Line
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode

from config import COLORS, TOOLTIP_CSS


def chart_to_html(chart, chart_id):
    """将ECharts图表转换为内嵌HTML"""
    options = chart.dump_options()
    return f'''
<div id="{chart_id}" style="width:100%;height:{chart.height if hasattr(chart, 'height') else '350px'}"></div>
<script>
echarts.init(document.getElementById('{chart_id}')).setOption({options});
</script>
'''


def create_pie_chart(data, title, hole=0.4, colors=None, height="350px", outer_radius="70%"):
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
        radius=[f"{hole*100}%", outer_radius],
        center=["50%", "50%"],
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


def create_horizontal_bar_with_legend(data, title, colors=None, chart_id="chart", order=None, grid_left="120px"):
    """创建带自定义图例的横向柱状图"""
    counts = data.value_counts()

    if order is not None:
        full_counts = {}
        for o in order:
            full_counts[o] = counts.get(o, 0)
        counts = pd.Series(full_counts)

    if len(counts) == 0:
        return f'<div id="{chart_id}" style="width:100%;height:350px"></div><p style="text-align:center;color:#999;">暂无数据</p>'

    categories = [str(x) for x in counts.index.tolist()]
    values = counts.values.tolist()
    if colors is None:
        colors = COLORS['fresh'][:len(counts)]

    while len(colors) < len(categories):
        colors.append(COLORS['fresh'][len(colors) % len(COLORS['fresh'])])

    bar = Bar(init_opts=opts.InitOpts(height="350px"))
    bar.add_xaxis(categories)
    bar.add_yaxis(
        "数量",
        values,
        label_opts=opts.LabelOpts(
            is_show=True,
            position="right",
            font_family="Microsoft YaHei",
            font_size=12
        )
    )

    bar.set_series_opts(
        itemstyle_opts=opts.ItemStyleOpts(
            color=JsCode(f"function(params) {{ var colors = {colors}; return colors[params.dataIndex]; }}"),
            border_color="white",
            border_width=2,
            opacity=0.85
        )
    )

    bar.reversal_axis()
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
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

    options = bar.dump_options()
    legend_items = ''.join([
        f'<span class="legend-item" data-index="{i}" style="cursor:pointer;display:inline-block;margin:0 8px;"><span style="display:inline-block;width:14px;height:14px;background:{colors[i]};border-radius:2px;margin-right:4px;"></span><span style="font-family:Microsoft YaHei;font-size:11px;color:#333;">{cat}</span></span>'
        for i, cat in enumerate(categories)
    ])

    cat_json = str(categories)
    val_json = str(values)
    colors_json = str(colors)

    return f'''
<div id="{chart_id}" style="width:100%;height:350px"></div>
<div class="custom-legend" style="text-align:center;margin-top:5px;">{legend_items}</div>
<script>
(function() {{
    var categories = {cat_json};
    var values = {val_json};
    var colors = {colors_json};
    var selected = {{}};
    for (var i = 0; i < categories.length; i++) selected[i] = true;

    function updateChart() {{
        var newCat = [], newVal = [], newColors = [];
        for (var i = 0; i < categories.length; i++) {{
            if (selected[i]) {{
                newCat.push(categories[i]);
                newVal.push(values[i]);
                newColors.push(colors[i]);
            }}
        }}
        chart.setOption({{
            yAxis: {{data: newCat}},
            series: {{
                data: newVal,
                itemStyle: {{color: function(params) {{ return newColors[params.dataIndex]; }}}}
            }}
        }});
    }}

    var chart = echarts.init(document.getElementById('{chart_id}'));
    chart.setOption({options});
    chart.setOption({{grid: {{left: '{grid_left}', right: '60px', top: '50px', bottom: '30px'}}}});

    var legendItems = document.querySelectorAll('#{chart_id} + .custom-legend .legend-item');
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
'''


def create_vertical_bar_with_legend(data, title, colors=None, chart_id="chart", order=None):
    """创建带自定义图例的纵向柱状图"""
    counts = data.value_counts()

    if order is not None:
        full_counts = {}
        for o in order:
            full_counts[o] = counts.get(o, 0)
        counts = pd.Series(full_counts)

    if len(counts) == 0:
        return f'<div id="{chart_id}" style="width:100%;height:350px"></div><p style="text-align:center;color:#999;">暂无数据</p>'

    categories = [str(x) for x in counts.index.tolist()]
    values = counts.values.tolist()
    if colors is None:
        colors = COLORS['fresh'][:len(counts)]

    while len(colors) < len(categories):
        colors.append(COLORS['fresh'][len(colors) % len(COLORS['fresh'])])

    bar = Bar(init_opts=opts.InitOpts(height="350px"))
    bar.add_xaxis(categories)
    bar.add_yaxis(
        "数量",
        values,
        label_opts=opts.LabelOpts(
            is_show=True,
            position="top",
            font_family="Microsoft YaHei",
            font_size=12
        )
    )

    bar.set_series_opts(
        itemstyle_opts=opts.ItemStyleOpts(
            color=JsCode(f"function(params) {{ var colors = {colors}; return colors[params.dataIndex]; }}"),
            border_color="white",
            border_width=2,
            opacity=0.85
        )
    )

    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            pos_left="center",
            title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#2c3e50", font_family="Microsoft YaHei")
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            axis_pointer_type="shadow",
            extra_css_text=TOOLTIP_CSS
        ),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
        ),
        yaxis_opts=opts.AxisOpts(
            name="数量",
            splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(type_="dashed")),
            axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)
        ),
        legend_opts=opts.LegendOpts(is_show=False)
    )

    options = bar.dump_options()
    legend_items = ''.join([
        f'<span class="legend-item" data-index="{i}" style="cursor:pointer;display:inline-block;margin:0 8px;"><span style="display:inline-block;width:14px;height:14px;background:{colors[i]};border-radius:2px;margin-right:4px;"></span><span style="font-family:Microsoft YaHei;font-size:11px;color:#333;">{cat}</span></span>'
        for i, cat in enumerate(categories)
    ])

    cat_json = str(categories)
    val_json = str(values)
    colors_json = str(colors)

    return f'''
<div id="{chart_id}" style="width:100%;height:350px"></div>
<div class="custom-legend" style="text-align:center;margin-top:-20px;">{legend_items}</div>
<script>
(function() {{
    var categories = {cat_json};
    var values = {val_json};
    var colors = {colors_json};
    var selected = {{}};
    for (var i = 0; i < categories.length; i++) selected[i] = true;

    function updateChart() {{
        var newCat = [], newVal = [], newColors = [];
        for (var i = 0; i < categories.length; i++) {{
            if (selected[i]) {{
                newCat.push(categories[i]);
                newVal.push(values[i]);
                newColors.push(colors[i]);
            }}
        }}
        chart.setOption({{
            xAxis: {{data: newCat}},
            series: {{
                data: newVal,
                itemStyle: {{color: function(params) {{ return newColors[params.dataIndex]; }}}}
            }}
        }});
    }}

    var chart = echarts.init(document.getElementById('{chart_id}'));
    chart.setOption({options});

    var legendItems = document.querySelectorAll('#{chart_id} + .custom-legend .legend-item');
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
'''


def create_histogram(data, title, height="300px"):
    """创建直方图 - ECharts版本"""
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


def create_metrics_cards_html(df, total, task_count, subtask_count):
    """创建质量指标卡片HTML"""
    closed = len(df[df['缺陷状态'] == 'Closed'])
    legacy_count = len(df[df['缺陷状态'] != 'Closed'])
    close_rate = closed / total * 100 if total > 0 else 0

    df['发现阶段'] = df['发现阶段'].str.strip()
    basic_flow = len(df[df['发现阶段'].str.contains('基本流', na=False)])
    basic_flow_rate = basic_flow / total * 100 if total > 0 else 0

    rework = len(df[df['返工次数'] > 0])
    rework_rate = rework / total * 100 if total > 0 else 0

    fix_period = df['缺陷修复周期(天)'].dropna()
    avg_fix_time = fix_period.mean()
    max_fix_time = fix_period.max()
    min_fix_time = fix_period.min()
    avg_fix_time_str = f'{avg_fix_time:.2f}天' if avg_fix_time > 0 else '--'
    max_fix_time_str = f'{max_fix_time:.0f}天' if max_fix_time > 0 else '--'
    min_fix_time_str = f'{min_fix_time:.0f}天' if min_fix_time > 0 else '--'

    cards = [
        ('任务项', f'{task_count}个', 'linear-gradient(135deg, rgba(168, 216, 234, 0.7) 0%, rgba(184, 224, 210, 0.7) 100%)', 'icon-task', f'子任务项{subtask_count}个'),
        ('平均修复时长', avg_fix_time_str, 'linear-gradient(135deg, rgba(247, 220, 111, 0.7) 0%, rgba(249, 213, 167, 0.7) 100%)', 'icon-clock', f'最大{max_fix_time_str}<br>最小{min_fix_time_str}'),
        ('遗留缺陷', f'{legacy_count}个', 'linear-gradient(135deg, rgba(130, 224, 170, 0.7) 0%, rgba(168, 232, 234, 0.7) 100%)', 'icon-bug', f'关闭率{close_rate:.1f}%'),
        ('基本流占比', f'{basic_flow_rate:.1f}%', 'linear-gradient(135deg, rgba(240, 178, 122, 0.7) 0%, rgba(252, 186, 211, 0.7) 100%)', 'icon-chart', f'{basic_flow}/{total}个'),
        ('返工率', f'{rework_rate:.1f}%', 'linear-gradient(135deg, rgba(170, 150, 218, 0.7) 0%, rgba(214, 234, 223, 0.7) 100%)', 'icon-refresh', f'{rework}/{total}个')
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