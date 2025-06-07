'use client';

import { useTranslations } from '../hooks/useTranslations';
import { HiArrowRight, HiDocumentText, HiBookOpen, HiCode } from 'react-icons/hi';
import { motion } from 'framer-motion';
import { useState, useEffect, useCallback, memo } from 'react';

// 数字动画Hook - 优化性能
function useAnimatedCounter(end: number, duration: number = 2000, delay: number = 0) {
  const [count, setCount] = useState(0);

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
      requestAnimationFrame((startTime) => animate(startTime, startTime));
    }, delay);

    return () => clearTimeout(timer);
  }, [animate, delay]);

  return count;
}

function HeroSection() {
  const t = useTranslations();

  // 从stats.json文件读取统计数据
  const [statsData, setStatsData] = useState({
    total_issues: 104,
    total_articles: 1261,
    total_projects: 1182,
    total_audio_video: 117,
    total_hot_topics: 51,
    total_books: 98
  });

  useEffect(() => {
    // 尝试从stats.json文件加载统计数据
    fetch('/stats.json')
      .then(response => response.json())
      .then(data => setStatsData(data))
      .catch(error => {
        console.log('Using default stats data:', error);
        // 如果加载失败，使用默认值
      });
  }, []);

  const stats = [
    {
      icon: HiDocumentText,
      value: statsData.total_issues,
      label: t('hero.stats.issues'),
    },
    {
      icon: HiBookOpen,
      value: statsData.total_articles,
      label: t('hero.stats.articles'),
    },
    {
      icon: HiCode,
      value: statsData.total_projects,
      label: t('hero.stats.projects'),
    },
  ];

  const additionalStats = [
    {
      value: statsData.total_audio_video,
      label: t('hero.stats.audioVideo'),
    },
    {
      value: statsData.total_hot_topics,
      label: t('hero.stats.hotTopics'),
    },
    {
      value: statsData.total_books,
      label: t('hero.stats.books'),
    },
  ];

  // 为主要统计数据创建动画计数器
  const animatedValue1 = useAnimatedCounter(stats[0]?.value || 0, 2000, 1200);
  const animatedValue2 = useAnimatedCounter(stats[1]?.value || 0, 2000, 1300);
  const animatedValue3 = useAnimatedCounter(stats[2]?.value || 0, 2000, 1400);

  // 为附加统计数据创建动画计数器
  const animatedAdditionalValue1 = useAnimatedCounter(additionalStats[0]?.value || 0, 1800, 1600);
  const animatedAdditionalValue2 = useAnimatedCounter(additionalStats[1]?.value || 0, 1800, 1750);
  const animatedAdditionalValue3 = useAnimatedCounter(additionalStats[2]?.value || 0, 1800, 1900);

  const animatedStats = stats.map((stat, index) => ({
    ...stat,
    animatedValue: [animatedValue1, animatedValue2, animatedValue3][index] || 0
  }));

  const animatedAdditionalStats = additionalStats.map((stat, index) => ({
    ...stat,
    animatedValue: [animatedAdditionalValue1, animatedAdditionalValue2, animatedAdditionalValue3][index] || 0
  }));

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-100/80 via-blue-100/60 to-indigo-100/70 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-24 sm:pt-16">
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
              <HiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
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
            className="pt-16 space-y-8 -mt-4 sm:mt-0"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.0 }}
          >
            {/* Main Stats - Desktop: Large cards, Mobile: Small pills */}
            <div className="hidden sm:grid grid-cols-3 gap-6 max-w-4xl mx-auto">
              {animatedStats.map((stat, index) => {
                const Icon = stat.icon;
                const animatedValue = stat.animatedValue;
                
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
            
            {/* Mobile Stats - Compact 3-column grid */}
            <div className="grid grid-cols-3 gap-2 max-w-xs mx-auto sm:hidden">
              {animatedStats.map((stat, index) => {
                const Icon = stat.icon;
                const animatedValue = stat.animatedValue;
                
                return (
                  <motion.div
                    key={index}
                    className="group p-2 backdrop-blur-md rounded-lg border transition-all duration-500 shadow-md bg-white/30 dark:bg-gray-800/30 border-white/20 dark:border-gray-700/20 hover:bg-white/50 dark:hover:bg-gray-800/50 hover:border-white/40 dark:hover:border-gray-600/40 shadow-black/5 dark:shadow-black/10 hover:shadow-lg hover:shadow-python-blue/10 dark:hover:shadow-python-blue/20"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 1.2 + index * 0.1 }}
                    whileHover={{ scale: 1.05, y: -2 }}
                  >
                    <div className="text-center space-y-1">
                      <div className="inline-flex items-center justify-center w-6 h-6 rounded-lg transition-all duration-500 bg-python-blue/10 group-hover:bg-python-blue/20">
                        <Icon className="w-3 h-3 transition-colors duration-300 text-python-blue/70 group-hover:text-python-blue" />
                      </div>
                      <div className="space-y-0.5">
                        <motion.div 
                          className="text-sm font-semibold transition-colors duration-300 text-gray-800 dark:text-gray-200 group-hover:text-python-blue dark:group-hover:text-python-blue/90"
                          key={animatedValue}
                          initial={{ scale: 1.1 }}
                          animate={{ scale: 1 }}
                          transition={{ duration: 0.2 }}
                        >
                          {animatedValue.toLocaleString()}
                        </motion.div>
                        <div className="text-xs font-medium transition-colors duration-300 text-gray-600 dark:text-gray-400 group-hover:text-python-blue/80 dark:group-hover:text-python-blue/70">
                          {stat.label}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
            
            {/* Additional Stats - Same style as main stats */}
            <motion.div 
              className="grid grid-cols-3 gap-2 sm:flex sm:flex-wrap sm:justify-center sm:gap-4 max-w-xs sm:max-w-2xl mx-auto mb-4 sm:mb-0"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.6 }}
            >
              {animatedAdditionalStats.map((stat, index) => {
                const animatedValue = stat.animatedValue;
                
                return (
                  <motion.div
                    key={index}
                    className="group p-2 sm:px-6 sm:py-3 backdrop-blur-md rounded-lg sm:rounded-full border transition-all duration-500 shadow-md bg-white/30 dark:bg-gray-800/30 border-white/20 dark:border-gray-700/20 hover:bg-white/50 dark:hover:bg-gray-800/50 hover:border-white/40 dark:hover:border-gray-600/40 shadow-black/5 dark:shadow-black/10 hover:shadow-lg hover:shadow-python-blue/10 dark:hover:shadow-python-blue/20"
                    whileHover={{ scale: 1.05, y: -2 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  >
                    <div className="text-center space-y-0.5 sm:flex sm:items-center sm:space-x-3 sm:space-y-0">
                      <motion.div 
                        className="text-sm font-semibold transition-colors duration-300 text-gray-800 dark:text-gray-200 group-hover:text-python-blue dark:group-hover:text-python-blue/90"
                        key={animatedValue}
                        initial={{ scale: 1.1 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.2 }}
                      >
                        {animatedValue.toLocaleString()}
                      </motion.div>
                      <div className="text-xs sm:text-sm font-medium transition-colors duration-300 text-gray-600 dark:text-gray-400 group-hover:text-python-blue/80 dark:group-hover:text-python-blue/70">
                        {stat.label}
                      </div>
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