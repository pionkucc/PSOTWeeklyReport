# 缺陷质量分析报告生成器 - 代码结构与数据流

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     defect_quality_report.py                     │
│                        (主入口 - 协调层)                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ config.py     │   │ data_processor│   │   views/      │
│ colors.py     │   │     .py       │   │               │
│ (配置层)      │   │ (数据层)      │   │ (视图层)      │
└───────────────┘   └───────────────┘   └───────────────┘
                                                │
                        ┌───────────────────────┼───────────────────┐
                        │                       │                   │
                        ▼                       ▼                   ▼
                ┌───────────────┐       ┌───────────────┐   ┌───────────────┐
                │ home_view.py  │       │ chart_views.py│   │ detail_view.py│
                │ (主页视图)    │       │ (图表视图)    │   │ (明细视图)    │
                └───────────────┘       └───────────────┘   └───────────────┘
                        │                       │                   │
                        └───────────────────────┼───────────────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │ templates/            │
                                    │ html_template.py      │
                                    │ (HTML模板组装层)      │
                                    └───────────────────────┘
```

---

## 二、数据流详解

### 2.1 主入口执行流程 (defect_quality_report.py)

```python
# 1. 加载原始数据
df, total, task_count, subtask_count = load_data()  # 从Excel读取
df = preprocess_data(df)  # 预处理：修复周期列转为数值

# 2. 生成图表视图（13个图表）
metrics_html = create_metrics_cards_html(df, total, task_count, subtask_count)  # 质量指标卡片
charts_html = []  # 各类图表HTML
trend_chart_html = create_trend_chart(df, SUBTITLE)  # 缺陷趋势分析

# 3. 加载主页视图数据
panels_data = load_panels_data()    # Sheet3公共面板
sheet2_data = load_sheet2_data()    # Sheet2测试进度统计
warning_data = load_warning_data()  # 缺陷预警数据

# 4. 生成各视图HTML
detail_view_html = create_detail_view_html(df, total)  # 明细视图
home_view_html = create_home_view_html(panels_data, sheet2_data, warning_data, df, total)  # 主页视图

# 5. 组装完整HTML并保存
html_content = build_html_template(total, metrics_html, charts_html, trend_chart_html, detail_view_html, home_view_html)
save_report(html_content)  # 保存到 history_reports/ + PSOT_Weekly_Report.html
```

### 2.2 数据加载流程 (data_processor.py)

| 函数 | 数据来源 | 返回值 | 说明 |
|------|----------|--------|------|
| `load_data()` | Sheet1 | `(df, total, task_count, subtask_count)` | 读取缺陷明细+Sheet2任务计数 |
| `preprocess_data(df)` | DataFrame | `df` | 处理修复周期列，'/'转NaN，转数值 |
| `load_panels_data()` | Sheet3 | `[{title, content_parts}]` | 读取公共面板，保留富文本格式 |
| `load_sheet2_data()` | Sheet2 | `df` | 读取测试进度和缺陷统计表格 |
| `load_warning_data()` | Sheet1 | `{overdue_rework, overdue, rework, total}` | 筛选三类预警数据 |

### 2.3 数据传递关系

```
缺陷明细.xlsx (Sheet1)
    │
    ├── load_data() → df, total ─────────────────────────────────┐
    │                                                            │
    ├── preprocess_data() → df (处理后)                          │
    │       │                                                    │
    │       ├── chart_views.create_metrics_cards_html(df, total) │
    │       ├── chart_views.*_chart(df) → 各图表                 │
    │       ├── detail_view.create_detail_view_html(df, total)   │
    │       └── home_view._render_first_panel_content(df, total) │ ← v3.5新增
    │                                                            │
    └── load_warning_data() → warning_data ──────────────────────┤
                                                                │
缺陷明细.xlsx (Sheet2)                                          │
    │                                                           │
    └── load_sheet2_data() → sheet2_data ───────────────────────┤
                                                                │
