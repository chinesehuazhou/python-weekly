'use client';

import {useEffect, useState} from 'react';

// 「回到开头」按钮：窗口往下读一点之后才出现，点一下把阅读窗口滚回顶部。
// 刻意不接正文、只观察 DOM —— 否则整期文本会为了一个按钮被打进客户端包。
// 2026-10-25 用户反馈：原来那个向下的装饰箭头点了没反应，改成向上三角并让它可点。
const SHOW_AFTER = 120;

export default function ScrollCue({label}: {label: string}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const body = document.querySelector<HTMLElement>('.issue__body');
    if (!body) return;

    const update = () => setVisible(body.scrollTop > SHOW_AFTER);

    update();
    body.addEventListener('scroll', update, {passive: true});
    return () => body.removeEventListener('scroll', update);
  }, []);

  if (!visible) return null;

  return (
    <button
      type="button"
      className="issue__cue"
      aria-label={label}
      onClick={() => {
        document
          .querySelector<HTMLElement>('.issue__body')
          ?.scrollTo({top: 0, behavior: 'smooth'});
      }}
    />
  );
}
