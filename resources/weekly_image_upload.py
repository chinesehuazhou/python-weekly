"""周刊图片上传到七牛云。

用法：
  python3 resources/weekly_image_upload.py <image_url> <issue_date> <slug>

参数：
  image_url   - 图片原始 URL
  issue_date  - 周刊日期，如 2026-06-06
  slug        - 文件名 slug，如 agenticSeek

功能：
  1. 下载图片（GitHub blob URL 优先用 gh CLI，其他 URL 优先 curl，降级 httpx）
  2. 如果图片 > 100KB，用 Pillow 压缩到 100KB 以内
  3. 上传到七牛云，命名为 YYYY-MM-DD-slug.ext
  4. 保存本地副本到图片归档目录
  5. 输出 markdown 引用: ![](https://img.pythoncat.top/YYYY-MM-DD-slug.ext)
"""

import io
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx
from PIL import Image

# 从 .env 加载七牛云配置
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

QINIU_ACCESS_KEY = os.getenv("QINIU_ACCESS_KEY")
QINIU_SECRET_KEY = os.getenv("QINIU_SECRET_KEY")
QINIU_BUCKET = os.getenv("QINIU_BUCKET", "pythoncat")
QINIU_URL = os.getenv("QINIU_URL", "https://img.pythoncat.top")

# 本地图片归档目录（只存电脑文档归档目录，不在项目内留副本）
LOCAL_IMG_DIR_ARCHIVE = Path.home() / "Documents" / "周刊" / "ebook" / "season4" / "img"

MAX_SIZE_BYTES = 100 * 1024  # 100KB


def parse_github_url(url: str) -> tuple[str, str, str, str] | None:
    """解析 GitHub blob URL，返回 (owner, repo, ref, path) 或 None"""
    import re
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)", url)
    if m:
        return m.group(1), m.group(2), m.group(3), m.group(4)
    return None


