'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { FaTimes } from 'react-icons/fa';

export default function SocialProofSection() {
  const t = useTranslations('SocialProof');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const testimonialImages = [
    {
      id: 1,
      src: "https://img.pythoncat.top/2024-weekly-comment-2.png",
      alt: "Python潮流周刊的用户评论1"
    },
    {
      id: 2,
      src: "https://img.pythoncat.top/2024-weekly-comment-4.png",
      alt: "Python潮流周刊的用户评论2"
    },
    {
      id: 3,
      src: "https://img.pythoncat.top/2024-weekly-comment-1.png",
      alt: "Python潮流周刊的用户评论3"
    }
  ];

  return (
    <section className="py-16 bg-gradient-to-br from-blue-100/60 via-slate-100/70 to-gray-100/90 dark:bg-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 标题 */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            {t('title')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-100 max-w-3xl mx-auto">
            {t('subtitle')}
          </p>
        </div>



        {/* 用户评价 */}
        <div className="grid md:grid-cols-3 gap-8">
          {testimonialImages.map((image) => (
            <div
              key={image.id}
              className="group relative bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-800 dark:to-gray-700 rounded-xl p-1 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
            >
              <div className="bg-white dark:bg-gray-800 rounded-lg p-3 h-full">
                <img
                  src={image.src}
                  alt={image.alt}
                  className="w-full h-auto rounded-lg border-2 border-gray-100 dark:border-gray-600 shadow-md group-hover:border-blue-200 dark:group-hover:border-blue-400 transition-colors duration-300 cursor-pointer"
                  onClick={() => setSelectedImage(image.src)}
                />
              </div>
              {/* 装饰性渐变边框 */}
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 opacity-0 group-hover:opacity-20 transition-opacity duration-500 pointer-events-none"></div>
            </div>
          ))}
        </div>


      </div>

      {/* 图片放大模态框 */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl max-h-full">
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 transition-colors"
            >
              <FaTimes size={32} />
            </button>
            <img
              src={selectedImage}
              alt="放大查看"
              className="max-w-full max-h-full object-contain rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </section>
  );
}