缺陷明细.xlsx (Sheet3)                                          │
    │                                                           │
    └── load_panels_data() → panels_data ───────────────────────┤
                                                                │
                                                                ▼
                                          create_home_view_html(panels_data, sheet2_data, warning_data, df, total)
```

---

## 三、各模块职责详解

### 3.1 config.py - 配置层

```python
# 核心配置
TITLE = 'POST-产品标准化运营工具-质量周报'
SUBTITLE = '报告周期：2026年05月25日-2026年05月29日'
INPUT_FILE = '缺陷明细.xlsx'
OUTPUT_FILE = generate_output_filename()  # 动态生成

# 阈值配置
OVERDUE_DAYS = 3        # 超期天数阈值
REWORK_THRESHOLD = 3    # 返工次数阈值

# 功能开关
SHOW_STATS_DATA = True  # 明细数据展示开关（v3.5新增）

# 导入颜色配置
from colors import COLORS
```

### 3.2 colors.py - 颜色配置层

```python
COLORS = {
    # 图表配色
    'pastel': [...],      # 饼图柔和色系
    'fresh': [...],       # 柱状图清新色系
    
    # 状态配色（多场景）
    'status': {...},      # 基础状态色
    'status_soft': {...}, # 柔和状态色
    'status_detail': {...}, # 明细视图状态色
    'status_home': {...}, # 主页视图状态色
    
    # 优先级配色
    'priority': {...},
    'priority_detail': {'优先': '#EF5350', '高': '#EF5350', '中': '#FFA726', '低': '#1C91FD'},
    
    # 全局主题色
    'theme': {'primary': '#1C91FD', 'secondary': '#AA96DA', ...},
    
    # 背景配色
    'background': {'modal': 'rgba(170,150,218,0.15)', ...},
    
    # 质量指标卡片渐变
    'metric_cards': {'任务项': '...', '平均修复时长': '...', ...}
}
```

### 3.3 views/home_view.py - 主页视图

**核心函数**：

| 函数 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `create_home_view_html()` | panels_data, sheet2_data, warning_data, df, total | HTML | 主页视图主入口 |
| `_create_panel_card()` | panel, is_first, is_second, df, total | HTML | 单个面板卡片 |
| `_render_first_panel_content()` | content_parts, df, total | (content, stats, stats_data, defect) | 第一个面板内容渲染 |
| `_render_table_content()` | sheet2_data | (table, bar, title) | 测试进度表格+条形图 |
| `_render_ui_automation()` | content_parts | (metrics, remaining) | UI自动化建设章节 |
| `_render_coord_items()` | content_parts | HTML | 待协调事项章节 |
| `_render_next_week_plan()` | content_parts | HTML | 下周测试计划章节 |
| `get_home_view_css()` | - | CSS | 主页视图样式 |
| `get_home_view_js()` | - | JS | 主页视图脚本 |

**第一个面板结构（测试进度概览）**：

```
panel-card (left-progress-card)
    │
    ├── panel-card-title: "测试进度概览"
    │
    ├── panel-content: 提测功能标签
    │
    ├── stat-grid: 测试总进度 + 回归总进度
    │
    ├── stats-data-wrapper: 明细统计数据（v3.5新增，可配置关闭）
    │   └── stats-data-grid
    │       ├── 遗留缺陷
    │       ├── 平均修复时间
    │       ├── 基本流占比
    │       └── 返工次数
    │
    └── defect-summary: 本周新增缺陷总数 + 状态分布
```

**明细统计数据计算（v3.5）**：

```python
if SHOW_STATS_DATA and df is not None and total > 0:
    # 遗留缺陷：非Closed状态的缺陷数
    legacy_count = len(df[df['缺陷状态'] != 'Closed'])
    
    # 平均修复时间：修复周期列的均值
    avg_fix_time = df['缺陷修复周期(天)'].dropna().mean()
    
    # 基本流占比：发现阶段含"基本流"的缺陷占比
    basic_flow = len(df[df['发现阶段'].str.contains('基本流', na=False)])
    basic_flow_rate = basic_flow / total * 100
    
    # 返工次数：所有缺陷返工次数的总和
    rework_count = int(df['返工次数'].sum())
