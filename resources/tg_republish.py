#!/usr/bin/env python3
"""Telegram 补发脚本：重发 weekly_workflow.py 发送失败时保存的完整消息。

weekly_workflow.py 第 7 步发送 Telegram 超时/失败时，会把组装好的完整消息
（header + content_body + footer + channel）保存为 docs/tmp/YYYY-MM-DD-tg-message.txt。
网络恢复后运行本脚本即可快速重发，内容与格式与原始消息完全一致。

用法:
    ./.venv/bin/python resources/tg_republish.py 2026-08-29
"""
import os
import sys
import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: python tg_republish.py <date>   # 如 2026-08-29")
        sys.exit(1)

    date_str = sys.argv[1]
    msg_file = PROJECT_ROOT / "docs" / "tmp" / f"{date_str}-tg-message.txt"
    if not msg_file.exists():
        print(f"❌ 未找到待发消息文件: {msg_file}")
        sys.exit(1)

    message = msg_file.read_text(encoding="utf-8")
    print(f"📝 待发消息: {msg_file}（{len(message)} 字符）")
    print("⚠️ 发送前请确认频道 @pythontrendingweekly 尚未出现本期消息（超时可能已送达）！")
    print("   若已出现，直接删除本文件即可，不要补发。")
    print("   确认未出现后按 Enter 继续，Ctrl+C 取消...")
    input()

    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / "resources" / ".env")
    tg_bot_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    image_path = PROJECT_ROOT / "resources" / "img" / "python-weekly.png"
    if not tg_bot_token or not tg_chat_id:
        print("❌ .env 中缺少 TG_BOT_TOKEN 或 TG_CHAT_ID")
        sys.exit(1)

    async def send() -> None:
        from telegram import Bot, InputFile
        bot = Bot(token=tg_bot_token)
        with open(image_path, "rb") as f:
            await bot.send_photo(
                chat_id=tg_chat_id, photo=InputFile(f),
                caption=message, parse_mode="Markdown",
                read_timeout=60, write_timeout=60,
                connect_timeout=60, pool_timeout=60,
            )

    try:
        asyncio.run(send())
    except Exception as e:
        print(f"❌ 发送失败（{type(e).__name__}: {e}）")
        print(f"   消息文件已保留: {msg_file}")
        print("   若不确定是否已送达，请先查频道；确认未出现后再重试本脚本。")
        sys.exit(1)

    print("✅ 发送成功！")
    msg_file.unlink()
    print(f"  已删除临时文件: {msg_file}")


if __name__ == "__main__":
    main()
