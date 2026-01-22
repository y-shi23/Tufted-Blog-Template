# /// script
# requires-python = ">=3.6"
# dependencies = ["markdown", "python-frontmatter", "jinja2", "tomli"]
# ///

"""
Tufted Blog Template 构建脚本

这是一个跨平台的构建脚本，用于将 Markdown (.md) 文件编译为 HTML，
并复制静态资源到输出目录。

支持增量编译：只重新编译修改后的文件，加快构建速度。

用法:
    uv run build.py build       # 完整构建 (HTML + 资源)
    uv run build.py assets      # 仅复制静态资源
    uv run build.py clean       # 清理生成的文件
    uv run build.py preview     # 启动本地预览服务器（默认端口 8000）
    uv run build.py preview -p 3000  # 使用自定义端口
    uv run build.py --help      # 显示帮助信息

增量编译选项:
    --force, -f                 # 强制完整重建，忽略增量检查

预览服务器选项:
    --port, -p PORT             # 指定服务器端口号（默认: 8000）
"""

import argparse
import os
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path
from typing import List, Dict, Any

import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader

# ============================================================================
# 配置
# ============================================================================

CONTENT_DIR = Path("content")  # 源文件目录
SITE_DIR = Path("_site")  # 输出目录
ASSETS_DIR = Path("assets")  # 静态资源目录
TEMPLATE_DIR = Path("templates") # 模板目录
CONFIG_FILE = Path("config.toml")  # 全局配置文件

# ============================================================================
# 辅助函数
# ============================================================================

def load_config() -> Dict[str, Any]:
    """加载 config.toml 配置"""
    if not CONFIG_FILE.exists():
        print(f"❌ 配置文件 {CONFIG_FILE} 不存在")
        sys.exit(1)
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)

def get_file_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except (OSError, FileNotFoundError):
        return 0.0

def needs_rebuild(source: Path, target: Path, extra_deps: List[Path] = None) -> bool:
    if not target.exists():
        return True
    
    target_mtime = get_file_mtime(target)
    if get_file_mtime(source) > target_mtime:
        return True
        
    if extra_deps:
        for dep in extra_deps:
            if dep.exists() and get_file_mtime(dep) > target_mtime:
                return True
    return False

# ============================================================================
# 构建命令
# ============================================================================

def build_html(force: bool = False):
    """编译 Markdown 文件为 HTML"""
    print("正在构建 HTML 文件...")
    
    config = load_config()
    
    # 初始化 Jinja2 环境
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("base.html")
    
    # 查找依赖 (config.toml 和 base.html)
    deps = [CONFIG_FILE, TEMPLATE_DIR / "base.html"]
    
    md_files = list(CONTENT_DIR.rglob("*.md"))
    if not md_files:
        print("⚠️ 未找到任何 Markdown 文件。")
        return True

    success_count = 0
    skip_count = 0
    fail_count = 0

    for md_file in md_files:
        # 跳过以 _ 开头的目录或文件
        relative_path = md_file.relative_to(CONTENT_DIR)
        if any(part.startswith("_") for part in relative_path.parts):
            continue
            
        html_output = SITE_DIR / relative_path.with_suffix(".html")
        
        if not force and not needs_rebuild(md_file, html_output, deps):
            skip_count += 1
            continue
            
        try:
            # 读取 Frontmatter 和 内容
            post = frontmatter.load(md_file)
            content_md = post.content
            metadata = post.metadata
            
            # 使用 Python-Markdown 转换
            # 启用常见扩展
            html_content = markdown.markdown(
                content_md,
                extensions=[
                    'extra',       # 表格, 脚注等
                    'codehilite',  # 代码高亮
                    'toc',         # 目录
                    'sane_lists'   # 更好的列表处理
                ]
            )
            
            # 渲染模板
            # 页面标题优先使用 metadata 中的 title，否则使用文件名
            page_title = metadata.get('title', md_file.stem)
            
            final_html = template.render(
                config=config,
                content=html_content,
                metadata=metadata,
                page_title=page_title
            )
            
            # 写入文件
            html_output.parent.mkdir(parents=True, exist_ok=True)
            html_output.write_text(final_html, encoding='utf-8')
            success_count += 1
            
        except Exception as e:
            print(f"❌ {md_file} 编译失败: {e}")
            fail_count += 1

    print(f"✅ HTML 构建完成。编译: {success_count}, 跳过: {skip_count}, 失败: {fail_count}")
    return fail_count == 0

