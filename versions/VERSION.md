# 缺陷质量分析报告生成器 - 版本记录

## v3.5.1 (2026-06-01)

**更新内容**：
- 待协调事项支持HTML文件引用
  - 当内容为HTML文件路径时，自动读取文件内容
  - 解决Excel单元格32767字符限制导致表格截断问题
  - 支持相对路径和绝对路径
- 面板图片功能
  - 每个面板支持多列图片路径（从第3列开始）
  - 图片以缩略图形式显示在面板内容最下方
  - 点击缩略图可放大查看
  - 支持png、jpg、jpeg、gif、webp、bmp格式
  - 图片转base64嵌入HTML，无需外部依赖
- 表格结构修复
  - 移除强制补齐表格单元格的逻辑
  - 保持原始HTML表格结构，不强制统一列数

**新增函数**：
- `views/home_view.py` `_render_image_thumbnail()` - 渲染图片缩略图

**更新文件**：
- `data_processor.py` - 读取多列图片路径
- `views/home_view.py` - HTML文件引用 + 图片缩略图功能 + 表格修复

**备份文件**：
- `versions/v3.5.1_modular_backup.zip`

---

## v3.5 (2026-05-31)

**更新内容**：
- 主视图测试进度概览新增明细统计数据
  - 配置开关 `SHOW_STATS_DATA`（config.py），默认开启
  - 展示四项数据：遗留缺陷、平均修复时间、基本流占比、返工次数
  - 一行四列布局，背景色 #f0f4f8，数值颜色 #1c91fd
  - 位于测试总进度/回归总进度下方、缺陷统计上方
  - 数据来源：从 DataFrame 实时计算
  - 无 .defect-summary 时自动放在内容区域顶部
- 明细视图缺陷详情弹窗样式统一
  - 替换 el-dialog 为自定义弹窗，与主视图缺陷预警弹窗样式一致
  - 统一展示字段（新增产品线、产品模块、返工次数等）
  - 状态标签和优先级标签样式保留并同步到主视图弹窗
- 主视图缺陷预警弹窗增强
  - 新增状态标签（彩色背景）和优先级标签（彩色文字）渲染
  - 弹窗毛玻璃背景色统一为 #1c91fd0d
- 图表视图按钮样式更新
  - active 状态：背景 #1c91fd40，白色边框，蓝色阴影
  - hover 状态：图标颜色 #1C91FD
- 图表切换表格修复
  - 使用 visibility 替代 display，保留容器尺寸
  - 切换回图表时延迟 resize 确保正确渲染
- 放大弹窗关闭按钮修复
  - 按钮样式与明细视图弹窗一致（蓝色圆形，hover 旋转变色）
  - 添加 z-index 和 pointer-events 确保可点击
  - 重构关闭逻辑，使用事件监听器替代内联 onclick
- 表格样式优化
  - 明细视图表格：表头整行蓝色 #1C91FD，文字白色加粗
  - 主视图测试进度表格：表头整行蓝色 #1C91FD，文字白色加粗
  - 表格内容左右留白16px，最后一行圆角处理
  - 缺陷编号列：表头白色，数据行蓝色 #1C91FD
- 明细视图缺陷行改为单击展示弹窗
- 缺陷预警列表滚动条：默认透明，hover 时显示灰色
- 所有弹窗滚动条颜色统一为灰色 #ccc
- UI自动化建设第一个卡片 SVG 颜色改为 #1c91fd，metric-value 颜色改为 #1c91fd
- 缺陷预警行去掉 margin-bottom
- 测试进度概览各区域间距统一调整为 10px
- .defect-list 列宽调整为 minmax(100px, 1fr)
- 本周新增缺陷总数数值和单位之间添加空格

**新增配置**：
- `config.py` `SHOW_STATS_DATA = True` - 明细数据开关
- `colors.py` `priority_detail['优先']` - 优先级颜色

**更新文件**：
- `config.py` - 新增 SHOW_STATS_DATA 配置
- `colors.py` - 新增"优先"优先级颜色
- `defect_quality_report.py` - 传递 df, total 到主页视图
- `views/home_view.py` - 明细统计、弹窗增强、表格样式调整
- `views/detail_view.py` - 弹窗重构、单击触发、表格样式、滚动条颜色
- `templates/html_template.py` - 图表按钮样式、切换修复、放大弹窗修复

