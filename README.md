# CD Booklet OCR

将扫描的CD说明书/小册子图片OCR识别并转换为Obsidian兼容的Markdown格式。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Obsidian](https://img.shields.io/badge/Obsidian-Compatible-purple.svg)

## 功能特性

- ✅ 按顺序读取图片（使用natsort自然排序）
- ✅ OCR识别文字和样式（基于Tesseract）
- ✅ **智能布局分析**：自动检测多页扫描、分栏布局
- ✅ **分栏内容分离**：多栏文字独立输出，不混杂
- ✅ **图文混合处理**：识别图片区域，仅提取文字
- ✅ 检测标题、加粗、斜体等格式
- ✅ 生成Obsidian优化的Markdown（支持Frontmatter、Callouts、嵌入图片）
- ✅ 支持PDF和图片混合输入（使用PyMuPDF4LLM）
- ✅ 可配置的检测阈值和输出格式

## 快速开始

### 安装依赖

#### 基础依赖
```bash
pip install -r requirements.txt
```

#### 可选PDF支持
```bash
pip install pymupdf4llm
```

注意：需要安装Tesseract OCR（Windows: `choco install tesseract`）

### 基本使用

#### 处理图片目录
```bash
python src/main.py ./my-booklet-scan
```

#### 指定输出目录
```bash
python src/main.py ./my-booklet-scan -o ./docs
```

#### 禁用frontmatter
```bash
python src/main.py ./scan --no-footmatter
```

### 支持的文件命名

推荐格式（自动排序）：
- `page_01.png, page_02.png, ..., page_10.png`
- `001.jpg, 002.jpg, ..., 050.jpg`
- `booklet_p1.jpg, booklet_p2.jpg, ..., booklet_p10.jpg`

使用`natsort`自然排序，正确处理`page_10.png`在`page_2.png`之后。

## 高级配置

### 编辑 `src/config.py`

#### 语言设置
```python
OCR_LANGUAGE = "ch"  # 'ch' = 中文, 'en' = 英文
```

#### 样式检测阈值
```python
MIN_HEADING_FONT_SIZE = 36  # 标题最小字体大小（像素）
BOLD_STROKE_RATIO = 0.15    # 加粗检测阈值
ITALIC_MIN_ANGLE = 10       # 斜体最小倾斜角（度）
```

根据扫描分辨率和正文字体大小调整：
- 如果正文被误标为标题，提高 `MIN_HEADING_FONT_SIZE`
- 如果标题被遗漏，降低该值

#### 输出格式
```python
OBSIDIAN_FRONTMATTER = True  # 包含YAML元数据
ENABLE_CALLOUTS = True       # 使用Obsidian callout格式
EMBED_SOURCE_IMAGES = True   # 嵌入源图片
```

## 布局分析

本项目支持智能布局分析，可以处理复杂的扫描文档：

### 多页检测
如果一张图片包含多个扫描页面（如双页扫描），系统会自动检测并分开处理每个页面。

### 分栏检测
对于分栏布局（如报纸、杂志），系统会：
1. 自动识别栏数和边界
2. 按栏分别处理文字
3. 输出时用 `---` 分隔不同栏的内容

### 图文分离
系统会检测图片区域并排除，仅提取文字内容。

### 调试工具
```bash
python debug_layout.py path/to/image.jpg
```
查看布局检测结果，便于调试和参数调整。

## 输出示例

### 生成的Markdown结构

```markdown
---
created: 2026-02-13T11:23:00Z
modified: 2026-02-13T11:23:00Z
id: booklet_a1b2c3d4
type: booklet
source: ./my-booklet-scan
tags:
  - ocr
  - booklet
  - cd-doc
---

# Album Title

**Source:** `./my-booklet-scan`
**Generated:** 2026-02-13 11:23:00
**Type:** booklet

---

## About This Album

This is the introduction text detected by OCR.

> Note: Multiple styles detected:
> **Bold text** and *italic text* mixed

## Track Listing

1. Track One Title
2. Track Two Title
3. Track Three Title

> [!info]- Page 1 #ocr #booklet
> ![[my-booklet-scan/page_01.png]]
```

## 样式检测能力

| 样式 | 检测方法 | 准确性 |
|------|---------|--------|
| **标题** (H1-H6) | 字体大小分析 | ⭐⭐⭐⭐ |
| **加粗** | 笔画宽度 + 像素密度 | ⭐⭐⭐ |
| **斜体** | 轮廓倾斜角分析 | ⭐⭐⭐ |
| **居中对齐** | 文本中心位置 | ⭐⭐⭐⭐⭐ |
| **列表** | 正则模式匹配 | ⭐⭐⭐⭐⭐ |

## Obsidian特性支持

### Tags
```yaml
tags:
  - ocr
  - booklet      # 文档类型
  - cd-doc       # 分类
  - music        # 附加标签
```

### Callouts
- `> [!info]` - 默认信息块
- `> [!note]` - 多标题页面
- `> [!tip]` - 列表为主页面
- `> [!error]` - 错误信息

### Frontmatter属性
- `created`, `modified`: 创建和修改时间
- `id`: 基于源路径的唯一标识
- `type`: 文档类型（可配置）
- `source`: 源路径
- `tags`: 自动添加的标签

## 文件结构

```
booklet-OCR/
├── src/
│   ├── main.py              # 主程序入口
│   ├── ocr_processor.py     # Tesseract OCR处理
│   ├── layout_analyzer.py   # 布局分析（多页/分栏检测）
│   ├── markdown_generator.py # Markdown生成器
│   ├── image_utils.py       # 图片加载和排序
│   └── config.py            # 配置参数
├── debug_layout.py          # 布局分析调试工具
├── output/                  # 默认输出目录
├── requirements.txt         # 基础依赖
└── README.md
```

## 故障排除

### Tesseract未找到
```bash
# Windows
# 设置config.py中的TESSERACT_PATH
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 或安装
choco install tesseract
```

### 样式检测不准确
```python
# 调整config.py中的阈值
MIN_HEADING_FONT_SIZE = 20  # 如果标题被遗漏
BOLD_STROKE_RATIO = 0.12    # 如果加粗未被检测
ITALIC_MIN_ANGLE = 8        # 如果斜体被误判
```

### OCR语言设置错误
```python
# config.py
OCR_LANGUAGE = "en"        # 英文文档
OCR_LANGUAGE = "ch"        # 中文文档
```

## 技术细节

### OCR引擎选择

| 引擎 | 用途 | 优势 |
|------|------|------|
| Tesseract | 图片扫描 | 广泛支持，配置灵活 |
| PyMuPDF4LLM | PDF文档 | 完美保留样式，速度快 |

### 样式检测算法

- **加粗检测**: 结合笔画宽度和像素密度，需要2/3方法确认
- **斜体检测**: 使用轮廓椭圆拟合角度，中位数过滤异常值
- **标题检测**: 基于字体大小自动分级（H1-H4）

### 排序策略
```python
from natsort import natsorted
images = natsorted(image_files)  # 自然排序
```

## 贡献

欢迎提交问题和Pull Request！

## 许可证

MIT License

---

**Made with ❤️ for Obsidian users**

