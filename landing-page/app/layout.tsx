import './globals.css';

export const metadata = {
  title: 'Python 潮流周刊 | Python Trending Weekly',
  description: '由 Python猫 出品的高质量技术周刊，精心筛选中英文的 400+ 信息源，为 Python 开发者提供最值得分享的文章、教程、开源项目、软件工具等内容。',
  keywords: 'Python, 周刊, 技术, 开发者, 编程, 教程, 开源项目, Python newsletter, programming, developer, tutorial, open source',
  authors: [{ name: 'Python猫', url: 'https://pythoncat.top' }],
  creator: 'Python猫',
  publisher: 'Python 潮流周刊',
  icons: {
    icon: '/logo_python_weekly.svg',
    shortcut: '/logo_python_weekly.svg',
    apple: '/logo_python_weekly.svg',
  },
  openGraph: {
    title: 'Python 潮流周刊 | Python Trending Weekly',
    description: '🐍 已助力 350+ 技术人高效成长！精选 Python 技术干货，每期 12 篇文章 + 12 个开源项目，告别信息过载',
    type: 'website',
    locale: 'zh_CN',
    alternateLocale: ['en_US', 'zh_TW'],
    siteName: 'Python 潮流周刊',
    url: 'https://weekly.pythoncat.top',
    images: [
      {
        url: '/og-image.svg',
        width: 1200,
        height: 630,
        alt: 'Python 潮流周刊 - 高质量技术内容精选',
        type: 'image/svg+xml',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@pythoncat',
    creator: '@pythoncat',
    title: 'Python 潮流周刊 | Python Trending Weekly',
    description: '🐍 已助力 350+ 技术人高效成长！精选 Python 技术干货，每期 12 篇文章 + 12 个开源项目',
    images: ['/og-image.svg'],
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
  verification: {
    google: 'your-google-verification-code',
    // 可以添加其他搜索引擎的验证码
  },
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({
  children
}: RootLayoutProps) {
  return (
    <html className="scroll-smooth" lang="zh">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}