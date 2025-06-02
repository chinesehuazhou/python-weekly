import './globals.css';

export const metadata = {
  title: 'Python 潮流周刊 | Python Trending Weekly',
  description: '由 Python猫 出品的高质量技术周刊，精心筛选中英文的 400+ 信息源，为 Python 开发者提供最值得分享的文章、教程、开源项目、软件工具等内容。',
  keywords: 'Python, 周刊, 技术, 开发者, 编程, 教程, 开源项目',
  authors: [{ name: 'Python猫' }],
  icons: {
    icon: '/logo_python_weekly.svg',
    shortcut: '/logo_python_weekly.svg',
    apple: '/logo_python_weekly.svg',
  },
  openGraph: {
    title: 'Python 潮流周刊 | Python Trending Weekly',
    description: '精选 Python 技术内容，助力开发者成长',
    type: 'website',
    locale: 'zh_CN',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Python 潮流周刊 | Python Trending Weekly',
    description: '精选 Python 技术内容，助力开发者成长',
  },
  robots: {
    index: true,
    follow: true,
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