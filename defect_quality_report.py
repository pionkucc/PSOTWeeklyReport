"""
缺陷质量分析可视化报告生成器
生成清新UI风格的交互式HTML图表 (卡片平铺布局)
使用ECharts渲染图表，支持hover tooltip圆角+阴影+padding

使用方法:
    python defect_quality_report.py

输出文件:
    缺陷质量分析报告.html
"""

import re
import pandas as pd
from pyecharts.charts import Bar, Line
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode

# 导入模块
from config import COLORS, TOOLTIP_CSS, TITLE, SUBTITLE, OUTPUT_FILE
from data_processor import load_data, preprocess_data, load_panels_data, load_sheet2_data, load_warning_data
from views.chart_views import (
    chart_to_html,
    create_pie_chart,
    create_horizontal_bar_with_legend,
    create_vertical_bar_with_legend,
    create_histogram,
    create_metrics_cards_html
)
from views.detail_view import create_detail_view_html
from views.home_view import create_home_view_html
from templates.html_template import build_html_template, save_report


# 加载并预处理数据
df, total, task_count, subtask_count = load_data()
df = preprocess_data(df)

# 生成图表HTML列表
charts_html = []

# 1. 质量指标概览
metrics_html = create_metrics_cards_html(df, total, task_count, subtask_count)

# 2. 处理人员缺陷统计 (堆叠柱状图 + 折线图)
status_list = ['Closed', 'Fixed', 'New', 'Pending', 'ReOpen']
handler_status_counts = df.groupby(['处理人员', '缺陷状态']).size().unstack(fill_value=0)

for status in status_list:
    if status not in handler_status_counts.columns:
        handler_status_counts[status] = 0

handler_status_counts = handler_status_counts[status_list]
handler_totals = handler_status_counts.sum(axis=1)
handler_status_counts = handler_status_counts.loc[handler_totals.sort_values(ascending=False).index]
handlers = handler_status_counts.index.tolist()

avg_fix_time = df.groupby('处理人员')['缺陷修复周期(天)'].mean()
avg_fix_time = avg_fix_time.reindex(handlers).fillna(0)

bar = Bar(init_opts=opts.InitOpts(height="400px"))
bar.add_xaxis(handlers)
handler_totals_list = handler_status_counts.sum(axis=1).tolist()

for i, status in enumerate(status_list):
    if i == len(status_list) - 1:
        bar.add_yaxis(
            status, handler_status_counts[status].tolist(), stack="total",
            color=COLORS['status_soft'].get(status, '#A8D8EA'),
            label_opts=opts.LabelOpts(
                is_show=True, position="top",
                formatter=JsCode(f"function(p){{ var totals = {handler_totals_list}; return totals[p.dataIndex]; }}"),
                font_family="Microsoft YaHei", font_size=11, color="#2c3e50"
            )
        )
    else:
        bar.add_yaxis(
            status, handler_status_counts[status].tolist(), stack="total",
            color=COLORS['status_soft'].get(status, '#A8D8EA'),
            label_opts=opts.LabelOpts(is_show=False)
        )

bar.set_global_opts(
    title_opts=opts.TitleOpts(title="处理人员缺陷统计", pos_left="center",
        title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#2c3e50", font_family="Microsoft YaHei")),
    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow", extra_css_text=TOOLTIP_CSS,
        formatter=JsCode("function(params){var result=params[0].name+'<br/>';params.forEach(function(item){if(item.seriesName==='平均修复时长(天)'){var val=item.value[1]!==undefined?item.value[1]:item.value;result+=item.marker+item.seriesName+': '+val.toFixed(2)+'<br/>';}else{result+=item.marker+item.seriesName+': '+item.value+'<br/>';} });return result;}")),
    xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11, rotate=15)),
    yaxis_opts=opts.AxisOpts(name="数量", splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(type_="dashed")),
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei")),
    legend_opts=opts.LegendOpts(is_show=True, orient="horizontal", pos_top="bottom", pos_left="center",
        item_width=25, item_height=14, textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei", font_size=11))
)

