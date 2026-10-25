import type {WhyItem} from '../lib/landing-copy';

type WhyCopy = {
  kicker: string;
  title: string[];
  items: WhyItem[];
};

// 旧站「为什么选择 Python 潮流周刊」的六条理由原样保留，只换版式（编号列表 → 三列卡片）。
// 上一版把六条压成三条抽象原则，把「内容体量」「AI+人工」这些具体事实弄丢了。
export default function WhySection({copy}: {copy: WhyCopy}) {
  return (
    <section id="why" className="principles" aria-labelledby="principles-title">
      <div className="shell">
        <div className="section-heading">
          <p className="section-kicker">{copy.kicker}</p>
          <h2 id="principles-title">
            {copy.title[0]}
            <br />
            {copy.title[1]}
          </h2>
        </div>

        <ol className="principles__list">
          {copy.items.map((item, index) => (
            <li key={item.title}>
              <span className="principles__number">
                {String(index + 1).padStart(2, '0')}
              </span>
              <h3>{item.title}</h3>
              <p>{item.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
