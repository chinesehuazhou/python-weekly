'use client';

import {useEffect, useState} from 'react';
import Image from 'next/image';
import {FaTimes} from 'react-icons/fa';

type ProofCopy = {
  kicker: string;
  title: string;
  intro: string;
  caption: string;
  images: Array<{src: string; alt: string; width: number; height: number}>;
};

// 读者反馈用截图，不用改写过的引文。
// 2026-10-25 用户指出：上一版那三段「读者的话」是编的，旧站一直是放留言截图当证据。
// 截图放的是公众号留言与读者群原图，改一个字就不再是证据。
export default function SocialProofSection({copy}: {copy: ProofCopy}) {
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    if (!active) return;

    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setActive(null);
    };

    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [active]);

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
          {copy.images.map((image, index) => (
            <figure key={image.src}>
              <button
                type="button"
                className="testimonials__shot"
                onClick={() => setActive(image.src)}
                aria-label={image.alt}
              >
                <Image
                  src={image.src}
                  alt={image.alt}
                  width={image.width}
                  height={image.height}
                  sizes="(max-width: 640px) 100vw, 33vw"
                  className="testimonials__img"
                />
              </button>
              <figcaption>
                <span>{copy.caption}</span>
                <span>{String(index + 1).padStart(2, '0')}</span>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>

      {active ? (
        <div
          className="lightbox"
          role="dialog"
          aria-modal="true"
          onClick={() => setActive(null)}
        >
          <button
            type="button"
            className="lightbox__close"
            onClick={() => setActive(null)}
            aria-label="关闭"
          >
            <FaTimes aria-hidden="true" />
          </button>
          <Image
            src={active}
            alt=""
            width={1200}
            height={900}
            className="lightbox__img"
            onClick={(event) => event.stopPropagation()}
          />
        </div>
      ) : null}
    </section>
  );
}
