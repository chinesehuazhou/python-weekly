import { getRequestConfig } from 'next-intl/server';
import { IntlErrorCode } from 'next-intl';
import { notFound } from 'next/navigation';

// Can be imported from a shared config
const locales = ['zh', 'en', 'zh-TW'];

export default getRequestConfig(async ({ requestLocale }) => {
  // This typically corresponds to the `[locale]` segment
  const locale = await requestLocale;
  
  // Validate that the incoming `locale` parameter is valid
  // If locale is not supported, use default locale 'zh'
  const validLocale = (!locale || !locales.includes(locale as any)) ? 'zh' : locale;

  return {
    locale: validLocale,
    messages: (await import(`../messages/${validLocale}.json`)).default,
    onError(error) {
      if (error.code === IntlErrorCode.MISSING_MESSAGE) {
        // Silently ignore missing translation keys - no console output
        return;
      } else {
        console.error(error);
      }
    },
    getMessageFallback({ namespace, key, error }) {
      const path = [namespace, key].filter((part) => part != null).join('.');
      if (error.code === IntlErrorCode.MISSING_MESSAGE) {
        return path; // Return the key itself for missing translations
      } else {
        return `Error: ${path}`;
      }
    }
  };
});