line = Line()
line.add_xaxis(handlers)
line.add_yaxis("平均修复时长(天)", avg_fix_time.values.tolist(), yaxis_index=1, is_smooth=True,
    color="#F5C4D0", linestyle_opts=opts.LineStyleOpts(width=2.5), symbol="circle", symbol_size=8,
    label_opts=opts.LabelOpts(is_show=True, position="top", distance=8,
        formatter=JsCode("function(p){return p.value[1]>0?p.value[1].toFixed(2):''}"),
        font_family="Microsoft YaHei", font_size=12, font_weight="bold", color="#F5C4D0"),
    z=10)

bar.overlap(line)
bar.extend_axis(yaxis=opts.AxisOpts(name="平均修复时长(天)", position="right",
    axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei"),
    splitline_opts=opts.SplitLineOpts(is_show=False)))

charts_html.append(chart_to_html(bar, "chart_handler"))

# 3. 缺陷状态分布
pie = create_pie_chart(df['缺陷状态'], '缺陷状态分布', hole=0.4,
    colors=[COLORS['status'].get(s, '#A8D8EA') for s in df['缺陷状态'].value_counts().index])
charts_html.append(chart_to_html(pie, "chart_status"))

# 4. 关联任务项统计 (横向柱状图，带底部自定义图例)
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
task_legend_items = ''.join([
    f'<span class="legend-item" data-index="{i}" style="cursor:pointer;display:inline-block;margin:0 8px;"><span style="display:inline-block;width:14px;height:14px;background:{task_colors[i]};border-radius:2px;margin-right:4px;"></span><span style="font-family:Microsoft YaHei;font-size:11px;color:#333;">{cat}</span></span>'
    for i, cat in enumerate(task_categories)
])

task_cat_json = str(task_categories)
task_val_json = str(task_values)
task_colors_json = str(task_colors)

