type TestimonialsCopy = {
  kicker: string;
  title: string;
  intro: string;
  items: Array<{quote: string; source: string; date: string}>;
};

export default function SocialProofSection({copy}: {copy: TestimonialsCopy}) {
  return (
    <section className="testimonials" aria-labelledby="testimonials-title">
      <div className="shell">
        <div className="section-heading section-heading--row">
          <div>
            <p className="section-kicker">{copy.kicker}</p>
            <h2 id="testimonials-title">{copy.title}</h2>
          </div>
          <p>{copy.intro}</p>
        </div>

        <div className="testimonials__grid">
          {copy.items.map((item, index) => (
            <figure key={item.quote}>
              <span className="testimonials__mark" aria-hidden="true">
                “
              </span>
              <blockquote>{item.quote}</blockquote>
              <figcaption>
                <span>{item.source}</span>
                <span>{item.date}</span>
              </figcaption>
              <span className="testimonials__index" aria-hidden="true">
                {String(index + 1).padStart(2, '0')}
              </span>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
