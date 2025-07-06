'use client';

import { useState } from 'react';
import { useTranslations } from '../hooks/useTranslations';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';

interface FAQ {
  id: number;
  question: string;
  answer: string;
}

export default function FAQSection() {
  const t = useTranslations('FAQ');
  
  // 从国际化文件中获取FAQ数据
  const faqItems = t.raw('items') as Array<{question: string; answer: string}> || [];
  const faqs: FAQ[] = faqItems.map((item, index) => ({
    id: index + 1,
    question: item.question,
    answer: item.answer
  }));
  
  // 默认展开所有FAQ项目
  const [openItems, setOpenItems] = useState<number[]>(() => 
    faqs.map(faq => faq.id)
  );

  const toggleItem = (id: number) => {
    setOpenItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  return (
    <section id="faq" className="py-16 bg-gradient-to-br from-gray-50/70 via-slate-100/40 to-blue-50/60 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 标题 */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            {t('title')}
          </h2>
        </div>

        {/* FAQ 列表 */}
        <div className="space-y-4">
          {faqs.map((faq) => {
            const isOpen = openItems.includes(faq.id);
            return (
              <div
                key={faq.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
              >
                <button
                  onClick={() => toggleItem(faq.id)}
                  className="w-full px-6 py-4 text-left bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 flex items-center justify-between"
                >
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white pr-4">
                    {faq.question}
                  </h3>
                  <div className="flex-shrink-0">
                    {isOpen ? (
                      <FaChevronUp className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                    ) : (
                      <FaChevronDown className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                    )}
                  </div>
                </button>
                {isOpen && (
                  <div className="px-6 py-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
                    <div 
                      className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line"
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