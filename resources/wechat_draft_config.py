#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""微信公众号草稿配置脚本 —— 通过浏览器自动化设置：原创声明、合集、广告、原文链接、摘要。

用法：
  python3 resources/wechat_draft_config.py <draft_media_id> --issue N [--full] [--source-url URL]

`--issue N` 是**必填**：草稿箱按更新时间倒序，不指定期号会配置到草稿箱里最新那篇
（2026-09-19 补发 #118 全文版时就因此误改了 #168 的广告设置）。

由于微信 API 不支持直接设置原创声明/合集/广告，此脚本通过 CDP 连接已运行的
Edge 浏览器，在公众号后台自动完成这些配置。

前置条件：
  - Edge 浏览器已运行并开启 CDP 调试端口 (localhost:18800)
  - 已在浏览器中登录微信公众号后台
  - 草稿已通过 wechat_publish.py 创建

行为：
  - 简化版（默认）：声明原创、选合集「Python潮流周刊」、文中广告设「不展示」、清空摘要
  - 全文版（--full）：声明原创、选合集、文中广告设「智能插入」、保留摘要

示例：
  # 简化版（默认，原创+合集+不展示文中广告+清空摘要）
  python3 resources/wechat_draft_config.py <media_id> --issue 168 \
      --source-url https://xiaobot.net/post/...

  # 往期全文版（原创+合集+智能插入文中广告+保留摘要）
  python3 resources/wechat_draft_config.py <media_id> --issue 118 --full \
      --source-url https://pythoncat.top/posts/2025-09-06-weekly

2026-09 编辑器改版要点（旧选择器已全部失效，勿回退）：
  - 设置项都在底部设置栏的 `.setting-group__checkbox-item` 里，
    条目文字是 `<span class="lbl_content">原创/合集/广告/原文链接</span>`
  - 点整条 item 不会触发弹窗，必须点条目内的 `.allow_click_opr`
  - 合集弹窗：`li.select-opt-li` 是选项，确认按钮是 `.weui-desktop-btn_primary`
  - 广告弹窗：内容是 file.daihuo.qq.com 的 iframe，选项是 span（智能插入/手动插入/不展示文中广告）
  - 原创已声明时 `#js_original_open` 存在；未声明时是 `#js_original_type`
  - **摘要**：`draft/add` 走 API 时微信会强制自动抓取正文前段，传空也不行；
    只有清空编辑器里的 `#js_description` 再保存才能真正置空