charts_html.append(f'''
<div id="chart_task" style="width:100%;height:350px"></div>
<div class="custom-legend" style="text-align:center;margin-top:5px;">{task_legend_items}</div>
<script>
(function() {{
    var categories = {task_cat_json};
    var values = {task_val_json};
    var colors = {task_colors_json};
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
                itemStyle: {{
                    color: function(params) {{ return newColors[params.dataIndex]; }}
                }}
            }}
        }});
    }}

    var chart = echarts.init(document.getElementById('chart_task'));
    chart.setOption({task_options});
    chart.setOption({{grid: {{left: '120px', right: '60px', top: '50px', bottom: '30px'}}}});

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

# 5. 缺陷趋势分析
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
line_chart.add_yaxis("新增缺陷", new_data, is_smooth=True, color="#A0E7E5", symbol="circle", symbol_size=8,
    areastyle_opts=opts.AreaStyleOpts(opacity=0.3), label_opts=opts.LabelOpts(is_show=False))
line_chart.add_yaxis("遗留缺陷", legacy_data, is_smooth=True, color="#FFD69B", symbol="circle", symbol_size=8,
    areastyle_opts=opts.AreaStyleOpts(opacity=0.3), label_opts=opts.LabelOpts(is_show=False))
line_chart.add_yaxis("关闭缺陷", closed_data, is_smooth=True, color="#F5C4D0", symbol="circle", symbol_size=8,
    areastyle_opts=opts.AreaStyleOpts(opacity=0.3), label_opts=opts.LabelOpts(is_show=False))

line_chart.set_global_opts(
    title_opts=opts.TitleOpts(title="缺陷趋势分析", pos_left="center",
        title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#2c3e50", font_family="Microsoft YaHei")),
    tooltip_opts=opts.TooltipOpts(trigger="axis", extra_css_text=TOOLTIP_CSS),
    xaxis_opts=opts.AxisOpts(name="日期", axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei", font_size=11)),
    yaxis_opts=opts.AxisOpts(name="缺陷数量", splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(type_="dashed")),
        axislabel_opts=opts.LabelOpts(font_family="Microsoft YaHei")),
    legend_opts=opts.LegendOpts(is_show=True, orient="horizontal", pos_top="bottom", pos_left="center",
        item_width=25, item_height=14, textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei", font_size=11))
)

trend_chart_html = chart_to_html(line_chart, "chart_trend")

# 6. 缺陷修复周期分布
fix_period = df['缺陷修复周期(天)'].dropna()
hist_chart = create_histogram(fix_period, '缺陷修复周期分布')
charts_html.append(chart_to_html(hist_chart, "chart_histogram"))

# 7. 缺陷返工情况
rework_counts = df['返工次数'].value_counts()
rework_labels = [f'返工{i}次' if i > 0 else '无返工' for i in rework_counts.index]
rework_data = [(rework_labels[i], int(rework_counts.values[i])) for i in range(len(rework_counts))]
rework_colors = ['#82E0AA', '#F7DC6F', '#F0B27A'][:len(rework_counts)]

from pyecharts.charts import Pie
pie_rework = Pie(init_opts=opts.InitOpts(height="350px"))
pie_rework.add("", rework_data, radius=["40%", "70%"], center=["50%", "45%"],
    label_opts=opts.LabelOpts(formatter="{b}: {d}%", font_family="Microsoft YaHei"))
rework_color_js = f"""function(params) {{ var colors = {rework_colors}; return colors[params.dataIndex]; }}"""
pie_rework.set_series_opts(itemstyle_opts=opts.ItemStyleOpts(color=JsCode(rework_color_js)))
pie_rework.set_global_opts(
    title_opts=opts.TitleOpts(title="缺陷返工情况", pos_left="center",
        title_textstyle_opts=opts.TextStyleOpts(font_size=16, color="#2c3e50", font_family="Microsoft YaHei")),
    tooltip_opts=opts.TooltipOpts(trigger="item", extra_css_text=TOOLTIP_CSS),
    legend_opts=opts.LegendOpts(is_show=True, orient="horizontal", pos_top="bottom", pos_left="center",
        item_width=25, item_height=14, textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei", font_size=11))
)
charts_html.append(chart_to_html(pie_rework, "chart_rework"))

# 8. 缺陷发现阶段分布
stage_order = ['2.1-系统测试【基本流】', '2.2-系统测试【备选流】', '4.1-回归测试【基本流】', '4.2-回归测试【备选流】']
stage_colors = [COLORS['stage_find'].get(s, '#C4E1C1') for s in stage_order]
charts_html.append(create_horizontal_bar_with_legend(df['发现阶段'], '缺陷发现阶段分布', colors=stage_colors, chart_id="chart_stage", order=stage_order, grid_left="200px"))

# 9. 缺陷类型分布
pie_type = create_pie_chart(df['缺陷类型'], '缺陷类型分布', hole=0.35, colors=COLORS['pastel'], height="420px", outer_radius="60%")
charts_html.append(chart_to_html(pie_type, "chart_type"))

# 10. 缺陷引入原因分析
charts_html.append(create_horizontal_bar_with_legend(df['引入原因'].dropna(), '缺陷引入原因分析', colors=COLORS['pastel'], chart_id="chart_cause", grid_left="140px"))

# 11. 缺陷优先级分布
priority_order = ['优先', '高', '中', '低']
priority_colors = [COLORS['priority'].get(p, '#A8D8EA') for p in priority_order]
charts_html.append(create_vertical_bar_with_legend(df['优先级'], '缺陷优先级分布', colors=priority_colors, chart_id="chart_priority", order=priority_order))

# 12. 缺陷严重程度分布
severity_order = ['严重', '一般', '轻微', '建议']
severity_colors = [COLORS['severity'].get(s, '#A8D8EA') for s in severity_order]
charts_html.append(create_horizontal_bar_with_legend(df['严重程度'], '缺陷严重程度分布', colors=severity_colors, chart_id="chart_severity", order=severity_order, grid_left="80px"))

# 13. 缺陷引入阶段分布
charts_html.append(create_horizontal_bar_with_legend(df['引入阶段'].dropna(), '缺陷引入阶段分布', colors=COLORS['fresh'], chart_id="chart_intro", grid_left="140px"))

# 生成明细视图
detail_view_html = create_detail_view_html(df, total)

# 加载公共面板数据
panels_data = load_panels_data()
sheet2_data = load_sheet2_data()
warning_data = load_warning_data()

# 生成主页视图
home_view_html = create_home_view_html(panels_data, sheet2_data, warning_data)

# 组装HTML并保存
html_content = build_html_template(total, metrics_html, charts_html, trend_chart_html, detail_view_html, home_view_html)
save_report(html_content)

print(f'报告已生成: {OUTPUT_FILE}')
print(f'共 {total} 条缺陷数据')