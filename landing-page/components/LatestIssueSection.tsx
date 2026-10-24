'use client';

import type {LatestIssue} from '../lib/latest-issue';

type LatestIssueSectionProps = {
  issue: LatestIssue;
  copy: {
    kicker: string;
    title: string;
    intro: string;
    articles: string;
    projects: string;
    cta: string;
  };
};

export default function LatestIssueSection({issue, copy}: LatestIssueSectionProps) {
  const articles = issue.items.filter((item) => !item.section.includes('项目'));
  const projects = issue.items.filter((item) => item.section.includes('项目'));

  return (
    <section className="issue-index" aria-labelledby="issue-index-title">
      <div className="shell">
        <div className="section-heading section-heading--row">
          <div>
            <p className="section-kicker">{copy.kicker}</p>
            <h2 id="issue-index-title">{copy.title}</h2>
          </div>
          <p>{copy.intro.replace('{number}', String(issue.number))}</p>
        </div>

        <div className="issue-index__columns">
          <div>
            <h3>{copy.articles}</h3>
            <ol>
              {articles.map((item, index) => (
                <li key={item.title}>
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  {item.title}
                </li>
              ))}
            </ol>
          </div>
          <div>
            <h3>{copy.projects}</h3>
            <ol>
              {projects.map((item, index) => (
                <li key={item.title}>
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  {item.title}
                </li>
              ))}
            </ol>
          </div>
        </div>

        <a
          className="button button--outline"
          href={issue.fullTextUrl}
          target="_blank"
          rel="noopener noreferrer"
        >
          {copy.cta.replace('{number}', String(issue.number))}
          <span aria-hidden="true">↗</span>
        </a>
      </div>
    </section>
  );
}
