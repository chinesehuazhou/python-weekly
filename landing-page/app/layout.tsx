import {NextIntlClientProvider} from 'next-intl';
import {getMessages} from 'next-intl/server';
import './globals.css';

export async function generateMetadata({
  params: { locale }
}: {
  params: { locale: string }
}) {
  const messages = await getMessages();
  const t = (key: string) => {
    const keys = key.split('.');
    let value: any = messages;
    for (const k of keys) {
      value = value?.[k];
    }
    return value || key;
  };

  const isZh = locale === 'zh';
  const title = isZh ? 'Python 潮流周刊 | Python Trending Weekly' : 'Python Trending Weekly | Python 潮流周刊';
  const description = isZh 
    ? '由 Python猫 出品的高质量技术周刊，精心筛选中英文的 400+ 信息源，为 Python 开发者提供最值得分享的文章、教程、开源项目、软件工具等内容。'
    : 'A high-quality tech newsletter by Python Cat, carefully curating from 400+ Chinese and English sources to provide Python developers with the most valuable articles, tutorials, open source projects, and tools.';

  return {
    metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://pythoncat.top'),
    title,
    description,
    keywords: isZh ? 'Python, 周刊, 技术, 开发者, 编程, 教程, 开源项目' : 'Python, newsletter, technology, developers, programming, tutorials, open source projects',
    authors: [{ name: 'Python猫' }],
    openGraph: {
      title,
      description: isZh ? '精选 Python 技术内容，助力开发者成长' : 'Curated Python technical content to help developers grow',
      type: 'website',
      locale: isZh ? 'zh_CN' : 'en_US',
      alternateLocale: isZh ? 'en_US' : 'zh_CN',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description: isZh ? '精选 Python 技术内容，助力开发者成长' : 'Curated Python technical content to help developers grow',
    },
    robots: {
      index: true,
      follow: true,
    },
  };
}

export default async function RootLayout({
  children,
  params: {locale}
}: {
  children: React.ReactNode;
  params: {locale: string};
}) {
  const messages = await getMessages();

  return (
    <html lang={locale} className="scroll-smooth">
      <body className="font-sans antialiased">
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}