**备份文件**：
- `versions/v3.5_modular_backup.zip`

---

## v3.4.5 (2026-05-31)

**更新内容**：
- 主视图缺陷预警卡片高度同步
  - JS动态设置缺陷预警卡片高度等于左侧测试进度概览卡片
  - CSS改为 `align-items: flex-start`，去除强制等高
  - `.warning-list` 添加 `min-height: 0` 确保flex收缩正确
  - 超出高度显示滚动条

**更新文件**：
- `views/home_view.py` - CSS + JS高度同步逻辑

**备份文件**：
- `versions/v3.4.5_modular_backup.zip`

---

## v3.4.4 (2026-05-31)

**更新内容**：
- 颜色配置独立与优化
  - 新建 `colors.py` 模块，颜色配置独立管理
  - 简化 `config.py`，从 colors 导入 COLORS
  - 颜色按功能分类：theme、text、background、border、progress、status、metric_cards 等
- 视图颜色配置化
  - `chart_views.py`：图表颜色、标题颜色、文字颜色替换为 COLORS 引用
  - `detail_view.py`：状态标签、优先级、弹窗颜色替换为 COLORS 引用
  - `home_view.py`：进度条、状态颜色替换为 COLORS 引用
- 质量指标卡片配色
  - 新增 `metric_cards` 配置，5个卡片渐变背景独立配置
  - 数值颜色 `#103979`
- 视图按钮优化
  - 去除"图表""明细"文字，只保留图标
  - 所有按钮统一为正圆形（padding 相等）
- 标题颜色修改
  - `.metrics-title` 颜色改为 `#103979`
- 修复周期分布图表修复
  - 修复 numpy.int64 序列化问题（数据显示为 null）
  - 优化分组逻辑：按 0.5 天分段（0-0.5天、0.5-1天...）
  - 图表颜色改为 `#7BC0F7`

**新增文件**：
- `colors.py` - 颜色配置模块

**更新文件**：
- `config.py` - 简化，导入 COLORS
- `views/chart_views.py` - 颜色配置化 + 修复周期图表修复
- `views/detail_view.py` - 颜色配置化
- `views/home_view.py` - 颜色配置化
- `templates/html_template.py` - 视图按钮优化 + 标题颜色

**备份文件**：
- `versions/v3.4.4_modular_backup.zip`

---

## v3.4.3 (2026-05-31)

**更新内容**：
- 双平台推送支持
  - 新增 GitLab（极狐）远程仓库配置
  - `auto_push.py` 支持选择推送平台：GitHub / GitLab / 双平台
  - SSH 密钥配置指南
- 报告保存优化
  - 历史版本归档：`history_reports/` 目录（带日期文件名）
  - Pages 版本：固定名称 `PSOT_Weekly_Report.html`（便于访问）
  - 保存时自动创建 `history_reports/` 目录
- CI/CD 配置更新
  - GitHub Actions：只部署固定名称文件
  - GitLab CI：只部署固定名称文件

**更新文件**：
- `auto_push.py` - 双平台推送脚本
- `templates/html_template.py` - 报告保存逻辑优化
- `.gitlab-ci.yml` - GitLab CI 配置
- `.github/workflows/deploy.yml` - GitHub Actions 配置

**备份文件**：
- `versions/v3.4.3_modular_backup.zip`

---

## v3.4.2 (2026-05-31)

**更新内容**：
- 截图功能实现
  - 右上角刷新按钮改为截图按钮（相机图标）
  - 点击截取当前页面完整内容（包含标题、视图切换按钮、两侧留白）
  - 使用 dom-to-image-more 库替代 html2canvas，完美保留 CSS 渐变背景
  - 截图成功弹窗：预览图片 + 保存按钮 + 复制到剪贴板按钮
  - 保存功能：调用 File System Access API，用户可选择保存位置
  - 复制到剪贴板：使用 Clipboard API，支持图片直接粘贴
  - 加载遮罩：截图过程中显示加载动画
- 按钮样式优化
  - CSS类名：`.icon-refresh` → `.icon-screenshot`（相机图标）
  - CSS类名：`.view-btn.refresh-btn` → `.view-btn.screenshot-btn`
  - JS函数：`refreshData()` → `screenshotReport()`
  - 保存按钮图标改为保存样式