"""

import sys
from playwright.sync_api import sync_playwright

# ===== 配置 =====
CDP_URL = "http://localhost:18800"
WECHAT_MP_DRAFTS = "https://mp.weixin.qq.com/cgi-bin/appmsg?begin=0&count=10&type=77&action=list_card&lang=zh_CN"
COLLECTION_NAME = "Python潮流周刊"
DIALOG = ".weui-desktop-dialog"

# 设置栏条目：按 span.lbl_content 的文本定位
ITEM_BY_LABEL = """(label) => {
    const vis = e => e.getBoundingClientRect().width > 0;
    const sp = [...document.querySelectorAll('span.lbl_content')]
        .find(e => vis(e) && (e.innerText || '').trim() === label);
    return sp ? sp.closest('.setting-group__checkbox-item') : null;
}"""


# ===== 弹窗工具 =====

def dialog_text(page) -> str:
    """当前可见弹窗的文本（没有则空串），用于调试与断言。"""
    return page.evaluate("""(sel) => {
        const d = [...document.querySelectorAll(sel)]
            .find(e => e.getBoundingClientRect().width > 0);
        return d ? (d.innerText || '').replace(/\\s+/g, ' ').slice(0, 200) : '';
    }""", DIALOG)


def close_dialogs(page) -> int:
    """关掉所有可见弹窗（点右上角 X 或「取消」）。

    弹窗遮罩会拦截后续所有点击（Playwright 等可操作性超时），
    导致后面每一步都「未找到控件」——每个设置步骤前都该调用它。
    """
    n = page.evaluate("""(sel) => {
        let n = 0;
        [...document.querySelectorAll(sel)]
          .filter(e => e.getBoundingClientRect().width > 0)
          .forEach(d => {
              const btn = d.querySelector('.weui-desktop-dialog__close-btn')
                       || [...d.querySelectorAll('button')]
                              .find(b => (b.innerText || '').trim() === '取消');
              if (btn) { btn.click(); n++; }
          });
        return n;
    }""", DIALOG)
    if n:
        page.wait_for_timeout(800)
    return n


# ===== 草稿箱导航 =====

def find_or_create_wechat_page(context):
    """在已有页签中查找微信公众号后台页面，若没有则新建页签。

    不会覆盖或关闭用户已打开的其他网站页签。
    """
    for page in context.pages:
        url = (page.url or "").lower()
        # 只认公众号后台页签（cgi-bin）；排除 mp.weixin.qq.com/s 文章/预览页签
        if "mp.weixin.qq.com" in url and "/cgi-bin" in url:
            print(f"🔗 找到微信公众号已有页签")
            return page

    page = context.new_page()
    print("🔗 新建页签用于微信公众号配置")
    return page


def find_and_edit_draft(page, context, title_keyword: str, issue: str = "", is_full: bool = False):
    """在草稿箱中找到指定草稿并点击铅笔图标进入编辑页，返回编辑页 page。

    2026 新版后台草稿箱（action=list_card 卡片视图）的编辑入口是草稿卡
    右上角无文本的铅笔 SVG 图标（tooltip=编辑），点击后编辑器在**新页签**
    打开（appmsg_edit URL）。旧版「点击标题行直接进编辑页」的方式已失效：
    - 点击标题会打开 tempkey 预览链接（mp.weixin.qq.com/s），不是编辑页
    - 「编辑」按钮无文本，是 SVG 图标，不能用 text= 定位

    ⚠️ **必须按期号定位**。草稿箱按更新时间倒序，直接取第一张卡会拿到最新那篇：
    2026-09-19 补发 #118 全文版时，就因此把配置打到了 #168 的草稿上（把简化版的
    广告从「不展示」改成了「智能插入」）。`--issue` 缺失时会明确报警而不是猜。
    """
    print("📋 浏览草稿箱...")

    # 直接访问草稿列表 URL 会提示「请重新登录」，需先访问首页获取带 token 的会话
    if "token=" not in (page.url or ""):
        page.goto("https://mp.weixin.qq.com/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

    token = ""
    if "token=" in (page.url or ""):
        token = page.url.split("token=")[-1].split("&")[0]

    # 直接 goto 草稿箱 URL 会被微信重定向回 home，须点击左侧菜单「草稿箱」进入
    drafts_url = WECHAT_MP_DRAFTS
    if token:
        drafts_url += f"&token={token}"

    # 激活页签（后台页签被浏览器节流渲染，控件定位/点击会超时失败）
    try:
        page.bring_to_front()
        page.wait_for_timeout(1000)
    except Exception:
        pass

    # 已在草稿箱页（list_card）则无需再导航（重复菜单点击会触发页面重载）
    if "list_card" in (page.url or ""):
        page.wait_for_timeout(2000)
        print("  ✓ 已在草稿箱页面，跳过导航")
    else:
        _enter_drafts(page, drafts_url)

    # 检查登录状态（进入后页面内容已刷新）
    if "请重新登录" in (page.content() or "")[:20000] or "login" in page.url.lower():
        raise RuntimeError(
            "需要登录微信公众号后台：请在浏览器中登录 mp.weixin.qq.com 后重跑本脚本")

    print(f"🔍 查找草稿: {title_keyword[:40]}...")

    # 定位草稿卡：必须先按期号确定是哪一张卡，否则会拿到最新那篇
    if not issue:
        raise RuntimeError(
            "缺少 --issue 期号：草稿箱按更新时间倒序，不指定期号会配置到最新草稿上。"
            "请加 --issue N 重跑")

    found = page.evaluate("""([issue, isFull]) => {
        // 期号后紧跟中/英文冒号，避免 #118 误配 #1180
        const re = new RegExp('#' + issue + '\\\\s*[:：]');
        const cards = [...document.querySelectorAll('div.weui-desktop-card')];
        for (let i = 0; i < cards.length; i++) {
            const first = (cards[i].innerText || '').split('\\n')[0].trim();
            if (!re.test(first)) continue;
            // 全文版标题带「【往期回顾】」前缀，简化版没有，用这个区分同名期号
            if (isFull !== first.includes('往期回顾')) continue;
            // data-appid 对应编辑页 URL 里的 appmsgid，用于稍后认领正确的编辑页签
            return {idx: i, appid: cards[i].getAttribute('data-appid') || ''};
        }
        return null;
    }""", [issue, is_full])
    if not found:
        kind = "往期全文版" if is_full else "简化版"
        raise RuntimeError(f"草稿箱中未找到第 {issue} 期的{kind}草稿")
    idx, appid = found["idx"], found["appid"]
    print(f"  ✓ 定位到草稿卡 [{idx}] 第 {issue} 期（appmsgid={appid}）")

    # 微信改版后铅笔 `<a class="weui-desktop-icon-btn">` 与提示文字 span 是兄弟节点，
    # 不再被 tooltip 容器包裹，故用 following-sibling 轴定位（原先的 ancestor 轴已失效）。
    pen_rel_xpath = (
        ".//div[contains(@class,'weui-desktop-card__bd')]"
        "//a[contains(@class,'weui-desktop-icon-btn')]"
        "[following-sibling::span[contains(@class,'weui-desktop-tooltip') "
        "and normalize-space(text())='编辑']]"
    )
    card = page.locator("div.weui-desktop-card").nth(idx)
    # 操作图标需先悬停卡片才会显示
    card.hover()
    page.wait_for_timeout(800)
    card.locator(f"xpath={pen_rel_xpath}").first.click(timeout=8000)
    print("  ✓ 已点击编辑（铅笔图标）")

    # 编辑器在新页签打开（appmsg_edit URL）。
    # 必须按 appmsgid 认领，不能只看 `appmsg_edit in url`——之前跑过的编辑页签会一直留着，
    # 随手取第一个 appmsg_edit 会拿到别的草稿的编辑器（2026-09-19 补发 #118 时踩到）。
    page.wait_for_timeout(4000)
    edit_page = None
    for pg in context.pages:
        url = pg.url or ""
        if "appmsg_edit" in url and (not appid or f"appmsgid={appid}" in url):
            print(f"  ✓ 已打开编辑页（appmsgid={appid}）")
            pg.bring_to_front()
            edit_page = pg
            break
    if edit_page is None and "appmsg_edit" in (page.url or "") \
            and (not appid or f"appmsgid={appid}" in page.url):
        # 回退：当前页签自身跳转到了编辑页
        edit_page = page
    if edit_page is None:
        raise RuntimeError(
            f"未找到第 {issue} 期的编辑页签（appmsgid={appid}）。"
            "可能是草稿箱里还开着其他期的编辑页，请关掉后重跑")

    # 打开后再核对一次标题：定位逻辑一旦失手，这一步是最后的防线，
    # 否则会静默改到别的草稿（曾把 #168 的广告配置改掉）
    edit_page.wait_for_timeout(3000)
    opened = get_draft_title(edit_page)
    if f"#{issue}" not in (opened or ""):
        raise RuntimeError(
            f"打开的草稿标题与期号不符：期望含 #{issue}，实际是「{opened[:50]}」。"
            "已中止，未做任何修改")
    print(f"  ✓ 标题核对通过: {opened[:50]}")
    return edit_page


def _enter_drafts(page, drafts_url):
    """通过左侧菜单进入草稿箱（直接 goto list_card URL 会被微信重定向回 home）"""
    entered = False
    # 策略 1：可见菜单项点击（二级菜单折叠时不可见会超时）
    try:
        page.locator('a.weui-desktop-menu__link:has-text("草稿箱")').first.click(timeout=4000)
        page.wait_for_timeout(3000)
        entered = "list_card" in (page.url or "")
    except Exception:
        pass
    # 策略 2：JS 强制点击（无视折叠/可见性）
    if not entered:
        try:
            page.evaluate("""() => {
                const a = [...document.querySelectorAll('a')]
                    .find(x => (x.textContent || '').trim() === '草稿箱' && x.className.includes('menu'));
                if (a) a.click();
            }""")
            page.wait_for_timeout(4000)
            entered = "list_card" in (page.url or "")
            if entered:
                print("  ✓ 已通过 JS 菜单点击进入草稿箱")
        except Exception:
            pass
    # 策略 3：直接导航（可能被重定向回 home，仅兜底）
    if not entered:
        print("  ⚠️ 菜单点击失败，尝试直接导航...")
        page.goto(drafts_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        entered = "list_card" in (page.url or "")
    if not entered:
        print("  ⚠️ 未能进入草稿箱页面，当前 URL:", (page.url or "")[:100])
    return entered


# ===== 各设置项 =====

def get_draft_title(page) -> str:
    try:
        return page.locator("#title").first.input_value()
    except Exception:
        return ""


def set_original_declaration(page) -> bool:
    """声明原创。已声明则跳过（幂等）。"""
    print("📝 原创声明")

    # ⚠️ 不能只判断元素是否存在：#js_original_open（已声明）与未声明块在 DOM 里**同时存在**，
    # 靠 inline display 切换。只查存在性会恒为真，把未声明的草稿误判成已声明。
    state = page.evaluate("""() => {
        const o = document.querySelector('#js_original_open');
        const visible = !!o && o.getBoundingClientRect().width > 0;
        return {declared: visible,
                tips: visible ? (o.innerText || '').replace(/\\s+/g, ' ').trim() : ''};
    }""")
    if state["declared"]:
        print(f"  ✓ 已声明（{state['tips'][:50]}）")
        return True
    print("  · 未声明，打开声明弹窗")

    # 点「未声明」那一栏的入口打开弹窗（取可见的那个，未声明块在 DOM 中靠前）
    clicked = page.evaluate("""() => {
        const vis = e => e.getBoundingClientRect().width > 0;
        const el = [...document.querySelectorAll('#js_original .js_edit_ori')].find(vis);
        if (!el) return false;
        el.click();
        return true;
    }""")
    if not clicked:
        print("  ⚠️ 未找到「未声明」入口")
        return False
    page.wait_for_timeout(2000)

    # 弹窗内：选「文字原创」→ 勾选协议 → 确定
    # ⚠️ 一律取**可见**的弹窗：页面上同时存在多个 .weui-desktop-dialog（含隐藏的模板），
    # document.querySelector 拿到的是第一个，可能是个隐藏弹窗，于是「找不到确定按钮」。
    page.evaluate("""() => {
        const d = [...document.querySelectorAll('.weui-desktop-dialog')]
            .find(e => e.getBoundingClientRect().width > 0);
        if (!d) return;
        const target = [...d.querySelectorAll('label')]
            .find(e => (e.innerText || '').trim() === '文字原创');
        if (target) target.click();
    }""")
    page.wait_for_timeout(600)
    page.evaluate("""() => {
        const d = [...document.querySelectorAll('.weui-desktop-dialog')]
            .find(e => e.getBoundingClientRect().width > 0);
        if (!d) return;
        [...d.querySelectorAll('input[type=checkbox]')].forEach(c => {
            if (!c.checked) c.click();
        });
    }""")
    page.wait_for_timeout(400)
    clicked = page.evaluate("""() => {
        const d = [...document.querySelectorAll('.weui-desktop-dialog')]
            .find(e => e.getBoundingClientRect().width > 0);
        if (!d) return 'no dialog';
        const btn = [...d.querySelectorAll('button')]
            .find(b => (b.innerText || '').trim() === '确定');
        if (!btn) return 'no 确定';
        btn.click();
        return 'ok';
    }""")
    page.wait_for_timeout(3000)

    state = page.evaluate("""() => {
        const o = document.querySelector('#js_original_open');
        const visible = !!o && o.getBoundingClientRect().width > 0;
        return {declared: visible,
                tips: visible ? (o.innerText || '').replace(/\\s+/g, ' ').trim() : ''};
    }""")
    if state["declared"]:
        print(f"  ✓ 已声明原创（{state['tips'][:50]}）")
        return True
    print(f"  ⚠️ 声明原创失败（{clicked}），请在后台手动设置")
    return False


def select_collection(page, collection_name: str = COLLECTION_NAME) -> bool:
    """选择合集。已选中同名合集则跳过（幂等）。"""
    print(f"📁 合集: {collection_name}")

    current = page.evaluate(
        "() => { const e = document.querySelector('.js_article_tags_content');"
        " return e ? e.innerText.trim() : ''; }")
    if current == collection_name:
        print(f"  ✓ 已选择（{current}）")
        return True

    # 点「合集」条目右侧的「未添加 / 合集名 >」打开弹窗
    page.evaluate(f"""() => {{
        const item = ({ITEM_BY_LABEL})('合集');
        const opr = item && item.querySelector('.allow_click_opr');
        if (opr) opr.click();
    }}""")
    page.wait_for_timeout(1800)

    if not dialog_text(page):
        print("  ⚠️ 合集弹窗未打开")
        return False

    # ⚠️ 必须点一下输入框，选项列表（select-opts-con）才会从 display:none 加载出来，
    # 否则 li.select-opt-li 恒为 0 个，误报「列表中未找到合集」
    page.evaluate("""() => {
        const i = [...document.querySelectorAll('input.weui-desktop-form__input')]
            .find(e => e.getBoundingClientRect().width > 0);
        if (!i) return;
        i.click();
        i.focus();
    }""")
    page.wait_for_timeout(2000)

    # 选项是 li.select-opt-li（文本带首尾空白，必须 strip 后比较）
    picked = page.evaluate("""(name) => {
        const li = [...document.querySelectorAll('li.select-opt-li')]
            .find(e => (e.innerText || '').trim() === name);
        if (!li) return false;
        li.click();
        return true;
    }""", collection_name)
    if not picked:
        print(f"  ⚠️ 列表中未找到「{collection_name}」")
        close_dialogs(page)
        return False
    page.wait_for_timeout(1000)

    # 确认按钮是 primary 样式（文本「确认」）
    page.evaluate("""() => {
        const d = [...document.querySelectorAll('.weui-desktop-dialog')]
            .find(e => e.getBoundingClientRect().width > 0);
        if (!d) return;
        const btn = [...d.querySelectorAll('button.weui-desktop-btn_primary')]
            .find(b => (b.innerText || '').trim() === '确认');
        if (btn) btn.click();
    }""")
    page.wait_for_timeout(2000)

    current = page.evaluate(
        "() => { const e = document.querySelector('.js_article_tags_content');"
        " return e ? e.innerText.trim() : ''; }")
    if current == collection_name:
        print(f"  ✓ 已选择合集: {current}")
        return True
    print(f"  ⚠️ 合集设置后仍为「{current}」，请手动确认")
    return False


# 三个 tab 的目标状态。
# 简化版「关闭广告」= API 建草稿时的默认值（文中/关键词都不展示、留言区展示），
# 这也是往期每一期简化版的实际状态——旧脚本的 set_ads 其实从未真正改动过任何值。
# 全文版「开启广告」= 文中智能插入、关键词与留言区都展示。
AD_TARGETS = {
    False: {"文中广告": "不展示文中广告",
            "关键词广告": "不展示关键词广告",
            "留言区广告": "展示留言区广告"},
    True: {"文中广告": "智能插入",
           "关键词广告": "展示关键词广告",
           "留言区广告": "展示留言区广告"},
}


def _ad_frame(page):
    return next((f for f in page.frames if "daihuo.qq.com" in (f.url or "")), None)


def _open_ad_dialog(page) -> bool:
    page.evaluate(f"""() => {{
        const item = ({ITEM_BY_LABEL})('广告');
        const opr = item && item.querySelector('.allow_click_opr');
        if (opr) opr.click();
    }}""")
    page.wait_for_timeout(3500)
    return _ad_frame(page) is not None


def _read_ad_tabs(page, frame, tabs) -> dict:
    """切到每个 tab 读出当前选中项。切 tab 后需点一下别处触发提交，否则读到上一个 tab 的值。"""
    out = {}
    for tab in tabs:
        frame.evaluate("""(t) => {
            const el = [...document.querySelectorAll('.adui-tabs-tab')]
                .find(e => (e.innerText || '').trim() === t);
            if (el) el.click();
        }""", tab)
        page.wait_for_timeout(1200)
        frame.evaluate(
            "() => { const l = document.querySelector('.adui-form-label'); if (l) l.click(); }")
        page.wait_for_timeout(1200)
        out[tab] = frame.evaluate("""() => {
            const c = document.querySelector('.adui-radio-checked');
            return c ? (c.innerText || '').trim() : '';
        }""")
    return out


def set_ads(page, enable: bool) -> bool:
    """设置三类广告（文中 / 关键词 / 留言区）。

    选项在 file.daihuo.qq.com 的 iframe 里，改完需在 iframe 内点「确认」；
    点确认会把**三个 tab 一起**提交，所以必须三个都设成目标值再点。
    """
    targets = AD_TARGETS[enable]
    tabs = list(targets)
    print("💰 广告: " + "、".join(f"{t}={v}" for t, v in targets.items()))

    if not _open_ad_dialog(page):
        print("  ⚠️ 广告弹窗未打开（未找到 iframe）")
        close_dialogs(page)
        return False
    frame = _ad_frame(page)

    now = _read_ad_tabs(page, frame, tabs)
    if all(now[t] == targets[t] for t in tabs):
        print("  ✓ 三项均已是目标值，无需改动")
        close_dialogs(page)
        return True

    for tab, want in targets.items():
        if now[tab] == want:
            continue
        print(f"  · {tab}: {now[tab]} → {want}")
        frame.evaluate("""(t) => {
            const el = [...document.querySelectorAll('.adui-tabs-tab')]
                .find(e => (e.innerText || '').trim() === t);
            if (el) el.click();
        }""", tab)
        page.wait_for_timeout(1200)
        # 必须点选项外层 label（.adui-radio-base），点内层 span 有时不触发选中
        ok = frame.evaluate("""(label) => {
            const sp = [...document.querySelectorAll('span')]
                .find(e => (e.innerText || '').trim() === label);
            if (!sp) return false;
            const lb = sp.closest('label') || sp.parentElement || sp;
            lb.click();
            return true;
        }""", want)
        if not ok:
            print(f"    ⚠️ iframe 内未找到「{want}」选项")
            close_dialogs(page)
            return False
        page.wait_for_timeout(800)

    frame.evaluate("""() => {
        const b = [...document.querySelectorAll('span.adui-button-content, button')]
            .find(e => (e.innerText || '').trim() === '确认');
        if (b) b.click();
    }""")
    page.wait_for_timeout(2500)

    # 回读校验：点确认不等于生效（曾出现「已设为不展示」但实际仍是智能插入）
    if not _open_ad_dialog(page):
        print("  ⚠️ 校验时广告弹窗未打开")
        return False
    frame = _ad_frame(page)
    after = _read_ad_tabs(page, frame, tabs)
    close_dialogs(page)
    bad = [f"{t}({after[t]})" for t in tabs if after[t] != targets[t]]
    if bad:
        print(f"  ⚠️ 回读不符: {'、'.join(bad)}")
        return False
    print("  ✓ 三项已确认写入")
    return True


def check_source_url(page, url: str) -> bool:
    """核对原文链接。

    原文链接由 `wechat_publish.py --source-url` 在 API 建草稿时写入，
    编辑器里通常已是目标值；这里只做核对，不一致才报出来让用户手改
    （弹窗内的输入框是隐藏的 input.js_url，改起来并不比手点可靠）。
    """
    print(f"🔗 原文链接")
    current = page.evaluate(
        "() => { const e = document.querySelector('.article_url_setting');"
        " return e ? e.innerText.trim() : ''; }")
    if current == url:
        print(f"  ✓ 已是 {url[:60]}")
        return True
    if not current:
        print(f"  ⚠️ 原文链接为空，应为 {url[:60]}（请在后台「原文链接」里填写）")
    else:
        print(f"  ⚠️ 原文链接为 {current[:60]}，应为 {url[:60]}")
    return False


def clear_digest(page) -> bool:
    """清空摘要。

    必须走编辑器：`draft/add` 走 API 时微信会强制用正文前段自动填充摘要，
    显式传 digest="" 也无效；只有清空 `#js_description` 再保存才真正置空。
    """
    print("📄 摘要: 清空")
    length = page.evaluate("""() => {
        const d = document.querySelector('#js_description');
        if (!d) return -1;
        d.focus();
        d.value = '';
        d.dispatchEvent(new Event('input', {bubbles: true}));
        d.dispatchEvent(new Event('change', {bubbles: true}));
        d.blur();
        return d.value.length;
    }""")
    page.wait_for_timeout(600)
    if length == 0:
        print("  ✓ 已清空")
        return True
    if length < 0:
        print("  ⚠️ 未找到摘要输入框")
        return False
    print(f"  ⚠️ 清空后仍有 {length} 字")
    return False


def save_draft(page) -> bool:
    """点「保存为草稿」（页面右下角按钮）"""
    print("💾 保存草稿...")
    ok = page.evaluate("""() => {
        const btn = [...document.querySelectorAll('button')]
            .find(b => (b.innerText || '').trim() === '保存为草稿');
        if (!btn) return false;
        btn.click();
        return true;
    }""")
    if not ok:
        print("  ⚠️ 未找到「保存为草稿」按钮")
        return False
    page.wait_for_timeout(4000)
    print("  ✓ 已保存")
    return True


# ===== 主流程 =====

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    draft_media_id = sys.argv[1]
    is_full = "--full" in sys.argv

    def arg_value(flag):
        for i, a in enumerate(sys.argv):
            if a == flag and i + 1 < len(sys.argv):
                return sys.argv[i + 1]
        return ""

    source_url = arg_value("--source-url")
    issue = arg_value("--issue").lstrip("#")

    mode_label = "全文版" if is_full else "简化版"
    print("=" * 60)
    print(f"📡 微信公众号草稿配置 — {mode_label}")
    print("=" * 60)
    print(f"  草稿 media_id: {draft_media_id[:20]}...")

    with sync_playwright() as p:
        print("🔗 通过 CDP 连接已有 Edge...")
        browser = p.chromium.connect_over_cdp(CDP_URL)

        if not browser.contexts:
            print("❌ 没有打开的浏览器上下文")
            sys.exit(1)

        context = browser.contexts[0]

        try:
            page = find_or_create_wechat_page(context)
            page = find_and_edit_draft(page, context, "Python 潮流周刊", issue, is_full)

            page.wait_for_timeout(3000)
            print(f"  当前编辑: {get_draft_title(page)[:60]}")
            close_dialogs(page)

            results = {}
            results["原创"] = set_original_declaration(page)
            close_dialogs(page)

            results["合集"] = select_collection(page, COLLECTION_NAME)

            results["广告"] = set_ads(page, enable=is_full)

            if source_url:
                results["原文链接"] = check_source_url(page, source_url)
            else:
                print("  💡 未指定 --source-url，跳过原文链接核对")

            # 摘要：简化版必须清空；全文版保留（不动）
            if not is_full:
                results["摘要"] = clear_digest(page)

            results["保存"] = save_draft(page)

            print("\n" + "=" * 60)
            failed = [k for k, v in results.items() if not v]
            if failed:
                print(f"⚠️ 完成，但以下项需人工确认: {'、'.join(failed)}")
                sys.exit(2)
            print("✅ 配置完成！请在公众号后台确认")
            print("=" * 60)

        except Exception as e:
            print(f"❌ 出错: {e}")
            try:
                page.screenshot(path="wechat_config_error.png")
                print("  截图保存到 wechat_config_error.png")
            except Exception:
                pass
            sys.exit(1)


if __name__ == "__main__":
    main()