```

### 3.4 views/chart_views.py - 图表视图

**核心函数**：

| 函数 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `create_metrics_cards_html()` | df, total, task_count, subtask_count | HTML | 质量指标卡片（5个） |
| `create_pie_chart()` | data, title, hole, colors, height | chart | 饼图/环形图 |
| `create_horizontal_bar_with_legend()` | data, title, colors, chart_id, order | HTML | 横向柱状图 |
| `create_vertical_bar_with_legend()` | data, title, colors, chart_id, order | HTML | 纵向柱状图 |
| `create_histogram()` | data, title, height | chart | 直方图 |
| `chart_to_html()` | chart, chart_id | HTML | ECharts转内嵌HTML |

**质量指标卡片数据**（与主页明细统计一致）：

```python
# 任务项：从Sheet2合计行获取
# 平均修复时长：df['缺陷修复周期(天)'].dropna().mean()
# 遗留缺陷：len(df[df['缺陷状态'] != 'Closed'])
# 基本流占比：len(df[df['发现阶段'].str.contains('基本流')]) / total * 100
# 返工率：len(df[df['返工次数'] > 0]) / total * 100  # 注意：是返工率，不是返工次数
```

### 3.5 views/detail_view.py - 明细视图

**技术栈**：Vue3 + Element Plus

**核心功能**：
- 筛选器：状态、处理人员、优先级、发现阶段、缺陷类型、日期范围
- 表格：按登记时间倒序，7列展示
- 弹窗：单击行触发，显示完整字段

**弹窗字段**（v3.5统一）：

```python
detail_cols = {
    '缺陷编号', '产品线', '产品模块', '缺陷状态', '缺陷摘要',
    '优先级', '登记人', '处理人员', '登记时间', '修复时间', '关闭时间',
    '发现阶段', '引入阶段', '引入原因', '缺陷来源', '返工次数',
    '严重程度', '缺陷类型', '缺陷修复周期(天)', '缺陷关闭周期(天)'
}
```

### 3.6 templates/html_template.py - HTML模板

**核心函数**：

| 函数 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `build_html_template()` | total, metrics_html, charts_html, ... | HTML | 组装完整HTML |
| `save_report()` | html_content | - | 保存报告文件 |

**HTML结构**：

```html
<html>
<head>
    <!-- CSS样式：全局 + 图表 + 视图按钮 -->
    <!-- CDN：ECharts、dom-to-image-more、Element Plus -->
</head>
<body>
    <!-- 导航栏：标题 + 视图切换按钮 + 截图按钮 -->
    
    <!-- 主页视图 homeView -->
    <!-- 图表视图 chartView -->
    <!-- 明细视图 detailView -->
    
    <!-- 放大弹窗 modalOverlay -->
    <!-- 截图加载遮罩 -->
    
    <!-- JavaScript -->
    <script>
        // chartConfigs: 图表配置数组
        // toggleTable(): 切换图表/表格
        // enlargeChart() / closeEnlargeModal(): 放大弹窗
        // switchView(): 视图切换
        // screenshotReport(): 截图功能
        // home_view_css + home_view_js: 主页视图注入
    </script>
