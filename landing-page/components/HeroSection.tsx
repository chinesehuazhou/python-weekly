import type { LatestIssue } from '../lib/latest-issue';
import LatestIssueCard from './LatestIssueCard';

type HeroCopy = {
  eyebrow: string;
  title: string[];
  lede: string;
  subscribe: string;
  preview: string;
  proof: string[][];
};

type IssueLabels = {
  latest: string;
  articles: string;
  projects: string;
  readFull: string;
};

type HeroSectionProps = {
  issue: LatestIssue;
  copy: HeroCopy;
  issueLabels: IssueLabels;
};

export default function HeroSection({
  issue,
  copy,
  issueLabels,
}: HeroSectionProps) {
  const proof = copy.proof.map(([label, value], index) => ({
    label,
    value: index === 0 && !value ? String(issue.number) : value,
  }));

  return (
    <section className="hero">
      <div className="hero__glow" aria-hidden="true" />
      <div className="shell hero__grid">
        <div className="hero__copy">
          <p className="hero__eyebrow">
            <span className="hero__pulse" aria-hidden="true" />
            {copy.eyebrow}
          </p>

          <h1 className="hero__title">
            {copy.title[0]}
            <br />
            {copy.title[1]}
          </h1>

          <p className="hero__lede">{copy.lede}</p>

          <div className="hero__actions">
            <a className="button button--primary" href="#subscription">
              {copy.subscribe}
              <span aria-hidden="true">→</span>
            </a>
            <a className="text-link" href={`#issue-${issue.number}`}>
              {copy.preview}
            </a>
          </div>

          <dl className="hero__proof">
            {proof.map((item) => (
              <div key={item.label}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div id={`issue-${issue.number}`} className="hero__issue">
          <LatestIssueCard
            issue={issue}
            labels={issueLabels}
          />
        </div>
      </div>
    </section>
  );
}
