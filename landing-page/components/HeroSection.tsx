import type {SiteStats} from '../lib/stats';

type HeroCopy = {
  title: string[];
  tagline: string;
  description: string;
  subscribe: string;
  sample: string;
  stats: {
    issues: string;
    articles: string;
    projects: string;
    media: string;
  };
};

// 首屏只讲「这是什么」和「有多大」，不再塞一张本期卡片：
// 2026-10-25 用户定稿——卡片放这里既和下面的样例区重复，又因为最新一期是付费内容而点不进去。
export default function HeroSection({copy, stats}: {copy: HeroCopy; stats: SiteStats}) {
  const numbers = [
    {label: copy.stats.issues, value: stats.issues},
    {label: copy.stats.articles, value: stats.articles},
    {label: copy.stats.projects, value: stats.projects},
    {label: copy.stats.media, value: stats.media},
  ];

  return (
    <section className="hero">
      <div className="hero__glow" aria-hidden="true" />
      <div className="shell">
        <div className="hero__copy">
          <h1 className="hero__title">
            {copy.title[0]}
            <br />
            {copy.title[1]}
          </h1>

          <p className="hero__tagline">{copy.tagline}</p>
          <p className="hero__lede">{copy.description}</p>

          <div className="hero__actions">
            <a className="button button--primary" href="#subscription">
              {copy.subscribe}
              <span aria-hidden="true">→</span>
            </a>
            <a className="text-link" href="#sample">
              {copy.sample}
            </a>
          </div>
        </div>

        <div className="hero__stats">
          {numbers.map((item) => (
            <div key={item.label} className="hero__stat">
              <span className="hero__stat-label">{item.label}</span>
              <span className="hero__stat-value">{item.value.toLocaleString('en-US')}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
