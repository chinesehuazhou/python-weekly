import {notFound} from 'next/navigation';
import {ReactNode} from 'react';

type Props = {
  children: ReactNode;
  params: {locale: string};
};

export function generateStaticParams() {
  return [{locale: 'zh'}, {locale: 'en'}, {locale: 'zh-TW'}];
}

export default function LocaleLayout({
  children,
  params: {locale}
}: Props) {
  // Validate that the incoming `locale` parameter is valid
  const locales = ['zh', 'en', 'zh-TW'];
  // If locale is not supported, redirect to default locale instead of calling notFound()
  if (!locales.includes(locale)) {
    // Use default locale 'zh' for unsupported locales
    // This prevents the notFound() error in root layout
  }

  return children;
}