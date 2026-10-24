import fs from 'node:fs';
import path from 'node:path';

export type IssueItem = {
  title: string;
  section: string;
};

export type LatestIssue = {
  number: number;
  title: string;
  date: string;
  displayDate: string;
  summary: string;
  articleCount: number;
  projectCount: number;
  fullTextUrl: string;
  items: IssueItem[];
};

const CONTENT_ROOT = path.resolve(process.cwd(), '../docs');
const ISSUE_FILE = /^(\d{4}-\d{2}-\d{2})-weekly\.md$/;
const BODY_ITEM = /^(?:[①-⑳]|\d+[、.])\s*(.+)$/u;

function isBodyItem(line: string, section: string): boolean {
  const item = line.match(BODY_ITEM);
  if (!item?.[1]) return false;

  // 旧版双语稿用“## 分类 / 1、标题”结构；正文里的“1、”是链接序号，
  // 而“①”只出现在新版“标题摘要”清单里，借此避开说明段落中的编号。
  return section.startsWith('## ') || /^[①-⑳]/.test(line);
}

function readIssueFile(filePath: string): LatestIssue | null {
  const markdown = fs.readFileSync(filePath, 'utf8');
  const lines = markdown.split('\n');
  const heading = lines[0]?.match(
    /^# Python (?:潮流周刊|Trending Weekly)\s*#(\d+)[：:]\s*(.+)$/,
  );
  const fileName = path.basename(filePath);
  const fileDate = fileName.match(ISSUE_FILE)?.[1];

  if (!heading || !fileDate) return null;

  let section = '';
  const items: IssueItem[] = [];

  for (const rawLine of lines) {
    const line = rawLine.trim();
    const sectionMatch = line.match(
      /^\*\*\[([^\]]+)\]\([^)]+\)\*\*$/,
    );

    if (sectionMatch?.[1]) {
      section = sectionMatch[1].trim();
      continue;
    }

    if (isBodyItem(line, section)) {
      const title = line.match(BODY_ITEM)?.[1]?.trim();
      if (!title) continue;
      items.push({
        title,
        section,
      });
    }
  }

  const countText = lines.find((line) => line.startsWith('分享了')) ?? '';
  const articleCount = Number(
    countText.match(/(\d+)\s*篇文章/)?.[1] ??
      items.filter((item) => !item.section.includes('项目')).length,
  );
  const projectCount = Number(
    countText.match(/(\d+)\s*个开源项目/)?.[1] ??
      items.filter((item) => item.section.includes('项目')).length,
  );
  const fullTextUrl =
    markdown.match(/https:\/\/xiaobot\.net\/post\/[a-z0-9-]+/)?.[0] ??
    'https://xiaobot.net/p/python_weekly';

  return {
    number: Number(heading[1]),
    title: heading[2]!.trim(),
    date: fileDate,
    displayDate: fileDate.replaceAll('-', '.'),
    summary: countText.trim(),
    articleCount,
    projectCount,
    fullTextUrl,
    items,
  };
}

export function getLatestIssue(locale: string): LatestIssue {
  const localeRoot =
    locale === 'en' ? path.join(CONTENT_ROOT, 'en') : CONTENT_ROOT;
  const fallbackRoot = path.join(CONTENT_ROOT, 'en');
  const roots = localeRoot === CONTENT_ROOT ? [localeRoot] : [localeRoot, fallbackRoot];

  for (const root of roots) {
    if (!fs.existsSync(root)) continue;

    const files = fs
      .readdirSync(root)
      .filter((name) => ISSUE_FILE.test(name))
      .sort()
      .reverse();

    for (const name of files) {
      const issue = readIssueFile(path.join(root, name));
      if (issue) return issue;
    }
  }

  throw new Error(`No weekly issue found under ${CONTENT_ROOT}`);
}
