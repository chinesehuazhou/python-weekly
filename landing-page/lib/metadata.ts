import { Metadata } from 'next';
import { getMessages } from '../i18n';

type LocaleMetadata = {
  siteName: string;
  footerDescription: string;
  hero: {
    title: string;
    subtitle: string;
    description: string;
  };
};

// 语言到 Open Graph locale 的映射
const localeMap: Record<string, string> = {
  'zh': 'zh_CN',
  'en': 'en_US',
  'zh-TW': 'zh_TW',
};

// 生成多语言 metadata
export async function generateMetadata(locale: string): Promise<Metadata> {
  const messages = await getMessages(locale) as LocaleMetadata;
  const ogLocale = localeMap[locale] || 'zh_CN';
  
  // 获取其他语言作为 alternateLocale
  const alternateLocales = Object.values(localeMap).filter(l => l !== ogLocale);
  
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://weekly.pythoncat.top';
  const currentUrl = locale === 'zh' ? baseUrl : `${baseUrl}/${locale}`;
  
  return {
    title: messages.siteName,
    description: messages.footerDescription,
    keywords: locale === 'en' 
      ? 'Python, newsletter, programming, developer, tutorial, open source, weekly, tech'
      : 'Python, 周刊, 技术, 开发者, 编程, 教程, 开源项目, 技术周刊',
    authors: [{ name: 'Python猫', url: 'https://pythoncat.top' }],
    creator: 'Python猫',
    publisher: messages.siteName,
    alternates: {
      canonical: currentUrl,
      languages: {
        'zh': baseUrl,
        'en': `${baseUrl}/en`,
        'zh-TW': `${baseUrl}/zh-TW`,
      },
    },
    openGraph: {
      title: messages.hero.title,
      description: messages.hero.description,
      type: 'website',
      locale: ogLocale,
      alternateLocale: alternateLocales,
      siteName: messages.siteName,
      url: currentUrl,
      images: [
        {
          url: `${baseUrl}/og-image${locale === 'en' ? '-en' : ''}.png`,
          width: 1200,
          height: 630,
          alt: `${messages.siteName} - ${messages.hero.subtitle}`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      site: '@pythoncat',
      creator: '@pythoncat',
      title: messages.hero.title,
      description: messages.hero.description,
      images: [`${baseUrl}/og-image${locale === 'en' ? '-en' : ''}.png`],
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
    other: {
      'twitter:label1': locale === 'en' ? 'Reading time' : '阅读时间',
      'twitter:data1': locale === 'en' ? '5 min read' : '5分钟阅读',
      'twitter:label2': locale === 'en' ? 'Issues' : '总期数',
      'twitter:data2': '104+',
    },
  };
}

// 生成结构化数据
export function generateStructuredData(locale: string, messages: LocaleMetadata) {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://weekly.pythoncat.top';
  
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: messages.siteName,
    description: messages.footerDescription,
    url: locale === 'zh' ? baseUrl : `${baseUrl}/${locale}`,
    author: {
      '@type': 'Person',
      name: 'Python猫',
      url: 'https://pythoncat.top',
    },
    publisher: {
      '@type': 'Organization',
      name: messages.siteName,
      logo: {
        '@type': 'ImageObject',
        url: `${baseUrl}/logo_python_weekly.svg`,
      },
    },
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${baseUrl}/search?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
    inLanguage: locale === 'zh-TW' ? 'zh-Hant' : locale,
    isAccessibleForFree: true,
  };
}