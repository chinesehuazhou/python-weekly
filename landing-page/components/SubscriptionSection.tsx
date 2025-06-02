'use client';

import { useTranslations, useLocale } from 'next-intl';
import { motion } from 'framer-motion';
import { FaCrown, FaHeart, FaStar, FaCheck } from 'react-icons/fa';

export default function SubscriptionSection() {
  const t = useTranslations();
  const locale = useLocale();

  const getFeatures = (platform: string, plan?: string) => {
    const features: string[] = [];
    const baseKey = plan 
      ? `subscription.platforms.${platform}.${plan}.features`
      : `subscription.platforms.${platform}.features`;
    
    // Define known feature counts for each platform to avoid calling non-existent keys
    const maxFeatures: { [key: string]: number } = {
      'xiaobot': 6,
      'afdian': 6,
      'patreon.monthly': 5
    };
    
    const platformKey = plan ? `${platform}.${plan}` : platform;
    const maxCount = maxFeatures[platformKey] || 6; // Default to 6 if not specified
    
    for (let index = 0; index < maxCount; index++) {
      const featureKey = `${baseKey}.${index}`;
      
      try {
        const feature = t(featureKey);
        
        // Check if the translation actually exists (not the key itself)
        if (feature && feature !== featureKey && !feature.startsWith('subscription.platforms.')) {
          features.push(feature);
        }
      } catch (error) {
        // Continue to next feature even if one fails
      }
    }
    
    return features;
  };

  interface PremiumOption {
    name: string;
    description: string;
    icon: any;
    color: string;
    url: string;
    featured: boolean;
    price: string;
    originalPrice?: string;
    discount?: string;
    logoUrl?: string;
    specialFeature?: string;
    features: string[];
  }

  const premiumOptions: PremiumOption[] = (locale === 'zh' || locale === 'zh-TW') ? [
    {
      name: t('subscription.platforms.xiaobot.name'),
      description: t('subscription.platforms.xiaobot.description'),
      icon: FaHeart,
      color: 'from-pink-500 to-rose-500',
      url: 'https://www.xiaobot.net/coupon/524cb33e-114f-469d-9b53-5066bcd0be46',
      featured: true,
      price: t('subscription.platforms.xiaobot.price'),
      originalPrice: t('subscription.platforms.xiaobot.originalPrice'),
      discount: t('subscription.platforms.xiaobot.discount'),
      logoUrl: 'https://xiaobot.net/favicon.ico',
      specialFeature: t('subscription.platforms.xiaobot.specialFeature'),
      features: getFeatures('xiaobot')
    },
    {
      name: t('subscription.platforms.afdian.name'),
      description: t('subscription.platforms.afdian.description'),
      icon: FaStar,
      color: 'from-purple-500 to-indigo-500',
      url: 'https://afdian.com/a/python_weekly',
      featured: false,
      price: t('subscription.platforms.afdian.price'),
      originalPrice: t('subscription.platforms.afdian.originalPrice'),
      discount: t('subscription.platforms.afdian.discount'),
      logoUrl: 'https://afdian.com/favicon.ico',
      features: getFeatures('afdian')
    },
  ] : [
    {
      name: t('subscription.platforms.patreon.monthly.name'),
      description: t('subscription.platforms.patreon.monthly.description'),
      icon: FaCrown,
      color: 'from-orange-500 to-red-500',
      url: 'https://patreon.com/PythonCat666',
      featured: true,
      price: t('subscription.platforms.patreon.monthly.price'),
      originalPrice: t('subscription.platforms.patreon.monthly.originalPrice'),
      features: getFeatures('patreon', 'monthly')
    },
  ];

  return (
    <section id="subscription" className="py-20 bg-gradient-to-br from-gray-50/80 via-slate-100/60 to-blue-50/70 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {t('subscription.title')}
          </h2>
          <div className="w-24 h-1 bg-gradient-to-r from-python-blue to-deep-green mx-auto rounded-full"></div>
        </motion.div>

        <div className="max-w-6xl mx-auto">
          {/* Premium Subscription */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <div className={`grid gap-8 ${premiumOptions.length === 1 ? 'justify-center' : 'md:grid-cols-2'}`}>
                  {premiumOptions.map((option, index) => {
                    const Icon = option.icon;
                    return (
                      <motion.a
                        key={index}
                        href={option.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`block p-12 rounded-3xl transition-all duration-300 transform hover:scale-105 relative min-h-[400px] flex flex-col ${
                          premiumOptions.length === 1 ? 'max-w-md mx-auto' : ''
                        } ${
                          option.featured 
                            ? 'bg-white text-gray-900 shadow-xl ring-2 ring-yellow-400' 
                            : 'bg-white text-gray-900 shadow-lg hover:shadow-xl'
                        }`}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        {option.featured && (
                          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                            <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                              {t('subscription.recommended')}
                            </div>
                          </div>
                        )}
                        
                        <div className="flex items-center mb-6">
                          <div className={`w-12 h-12 bg-white rounded-lg flex items-center justify-center mr-4 shadow-sm`}>
                            {option.logoUrl ? (
                              <img 
                                src={option.logoUrl} 
                                alt={`${option.name} logo`}
                                className="w-8 h-8 object-contain"
                                onError={(e) => {
                                  // Fallback to icon if logo fails to load
                                  e.currentTarget.style.display = 'none';
                                  const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                                  if (nextElement) {
                                    nextElement.style.display = 'block';
                                  }
                                }}
                              />
                            ) : null}
                            <Icon className={`w-8 h-8 text-gray-600 ${option.logoUrl ? 'hidden' : 'block'}`} />
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold text-xl">{option.name}</h4>
                            <p className={`text-sm ${
                              option.featured ? 'text-gray-600' : 'text-gray-600'
                            }`}>
                              {option.description}
                            </p>
                          </div>
                        </div>

                        <div className="mb-6">
                          <div className="flex items-baseline">
                            <span className={`text-3xl font-bold ${
                              option.featured ? 'text-gray-900' : 'text-gray-900'
                            }`}>
                              {option.price}
                            </span>
                            {option.originalPrice && (
                              <span className={`ml-3 text-xl line-through ${
                                option.featured ? 'text-gray-500' : 'text-gray-500'
                              }`}>
                                {option.originalPrice}
                              </span>
                            )}
                          </div>
                          {option.discount && (
                            <div className="mt-2">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                🎉 {option.discount}
                              </span>
                            </div>
                          )}
                          {option.specialFeature && (
                            <div className="mt-3 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg">
                              <div className="text-sm font-medium text-orange-800">
                                {option.specialFeature}
                              </div>
                            </div>
                          )}
                        </div>

                        <ul className="space-y-3 flex-1">
                          {option.features.map((feature, featureIndex) => (
                            <li key={featureIndex} className="flex items-center text-base">
                              <FaCheck className={`w-5 h-5 mr-3 ${
                                option.featured ? 'text-green-600' : 'text-green-400'
                              }`} />
                              <span className={option.featured ? 'text-gray-700' : 'text-gray-700'}>
                                {feature}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </motion.a>
                    );
                  })}
            </div>
          </motion.div>
        </div>


      </div>
    </section>
  );
}