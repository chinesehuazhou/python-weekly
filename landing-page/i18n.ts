import {notFound} from 'next/navigation';
import {getRequestConfig} from 'next-intl/server';

// Can be imported from a shared config
const locales = ['zh', 'en', 'zh-TW'];

export default getRequestConfig(async ({locale}) => {
  // Validate that the incoming `locale` parameter is valid
  // If locale is not supported, use default locale 'zh'
  const validLocale = locales.includes(locale as any) ? locale : 'zh';

  return {
    messages: (await import(`./messages/${validLocale}.json`)).default
  };
});