</body>
</html>
```

---

## 四、交互功能详解

### 4.1 图表切换表格 (toggleTable)

```javascript
function toggleTable(chartId, idx) {
    // 使用 visibility 替代 display，保留容器尺寸
    chartDiv.style.visibility = 'hidden';  // 隐藏图表
    tableDiv.classList.add('active');       // 显示表格
    
    // 切换回图表时延迟 resize
    setTimeout(function() {
        chart.resize();  // 确保正确渲染
    }, 100);
}
```

### 4.2 视图切换 (switchView)

```javascript
function switchView(view) {
    // 切换到图表视图时 resize 所有图表
    if (view === 'chart') {
        setTimeout(function() {
            document.querySelectorAll('div[id^="chart_"]').forEach(function(chartDiv) {
                var chart = echarts.getInstanceByDom(chartDiv);
                if (chart) chart.resize();
            });
        }, 100);
    }
}
```

### 4.3 缺陷预警弹窗

```javascript
function showWarningModal(detail) {
    // 渲染状态标签和优先级标签
    if (key === '缺陷状态') {
        valueHtml = '<span class="status-tag status-' + value + '">' + value + '</span>';
    } else if (key === '优先级') {
        valueHtml = '<span class="priority-tag priority-' + value + '">' + value + '</span>';
    }
    
    // 毛玻璃背景 #1c91fd0d
    // 点击遮罩关闭
}
```

---

## 五、配置开关说明

| 配置项 | 文件 | 默认值 | 作用 |
|--------|------|--------|------|
| `SHOW_STATS_DATA` | config.py | True | 主页测试进度概览中是否显示明细统计数据 |
| `OVERDUE_DAYS` | config.py | 3 | 超期天数阈值，>=此值纳入超期预警 |
| `REWORK_THRESHOLD` | config.py | 3 | 返工次数阈值，>=此值纳入返工预警 |

---

## 六、关键CSS类名速查

| 类名 | 用途 | 文件 |
|------|------|------|
| `.stat-grid` / `.stat-box` | 测试总进度/回归总进度卡片 | home_view.py |
| `.stats-data-wrapper` / `.mini-stat-box` | 明细统计数据区域（v3.5） | home_view.py |
| `.defect-summary` | 缺陷统计区域 | home_view.py |
| `.warning-row` | 缺陷预警行 | home_view.py |
| `.warning-modal-overlay` | 缺陷预警弹窗遮罩 | home_view.py |
| `.detail-modal-overlay` | 明细视图弹窗遮罩 | detail_view.py |
| `.modal-overlay` | 图表放大弹窗遮罩 | html_template.py |
| `.chart-btn` | 图表右上角按钮 | html_template.py |
| `.chart-btn.active` | 切换表格按钮激活状态 | html_template.py |
| `.detail-table` / `.stats-table` | 明细视图表格 / 主视图统计表格 | detail_view.py / home_view.py |
| `.detail-table th` / `.stats-table th` | 表头（蓝色 #1C91FD，白色加粗） | detail_view.py / home_view.py |

---

## 七、版本迭代要点

### v3.5 关键变更

1. **数据传递**：`create_home_view_html()` 新增 `df, total` 参数
2. **函数返回值**：`_render_first_panel_content()` 返回四元组
3. **弹窗统一**：明细视图替换 el-dialog 为自定义弹窗
4. **样式统一**：弹窗背景色 `#1c91fd0d`，滚动条灰色 `#ccc`
5. **交互修复**：图表切换使用 visibility，放大弹窗重构关闭逻辑
6. **表格样式**：表头整行蓝色 #1C91FD，文字白色加粗；表格内容左右留白16px；最后一行圆角处理
7. **列样式分离**：`.col-0` 只设置宽度，`td.col-0` 设置蓝色（数据行），表头继承白色

---

## 八、常见问题排查

### Q1: 预警数据不正确？

检查配置阈值：
```python
OVERDUE_DAYS = 3    # 超期天数阈值
REWORK_THRESHOLD = 3  # 返工次数阈值
```
修改阈值后需重新运行脚本生成报告。

### Q2: 图表切换后空白？

v3.5已修复，使用 `visibility` 替代 `display`，并延迟 resize。

### Q3: 弹窗关闭按钮无响应？

v3.5已修复，添加 `z-index` 和 `pointer-events`，重构事件监听。

---

## 九、扩展开发指南

### 添加新统计指标

在 `_render_first_panel_content()` 中添加计算逻辑：
```python
if SHOW_STATS_DATA and df is not None and total > 0:
    # 新增计算
    new_metric = ...  # 从 df 计算
    
    # 添加到 stats_data_html
    stats_data_html += '<div class="mini-stat-box">...</div>'
```

