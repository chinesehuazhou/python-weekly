'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    // 检查保存的语言偏好
    const savedLocale = document.cookie
      .split('; ')
      .find(row => row.startsWith('NEXT_LOCALE='))
      ?.split('=')[1];

    if (savedLocale && ['zh', 'en', 'zh-TW'].includes(savedLocale)) {
      router.replace(`/${savedLocale}`);
      return;
    }

    // 检测浏览器语言
    const browserLang = navigator.language.toLowerCase();
    let detectedLocale = 'en'; // 默认英文

    if (browserLang.startsWith('zh')) {
      if (browserLang.includes('tw') || browserLang.includes('hk') || browserLang.includes('mo')) {
        detectedLocale = 'zh-TW';
      } else {
        detectedLocale = 'zh';
      }
    } else if (browserLang.startsWith('en')) {
      detectedLocale = 'en';
    }

    // 保存检测到的语言偏好
    document.cookie = `NEXT_LOCALE=${detectedLocale}; path=/; max-age=${30 * 24 * 60 * 60}; SameSite=Lax`;
    
    router.replace(`/${detectedLocale}`);
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">正在跳转...</p>
      </div>
    </div>
  );
}