def download_image(url: str) -> bytes:
    """下载图片，返回 bytes。
    GitHub blob URL 优先用 gh CLI（已认证 API，无速率限制），
    其他 URL 优先用 curl，降级 httpx。"""
    import subprocess

    # 1. 尝试用 gh CLI 下载 GitHub blob URL
    gh_parts = parse_github_url(url)
    if gh_parts:
        owner, repo, ref, path = gh_parts
        api_path = f"/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        print(f"  下载 (gh api): github.com/{owner}/{repo}")
        try:
            result = subprocess.run(
                ["gh", "api", "-H", "Accept: application/vnd.github.raw", api_path],
                capture_output=True, timeout=60,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
            print(f"  gh api 返回 {result.returncode}，降级 curl...")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("  gh CLI 不可用，降级 curl...")

    # 2. 用系统 curl（能正确使用系统代理），超时 60s，跟随重定向
    print(f"  下载: {url}")
    try:
        result = subprocess.run(
            ["curl", "-sSL", "--max-time", "60", url],
            capture_output=True, timeout=65,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
        print(f"  curl 返回 {result.returncode}，尝试 httpx...")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("  curl 不可用，尝试 httpx...")

    # 3. 降级：httpx（trust_env=False 绕过系统代理，避免 flyingbird SSL 超时）
    resp = httpx.get(url, follow_redirects=True, timeout=60, trust_env=False)
    resp.raise_for_status()
    return resp.content


def get_ext(content: bytes, url: str) -> str:
    """推测图片扩展名"""
    # 优先从 URL 获取
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]:
        if path.endswith(ext):
            return ext.lstrip(".")
    # 从 magic bytes 判断
    if content.startswith(b"\x89PNG"):
        return "png"
    if content.startswith(b"\xff\xd8"):
        return "jpg"
    if content.startswith(b"GIF"):
        return "gif"
    return "png"


def convert_to_png(data: bytes, ext: str) -> bytes:
    """将 webp/svg 格式转为 PNG，其他格式原样返回"""
    if ext == "webp":
        img = Image.open(io.BytesIO(data))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    if ext == "svg":
        try:
            import cairosvg
            return cairosvg.svg2png(bytestring=data)
        except ImportError:
            print("  警告: 未安装 cairosvg，SVG 无法转换，请 pip install cairosvg")
            return data  # 返回原数据，上传时会失败或显示异常
    return data


def compress_image(data: bytes, ext: str) -> tuple[bytes, str]:
    """压缩图片到 100KB 以内，返回 (compressed_bytes, new_ext)"""
    img = Image.open(io.BytesIO(data))

    def save_jpeg(im, quality):
        buf = io.BytesIO()
        rgb = im.convert("RGB") if im.mode in ("RGBA", "P") else im
        rgb.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()

    def save_png(im):
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    # 1. 尝试 PNG 无损优化
    result = save_png(img)
    if len(result) <= MAX_SIZE_BYTES:
        return result, "png"

    # 2. PNG 太大，转 JPEG 逐步降 quality
    for quality in range(85, 9, -10):
        result = save_jpeg(img, quality)
        if len(result) <= MAX_SIZE_BYTES:
            return result, "jpg"

    # 3. JPEG 最低 quality 仍超限，缩放到 70%
    w, h = img.size
    img = img.resize((int(w * 0.7), int(h * 0.7)), Image.LANCZOS)
    for quality in range(75, 9, -10):
        result = save_jpeg(img, quality)
        if len(result) <= MAX_SIZE_BYTES:
            return result, "jpg"

    # 4. 兜底：缩到 40%
    w, h = img.size
    img = img.resize((int(w * 0.4), int(h * 0.4)), Image.LANCZOS)
    result = save_jpeg(img, 40)
    return result, "jpg"


def upload_to_qiniu(key: str, data: bytes) -> bool:
    """上传文件到七牛云"""
    try:
        from qiniu import Auth, put_data
    except ImportError:
        print("  错误: 未安装 qiniu SDK，请执行 pip install qiniu")
        return False

    auth = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    token = auth.upload_token(QINIU_BUCKET, key, 3600)
    ret, info = put_data(token, key, data)
    if info.status_code == 200:
        print(f"  上传成功: {QINIU_URL}/{key}")
        return True
    else:
        print(f"  上传失败: {info.status_code} {info.text_body}")
        return False


def _archive_local(filename: str, data: bytes) -> Path | None:
    """保存本地副本到归档目录。失败时警告但不阻断流程。"""
    import traceback

    # 优先归档到 ~/Documents/周刊/ebook/season4/img/
    primary = LOCAL_IMG_DIR_ARCHIVE / filename
    fallback = Path("/tmp") / filename

    for target in (primary, fallback):
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            label = "本地归档" if target == primary else "归档(回退 /tmp)"
            print(f"  {label}: {target}")
            return target
        except Exception as e:
            if target == primary:
                print(f"  ⚠ 主归档路径写入失败: {e}", file=sys.stderr)
                print(f"  ⚠ 回退到 /tmp 目录", file=sys.stderr)
            else:
                print(f"  ❌ 归档完全失败: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

    return None


def main():
    if len(sys.argv) < 4:
        print("用法: python3 resources/weekly_image_upload.py <image_url> <issue_date> <slug>")
        print("示例: python3 resources/weekly_image_upload.py https://example.com/pic.png 2026-06-06 agenticSeek")
        sys.exit(1)

    image_url = sys.argv[1]
    issue_date = sys.argv[2]  # YYYY-MM-DD
    slug = sys.argv[3]

    # 1. 下载
    raw_data = download_image(image_url)
    ext = get_ext(raw_data, image_url)
    print(f"  原始大小: {len(raw_data) / 1024:.1f}KB, 格式: {ext}")

    # 1b. webp/svg → png 格式转换
    if ext in ("webp", "svg"):
        print(f"  转换 {ext} → png...")
        raw_data = convert_to_png(raw_data, ext)
        ext = "png"
        print(f"  转换后: {len(raw_data) / 1024:.1f}KB")

    # 2. 压缩（如需要）
    if len(raw_data) > MAX_SIZE_BYTES:
        print(f"  超过 100KB，开始压缩...")
        data, ext = compress_image(raw_data, ext)
        print(f"  压缩后: {len(data) / 1024:.1f}KB, 格式: {ext}")
    else:
        data = raw_data
        print("  无需压缩")

    # 3. 确定文件名
    filename = f"{issue_date}-{slug}.{ext}"
    print(f"  文件名: {filename}")

    # 4. 保存到归档目录（~/Documents/周刊/ebook/season4/img/）
    archive_path = _archive_local(filename, data)

    # 5. 上传七牛云
    success = upload_to_qiniu(filename, data)

    # 6. 输出 markdown
    if success:
        md = f"![]({QINIU_URL}/{filename})"
        print(f"\nMarkdown 引用:\n{md}")
    else:
        print("\n  上传失败，本地副本已保存到:", archive_path)
        sys.exit(1)


if __name__ == "__main__":
    main()
