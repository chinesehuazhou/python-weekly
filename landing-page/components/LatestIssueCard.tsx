import type { LatestIssue } from '../lib/latest-issue';

type LatestIssueCardProps = {
  issue: LatestIssue;
  labels: {
    latest: string;
    articles: string;
    projects: string;
    readFull: string;
  };
};

export default function LatestIssueCard({
  issue,
  labels,
}: LatestIssueCardProps) {
  const articles = issue.items.filter((item) => !item.section.includes('项目'));
  const projects = issue.items.filter((item) => item.section.includes('项目'));
  const preview = [...articles.slice(0, 3), ...projects.slice(0, 2)];

  return (
    <article className="issue-card">
      <div className="issue-card__top">
        <span className="issue-card__label">{labels.latest}</span>
        <span className="issue-card__date">{issue.displayDate}</span>
      </div>

      <p className="issue-card__number">ISSUE {issue.number}</p>
      <h2 className="issue-card__title">{issue.title}</h2>

      <div className="issue-card__counts">
        <span>
          <strong>{issue.articleCount}</strong> {labels.articles}
        </span>
        <span>
          <strong>{issue.projectCount}</strong> {labels.projects}
        </span>
      </div>

      <ol className="issue-card__items">
        {preview.map((item, index) => (
          <li key={`${item.section}-${item.title}`}>
            <span className="issue-card__index">
              {String(index + 1).padStart(2, '0')}
            </span>
            <span>
              <span className="issue-card__section">
                {item.section.replace(/^[^\p{L}]+/u, '').trim()}
              </span>
              {item.title}
            </span>
          </li>
        ))}
      </ol>

      <a
        className="issue-card__link"
        href={issue.fullTextUrl}
        target="_blank"
        rel="noopener noreferrer"
      >
        {labels.readFull}
        <span aria-hidden="true">↗</span>
      </a>
    </article>
  );
}
