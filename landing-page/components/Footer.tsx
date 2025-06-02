'use client';

import { useTranslations } from '../hooks/useTranslations';
import Image from 'next/image';
import { FaGithub, FaTwitter, FaRss, FaTimes } from 'react-icons/fa';
import { FaTelegram, FaWeixin } from 'react-icons/fa';
import { useState } from 'react';

// PythonLink SVG 图标组件
const PythonLink = ({ className }: { className?: string }) => (
  <Image
    src="/logo_pythonlink.svg"
    alt="PythonLink"
    width={24}
    height={24}
    className={`w-6 h-6 ${className || ''}`}
    unoptimized
  />
);

export default function Footer() {
  const t = useTranslations();
  const currentYear = new Date().getFullYear();
  const [showWechatModal, setShowWechatModal] = useState(false);

  const socialLinks = [
    {
      name: 'GitHub',
      icon: FaGithub,
      url: 'https://github.com/chinesehuazhou/python-weekly',
      color: 'text-white-300',
    },
    {
      name: 'Telegram',
      icon: FaTelegram,
      url: 'https://t.me/pythontrendingweekly',
      color: 'text-blue-400',
    },
    {
      name: 'WeChat',
      icon: FaWeixin,
      url: 'https://img.pythoncat.top/python_cat.jpg',
      color: 'text-green-500',
    },
    {
      name: 'Twitter',
      icon: FaTwitter,
      url: 'https://twitter.com/chinesehuazhou',
      color: 'text-blue-500',
    },
    {
      name: 'RSS',
      icon: FaRss,
      url: 'https://pythoncat.substack.com/feed',
      color: 'text-orange-500',
    },
    {
      name: 'PythonLink',
      icon: PythonLink,
      url: 'https://pythonlink.xyz',
      color: 'text-blue-400',
    },
  ];



  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          {/* Brand Section */}
          <div className="mb-8">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-10 h-10 rounded-lg overflow-hidden flex items-center justify-center">
                <Image
                  src="/logo_python_weekly.svg"
                  alt="Python Weekly Logo"
                  width={40}
                  height={40}
                  className="object-cover rounded-lg"
                  priority
                />
              </div>
              <span className="font-bold text-xl">{t('siteName')}</span>
            </div>
            <p className="text-gray-400 mb-6 leading-relaxed max-w-2xl mx-auto">
              {t('footerDescription')}
            </p>
            
            {/* Social Links */}
            <div className="flex justify-center space-x-4">
              {socialLinks.map((social, index) => {
                const Icon = social.icon;
                const isWechat = social.name === '微信';
                const isPythonLink = social.name === 'PythonLink';
                
                if (isWechat) {
                  return (
                    <button
                      key={index}
                      onClick={() => setShowWechatModal(true)}
                      className={`text-gray-400 ${social.color} transition-colors duration-200`}
                      aria-label={social.name}
                    >
                      <Icon className="w-6 h-6" />
                    </button>
                  );
                }
                
                return (
                  <a
                    key={index}
                    href={social.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="transition-all duration-200 hover:scale-110 hover:drop-shadow-lg"
                    aria-label={social.name}
                  >
                    {isPythonLink ? (
                      <Icon className={`${social.color} transition-all duration-200`} />
                    ) : (
                      <Icon className={`w-6 h-6 ${social.color} transition-all duration-200`} />
                    )}
                  </a>
                );
              })}
            </div>
          </div>
        </div>



        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8 mt-8">
          <div className="text-center">
            <p className="text-gray-400 text-sm">
              {t('copyright', {year: currentYear})}
            </p>
          </div>
        </div>
      </div>
      
      {/* WeChat QR Code Modal */}
      {showWechatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowWechatModal(false)}>
          <div className="bg-white rounded-lg p-6 max-w-sm mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">微信公众号</h3>
              <button
                onClick={() => setShowWechatModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <FaTimes className="w-5 h-5" />
              </button>
            </div>
            <div className="text-center">
              <Image
                src="/wechat_pythoncat.jpg"
                alt="微信公众号二维码"
                width={192}
                height={192}
                className="w-48 h-48 mx-auto mb-4"
              />
              <p className="text-sm text-gray-600">扫描二维码关注微信公众号</p>
            </div>
          </div>
        </div>
      )}
    </footer>
  );
}