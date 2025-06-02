'use client';

import { useTranslations } from '../hooks/useTranslations';
import { motion } from 'framer-motion';
import { memo } from 'react';
import { FaGlobe, FaLayerGroup, FaTh, FaFilter, FaBookOpen, FaStar } from 'react-icons/fa';

function FeaturesSection() {
  const t = useTranslations();

  const features = [
    {
      icon: FaGlobe,
      key: 'quality',
      iconColor: 'text-white',
      bgGradient: 'from-blue-500 to-blue-600',
      shadowColor: 'shadow-blue-500/25',
      hoverShadow: 'group-hover:shadow-blue-500/40',
    },
    {
      icon: FaLayerGroup,
      key: 'diversity',
      iconColor: 'text-white',
      bgGradient: 'from-emerald-500 to-teal-600',
      shadowColor: 'shadow-emerald-500/25',
      hoverShadow: 'group-hover:shadow-emerald-500/40',
    },
    {
      icon: FaTh,
      key: 'volume',
      iconColor: 'text-white',
      bgGradient: 'from-orange-500 to-red-600',
      shadowColor: 'shadow-orange-500/25',
      hoverShadow: 'group-hover:shadow-orange-500/40',
    },
    {
      icon: FaFilter,
      key: 'curation',
      iconColor: 'text-white',
      bgGradient: 'from-purple-500 to-indigo-600',
      shadowColor: 'shadow-purple-500/25',
      hoverShadow: 'group-hover:shadow-purple-500/40',
    },
    {
      icon: FaBookOpen,
      key: 'depth',
      iconColor: 'text-white',
      bgGradient: 'from-indigo-500 to-purple-600',
      shadowColor: 'shadow-indigo-500/25',
      hoverShadow: 'group-hover:shadow-indigo-500/40',
    },
    {
      icon: FaStar,
      key: 'richness',
      iconColor: 'text-white',
      bgGradient: 'from-pink-500 to-rose-600',
      shadowColor: 'shadow-pink-500/25',
      hoverShadow: 'group-hover:shadow-pink-500/40',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };

  return (
    <section id="features" className="relative py-20 overflow-hidden">
      {/* Dynamic gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50/90 via-slate-100/70 to-blue-100/80 dark:from-gray-900 dark:via-blue-950/40 dark:to-indigo-950/50"></div>
      
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-60 dark:opacity-30">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-blue-400/30 to-purple-400/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-to-r from-emerald-400/30 to-teal-400/30 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-gradient-to-r from-orange-400/25 to-pink-400/25 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>
      </div>
      
      {/* Subtle grid pattern */}
      <div className="absolute inset-0 opacity-[0.02] dark:opacity-[0.05]" style={{
        backgroundImage: `radial-gradient(circle at 1px 1px, rgba(0,0,0,0.15) 1px, transparent 0)`,
        backgroundSize: '24px 24px'
      }}></div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {t('features.title')}
          </h2>
          <div className="w-24 h-1 bg-gradient-to-r from-python-blue to-deep-green mx-auto rounded-full"></div>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                variants={itemVariants}
                className="group relative"
              >
                <div className="bg-white/70 dark:bg-gray-800/60 backdrop-blur-2xl rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-3 border border-white/40 dark:border-gray-700/40 hover:border-white/60 dark:hover:border-gray-600/60 hover:bg-white/80 dark:hover:bg-gray-800/70">
                  {/* Icon Container */}
                  <div className="relative mb-8">
                    <div className={`w-20 h-20 bg-gradient-to-br ${feature.bgGradient} rounded-3xl flex items-center justify-center transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 ${feature.shadowColor} shadow-2xl ${feature.hoverShadow}`}>
                      <Icon className={`w-10 h-10 ${feature.iconColor} drop-shadow-sm`} strokeWidth={1.5} />
                    </div>
                    {/* Glow effect */}
                    <div className={`absolute inset-0 w-20 h-20 bg-gradient-to-br ${feature.bgGradient} rounded-3xl opacity-20 blur-2xl group-hover:opacity-40 transition-all duration-500 scale-150`}></div>
                  </div>

                  {/* Content */}
                  <div className="relative z-10">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 group-hover:text-gray-700 dark:group-hover:text-gray-100 transition-colors duration-300">
                      {t(`features.${feature.key}.title`)}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 leading-relaxed text-sm group-hover:text-gray-700 dark:group-hover:text-gray-200 transition-colors duration-300">
                      {t(`features.${feature.key}.description`)}
                    </p>
                  </div>

                  {/* Subtle background pattern */}
                  <div className="absolute top-0 right-0 w-32 h-32 opacity-[0.02] dark:opacity-[0.05] group-hover:opacity-[0.04] dark:group-hover:opacity-[0.08] transition-opacity duration-500">
                    <Icon className="w-full h-full" />
                  </div>
                  
                  {/* Border glow effect */}
                  <div className={`absolute inset-0 rounded-3xl bg-gradient-to-br ${feature.bgGradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500 -z-10`}></div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>


      </div>
    </section>
  );
}

// 使用 React.memo 优化重渲染
export default memo(FeaturesSection);