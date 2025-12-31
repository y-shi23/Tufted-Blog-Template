#!/usr/bin/env python3
"""
跨平台构建脚本 - 基于 Typst 和 Tufted
支持 Windows、macOS 和 Linux
"""

import http.server
import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from typing import List

# 配置
CONTENT_DIR = Path("content")
SITE_DIR = Path("_site")
ASSETS_DIR = Path("assets")
SITE_ASSETS_DIR = SITE_DIR / "assets"

# JavaScript 文件
JS_FILES = [
    "copy-code.js",
    "line-numbers.js",
    "format-headings.js",
    "favicon.ico",
]


def find_typ_files() -> List[Path]:
    """查找所有 .typ 文件，排除隐藏文件（目录名以 _ 开头）"""
    typ_files = []

    for typ_file in CONTENT_DIR.rglob("*.typ"):
        # 检查路径中是否有隐藏目录（以 _ 开头）
        if not any(part.startswith("_") for part in typ_file.parts):
            typ_files.append(typ_file)

    return typ_files


def find_pdf_typ_files(typ_files: List[Path]) -> List[Path]:
    """查找文件名包含 'PDF' 的 .typ 文件（不区分大小写）"""
    return [f for f in typ_files if "pdf" in f.name.lower()]


def compile_to_html(typ_file: Path, html_file: Path):
    """编译 .typ 文件为 HTML"""
    print(f"编译 HTML: {typ_file}")

    html_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "typst",
        "compile",
        "--root",
        ".",
        "--font-path",
        "assets",
        "--features",
        "html",
        "--format",
        "html",
        str(typ_file),
        str(html_file),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"错误：编译 {typ_file} 失败")
        print(result.stderr)
        sys.exit(1)

    # 注入 JavaScript 和 favicon
    inject_assets(html_file)


def compile_to_pdf(typ_file: Path, pdf_file: Path):
    """编译 .typ 文件为 PDF"""
    print(f"编译 PDF: {typ_file}")

    pdf_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["typst", "compile", "--root", ".", "--font-path", "assets", str(typ_file), str(pdf_file)]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"错误：编译 {typ_file} 失败")
        print(result.stderr)
        sys.exit(1)


def inject_assets(html_file: Path):
    """在 HTML 文件的 </head> 前注入 JavaScript 和 favicon"""
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 构建注入的内容
    inject_content = ""

    # 添加 favicon
    inject_content += '<link rel="icon" href="/assets/favicon.ico">'

    # 添加 JavaScript 文件
    for js_file in JS_FILES:
        if js_file.endswith(".js"):
            inject_content += f'<script src="/assets/{js_file}"></script>'

    # 在 </head> 前插入
    content = content.replace("</head>", inject_content + "</head>")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content)


def copy_assets():
    """复制 assets 目录到 _site"""
    print(f"复制 assets 到 {SITE_ASSETS_DIR}")

    if not ASSETS_DIR.exists():
        print(f"警告：{ASSETS_DIR} 目录不存在")
        return

    # 删除旧的 assets（如果存在）
    if SITE_ASSETS_DIR.exists():
        shutil.rmtree(SITE_ASSETS_DIR)

    # 复制整个 assets 目录
    shutil.copytree(ASSETS_DIR, SITE_ASSETS_DIR)


def clean():
    """清理生成的文件"""
    print(f"清理 {SITE_DIR}")

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)

    print("清理完成")


def build():
    """构建网站（HTML + PDF）"""
    print("开始构建网站...")

    # 1. 查找所有 .typ 文件
    typ_files = find_typ_files()
    print(f"找到 {len(typ_files)} 个 .typ 文件")

    # 2. 查找需要编译为 PDF 的文件
    pdf_typ_files = find_pdf_typ_files(typ_files)
    print(f"找到 {len(pdf_typ_files)} 个 PDF 文件")

    # 3. 编译所有 HTML 文件
    for typ_file in typ_files:
        # 计算目标 HTML 文件路径
        relative_path = typ_file.relative_to(CONTENT_DIR)
        html_file = SITE_DIR / relative_path.with_suffix(".html")
        compile_to_html(typ_file, html_file)

    # 4. 编译所有 PDF 文件
    for typ_file in pdf_typ_files:
        # 计算目标 PDF 文件路径
        relative_path = typ_file.relative_to(CONTENT_DIR)
        pdf_file = SITE_DIR / relative_path.with_suffix(".pdf")
        compile_to_pdf(typ_file, pdf_file)

    # 5. 复制 assets
    copy_assets()

    print(f"\n构建完成！输出目录: {SITE_DIR}")


