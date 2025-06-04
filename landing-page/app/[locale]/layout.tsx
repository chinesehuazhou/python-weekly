import React from 'react';
import {NextIntlClientProvider} from 'next-intl';
import {setRequestLocale} from 'next-intl/server';
import {notFound} from 'next/navigation';
import {locales} from '../../i18n';
import {generateMetadata as generateLocalizedMetadata, generateStructuredData} from '../../lib/metadata';
import Script from 'next/script';

// 为静态导出生成所有语言参数
export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

// 生成多语言 metadata
export async function generateMetadata({ params }: { params: Promise<{locale: string}> }) {
  const { locale } = await params;
  return generateLocalizedMetadata(locale);
}

type Props = {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
};

export default async function LocaleLayout({
  children,
  params
}: Props) {
  const { locale } = await params;
  
  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale as any)) {
    notFound();
  }

  // Enable static rendering
  setRequestLocale(locale);

  let messages;
  try {
    messages = (await import(`../../messages/${locale}.json`)).default;
  } catch (error) {
    console.error(`Failed to load messages for locale ${locale}:`, error);
    messages = {}; // Provide an empty object as fallback
  }

  // 生成结构化数据
  const structuredData = generateStructuredData(locale, messages);

  return (
    <>
      {/* 结构化数据 */}
      <Script
        id="structured-data"
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData),
        }}
      />
      
      <NextIntlClientProvider locale={locale} messages={messages} timeZone="Asia/Shanghai">
        {children}
      </NextIntlClientProvider>
    </>
  );
}