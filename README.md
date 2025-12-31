# Tufted-Blog-Template

这是一个基于 [Typst](https://typst.app/) 和 [Tufted](https://github.com/vsheg/tufted) 的静态网站构建模板，手把手教你搭建简洁、美观的个人博客、作品集和简历设计。

---

## ✨ 特点

- 🚀 使用 Typst 编写内容，语法简洁，编译极快
- 🎨 基于 Tufte CSS 设计，排版优雅，注重阅读体验
- 📦 内置构建脚本，上手简单，支持跨平台
- 📝 支持生成 HTML 网页和 PDF 文档，支持链接到 PDF 版本
- 🌐 内置 GitHub Pages 部署支持，一键发布网站

---

## 📦 依赖安装

### 1. 安装 Typst

- **Windows:** `winget install typst.typst`
- **macOS:** `brew install typst`
- **Linux:** `cargo install typst-cli`
- 或访问 [Typst 官网](https://typst.app/docs/installation/)。

### 2. 安装 uv (推荐)

uv 是一个极速的 Python 包管理工具，用于运行构建脚本。

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

_注：也可以使用标准 Python 环境运行 `build.py`，但需自行安装依赖。_

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Yousa-Mirage/Tufted-Blog-Template.git
cd Tufted-Blog-Template
```

### 2. 构建网站

```bash
uv run build.py build
```

此命令会将 `content/` 下的 `.typ` 文件编译为 HTML 和 PDF，并输出到 `_site/` 目录。

### 3. 本地预览

```bash
uv run build.py preview
```

或者使用 livereload 工具：

```bash
uvx livereload _site
```

访问 `http://localhost:8000` 查看效果。

---

## 🛠️ 常用命令

| 命令                      | 说明                          |
| :------------------------ | :---------------------------- |
| `uv run build.py build`   | 完整构建（HTML + PDF + 资源） |
| `uv run build.py html`    | 仅构建 HTML                   |
| `uv run build.py pdf`     | 仅构建 PDF                    |
| `uv run build.py clean`   | 清理 `_site` 目录             |
| `uv run build.py preview` | 启动本地预览服务器            |

---

## 📂 项目结构

```
Tufted-Blog-Template/
├── content/              # 网站内容源文件 (.typ)
│   ├── index.typ         # 首页
│   ├── Blog/             # 博客文章
│   └── About/            # 关于页面
├── assets/               # 静态资源 (CSS, JS, 字体)
├── _site/                # 构建输出目录 (自动生成)
├── build.py              # Python 构建脚本
├── config.typ            # 网站全局配置
└── Makefile              # Make 构建命令 (可选)
```

## 📝 编写指南

1.  **修改配置**：编辑 `config.typ` 设置网站标题、导航栏和语言。
2.  **添加文章**：在 `content/Blog/` 下创建新的 `.typ` 文件。
3.  **生成 PDF**：如果文件名包含 `PDF` (如 `CV-PDF.typ`)，构建脚本会自动将其编译为 PDF 文件。

---

## 📄 许可证

MIT License
