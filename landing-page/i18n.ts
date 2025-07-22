// Static export compatible i18n configuration
// 支持的语言：简体中文、英文、繁体中文、日语、韩语、法语、德语、西班牙语、俄语、意大利语、葡萄牙语
export const locales = ['zh', 'en', 'zh-TW', 'ja', 'ko', 'fr', 'de', 'es', 'ru', 'it', 'pt'] as const;
// 默认语言为英文，除非检测到中文浏览器语言
export const defaultLocale = 'en';

// Helper function to get messages for static export
export async function getMessages(locale: string) {
  const validLocale = locales.includes(locale as any) ? locale : defaultLocale;
  return (await import(`./messages/${validLocale}.json`)).default;
}