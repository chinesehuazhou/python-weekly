'use client';

import { useState, useEffect, useRef } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { HiMenu, HiX, HiSun, HiMoon, HiChevronDown, HiGlobe } from 'react-icons/hi';
import { FaGlobeAmericas } from 'react-icons/fa';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter, usePathname } from 'next/navigation';

// 语言选项配置
const languageOptions = [
  { code: 'zh', name: '简体中文', flag: '🇨🇳' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'zh-TW', name: '繁體中文', flag: '🇨🇳' },
];

export default function Header() {
  const t = useTranslations();
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isLanguageDropdownOpen, setIsLanguageDropdownOpen] = useState(false);
  const languageDropdownRef = useRef<HTMLDivElement>(null);

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
    // Remove current locale from pathname to get the base path
    let basePath = pathname;
    
    // Handle different pathname patterns
    if (pathname === '/') {
      basePath = '';
    } else if (pathname === `/${locale}`) {
      basePath = '';
    } else if (pathname.startsWith(`/${locale}/`)) {
      basePath = pathname.substring(`/${locale}`.length);
    } else if (pathname.startsWith('/zh/') || pathname.startsWith('/en/') || pathname.startsWith('/zh-TW/')) {
      // Handle cases where pathname already has a locale but it's different from current
      const segments = pathname.split('/');
      if (segments[1] === 'zh' || segments[1] === 'en' || segments[1] === 'zh-TW') {
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

  const currentLanguage = languageOptions.find(lang => lang.code === locale) || languageOptions[0];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href={`/${locale}`} className="flex items-center space-x-2">
            <div className="w-12 h-12 rounded-lg overflow-hidden flex items-center justify-center">
              <Image
                src="/python_cat.jpg"
                alt="Python Weekly Logo"
                width={48}
                height={48}
                className="object-cover rounded-lg"
              />
            </div>
            <span className="font-bold text-xl text-gray-900 dark:text-white">
              {t('siteName')}
            </span>
          </Link>

          {/* Desktop Controls */}
          <div className="hidden md:flex items-center space-x-3">
            {/* Language Dropdown */}
            <div className="relative" ref={languageDropdownRef}>
              <button
                onClick={() => setIsLanguageDropdownOpen(!isLanguageDropdownOpen)}
                className="flex items-center p-2 text-gray-700 dark:text-gray-300 hover:text-python-blue dark:hover:text-python-blue transition-colors duration-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                aria-label="Select language"
              >
                <FaGlobeAmericas className="w-5 h-5 text-blue-500" />
                <span className="ml-1 text-sm font-medium">{currentLanguage.name}</span>
                <HiChevronDown className={`w-3 h-3 ml-1 transition-transform duration-200 ${isLanguageDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {isLanguageDropdownOpen && (
                <div className="absolute right-0 mt-2 w-40 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
                  {languageOptions.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => switchLanguage(lang.code)}
                      className={`w-full flex items-center px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 ${
                        locale === lang.code 
                          ? 'text-python-blue bg-blue-50 dark:bg-blue-900/20' 
                          : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <span className="mr-2">{lang.flag}</span>
                      <span>{lang.name}</span>
                      {locale === lang.code && (
                        <span className="ml-auto text-python-blue">✓</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 text-gray-700 dark:text-gray-300 hover:text-python-blue dark:hover:text-python-blue transition-colors duration-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              aria-label="Toggle theme"
            >
              {isDarkMode ? <HiSun className="w-5 h-5 text-yellow-500" /> : <HiMoon className="w-5 h-5 text-blue-400" />}
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 text-gray-700 dark:text-gray-300"
            aria-label="Toggle menu"
          >
            {isMenuOpen ? <HiX className="w-6 h-6" /> : <HiMenu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200 dark:border-gray-700">
            <nav className="flex flex-col space-y-4">
              <div className="flex items-center justify-center space-x-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="relative">
                  <button
                    onClick={() => setIsLanguageDropdownOpen(!isLanguageDropdownOpen)}
                    className="flex items-center text-gray-700 dark:text-gray-300 hover:text-python-blue dark:hover:text-python-blue transition-colors duration-200 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <HiGlobe className="w-4 h-4 mr-1 text-blue-500" />
                    <span className="text-sm font-medium">{currentLanguage.name}</span>
                    <HiChevronDown className={`w-3 h-3 ml-1 transition-transform duration-200 ${isLanguageDropdownOpen ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {isLanguageDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-40 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
                      {languageOptions.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => switchLanguage(lang.code)}
                          className={`w-full flex items-center px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 ${
                            locale === lang.code 
                              ? 'text-python-blue bg-blue-50 dark:bg-blue-900/20' 
                              : 'text-gray-700 dark:text-gray-300'
                          }`}
                        >
                          <span className="mr-2">{lang.flag}</span>
                          <span>{lang.name}</span>
                          {locale === lang.code && (
                            <span className="ml-auto text-python-blue">✓</span>
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                
                <button
                  onClick={toggleTheme}
                  className="text-gray-700 dark:text-gray-300 hover:text-python-blue dark:hover:text-python-blue transition-colors duration-200 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  {isDarkMode ? <HiSun className="w-5 h-5 text-yellow-500" /> : <HiMoon className="w-5 h-5 text-blue-400" />}
                </button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}