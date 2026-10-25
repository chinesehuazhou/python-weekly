'use client';

import { useState, useEffect, useRef } from 'react';
import { useTranslations, useLocale } from '../hooks/useTranslations';
import { HiSun, HiMoon, HiChevronDown } from 'react-icons/hi';
import { FaGlobeAmericas } from 'react-icons/fa';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';

// 语言选项配置
const languageOptions = [
  { code: 'zh', name: '简体中文', flag: '🇨🇳' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'zh-TW', name: '繁體中文', flag: '🇨🇳' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  { code: 'pt', name: 'Português', flag: '🇵🇹' },
];

type HeaderProps = {
  navLabels: {
    why: string;
    pricing: string;
    faq: string;
  };
};

export default function Header({navLabels}: HeaderProps) {
  const t = useTranslations();
  const locale = useLocale();
  const pathname = usePathname();

  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isLanguageDropdownOpen, setIsLanguageDropdownOpen] = useState(false);
  const languageDropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    document.documentElement.lang = locale === 'zh-TW' ? 'zh-Hant' : locale;
  }, [locale]);

  useEffect(() => {
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  // 点击外部关闭语言下拉菜单
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (languageDropdownRef.current && !languageDropdownRef.current.contains(event.target as Node)) {
        setIsLanguageDropdownOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    
    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const switchLanguage = (newLocale: string) => {
    // 保存用户语言偏好到 cookie (1个月)
    document.cookie = `NEXT_LOCALE=${newLocale}; path=/; max-age=${30 * 24 * 60 * 60}; SameSite=Lax`;
    
    // Remove current locale from pathname to get the base path
    const currentPath = pathname || '/';
    let basePath = currentPath;
    
    // Handle different pathname patterns
    if (currentPath === '/') {
      basePath = '';
    } else if (currentPath === `/${locale}`) {
      basePath = '';
    } else if (currentPath.startsWith(`/${locale}/`)) {
      basePath = currentPath.substring(`/${locale}`.length);
    } else {
      // Handle cases where pathname already has a locale but it's different from current
      const segments = currentPath.split('/');
      const supportedLocales = ['zh', 'en', 'zh-TW', 'ja', 'ko', 'fr', 'de', 'es', 'ru', 'it', 'pt'];
      if (segments[1] && supportedLocales.includes(segments[1])) {
        basePath = '/' + segments.slice(2).join('/');
        if (basePath === '/') basePath = '';
      }
    }
    
    // Construct new path
    const newPath = `/${newLocale}${basePath}`;
    setIsLanguageDropdownOpen(false);
    
    // Use window.location.href for immediate language switch with page refresh
    window.location.href = newPath;
  };

  const currentLanguage = languageOptions.find(lang => lang.code === locale) ?? languageOptions[0]!;

  return (
    <header className="site-header">
      <div className="shell site-header__inner">
        <div className="site-header__bar">
          {/* Logo */}
          <Link href={`/${locale}`} className="site-header__brand">
            <div className="site-header__logo">
              <Image
                src="/logo_python_weekly.svg"
                alt="Python Weekly Logo"
                width={48}
                height={48}
                className="object-cover rounded-lg"
                priority
                unoptimized
              />
            </div>
            <span className="site-header__name">
              {t('siteName')}
            </span>
          </Link>

          <nav className="site-header__nav" aria-label="Primary navigation">
            <a href="#why">{navLabels.why}</a>
            <a href="#subscription">{navLabels.pricing}</a>
            <a href="#faq">{navLabels.faq}</a>
          </nav>

          {/* Controls */}
          <div className="site-header__controls">
            {/* Language Dropdown */}
            <div className="site-header__dropdown" ref={languageDropdownRef}>
              <button
                onClick={() => setIsLanguageDropdownOpen(!isLanguageDropdownOpen)}
                className="site-header__control"
                aria-label="Select language"
              >
                <FaGlobeAmericas className="w-5 h-5 text-blue-500" />
                <span className="site-header__locale">{currentLanguage?.name ?? '简体中文'}</span>
                <HiChevronDown className={`site-header__chevron ${isLanguageDropdownOpen ? 'is-open' : ''}`} />
              </button>
              
              {isLanguageDropdownOpen && (
                <div className="site-header__menu">
                  {languageOptions.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => switchLanguage(lang.code)}
                      className={`site-header__menu-item ${
                        locale === lang.code 
                          ? 'is-current'
                          : ''
                      }`}
                    >
                      <span className="site-header__flag">{lang.flag}</span>
                      <span>{lang.name}</span>
                      {locale === lang.code && (
                        <span className="site-header__check">✓</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="site-header__control"
              aria-label="Toggle theme"
            >
              {isDarkMode ? <HiSun className="w-5 h-5 text-yellow-500" /> : <HiMoon className="w-5 h-5 text-blue-400" />}
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
