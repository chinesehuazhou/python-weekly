import {getRequestConfig} from 'next-intl/server';

// Static export compatible i18n configuration
export const locales = ['zh', 'en', 'zh-TW'];
export const defaultLocale = 'en';

// Helper function to get messages for static export
export async function getMessages(locale: string) {
  const validLocale = locales.includes(locale) ? locale : defaultLocale;
  return (await import(`./messages/${validLocale}.json`)).default;
}

export default getRequestConfig(async ({locale}) => {
  return {
    messages: (await import(`./messages/${locale}.json`)).default,
    timeZone: 'Asia/Shanghai'
  };
});