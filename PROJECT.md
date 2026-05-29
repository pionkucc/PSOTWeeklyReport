# 缺陷质量分析可视化报告生成器

生成清新UI风格的交互式HTML图表报告，支持图表视图和明细视图切换。

## 在线访问

- **访问地址**: https://pionkucc.github.io/PSOTWeeklyReport/PSOT_Weekly_Report_2026.05.18-2026.05.22.html
- **仓库地址**: https://github.com/pionkucc/PSOTWeeklyReport

> 注：仓库为私有，但Pages公开可访问

## 快速开始

```bash
python defect_quality_report.py
```

输出文件：`PSOT_Weekly_Report_YYYY.MM.DD-YYYY.MM.DD.html`（根据日期动态生成）

## 更新数据流程

### 方式一：本地脚本推送（推荐）

```bash
python auto_push.py
```

脚本自动执行：生成报告 → Git提交 → 推送到GitHub → Actions自动部署

### 方式二：手动操作

1. 替换 `缺陷明细.xlsx` 数据文件
2. 修改 `config.py` 中的 `SUBTITLE`（日期范围）
3. 运行 `python defect_quality_report.py`
4. Git提交并推送
5. 等待GitHub Actions部署完成

## GitHub Actions 自动部署

### 工作流配置

文件：`.github/workflows/deploy.yml`

**触发条件**：
- push到main/master分支
- 修改Excel文件、Python文件、配置文件时触发
- 支持手动触发（workflow_dispatch）

**部署流程**：
1. 检出代码
2. 安装Python依赖
3. 运行脚本生成HTML
4. 部署到GitHub Pages

**查看运行状态**：
```
https://github.com/pionkucc/PSOTWeeklyReport/actions
```

## 项目结构

```
F:\AI\Claude Code\Weekly_Report\
├── defect_quality_report.py    # 主入口程序
├── config.py                   # 配置常量模块（动态文件名生成）
├── data_processor.py           # 数据处理模块
├── auto_push.py                # 本地自动推送脚本（不提交到仓库）
├── requirements.txt            # Python依赖清单
├── .gitignore                  # Git排除配置
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions工作流
├── views/
│   ├── __init__.py
│   ├── chart_views.py          # 图表视图函数
│   ├── detail_view.py          # 明细视图函数
│   └── home_view.py            # 主页视图函数
├── templates/
│   ├── __init__.py
│   └── html_template.py        # HTML模板构建
├── versions/                    # 版本备份目录
│   ├── VERSION.md              # 版本记录
│   ├── v3.1_modular_backup.zip # v3.1备份
│   └── v3.2_modular_backup.zip # v3.2备份
├── 缺陷明细.xlsx                # 数据源
└── PSOT_Weekly_Report_*.html   # 输出报告（动态命名）
```

## 模块说明

### 1. config.py - 配置常量模块

**职责**：定义全局常量配置

**导出内容**：
| 常量 | 类型 | 说明 |
|------|------|------|
| `COLORS` | dict | 颜色配置字典，包含 pastel、fresh、status、status_soft、priority、severity、stage_find |
| `INPUT_FILE` | str | 输入文件路径 `'缺陷明细.xlsx'` |
| `OUTPUT_FILE` | str | 输出文件路径 `'缺陷质量分析报告.html'` |
| `TITLE` | str | 报告标题 |
| `SUBTITLE` | str | 报告副标题（日期范围） |
| `TOOLTIP_CSS` | str | Tooltip样式常量 |

**颜色配置结构**：
```python
COLORS = {
    'pastel': ['#A8D8EA', '#AA96DA', '#FCBAD3', ...],     # 柔和色调
    'fresh': ['#7FB3D5', '#76D7C4', '#F7DC6F', ...],      # 清新色调
    'status': {'New': '#F7DC6F', 'Closed': '#82E0AA', ...}, # 状态颜色
    'status_soft': {'Closed': '#B8E0D2', ...},             # 柔和状态色
    'priority': {'优先': '#E57373', '高': '#FFB74D', ...}, # 优先级颜色
    'severity': {'严重': '#E57373', ...},                  # 严重程度颜色
    'stage_find': {'2.1-系统测试【基本流】': '#A8D8EA', ...} # 发现阶段颜色
}
```

---

### 2. data_processor.py - 数据处理模块

**职责**：读取Excel数据并进行预处理

**导出函数**：

#### `load_data()`
- **功能**：读取Excel数据
- **返回**：`(df, total, task_count, subtask_count)`
  - `df`: DataFrame，主数据表
  - `total`: int，总缺陷数
  - `task_count`: int，任务项数量（从sheet2读取）
  - `subtask_count`: int，子任务项数量

