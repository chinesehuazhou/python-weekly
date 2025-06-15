import './globals.css';

export const metadata = {
  title: 'Python Trending Weekly | Python Weekly Newsletter',
  description: 'A high-quality technical newsletter by PythonCat, carefully curating 400+ information sources in Chinese and English, providing Python developers with the most valuable articles, tutorials, open source projects, software tools and more.',
  keywords: 'Python, weekly, technology, developer, programming, tutorial, open source, Python newsletter, programming, developer, tutorial, open source',
  authors: [{ name: 'PythonCat', url: 'https://pythoncat.top' }],
  creator: 'PythonCat',
  publisher: 'Python Trending Weekly',
  icons: {
    icon: ['/favicon.ico', '/logo_python_weekly.svg'],
    shortcut: '/favicon.ico',
    apple: '/logo_python_weekly.svg',
  },
  openGraph: {
    title: 'Python Weekly - Curated Python Articles, Resources & Tutorials',
    description: 'Discover the latest Python libraries, tools and best practices to enhance your Python development skills',
    url: 'https://weekly.pythoncat.top',
    siteName: 'Python Trending Weekly',
    images: ['/og-image.png'],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Python Weekly - Curated Python Resources & Tutorials',
    description: 'Discover the latest Python libraries, tools and best practices to enhance your Python development skills',
    images: ['/og-image.png'],
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
  }
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({
  children
}: RootLayoutProps) {
  return (
    <html className="scroll-smooth" lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}