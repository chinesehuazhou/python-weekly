'use client';

import { useTranslations, useLocale } from 'next-intl';
import Link from 'next/link';
import { HiArrowRight, HiDocumentText, HiBookOpen, HiCode, HiCalendar, HiChevronRight } from 'react-icons/hi';
import { motion } from 'framer-motion';
import { useState, useEffect, useCallback, memo } from 'react';

// 数字动画Hook - 优化性能
function useAnimatedCounter(end: number, duration: number = 2000, delay: number = 0) {
  const [count, setCount] = useState(0);
  const [hasStarted, setHasStarted] = useState(false);

  const animate = useCallback((currentTime: number, startTime: number) => {
    const progress = Math.min((currentTime - startTime) / duration, 1);
    
    // 使用easeOutCubic缓动函数
    const easeOutCubic = 1 - Math.pow(1 - progress, 3);
    setCount(Math.floor(end * easeOutCubic));
    
    if (progress < 1) {
      requestAnimationFrame((time) => animate(time, startTime));
    } else {
      setCount(end);
    }
  }, [end, duration]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setHasStarted(true);
      requestAnimationFrame((startTime) => animate(startTime, startTime));
    }, delay);

    return () => clearTimeout(timer);
  }, [animate, delay]);

  return count;
}

function HeroSection() {
  const t = useTranslations();
  const locale = useLocale();

  const stats = [
    {
      icon: HiDocumentText,
      value: 104,
      label: t('hero.stats.issues'),
    },
    {
      icon: HiBookOpen,
      value: 1261,
      label: t('hero.stats.articles'),
    },
    {
      icon: HiCode,
      value: 1182,
      label: t('hero.stats.projects'),
    },
  ];

  const additionalStats = [
    {
      value: 117,
      label: t('hero.stats.audioVideo'),
    },
    {
      value: 51,
      label: t('hero.stats.hotTopics'),
    },
    {
      value: 98,
      label: t('hero.stats.books'),
    },
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-100/80 via-blue-100/60 to-indigo-100/70 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-10 w-20 h-20 bg-python-blue rounded-full animate-bounce-gentle"></div>
        <div className="absolute top-32 right-20 w-16 h-16 bg-deep-green rounded-full animate-bounce-gentle" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-20 left-20 w-12 h-12 bg-accent-orange rounded-full animate-bounce-gentle" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-32 right-32 w-24 h-24 bg-python-blue rounded-full animate-bounce-gentle" style={{animationDelay: '0.5s'}}></div>
      </div>

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-python-blue/5 to-deep-green/5 animate-gradient"></div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-8"
        >
          {/* Main Title */}
          <div className="space-y-4">
            <motion.h1 
              className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <span className="bg-gradient-to-r from-python-blue to-deep-green bg-clip-text text-transparent">
                {t('hero.title')}
              </span>
            </motion.h1>
            
            <motion.p 
              className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 font-medium"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              {t('hero.subtitle')}
            </motion.p>
          </div>

          {/* Description */}
          <motion.p 
            className="max-w-3xl mx-auto text-lg text-gray-700 dark:text-gray-300 leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            {t('hero.description')}
          </motion.p>

          {/* CTA Buttons */}
          <motion.div 
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <a
              href="#subscription"
              className="group bg-gradient-to-r from-python-blue to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl flex items-center space-x-2 btn-hover"
            >
              <span>{t('hero.cta.subscribe')}</span>
              <HiChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
            </a>
            
            <a
              href="#latest-issue"
              className="group border-2 border-python-blue text-python-blue hover:bg-python-blue hover:text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl flex items-center space-x-2 btn-hover"
            >
              <span>{t('hero.cta.examples')}</span>
              <HiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
            </a>
          </motion.div>

          {/* Stats - Subtle decorative elements */}
          <motion.div 
            className="pt-16 space-y-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.0 }}
          >
            {/* Main Stats - Minimalist design as supporting elements */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto">
              {stats.map((stat, index) => {
                const Icon = stat.icon;
                const animatedValue = useAnimatedCounter(stat.value, 2000, 1200 + index * 100);
                
                return (
                  <motion.div
                    key={index}
                    className="group relative"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 1.2 + index * 0.1 }}
                    whileHover={{ y: -8, scale: 1.02 }}
                  >
                    {/* Subtle background with hover effects */}
                    <div className="relative p-6 text-center backdrop-blur-md rounded-2xl border shadow-lg transition-all duration-500 transform bg-white/40 dark:bg-gray-800/40 border-white/20 dark:border-gray-700/20 shadow-black/5 dark:shadow-black/10 group-hover:bg-white/60 dark:group-hover:bg-gray-800/60 group-hover:shadow-xl group-hover:shadow-python-blue/10 dark:group-hover:shadow-python-blue/20 group-hover:border-white/40 dark:group-hover:border-gray-600/40">
                      
                      {/* Simple icon */}
                      <div className="mb-4">
                        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl transition-all duration-500 bg-python-blue/10 group-hover:bg-python-blue/20 group-hover:scale-110 group-hover:rotate-3">
                          <Icon className="w-6 h-6 transition-colors duration-300 text-python-blue/70 group-hover:text-python-blue" />
                        </div>
                      </div>
                      
                      {/* Understated text with animation */}
                      <div className="space-y-1">
                        <motion.div 
                          className="text-2xl font-light transition-colors duration-300 text-gray-800 dark:text-gray-200 group-hover:text-python-blue dark:group-hover:text-python-blue/90"
                          key={animatedValue}
                          initial={{ scale: 1.1 }}
                          animate={{ scale: 1 }}
                          transition={{ duration: 0.2 }}
                        >
                          {animatedValue.toLocaleString()}
                        </motion.div>
                        <div className="text-sm font-medium transition-colors duration-300 text-gray-600 dark:text-gray-400 group-hover:text-python-blue/80 dark:group-hover:text-python-blue/70">
                          {stat.label}
                        </div>
                      </div>
                      
                      {/* Glow effect */}
                      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-python-blue/5 to-deep-green/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"></div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
            
            {/* Additional Stats - Minimalist pills */}
            <motion.div 
              className="flex flex-wrap justify-center gap-4 max-w-2xl mx-auto"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.6 }}
            >
              {additionalStats.map((stat, index) => {
                const animatedValue = useAnimatedCounter(stat.value, 1800, 1600 + index * 150);
                
                return (
                  <motion.div
                    key={index}
                    className="group px-6 py-3 backdrop-blur-md rounded-full border transition-all duration-500 shadow-md bg-white/30 dark:bg-gray-800/30 border-white/20 dark:border-gray-700/20 hover:bg-white/50 dark:hover:bg-gray-800/50 hover:border-white/40 dark:hover:border-gray-600/40 shadow-black/5 dark:shadow-black/10 hover:shadow-lg hover:shadow-python-blue/10 dark:hover:shadow-python-blue/20"
                    whileHover={{ scale: 1.08, y: -4 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  >
                    <div className="flex items-center space-x-3">
                      <motion.span 
                        className="text-lg font-semibold transition-colors duration-300 text-gray-800 dark:text-gray-200 group-hover:text-python-blue dark:group-hover:text-python-blue/90"
                        key={animatedValue}
                        initial={{ scale: 1.1 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.2 }}
                      >
                        {animatedValue.toLocaleString()}
                      </motion.span>
                      <span className="text-sm font-medium transition-colors duration-300 text-gray-600 dark:text-gray-400 group-hover:text-python-blue/80 dark:group-hover:text-python-blue/70">
                        {stat.label}
                      </span>
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll Indicator */}

    </section>
  );
}

// 使用 React.memo 优化重渲染
export default memo(HeroSection);