#### `preprocess_data(df)`
- **功能**：预处理修复周期列，将 '/' 替换为 NaN，转换为数值类型
- **参数**：`df` - DataFrame
- **返回**：处理后的 DataFrame

#### `load_panels_data()`
- **功能**：读取Sheet3公共面板数据，保留富文本格式
- **返回**：面板数据列表，每项包含 title 和 content_parts

#### `load_sheet2_data()`
- **功能**：读取Sheet2测试进度和缺陷统计数据
- **返回**：DataFrame（测试进度表格数据）

---

### 3. views/chart_views.py - 图表视图模块

**职责**：生成各类ECharts图表

**导出函数**：

| 函数 | 功能 | 参数 |
|------|------|------|
| `chart_to_html(chart, chart_id)` | 将ECharts图表转换为内嵌HTML | chart对象, chart_id |
| `create_pie_chart(data, title, hole, colors, height)` | 创建饼图/环形图 | 数据列, 标题, 内径比例, 颜色, 高度 |
| `create_horizontal_bar_with_legend(data, title, colors, chart_id, order)` | 创建横向柱状图（带图例） | 数据列, 标题, 颜色, 图表ID, 排序 |
| `create_vertical_bar_with_legend(data, title, colors, chart_id, order)` | 创建纵向柱状图（带图例） | 同上 |
| `create_histogram(data, title, height)` | 创建直方图 | 数据列, 标题, 高度 |
| `create_metrics_cards_html(df, total, task_count, subtask_count)` | 创建质量指标卡片 | df, 总数, 任务数, 子任务数 |

---

### 4. views/detail_view.py - 明细视图模块

**职责**：生成缺陷明细列表视图

**导出函数**：

#### `create_detail_view_html(df, total)`
- **功能**：创建完整的明细视图HTML
- **参数**：
  - `df`: DataFrame，数据源
  - `total`: int，总记录数
- **返回**：HTML字符串

**功能特性**：
1. **筛选导航栏**：状态、处理人员、优先级下拉筛选 + 重置按钮
2. **数据表格**：9列展示（缺陷编号、状态、摘要、优先级、严重程度、处理人员、发现阶段、缺陷类型、修复周期）
3. **排序**：按登记时间倒序
4. **弹窗详情**：双击行弹出17个字段完整展示
5. **样式**：淡紫色调 #AA96DA，毛玻璃弹窗效果

---

### 5. views/home_view.py - 主页视图模块

**职责**：生成主页视图HTML

**导出函数**：

#### `create_home_view_html(panels_data, sheet2_data)`
- **功能**：创建主页视图HTML
- **参数**：
  - `panels_data`: 公共面板数据列表
  - `sheet2_data`: Sheet2表格数据DataFrame
- **返回**：HTML字符串

**功能特性**：
1. **本周测试概况**：两列卡片布局
   - 测试进度概览：动态提取[xxx]标签、进度指标、缺陷统计
   - 缺陷预警：带圆形数量标签（背景色#ffdcdb9c）