**更新文件**：
- `templates/html_template.py` - 截图功能完整实现

**备份文件**：
- `versions/v3.4.2_modular_backup.zip`

---

## v3.4.1 (2026-05-31)

**更新内容**：
- 明细视图样式优化
  - 颜色主题从 `#AA96DA` 调整为 `#1C91FD`
  - 筛选器按钮、统计文字、表格首列、弹窗样式统一蓝色主题
- 主视图缺陷预警弹窗样式优化
  - 与明细视图弹窗样式一致：毛玻璃背景、弹性动画、圆角卡片
  - 关闭按钮 hover 旋转效果、内容行 hover 右滑动效
  - 字段标签蓝色加粗、滚动条样式优化
- 主视图样式作用域隔离
  - `.metric-card` 样式添加 `.three-col` 前缀，避免影响图表视图
- 修复筛选数据错误
  - 行数据添加筛选所需字段（发现阶段、缺陷类型），确保筛选器正常工作

**更新文件**：
- `views/detail_view.py` - 颜色主题调整
- `views/home_view.py` - 弹窗样式优化 + 样式作用域隔离

**备份文件**：
- `versions/v3.4.1_modular_backup.zip`

---

## v3.4 (2026-05-30)

**更新内容**：
- 下周测试计划章节：特殊渲染
  - 每行作为一个计划项，支持富文本格式
  - SVG同心圆图标（蓝色外圈 + 白色中圈）
  - 计划项样式：浅蓝背景(#f0f7ff) + 蓝色边框(#dbeafe) + 圆角卡片
  - 文本样式：font-size 13px, line-height 1.7, 垂直居中
- PSOT-UI自动化建设样式调整
  - 指标卡片 min-height 从 180px 调整为 160px

**更新文件**：
- `views/home_view.py` - 新增下周测试计划渲染函数和CSS样式

**备份文件**：
- `versions/v3.4_modular_backup.zip`

---

## v3.3 (2026-05-30)

**更新内容**：
- 缺陷预警功能实现
  - 三类预警数据：超期数据、返工数据、超期返工数据
  - 超期数据：状态=New + 登记时间超过阈值天数
  - 返工数据：状态=ReOpen + 返工次数>=阈值
  - 超期返工数据：返工数据 + 有修复时间 + 修复时间超过阈值
  - 优先展示：超期返工 > 超期 > 返工
  - 展示格式：缺陷编号 + 处理人 + 缺陷摘要（省略号截断）
  - 右侧浅红色标签显示：超期x天|返工x次 / 超期x天 / 返工x次
  - 点击行弹出详情弹窗，展示该缺陷全部字段
  - 最大高度同步左侧测试进度概览卡片，超出显示滚动条
- 新增配置项
  - `OVERDUE_DAYS = 3`：超期天数阈值
  - `REWORK_THRESHOLD = 3`：返工次数阈值

**更新文件**：
- `config.py` - 新增预警阈值配置
- `data_processor.py` - 新增load_warning_data()函数
- `defect_quality_report.py` - 调用预警数据函数
- `views/home_view.py` - 缺陷预警卡片重构（列表+标签+弹窗+滚动）

---

## v3.2 (2026-05-30)

**更新内容**：
- 主页视图重构优化
  - 本周测试概况章节：两列卡片布局（测试进度概览 + 缺陷预警）
  - 测试进度概览卡片：动态提取[xxx]转换为标签样式，提取进度和缺陷统计
  - 进度卡片：测试总进度、回归总进度两列展示，进度颜色规则：<30%红色，>=30%蓝色
  - 缺陷状态展示：彩色圆点 + 状态标签 + 数值
  - 缺陷预警卡片：标题右侧添加圆形数量标签（背景色#ffdcdb9c，红色文字）
- 测试进度和缺陷统计章节：表格 + 条形图双卡片布局
  - 表格：Sheet2数据展示，表头蓝色(#1c91fd)，居中对齐
  - 任务项名称列：居中显示，最大宽度300px，超出显示tooltip（浅蓝背景白色文字）
  - 进度列：圆形进度条，进度颜色规则同上
  - 条形图卡片：各任务项进度对比，进度100%时自动切换为回归进度对比
  - 条形图进度条：胶囊形状(border-radius: 14px)，颜色动态变化

**更新文件**：
- `views/home_view.py` - 主页视图模块重构
- `data_processor.py` - 新增load_sheet2_data()函数

**备份文件**：
- `versions/v3.2_modular_backup.zip`

---

## v3.1 (2026-05-29)

**更新内容**：
- GitHub Actions自动部署配置
  - 新增 `.github/workflows/deploy.yml` 工作流文件
  - push触发自动运行Python脚本生成HTML
  - 自动部署到GitHub Pages
  - 支持手动触发（workflow_dispatch）
- 输出文件名动态生成
  - 格式：`PSOT_Weekly_Report_开始日期-结束日期.html`
  - 示例：`PSOT_Weekly_Report_2026.05.18-2026.05.22.html`
  - 根据SUBTITLE日期范围自动生成
- 项目配置优化
  - 新增 `requirements.txt` 依赖清单
  - 新增 `.gitignore` 排除临时文件
  - 新增本地脚本 `auto_push.py`（一键生成+推送，不提交到仓库）
- 仓库设置为私有，Pages保持公开访问

**新增文件**：
- `.github/workflows/deploy.yml` - GitHub Actions工作流
- `requirements.txt` - Python依赖清单
- `.gitignore` - Git排除配置
- `auto_push.py` - 本地自动推送脚本

**更新文件**：
- `config.py` - 添加动态文件名生成函数

**备份文件**：
- `versions/v3.1_modular_backup.zip`

---

## v2.5 (2026-05-29)

**更新内容**：
- 弥散柔焦背景效果：以主色#1677ff为基调，多层径向渐变营造朦胧梦幻质感
- 视图切换按钮重构：
  - 扁平化SVG图标（主页/图表/明细/刷新）
  - 浅蓝色半透明背景 rgba(145, 202, 255, 0.5)
  - 白色文字，激活状态白色边框
  - 新增刷新按钮（功能待实现）
- 质量指标概览卡片：
  - 原鲜艳颜色基础上降低透明度至0.7
  - 保持渐变效果，与背景和谐融合
- 标题样式：黑色文字(#2c3e50)，去除阴影
- 背景渐变：从深蓝到浅蓝的自然过渡

**备份文件**：
- `versions/v2.5_modular_backup.zip`

---

## v2.4.2 (2026-05-29)

**更新内容**：
- UI风格重构，参考设计图优化
- 顶部导航栏：蓝色背景(#1677ff)，高度260px，底部圆弧形(border-radius: 0 0 50% 50%)
- 导航栏布局：标题居中，视图切换按钮右侧定位
- 内容容器与导航栏交叠效果：margin: -150px向上移动，卡片覆盖导航栏弧形部分
- 卡片样式优化：圆角16px，阴影增强
- 视图按钮样式：半透明白色背景，激活状态蓝色文字
- 背景色改为浅灰色(#f5f7fa)

**备份文件**：
- `versions/v2.4.2_modular_backup.zip`

---

## v2.4.1 (2026-05-28)

**更新内容**：
- 新增主页视图（🏠按钮），默认显示主页视图
- 主页视图保留"质量指标概览"（5个指标卡片，淡蓝渐变背景）
- 公共面板卡片：从sheet3读取数据，每行一个卡片
- 公共面板功能：蓝色标题栏（#5FB0FF渐变）+ 白色内容区域 + 点击折叠
- 公共面板内容：按换行分行展示，支持富文本样式（加粗、颜色）
- 视图切换优化：切换到图表视图自动resize ECharts图表
- 新增文件：
  - `views/home_view.py` - 主页视图模块
- 更新文件：
  - `config.py` - 添加 PANEL_SHEET_INDEX、PANEL_HEADER_COLOR 配置
  - `data_processor.py` - 添加 load_panels_data() 函数读取sheet3富文本
  - `templates/html_template.py` - 添加主页视图容器和视图切换逻辑
  - `defect_quality_report.py` - 集成主页视图生成

---

## v2.4 (2026-05-24)

**更新内容**：
- 图表右上角新增切换表格和放大按钮
- 切换按钮：点击切换图表/表格视图，表格表头根据图表类型动态生成
- 放大按钮：点击弹出模态框放大展示图表，毛玻璃背景效果
- 表格容器固定高度，超出显示滚动条
- 按钮样式：清新扁平设计，渐变背景，悬停上浮效果
- 放大图表尺寸：1000x650px

**备份文件**：
- `versions/v2.4_modular_backup.zip` - 模块化文件打包备份

---

## v2.3.2 (2026-05-24)

**更新内容**：
- 缺陷类型分布图例位置调整为底部（pos_top="bottom"），7个图例完全可见
- 缺陷优先级分布（纵向柱状图）图例向上移动（margin-top: -20px）

**备份文件**：
- `versions/v2.3.2_modular_backup.zip` - 模块化文件打包备份

---

## v2.1 (2026-05-23)

**更新内容**：
- 缺陷趋势分析图表：新增面积折线图（新增缺陷、遗留缺陷、关闭缺陷）
- 面积填充透明度0.3，曲线平滑样式

---

## v2.5 (2026-05-24)

**更新内容**：
- 明细视图引入 Vue3 + Element Plus 组件
- Element Select 下拉选择组件（状态、处理人员、优先级、发现阶段、缺陷类型、日期类型）
- 日期筛选组合设计：下拉框选择日期类型（登记时间/修复时间/关闭时间）+ 一个日期范围选择器
- Element DatePicker 日期范围选择器，切换日期类型自动更新默认范围
- Element Button 重置按钮、Element Dialog 弹窗
- 明细列表调整：去除发现阶段和缺陷类型列展示（详情弹窗保留）
- 查询栏新增发现阶段、缺陷类型筛选字段
- 样式隔离：所有 CSS 通过 `#detailVueApp` 选择器前缀，不影响图表视图
- Vue 应用挂载到独立容器 `#detailVueApp`，与页面其他部分隔离
- 弹窗效果：毛玻璃背景（backdrop-filter）、弹性弹出动画、关闭按钮旋转动效

---

## v2.4 (2026-05-24)

**更新内容**：
- 明细视图筛选栏新增登记日期范围查询
- 日期选择器：起始日期和结束日期，默认填充数据范围
- 日期筛选逻辑：与状态、处理人员、优先级筛选联动
- 重置按钮：恢复日期范围至默认值
- 新增 `.filter-date` 和 `.filter-separator` CSS样式

---

## v2.3.1 (2026-05-24)

**更新内容**：
- 明细视图引入 Vue3 + Element Plus 组件
- Element Select 下拉选择组件（状态、处理人员、优先级、发现阶段、缺陷类型、日期类型）
- 日期筛选组合设计：下拉框选择日期类型（登记时间/修复时间/关闭时间）+ 一个日期范围选择器
- 查询栏优化：折叠/展开功能，默认收起，字体字号13px，标签颜色#555
- 明细列表调整：去除发现阶段和缺陷类型列展示（详情弹窗保留），列宽优化
- 弹窗效果：毛玻璃背景、弹性弹出动画、关闭按钮旋转动效

**备份文件**：
- `versions/v2.3.1_modular_backup.zip` - 模块化文件打包备份（18KB）

---

## v2.3 (2026-05-23)

**更新内容**：
- 代码模块化重构，提升可维护性
- 文件结构拆分：
  - `config.py` - 配置常量模块（颜色、路径、标题等）
  - `data_processor.py` - 数据处理模块（加载、预处理）
  - `views/chart_views.py` - 图表视图模块（5个图表生成函数）
  - `views/detail_view.py` - 明细视图模块（筛选、表格、弹窗）
  - `templates/html_template.py` - HTML模板模块（页面组装）
  - `defect_quality_report.py` - 主入口（约210行，原1865行）
- 修复关联任务项统计图表数据显示异常

**备份文件**：
- `versions/v2.3_modular_backup.zip` - 模块化文件打包备份（16KB）

---

## v2.2.1 (2026-05-23)

**更新内容**：
- 新增明细视图：页面右上角视图切换按钮（图表视图/明细视图）
- 明细视图功能：
  - 筛选导航栏：状态、处理人员、优先级下拉筛选 + 重置按钮
  - 优先级枚举值：低、中、高、优先（从低到高）
  - 列表按登记时间倒序排列
  - 缺陷编号列宽增加，缺陷摘要超长截断+悬停展开
  - 双击行弹出详情弹窗（17个字段完整展示）
- 弹窗样式：
  - 毛玻璃背景效果（backdrop-filter: blur）
  - 弹性弹出动画（cubic-bezier曲线）
  - 关闭按钮悬停旋转90°
  - 明细项悬停右滑动效
- 整体淡紫色调 #AA96DA 统一配色

---

## v2.2 (2026-05-23)

**更新内容**：
- 处理人员缺陷统计图表优化：
  - 折线图节点上方显示平均修复时长数值
  - 数值字体颜色：#F5C4D0
  - 数值字体大小：12px，加粗
  - 数值距离节点8px
  - 折线图层叠顺序提升（z=10），确保在柱状图上方
- Tooltip格式化：平均修复时长保留两位小数显示
- 修复formatter：数据格式为[名称, 值]时使用p.value[1]获取值
- 代码清理：
  - 删除未使用函数 `create_bar_chart`（约155行）
  - 统一数据预处理：`缺陷修复周期(天)` 处理从3处重复合并为1处
  - 文件从1429行减少到1273行

---

## v2.0 (2026-05-23)

**重大更新 - ECharts迁移**：
- 完全迁移从Plotly到ECharts (pyecharts)
- Hover tooltip支持圆角(8px)、阴影、padding效果
- 文件大小从56MB压缩至112KB（减少99.8%）
- 所有12个图表使用ECharts渲染
- 移除饼图悬停放大JavaScript（ECharts原生支持）
- 保留原有配色方案和布局设计

**代码清理**：
- 移除未使用参数：`legend_y`, `x_label`, `y_label`
- 移除未使用变量：`total_count`, `totals`, `status_counts`
- 移除未使用CSS样式：`.icon-check`
- 移除重复代码：`df['发现阶段'].str.strip()` 重复执行
- 修复折线图label formatter：lambda → JsCode
- 移动 `import re` 到文件顶部

**图表类型对应**：
- 饼图/环形图: Pie (radius参数)
- 柱状图: Bar (支持横向/纵向)
- 直方图: Bar (手动分箱)
- 面积折线图: Line (areaStyle_opts)
- 复合图表: Bar.overlap(Line) + extend_axis

---

## v1.9 (2026-05-22)

**更新内容**：
- 尝试添加hover tooltip样式（圆角、阴影、padding），但Plotly不支持
- 添加hoverlabel基础配置（bgcolor、bordercolor、font）
- 添加饼图悬停放大动画（scale 1.05）
- 此版本为Plotly最终版本，后续将迁移至ECharts

---

## v1.8 (2026-05-22)

**更新内容**：
- 标题更新为"POST-产品标准化运营工具-质量周报"
- 质量指标概览优化：
  - 任务数 → 任务项（从sheet2获取，4个）
  - 子任务项数量从sheet2合计行获取（57个）
  - 关闭率 → 遗留缺陷（非Closed状态数量）
  - 主数值添加单位"个"
- HTML文件优化：从56M压缩至4.8M
  - 第一个图表内嵌Plotly库
  - 其他图表共享使用，避免重复嵌入

---

## v1.7 (2026-05-21)

**更新内容**：
- 新增缺陷趋势分析图表（面积折线图，宽卡片布局）
  - X轴：日期（MM-DD格式，从副标题时间范围提取）
  - Y轴：缺陷数量
  - 图例：新增缺陷、遗留缺陷、关闭缺陷
  - 曲线样式+标记点+半透明面积填充
- 质量指标概览调整：
  - 未关闭缺陷数 → 平均修复时长（保留两位小数）
  - 副标题显示最大/最小修复时长（换行）
  - 关闭率副标题改为遗留缺陷数（非Closed状态）
- 处理人员缺陷统计优化：
  - 平均修复时长折线改为曲线样式
  - 配色调整为淡紫丁香色（#C9B1FF）
- 缺陷趋势分析配色：清新柔和风格
  - 新增缺陷：#A0E7E5（薄荷蓝）
  - 遗留缺陷：#FFD69B（暖黄色）
  - 关闭缺陷：#F5C4D0（淡粉色）
- 新增时钟图标CSS样式
- 修复遗留缺陷统计逻辑（New+ReOpen+Pending+Fixed）

---

## v1.6.4 (2026-05-21)

**更新内容**：
- 处理人员缺陷统计新增平均修复时长维度（折线图+次轴）
- 处理人员缺陷统计改为堆叠柱状图，按缺陷状态细分
- 新增柔和清新配色方案`status_soft`，减少红绿黄蓝重复配色
- 修复循环变量覆盖全局变量导致的"共1条缺陷数据"错误
- 柱顶显示每人缺陷总数标注

---

## v1.6.3 (2026-05-21)

**更新内容**：
- 处理人员缺陷统计卡片宽度延伸至两列（card-wide样式）
- 添加`.card-wide` CSS样式类
- 优化卡片布局，自动响应式排列

---

## v1.6.2 (2026-05-21)

**更新内容**：
- 调整图表展示顺序，质量指标概览置顶
- 质量指标概览改为5个卡片平铺形式（替代表格）
- 新增指标：任务数、未关闭缺陷数、基本流占比、返工率
- 添加子任务项统计支持
- 添加CSS图标装饰（任务、Bug、检查、图表、刷新图标）
- 优化卡片布局，质量概览使用full-width布局

**图表顺序**：
1. 质量指标概览 (5卡片平铺)
2. 处理人员缺陷统计 (柱状图)
3. 缺陷状态分布 (饼图)
4. 关联任务项统计 (横向柱状图)
5. 缺陷修复周期分布 (直方图)
6. 缺陷返工情况 (饼图)
7. 缺陷发现阶段分布 (横向柱状图)
8. 缺陷类型分布 (环形图)
9. 缺陷引入原因分析 (横向柱状图)
10. 缺陷优先级分布 (柱状图)
11. 缺陷严重程度分布 (横向柱状图)
12. 缺陷引入阶段分布 (横向柱状图)

---

## v1.5.2 (2026-05-21)

**更新内容**：
- 优化所有图表的图例位置，支持自定义 `legend_y` 参数
- 添加发现阶段预定义颜色配置，支持预留图例（4.2-回归测试【备选流】）
- 修复发现阶段数据前导空格问题
- 图例位置配置：
  - 图表1 缺陷状态分布: y=-0.2
  - 图表2 缺陷优先级分布: y=-0.2
  - 图表3 缺陷严重程度分布: y=-0.2
  - 图表4 处理人员缺陷统计: y=-0.45
  - 图表5 关联任务项统计: y=-0.3
  - 图表6 缺陷类型分布: y=-0.5
  - 图表7 缺陷发现阶段分布: y=-0.45
  - 图表8 缺陷引入阶段分布: y=-0.2
  - 图表11 缺陷返工情况: y=-0.3

---

## v1.5.1 (2026-05-21)

**更新内容**：
- 调整饼图布局：增加高度(350px)、底部边距(80px)、图例上移至边距内
- 添加柱状图底部图例功能，新增 `show_legend` 和 `order` 参数
- 优化优先级和严重程度图表，添加底部平铺图例
- 统一清新配色风格：
  - 优先级：#E57373(红)、#FFB74D(橙)、#64B5F6(蓝)、#81C784(绿)
  - 严重程度：与优先级配色一致
- Material Design 400系列色调，柔和清新

---

## v1.4 (2026-05-21)

**更新内容**：
- 修复第一个图表（缺陷状态分布）渲染空白问题
- 恢复使用内嵌Plotly方案（与v1.0一致），移除 `include_plotlyjs=False`
- 移除head中的CDN引用，每个图表内嵌完整Plotly代码

**验证结果**：
- 文件大小：56 MB（内嵌Plotly） ✓
- 卡片数量：12 ✓
- 缺陷状态数据：Closed、New、ReOpen、Pending、Fixed ✓
- 饼图类型数量：15 ✓
- HTML结构完整 ✓

---

## v1.3 (2026-05-21)

**更新内容**：
- 修复缺陷状态分布图表空白问题
- 将Plotly CDN脚本移回head中，确保加载顺序正确
- 补充 Pending、Fixed 状态的颜色定义
- 添加 `include_plotlyjs=False` 参数避免重复加载
- 状态配色完整支持：New、Closed、ReOpen、Pending、Fixed

**验证结果**：
- Plotly CDN位置：head中 ✓
- 图表div数量：12 ✓
- 渲染调用：12 ✓
- 状态数据完整 ✓

---

## v1.2 (2026-05-21)

**更新内容**：
- 补充 Pending、Fixed 状态的颜色定义

---

## v1.1 (2026-05-21)

**更新内容**：
- 隐藏图表工具栏 (`displayModeBar: False`)
- 添加空数据异常处理，显示"暂无数据"提示
- 修复柱状图/饼图/直方图的空数据处理逻辑
- 移除无用的工具栏CSS样式

---

## v1.0 (2026-05-21)

**特性**：
- 卡片平铺布局，自动响应式网格
- 清新渐变背景配色 (#667eea → #764ba2)
- 白色圆角卡片，悬停上浮动画
- 12个可视化图表：饼图、柱状图、直方图、指标表格
- Plotly交互式图表，支持hover动效
- 移动端自适应单列布局

**图表内容**：
1. 质量指标概览 (表格)
2. 处理人员缺陷统计 (柱状图)
3. 缺陷状态分布 (饼图)
4. 关联任务项统计 (横向柱状图)
5. 缺陷修复周期分布 (直方图)
6. 缺陷返工情况 (饼图)
7. 缺陷发现阶段分布 (横向柱状图)
8. 缺陷类型分布 (环形图)
9. 缺陷引入原因分析 (横向柱状图)
10. 缺陷优先级分布 (柱状图)
11. 缺陷严重程度分布 (横向柱状图)
12. 缺陷引入阶段分布 (横向柱状图)

**配置项**：
- INPUT_FILE: 数据源文件
- OUTPUT_FILE: 输出HTML文件
- TITLE: 报告标题
- SUBTITLE: 报告副标题/时间范围
- COLORS: 配色方案字典

**依赖**：
- pandas
- pyecharts
- numpy
- openpyxl (Excel读取)

---

## 版本文件

| 版本 | 文件 | 说明 |
|------|------|------|
| v1.0 | versions/defect_quality_report_v1.0.py | 初始版本 |
| v1.1 | versions/defect_quality_report_v1.1.py | 隐藏工具栏+异常处理 |
| v1.2 | versions/defect_quality_report_v1.2.py | 补充状态颜色 |
| v1.3 | versions/defect_quality_report_v1.3.py | 修复CDN加载顺序 |
| v1.4 | versions/defect_quality_report_v1.4.py | 恢复内嵌Plotly |
| v1.5.2 | versions/defect_quality_report_v1.5.2.py | 图例位置优化+预定义发现阶段配色 |
| v1.6.1 | versions/defect_quality_report_v1.6.1.py | 图表顺序调整 |
| v1.6.2 | versions/defect_quality_report_v1.6.2.py | 质量指标卡片化+5卡片平铺 |
| v1.6.3 | versions/defect_quality_report_v1.6.3.py | 处理人员缺陷统计宽卡片布局 |
| v1.6.4 | versions/defect_quality_report_v1.6.4.py | 复合图表+平均修复时长+清新配色 |
| v1.7 | versions/defect_quality_report_v1.7.py | 缺陷趋势分析+质量指标优化 |
| v1.8 | versions/defect_quality_report_v1.8.py | 任务项优化+HTML压缩 |
| v1.9 | versions/defect_quality_report_v1.9.py | Plotly最终版本（hoverlabel配置+饼图动画） |
| v2.0 | versions/defect_quality_report_v2.0.py | ECharts迁移+代码清理 |
| v2.1 | versions/defect_quality_report_v2.1.py | 缺陷趋势分析面积折线图 |
| v2.2 | versions/defect_quality_report_v2.2.py | 折线图数值显示+tooltip优化+z层级 |
| v2.2.1 | versions/defect_quality_report_v2.2.1.py | 明细视图+筛选导航+弹窗详情+淡紫色调 |
| v2.3 | versions/defect_quality_report_v2.3.py | 模块化重构+关联任务项修复 |
| v2.4.1 | versions/v2.4.1_modular_backup.zip | 主页视图+公共面板卡片+富文本支持 |
| v3.4.1 | versions/v3.4.1_modular_backup.zip | 明细视图样式优化 + 筛选修复 |
| v3.4.2 | versions/v3.4.2_modular_backup.zip | 截图功能实现 + dom-to-image-more库 |
| v3.4.3 | versions/v3.4.3_modular_backup.zip | 双平台推送 + 历史版本归档 + 固定Pages文件名 |
| v3.4.4 | versions/v3.4.4_modular_backup.zip | 颜色配置独立 + 视图按钮优化 + 修复周期图表修复 |
| v3.4.5 | versions/v3.4.5_modular_backup.zip | 缺陷预警卡片高度同步修复 |