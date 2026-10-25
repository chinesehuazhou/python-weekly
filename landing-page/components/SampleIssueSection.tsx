import Image from 'next/image';
import type {SampleIssue} from '../lib/sample-issue';
import {renderInline} from '../lib/inline-markdown';
import ScrollCue from './ScrollCue';

type SampleCopy = {
  kicker: string;
  title: string;
  more: string;
  moreLink: string;
  moreUrl: string;
  backToTop: string;
  counts: {
    articles: string;
    projects: string;
    media: string;
  };
};

// 一整期的正文（标题 + 链接 + 摘要 + 配图），固定渲染第 100 期。
// 服务端组件：纯静态内容，没有任何交互，不占首屏 JS。
// 2026-10-25 用户定稿：全文不能平铺（一屏排不下，页面被拉成一米长），
// 改成固定高度的滚动窗口——旧版 landing 用的也是这个办法（max-h-96 + overflow-y）。
export default function SampleIssueSection({
  issue,
  copy,
}: {
  issue: SampleIssue;
  copy: SampleCopy;
}) {
  const counts = [
    `${issue.articleCount} ${copy.counts.articles}`,
    `${issue.projectCount} ${copy.counts.projects}`,
    `${issue.mediaCount} ${copy.counts.media}`,
  ];

  return (
    <section id="sample" className="sample">
      <div className="shell">
        <div className="section-heading section-heading--row">
          <div>
            <p className="section-kicker">{copy.kicker}</p>
            <h2 id="sample-title">{copy.title}</h2>
          </div>
          <p className="section-more">
            {copy.more}{' '}
            <a href={copy.moreUrl} target="_blank" rel="noopener noreferrer">
              {copy.moreLink}
              <span aria-hidden="true"> ↗</span>
            </a>
          </p>
        </div>

        <article className="issue">
          <header className="issue__head">
            <p className="issue__meta">
              ISSUE {issue.number} · {issue.displayDate}
            </p>
            <h3 id="sample-issue-title" className="issue__title">
              {issue.title}
            </h3>
            <p className="issue__counts">{counts.join(' · ')}</p>
          </header>

          <div className="issue__window">
            <div
              className="issue__body"
              tabIndex={0}
              role="region"
              aria-labelledby="sample-issue-title"
            >
              {issue.sections.map((section) => (
                <div key={section.name} className="issue__section">
                  <h4>{section.name}</h4>
                  <ol>
                    {section.items.map((item) => (
                      <li key={item.url}>
                        <div className="issue__item">
                          <a href={item.url} target="_blank" rel="noopener noreferrer">
                            {renderInline(item.title, item.url)}
                          </a>
                          {item.summary ? (
                            <p>{renderInline(item.summary, `${item.url}-s`)}</p>
                          ) : null}
                          {item.images.map((image) => (
                            <Image
                              key={image.src}
                              src={image.src}
                              alt={image.alt}
                              width={image.width}
                              height={image.height}
                              sizes="(max-width: 900px) 88vw, 720px"
                              className="issue__img"
                            />
                          ))}
                        </div>
                      </li>
                    ))}
                  </ol>
                </div>
              ))}
            </div>
            <ScrollCue label={copy.backToTop} />
          </div>
        </article>
      </div>
    </section>
  );
}
