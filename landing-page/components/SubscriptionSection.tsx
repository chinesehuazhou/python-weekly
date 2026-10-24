'use client';

import { useTranslations, useLocale } from '../hooks/useTranslations';
import { FaCrown, FaHeart, FaStar, FaCheck } from 'react-icons/fa';
import Image from 'next/image';
import { useEffect, useState, useRef } from 'react';

export default function SubscriptionSection() {
  const [highlightTarget, setHighlightTarget] = useState<string | null>(null);
  const sectionRef = useRef<HTMLElement>(null);
  const t = useTranslations();
  const locale = useLocale();

  useEffect(() => {
    const hash = window.location.hash.replace('#', '');
    const targetId = {'subscribe-xiaobot': 'xiaobot', 'subscribe-afdian': 'afdian'}[hash];
    if (!targetId) return;

    const scrollToCard = () => {
      const el = document.getElementById(targetId);
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      if (rect.top === 0 && rect.bottom === 0) return false; // not laid out yet
      const top = rect.top + window.scrollY - 65;
      window.scrollTo({ top, behavior: 'instant' });
      return true;
    };

    // 多次尝试直到定位稳定（页面渲染完成前后卡片位置会变化）
    let attempts = 0;
    const tryScroll = () => {
      if (scrollToCard() && attempts >= 3) {
        setHighlightTarget(targetId);
        setTimeout(() => setHighlightTarget(null), 3500);
        return;
      }
      attempts++;
      setTimeout(tryScroll, 200);
    };
    tryScroll();
  }, []);

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
      } catch {
        // Continue to next feature even if one fails
      }
    }
    
    return features;
  };

  interface PremiumOption {
    name: string;
    description: string;
    icon: React.ComponentType<{ className?: string; }>;
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
    <section id="subscription" ref={sectionRef} className="subscription">
      <div className="shell">
        <div className="section-heading section-heading--row subscription__heading">
          <div>
            <p className="section-kicker">SUBSCRIBE</p>
            <h2>
            {t('subscription.title')}
          </h2>
          </div>
          <p>
            选一个适合你的付款方式。两档内容一致，区别只在登录与支付渠道。
          </p>
        </div>

        <div className={`subscription__grid${premiumOptions.length === 1 ? ' subscription__grid--single' : ''}`}>
                  {premiumOptions.map((option, index) => {
                    const Icon = option.icon;
                    const platformId = option.url.includes('xiaobot') ? 'xiaobot' : option.url.includes('afdian') ? 'afdian' : 'patreon';
                    const isHighlighted = highlightTarget === platformId;
                    return (
                      <a
                        key={index}
                        id={platformId}
                        href={option.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`subscription__card ${
                          option.featured
                            ? 'is-featured'
                            : ''
                        } ${
                          isHighlighted ? 'is-highlighted' : ''
                        }`}
                      >
                        {option.featured && (
                          <div className="subscription__badge">
                            {t('subscription.recommended')}
                          </div>
                        )}
                        
                        <div className="subscription__platform">
                          <div className="subscription__logo">
                            {option.logoUrl ? (
                              <Image 
                                src={option.logoUrl} 
                                alt={`${option.name} logo`}
                                width={32}
                                height={32}
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
                            <h3>{option.name}</h3>
                            <p>
                              {option.description}
                            </p>
                          </div>
                        </div>

                        <div className="subscription__price">
                          <div>
                            <span className="subscription__amount">
                              {option.price}
                            </span>
                            {option.originalPrice && (
                              <span className="subscription__original">
                                {option.originalPrice}
                              </span>
                            )}
                          </div>
                          {option.discount && (
                            <div>
                              <span className="subscription__discount">
                                🎉 {option.discount}
                              </span>
                            </div>
                          )}
                          {option.specialFeature && (
                            <div className="subscription__special">
                              <div>
                                {option.specialFeature}
                              </div>
                            </div>
                          )}
                        </div>

                        <ul className="subscription__features">
                          {option.features.map((feature, featureIndex) => (
                            <li key={featureIndex}>
                              <FaCheck aria-hidden="true" />
                              <span>
                                {feature}
                              </span>
                            </li>
                          ))}
                        </ul>
                        
                        {/* Call-to-Action Button */}
                        <div className="subscription__cta-wrap">
                          <div className="subscription__cta">
                            <span>
                              {option.featured && <FaCrown className="w-4 h-4 mr-2" />}
                              {t('subscription.cta.button')}
                              <span aria-hidden="true">→</span>
                            </span>
                          </div>
                        </div>
                      </a>
                    );
                  })}
        </div>
      </div>
    </section>
  );
}