def copy_assets() -> bool:
    """复制静态资源"""
    results = []
    
    # 1. 复制全局 assets
    if ASSETS_DIR.exists():
        target_dir = SITE_DIR / "assets"
        try:
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(ASSETS_DIR, target_dir)
            results.append(True)
        except Exception as e:
            print(f"❌ 复制全局静态资源失败: {e}")
            results.append(False)
            
    # 2. 复制 content 中的非 md 文件
    if CONTENT_DIR.exists():
        try:
            for item in CONTENT_DIR.rglob("*"):
                if item.is_dir() or item.suffix == ".md" or item.suffix == ".typ":
                    continue
                
                relative_path = item.relative_to(CONTENT_DIR)
                if any(part.startswith("_") for part in relative_path.parts):
                    continue
                    
                target_path = SITE_DIR / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(item, target_path)
            results.append(True)
        except Exception as e:
            print(f"❌ 复制内容资源失败: {e}")
            results.append(False)
            
    return all(results)

def clean() -> bool:
    """清理生成的文件"""
    print("正在清理生成的文件...")
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
        print(f"✅ 已清理 {SITE_DIR}/ 目录。")
    return True

def preview(port: int = 8000, open_browser_flag: bool = True) -> bool:
    """启动本地预览服务器"""
    if not SITE_DIR.exists():
        print(f"⚠️ 输出目录 {SITE_DIR} 不存在，请先运行 build 命令。")
        return False

    print("正在启动本地预览服务器（按 Ctrl+C 停止）...")
    
    if open_browser_flag:
        def open_browser():
            time.sleep(1.5)
            url = f"http://localhost:{port}"
            print(f"🚀 正在打开浏览器: {url}")
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    # 尝试使用 uvx livereload
    try:
        subprocess.run(["uvx", "livereload", str(SITE_DIR), "-p", str(port)], check=False)
        return True
    except FileNotFoundError:
        pass
    except KeyboardInterrupt:
        return True

    # 回退到 http.server
    try:
        print("使用 Python 内置 http.server...")
        subprocess.run([sys.executable, "-m", "http.server", str(port), "--directory", str(SITE_DIR)], check=False)
        return True
    except KeyboardInterrupt:
        return True
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return False

def build(force: bool = False):
    """完整构建"""
    print("-" * 60)
    print("� 开始构建 (Markdown)...")
    print("-" * 60)
    
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    
    results = []
    results.append(build_html(force))
    results.append(copy_assets())
    
    print("-" * 60)
    if all(results):
        print("✅ 所有构建任务完成！")
    else:
        print("⚠️ 构建完成，但有部分任务失败。")
        
    return all(results)

# ============================================================================
# 命令行接口
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tufted Blog Template 构建脚本 (Markdown版)")
    subparsers = parser.add_subparsers(dest="command", title="可用命令")
    
    build_parser = subparsers.add_parser("build", help="完整构建")
    build_parser.add_argument("-f", "--force", action="store_true", help="强制重建")
    
    assets_parser = subparsers.add_parser("assets", help="仅复制资源")
    
    clean_parser = subparsers.add_parser("clean", help="清理")
    
    preview_parser = subparsers.add_parser("preview", help="预览")
    preview_parser.add_argument("-p", "--port", type=int, default=8000)
    preview_parser.add_argument("--no-open", action="store_false", dest="open_browser")
    preview_parser.set_defaults(open_browser=True)

    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
        
    os.chdir(Path(__file__).parent.absolute())
    
    commands = {
        "build": lambda: build(getattr(args, "force", False)),
        "assets": copy_assets,
        "clean": clean,
        "preview": lambda: preview(getattr(args, "port", 8000), getattr(args, "open_browser", True))
    }
    
    commands[args.command]()
