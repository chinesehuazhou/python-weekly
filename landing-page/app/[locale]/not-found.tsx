'use client';

import {useTranslations} from '../../hooks/useTranslations';
import Link from 'next/link';

export default function NotFoundPage() {
  const t = useTranslations('NotFoundPage');
  
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">{t('title')}</h1>
        <p className="text-gray-600 mb-8">{t('description')}</p>
        <Link 
          href="/" 
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors inline-block"
        >
          {t('backHome')}
        </Link>
      </div>
    </div>
  );
}