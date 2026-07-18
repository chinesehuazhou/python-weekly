"""周刊发布后清理临时文件。

各发布脚本在成功创建草稿/发布后调用本模块清理产生的临时文件。
"""

import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_TMP = PROJECT_ROOT / "docs" / "tmp"
DOCS_DIR = PROJECT_ROOT / "docs"


def wechat(date_str: str):
    """清理 wechat_publish.py 产生的临时文件"""
    # .wechat.html 由 wechat_publish.py 在 docs/ 根目录生成
    wechat_html = DOCS_DIR / f"{date_str}-weekly.wechat.html"
    if wechat_html.exists():
        wechat_html.unlink()
        print(f"  🧹 已清理: docs/{wechat_html.name}")

    # 也清理 docs/tmp/ 下可能残留的 .wechat.html
    for f in DOCS_TMP.glob(f"{date_str}*.wechat.html"):
        f.unlink()
        print(f"  🧹 已清理: docs/tmp/{f.name}")


def sspai(date_str: str):
    """清理 sspai_publish.py 产生的临时文件"""
    patterns = [
        f"{date_str}-sspai-body.html",
        f"{date_str}-sspai-draft.png",
        f"{date_str}-sspai-draft-url.txt",
        f"{date_str}-sspai-metadata.json",
        f"{date_str}-sspai-verify.png",
        f"{date_str}-sspai-cover.png",
        f"{date_str}-sspai-cover.jpg",
    ]
    for pattern in patterns:
        f = DOCS_TMP / pattern
        if f.exists():
            f.unlink()
            print(f"  🧹 已清理: docs/tmp/{f.name}")

    # 也清理临时封面（在系统临时目录下）
    for d in ["/tmp", DOCS_TMP]:
        for ext in [".png", ".jpg", ".jpeg"]:
            f = Path(d) / f"{date_str}-sspai-cover{ext}"
            if f.exists():
                f.unlink()
                print(f"  🧹 已清理: {f}")


def xiaobot(date_str: str):
    """清理 xiaobot_publish.py 产生的临时文件"""
    txt = DOCS_TMP / f"{date_str}-xiaobot-url.txt"
    if txt.exists():
        txt.unlink()
        print(f"  🧹 已清理: docs/tmp/{txt.name}")


def ifdian(date_str: str):
    """清理 ifdian_publish.py 产生的临时文件"""
    draft_png = DOCS_TMP / f"{date_str}-ifdian-draft.png"
    if draft_png.exists():
        draft_png.unlink()
        print(f"  🧹 已清理: docs/tmp/{draft_png.name}")

    error_png = DOCS_TMP / "ifdian_error.png"
    if error_png.exists():
        error_png.unlink()
        print(f"  🧹 已清理: docs/tmp/{error_png.name}")

    # ifdian URL 记录文件
    url_txt = DOCS_TMP / f"{date_str}-ifdian-url.txt"
    if url_txt.exists():
        url_txt.unlink()
        print(f"  🧹 已清理: docs/tmp/{url_txt.name}")


def all_for_date(date_str: str):
    """清理当期所有发布脚本产生的临时文件"""
    wechat(date_str)
    sspai(date_str)
    xiaobot(date_str)
    ifdian(date_str)
