import fs from 'node:fs';
import path from 'node:path';

export type SampleImage = {
  src: string;
  alt: string;
  width: number;
  height: number;
};

export type SampleItem = {
  title: string;
  url: string;
  summary: string;
  images: SampleImage[];
};

export type SampleSection = {
  name: string;
  items: SampleItem[];
};

export type SampleIssue = {
  number: number;
  title: string;
  date: string;
  displayDate: string;
  articleCount: number;
  projectCount: number;
  mediaCount: number;
  sections: SampleSection[];
};

const CONTENT_ROOT = path.resolve(process.cwd(), '../docs');
const IMAGE_ROOT = path.join(process.cwd(), 'public', 'sample');

// 固定用第 100 期当样例，不再跟着最新一期走。
// 原因（2026-10-25 用户定稿）：最新一期是付费内容，首页给不出可点的全文；
// 而「取最新一期」会让每次发刊都得重新构建一次 landing，维护成本不对等。
// 第 100 期发布时间已满一年，按 FAQ 里的承诺是全文免费公开的，拿来当样例不违约。
// 换期只改这两个常量，并确认下面 assertSampleNumber() 没抛错。
const SAMPLE_ISSUE_DATE = '2025-05-03';
const SAMPLE_ISSUE_NUMBER = 100;

const FRONTMATTER = /^---\n([\s\S]*?)\n---\n/;
const SECTION_LINE = /^##\s*\[([^\]]+)\]\([^)]*\)\s*$/;
const ITEM_LINE = /^(\d+)、\s*\[([^\]]+)\]\(([^)]+)\)\s*$/;
const IMAGE_LINE = /^!\[([^\]]*)\]\(([^)]+)\)\s*$/;
// 中文稿 frontmatter 里写「Python 潮流周刊#100：…」，英文稿没有 frontmatter、
// 标题行写「Python Trending Weekly #100: …」，两种冒号都要认。
const TITLE = /#(\d+)\s*[：:]\s*(.+)$/;

function stripEmoji(text: string): string {
  return text.replace(/^[^\p{L}]+/u, '').trim();
}

// 正文图片原本热链 img.pythoncat.top，一是不该让首页依赖别人的图床，
// 二是静态导出时热链图没有尺寸信息会撑不开版式。这里把图收进 public/sample/，
// 并从 PNG 头里读出真实宽高（IHDR 的 16~24 字节），避免渲染时跳版。
function readPngSize(filePath: string): { width: number; height: number } {
  const head = Buffer.alloc(24);
  const fd = fs.openSync(filePath, 'r');
  try {
    fs.readSync(fd, head, 0, 24, 0);
  } finally {
    fs.closeSync(fd);
  }

  if (head.toString('ascii', 12, 16) !== 'IHDR') {
    throw new Error(`${filePath} 不是 PNG（读不到 IHDR）`);
  }

  return { width: head.readUInt32BE(16), height: head.readUInt32BE(20) };
}

function localImage(url: string, alt: string): SampleImage {
  const base = path.basename(new URL(url).pathname);
  const filePath = path.join(IMAGE_ROOT, base);

  // 少一张图比报错更难查：样例区「把图弄没了」正是上一版的问题。
  if (!fs.existsSync(filePath)) {
    throw new Error(`样例期图片缺失：${base}，请下载到 public/sample/`);
  }

  return { src: `/sample/${base}`, alt, ...readPngSize(filePath) };
}


function parseIssue(markdown: string, fileDate: string): SampleIssue {
  const fmMatch = markdown.match(FRONTMATTER);
  const frontmatter = fmMatch?.[1] ?? '';
  const body = fmMatch ? markdown.slice(fmMatch[0].length) : markdown;

  const frontTitle = frontmatter.match(/^title:\s*'?(.+?)'?\s*$/m)?.[1];
  const headingLine = body.match(/^#\s+(.+)$/m)?.[1];
  const rawTitle = frontTitle ?? headingLine ?? '';
  const date =
    frontmatter.match(/^pubDate:\s*'?([\d-]+)'?\s*$/m)?.[1] ?? fileDate;
  const heading = rawTitle.match(TITLE);

  if (!heading) {
    throw new Error(`样例期标题解析失败：${rawTitle || '(空标题)'}`);
  }

  const sections: SampleSection[] = [];
  let current: SampleSection | null = null;
  let pending: SampleItem | null = null;
  let summaryLines: string[] = [];

  const flush = () => {
    if (pending) {
      pending.summary = summaryLines.join(' ').replace(/\s+/g, ' ').trim();
      current?.items.push(pending);
      pending = null;
      summaryLines = [];
    }
  };

  for (const rawLine of body.split('\n')) {
    const line = rawLine.trim();

    if (!line) {
      continue;
    }

    const image = line.match(IMAGE_LINE);
    if (image?.[2]) {
      // 正文里的图紧跟在所属条目的摘要后面，所以归给当前 pending 那条。
      pending?.images.push(localImage(image[2].trim(), image[1]?.trim() ?? ''));
      continue;
    }

    const section = line.match(SECTION_LINE);
    if (section?.[1]) {
      flush();
      current = { name: stripEmoji(section[1]), items: [] };
      sections.push(current);
      continue;
    }

    if (!current) continue;

    const item = line.match(ITEM_LINE);
    if (item?.[2] && item[3]) {
      flush();
      pending = { title: item[2].trim(), url: item[3].trim(), summary: '', images: [] };
      continue;
    }

    if (pending) summaryLines.push(line);
  }

  flush();

  // 「往年回顾 / Looking Back」「欢迎订阅」这类节只有链接和号召，没有编号条目，
  // 靠「这一节一条都没解析出来」自动剔掉，比按节名黑名单更不容易漏（中英节名并不一致）。
  const content = sections.filter((section) => section.items.length > 0);

  const count = (...keywords: string[]) =>
    content
      .filter((section) => keywords.some((keyword) => section.name.includes(keyword)))
      .reduce((total, section) => total + section.items.length, 0);

  return {
    number: Number(heading[1]),
    title: heading[2]!.trim(),
    date,
    displayDate: date.replaceAll('-', '.'),
    articleCount: count('文章', 'Article'),
    projectCount: count('项目', 'Project'),
    mediaCount: count('播客', 'Podcast'),
    sections: content,
  };
}

export function getSampleIssue(locale: string): SampleIssue {
  const fileName = `${SAMPLE_ISSUE_DATE}-weekly.md`;
  // 英文页给中文正文等于没做国际化：docs/en 有同一期的英文稿，按语言取。
  // 分界与 landing-copy 一致（只有 zh / zh-TW 用中文），这样日韩等回落语言拿到的是
  // 「英文文案 + 英文正文」，至少内部自洽，而不是英文标题配一整篇中文。
  const chinese = locale === 'zh' || locale === 'zh-TW';
  const root = chinese ? CONTENT_ROOT : path.join(CONTENT_ROOT, 'en');
  const issue = parseIssue(fs.readFileSync(path.join(root, fileName), 'utf8'), SAMPLE_ISSUE_DATE);

  // 换期时最怕「改了文件名忘了改期数」，静默渲染出第 99 期比构建失败更难查。
  if (issue.number !== SAMPLE_ISSUE_NUMBER) {
    throw new Error(
      `样例期期数不符：${fileName} 解析出 #${issue.number}，期望 #${SAMPLE_ISSUE_NUMBER}`,
    );
  }

  return issue;
}
