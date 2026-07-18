"""URL 去重检查 — 已迁移至 weekly_helper/scorer/dedup.py

此文件仅保留向后兼容，实际逻辑在 weekly_helper/scorer/dedup.py。
用法不变: python3 resources/weekly_dedup.py <url1> <url2> ...
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weekly_helper.scorer.dedup import main

if __name__ == '__main__':
    main()
