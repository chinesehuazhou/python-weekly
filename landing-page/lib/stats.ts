import fs from 'node:fs';
import path from 'node:path';

export type SiteStats = {
  issues: number;
  articles: number;
  projects: number;
  media: number;
};

// public/stats.json 由发刊流程随每期一起更新（见 git log：与「add weekly NNN」同提交），
// 所以首页只读它，不自己去数 docs/ —— 数一遍全量正文既慢，又和发刊时算的口径可能不一致。
export function getSiteStats(): SiteStats {
  const file = path.join(process.cwd(), 'public', 'stats.json');
  const raw = JSON.parse(fs.readFileSync(file, 'utf8')) as Record<string, number>;

  return {
    issues: raw.total_issues ?? 0,
    articles: raw.total_articles ?? 0,
    projects: raw.total_projects ?? 0,
    media: raw.total_audio_video ?? 0,
  };
}
