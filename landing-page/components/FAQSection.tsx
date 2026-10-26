'use client';

import { useState } from 'react';
import { useTranslations } from '../hooks/useTranslations';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';

interface FAQ {
  id: number;
  question: string;
  answer: string;
}

export default function FAQSection({kicker}: {kicker: string}) {
  const t = useTranslations('FAQ');
  
  // 从国际化文件中获取FAQ数据
  const faqItems = t.raw('items') as Array<{question: string; answer: string}> || [];
  const faqs: FAQ[] = faqItems.map((item, index) => ({
    id: index + 1,
    question: item.question,
    answer: item.answer
  }));
  
  // 2026-10-25 用户定稿：默认全部展开（此前只展开定价那一条，其余要逐条点）。
  const [openItems, setOpenItems] = useState<number[]>(() =>
    faqs.map((faq) => faq.id),
  );

  const toggleItem = (id: number) => {
    setOpenItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  return (
    <section id="faq" className="faq">
      <div className="shell">
        {/* 标题通栏，列表接在下面。
            2026-10-25 用户反馈：原来「标题钉在左栏、列表在右栏」的两栏布局，
            在导语被删掉后左栏只剩两个小行，宽屏下就是一片空白。 */}
        <div className="section-heading">
          <p className="section-kicker">{kicker}</p>
          <h2>{t('title')}</h2>
        </div>

        {/* FAQ 列表 */}
        <div className="faq__list">
          {faqs.map((faq) => {
            const isOpen = openItems.includes(faq.id);
            const panelId = `faq-panel-${faq.id}`;
            return (
              <div
                key={faq.id}
                className={`faq__item${isOpen ? ' is-open' : ''}`}
              >
                <button
                  type="button"
                  onClick={() => toggleItem(faq.id)}
                  className="faq__question"
                  aria-expanded={isOpen}
                  aria-controls={panelId}
                >
                  <span>{faq.question}</span>
                  {isOpen ? (
                    <FaChevronUp aria-hidden="true" />
                  ) : (
                    <FaChevronDown aria-hidden="true" />
                  )}
                </button>
                {isOpen && (
                  <div id={panelId} className="faq__answer">
                    <div 
                      className="faq__answer-copy"
                      dangerouslySetInnerHTML={{ __html: faq.answer }}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
