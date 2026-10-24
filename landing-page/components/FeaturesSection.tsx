type PrinciplesCopy = {
  kicker: string;
  title: string[];
  intro: string;
  items: Array<{title: string; body: string; note: string}>;
};

export default function FeaturesSection({copy}: {copy: PrinciplesCopy}) {
  return (
    <section className="principles" aria-labelledby="principles-title">
      <div className="shell">
        <div className="section-heading">
          <p className="section-kicker">{copy.kicker}</p>
          <h2 id="principles-title">
            {copy.title[0]}
            <br />
            {copy.title[1]}
          </h2>
          <p>{copy.intro}</p>
        </div>

        <ol className="principles__list">
          {copy.items.map((principle, index) => (
            <li key={principle.title}>
              <span className="principles__number">
                {String(index + 1).padStart(2, '0')}
              </span>
              <div>
                <h3>{principle.title}</h3>
                <p>{principle.body}</p>
                <span className="principles__note">{principle.note}</span>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
