import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // A list of all locales that are supported
  locales: ['zh', 'en', 'zh-TW'],

  // Used when no locale matches
  defaultLocale: 'zh'
});

export const config = {
  // Match only internationalized pathnames
  matcher: ['/', '/(zh|en|zh-TW)/:path*']
};