def build_html():
    """仅构建网站 HTML（不编译 PDF）"""
    print("开始构建网站（仅 HTML）...")

    # 1. 查找所有 .typ 文件
    typ_files = find_typ_files()
    print(f"找到 {len(typ_files)} 个 .typ 文件")

    # 2. 编译所有 HTML 文件
    for typ_file in typ_files:
        # 计算目标 HTML 文件路径
        relative_path = typ_file.relative_to(CONTENT_DIR)
        html_file = SITE_DIR / relative_path.with_suffix(".html")
        compile_to_html(typ_file, html_file)

    # 3. 复制 assets
    copy_assets()

    print(f"\nHTML 构建完成！输出目录: {SITE_DIR}")


def build_pdf():
    """仅构建 PDF 文件"""
    print("开始构建 PDF 文件...")

    # 1. 查找所有 .typ 文件
    typ_files = find_typ_files()
    print(f"找到 {len(typ_files)} 个 .typ 文件")

    # 2. 查找需要编译为 PDF 的文件
    pdf_typ_files = find_pdf_typ_files(typ_files)
    print(f"找到 {len(pdf_typ_files)} 个 PDF 文件")

    if not pdf_typ_files:
        print("未找到 PDF 文件，跳过构建")
        return

    # 3. 编译所有 PDF 文件
    for typ_file in pdf_typ_files:
        # 计算目标 PDF 文件路径
        relative_path = typ_file.relative_to(CONTENT_DIR)
        pdf_file = SITE_DIR / relative_path.with_suffix(".pdf")
        compile_to_pdf(typ_file, pdf_file)

    print(f"\nPDF 构建完成！输出目录: {SITE_DIR}")


def preview(port: int = 8000, open_browser: bool = True):
    """启动本地预览服务器"""
    if not SITE_DIR.exists() or not (SITE_DIR / "index.html").exists():
        print(f"错误：未找到构建输出 {SITE_DIR}")
        print("请先运行: uv run build.py build")
        sys.exit(1)

    # 切换到 _site 目录
    os.chdir(SITE_DIR)

    print(f"启动预览服务器: http://localhost:{port}")
    print("按 Ctrl+C 停止服务器")

    # 在新线程中打开浏览器
    if open_browser:

        def open_browser_thread():
            import time

            time.sleep(1)  # 等待服务器启动
            webbrowser.open(f"http://localhost:{port}")

        threading.Thread(target=open_browser_thread, daemon=True).start()

    # 启动 HTTP 服务器
    try:
        server_address = ("", port)
        httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"错误：端口 {port} 已被占用")
            print("请尝试使用其他端口: uv run build.py preview --port 端口号")
            sys.exit(1)
        else:
            raise


def print_usage():
    """打印使用说明"""
    print("用法: uv run build.py <命令> [选项]")
    print()
    print("命令:")
    print("  build      构建网站（HTML + PDF）（默认）")
    print("  html       仅构建 HTML")
    print("  pdf        仅构建 PDF")
    print("  clean      清理生成的文件")
    print("  preview    启动预览服务器")
    print()
    print("选项:")
    print("  --port PORT  预览服务器端口（默认：8000）")
    print("  --no-browser  不自动打开浏览器")
    print()
    print("示例:")
    print("  uv run build.py build           # 构建网站")
    print("  uv run build.py html            # 仅构建 HTML")
    print("  uv run build.py preview         # 启动预览服务器")
    print("  uv run build.py preview --port 3000  # 使用端口 3000")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    # 解析选项
    port = 8000
    open_browser = True

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--port" and i + 1 < len(args):
            try:
                port = int(args[i + 1])
                i += 2
            except ValueError:
                print(f"错误：无效的端口号: {args[i + 1]}")
                sys.exit(1)
        elif arg == "--no-browser":
            open_browser = False
            i += 1
        else:
            print(f"错误：未知选项: {arg}")
            print_usage()
            sys.exit(1)

    # 执行命令
    if command == "build":
        build()
    elif command == "html":
        build_html()
    elif command == "pdf":
        build_pdf()
    elif command == "clean":
        clean()
    elif command == "preview":
        preview(port=port, open_browser=open_browser)
    else:
        print(f"错误：未知命令: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