### 添加新图表

1. 在 `views/chart_views.py` 创建图表函数
2. 在 `defect_quality_report.py` 调用并添加到 `charts_html`
3. 在 `html_template.py` 的 `chartConfigs` 数组添加配置

### 添加新配置项

在 `config.py` 添加常量，在相应模块导入使用。

---

## 十、v3.5.1 新增功能

### 10.1 HTML文件引用

待协调事项内容支持引用外部HTML文件，解决Excel单元格字符限制：

```python
# data_processor.py
# 检测是否是HTML文件路径
if text_stripped.endswith('.html') or text_stripped.endswith('.htm'):
    # 读取HTML文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        full_text += file_content
```

**使用方法**：
- Excel待协调事项内容填写HTML文件路径（如 `/待协调事项文档.html`）
- 支持相对路径（基于Excel文件目录）和绝对路径

### 10.2 面板图片功能

每个面板支持在内容下方显示图片缩略图：

```python
# data_processor.py - 读取图片列
for col_idx in range(3, ws.max_column + 1):
    image_cell = ws.cell(row=row_idx, column=col_idx)
    if image_cell.value and not cell_val.startswith('='):
        # 添加到images列表
        images.append(full_path)

# views/home_view.py - 渲染缩略图
def _render_image_thumbnail(image_path):
    # 图片转base64嵌入
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    # 生成缩略图HTML
    html = f'''
    <div class="panel-image-section">
        <div class="image-thumbnail" onclick="showImageModal(...)">
            <img src="data:{mime_type};base64,{image_base64}" />
        </div>
    </div>
    '''
```

**使用方法**：
- Sheet3第3列及后续列填写图片文件路径
- 图片显示在对应面板内容最下方
- 点击缩略图弹出放大查看

### 10.3 图片相关CSS

```css
.panel-image-section {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
}
.image-thumbnail {
    max-width: 200px;
    border-radius: 8px;
    cursor: pointer;
}
.thumbnail-img {
    max-height: 150px;
    object-fit: cover;
}
.image-modal-overlay {
    background: rgba(0,0,0,0.85);
    /* 点击遮罩关闭 */
}
```

---

## 十一、v3.5.2 新增功能

### 11.1 测试进度概览剩余内容渲染

缺陷统计之后的内容单独渲染，添加分割线展示：

```python
# views/home_view.py - _render_first_panel_content
# 分割文本：缺陷统计之前和之后
before_defect_text = text_content[:defect_start_pos] if defect_start_pos > 0 else text_content
after_defect_text = text_content[defect_end_pos:] if defect_end_pos > 0 else ''

# 渲染剩余内容
if remaining_html and remaining_html.strip():
    remaining_section_html = f'''
        <div class="remaining-content-section">
            <hr class="section-divider" />
            <div class="remaining-content rich-text-content">
                {remaining_html}
            </div>
        </div>'''
```

### 11.2 缺陷预警缺省页

暂无预警数据时显示扁平风格SVG缺省图：

```python
# views/home_view.py - _render_warning_list
if not items:
    return '''
    <div class="empty-warning">
        <svg class="empty-warning-svg" viewBox="0 0 200 160">
            <!-- 蓝色圆形背景 + 盾牌图标 -->
        </svg>
        <p class="empty-warning-text">暂无预警数据</p>
    </div>
    '''
```

### 11.3 待协调事项font-size清理

清除内联`font-size`样式，避免与页面CSS冲突：

```python
# views/home_view.py - _render_coord_items
content_html = re.sub(r'\s*font-size:\s*\d+(?:\.\d+)?(?:pt|px|em|rem|%|vh|vw)?;?', '', content_html, flags=re.IGNORECASE)
content_html = re.sub(r'style="\s*"', '', content_html)  # 清理空的style属性
```

---

*文档版本：v3.5.2 (2026-06-08)*