2. **测试进度和缺陷统计**：表格 + 条形图双卡片
   - 表格：Sheet2数据，表头蓝色(#1c91fd)
   - 进度列：圆形进度条，<30%红色，>=30%蓝色
   - 条形图：各任务项进度对比，100%时自动切换回归进度

#### `get_home_view_css()`
- **功能**：获取主页视图专用CSS

#### `get_home_view_js()`
- **功能**：获取主页视图专用JS（tooltip宽度检测）

---

### 6. templates/html_template.py - HTML模板模块

**职责**：组装完整的HTML报告页面

**导出函数**：

#### `build_html_template(total, metrics_html, charts_html, trend_chart_html, detail_view_html)`
- **功能**：组装完整HTML报告
- **参数**：
  - `total`: 总缺陷数
  - `metrics_html`: 指标卡片HTML
  - `charts_html`: 图表HTML列表
  - `trend_chart_html`: 趋势图HTML
  - `detail_view_html`: 明细视图HTML
- **返回**：完整HTML字符串

#### `save_report(html_content)`
- **功能**：保存HTML报告到文件
- **参数**：`html_content` - HTML字符串

---

### 7. defect_quality_report.py - 主入口程序

**职责**：协调各模块，生成完整报告

**执行流程**：
```
1. 加载数据 (data_processor.load_data)
2. 预处理数据 (data_processor.preprocess_data)
3. 生成图表视图：
   - 质量指标概览
   - 处理人员缺陷统计（堆叠柱状图+折线图）
   - 缺陷状态分布（饼图）
   - 关联任务项统计（横向柱状图）
   - 缺陷趋势分析（面积折线图）
   - 缺陷修复周期分布（直方图）
   - 缺陷返工情况（饼图）
   - 缺陷发现阶段分布
   - 缺陷类型分布（环形图）
   - 缺陷引入原因分析
   - 缺陷优先级分布
   - 缺陷严重程度分布
   - 缺陷引入阶段分布
4. 加载公共面板数据 (data_processor.load_panels_data)
5. 加载Sheet2数据 (data_processor.load_sheet2_data)
6. 生成主页视图 (home_view.create_home_view_html)
7. 生成明细视图 (detail_view.create_detail_view_html)
8. 组装HTML模板 (html_template.build_html_template)
9. 保存报告 (html_template.save_report)
```

---

## 数据流

```
缺陷明细.xlsx
     │
     ▼
data_processor.load_data()
     │
     ▼
┌─────────────────────────────────────┐
│  df, total, task_count, subtask_count │
└─────────────────────────────────────┘
     │
     ├──────────────────┬──────────────────┐
     ▼                  ▼                  ▼
chart_views.py    detail_view.py    html_template.py
     │                  │                  │
     ▼                  ▼                  ▼
charts_html[]    detail_view_html    html_template
     │                  │                  │
     └──────────────────┴──────────────────┘
                        │
                        ▼
              缺陷质量分析报告.html
```

---

## 数据源结构

**文件**：`缺陷明细.xlsx`

**Sheet1 - 缺陷明细**：
| 列索引 | 列名 | 说明 |
|--------|------|------|
| 0 | 登记时间 | 时间范围 |
| 1 | 迭代版本 | 版本信息 |
| 2 | 关联模块 | 模块名称 |
| 3 | 缺陷编号 | 唯一标识 |
| 4 | 产品线 | 产品分类 |
| 5 | 产品模块 | 模块分类 |
| 6 | 缺陷状态 | New/Closed/Fixed/Pending/ReOpen |
| 7 | 缺陷摘要 | 问题描述 |
| 8 | 优先级 | 低/中/高/优先 |
| 9 | 登记人 | 登记者 |
| 10 | 处理人员 | 负责人 |
| 11 | 登记时间 | 具体时间 |
| 12 | 修改时间 | 修改时间 |
| 13 | 关闭时间 | 关闭时间 |
| 14 | 当前阶段 | 阶段状态 |
| 15 | 发现阶段 | 测试阶段 |
| 16 | 引入阶段 | 引入环节 |
| 17 | 引入原因 | 原因分类 |
| 18 | 缺陷来源 | 来源渠道 |
| 19 | 返工次数 | 返工计数 |
| 20 | 严重程度 | 严重/一般/轻微/建议 |
| 21 | 缺陷类型 | 类型分类 |
| 22 | 缺陷修复周期(天) | 修复时长 |
| 23 | 缺陷关闭周期(天) | 关闭时长 |

**Sheet2 - 任务项统计**：
- 用于统计任务项和子任务项数量

---

## 视图切换功能

报告支持两种视图：

### 图表视图
- 质量指标概览（5个卡片）
- 13个可视化图表
- 响应式网格布局

### 明细视图
- 筛选导航栏
- 数据表格（分页/排序）
- 详情弹窗

**切换方式**：页面右上角视图切换按钮

---

## 配色方案

**主色调**：淡紫色 #AA96DA

**配色应用**：
- 筛选框聚焦边框
- 重置按钮
- 缺陷编号
- 优先级-低
- 弹窗标题
- 明细标签

**状态配色**：
| 状态 | 颜色 |
|------|------|
| New | #F7DC6F（黄色） |
| Closed | #82E0AA（绿色） |
| Fixed | #76D7C4（青色） |
| Pending | #AA96DA（紫色） |
| ReOpen | #F0B27A（橙色） |

---

## 依赖库

```
pandas
pyecharts
numpy
openpyxl (Excel读取)
```

---

## 扩展指南

### 添加新图表

1. 在 `views/chart_views.py` 中创建新函数
2. 在主程序 `defect_quality_report.py` 中调用
3. 将返回的HTML添加到 `charts_html` 列表

### 修改配色

编辑 `config.py` 中的 `COLORS` 字典

### 调整明细表格列

编辑 `views/detail_view.py` 中的 `display_cols` 和 `detail_cols` 字典
