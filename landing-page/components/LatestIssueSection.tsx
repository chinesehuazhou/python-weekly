'use client';

import { useState, useEffect } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { motion } from 'framer-motion';
import dynamic from 'next/dynamic';
import remarkGfm from 'remark-gfm';
import { FaExpand, FaTimes } from 'react-icons/fa';

// 动态导入 ReactMarkdown 以减少初始包大小
const ReactMarkdown = dynamic(() => import('react-markdown'), {
  loading: () => <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-4 rounded"></div>,
  ssr: false
});

export default function LatestIssueSection() {
  const t = useTranslations();
  const locale = useLocale();
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // 根据语言环境获取对应的示例文件
        const filename = locale === 'en' ? 'example_en.md' : 'example_zh.md';
        const response = await fetch(`/docs/${filename}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const text = await response.text();
        setContent(text);
      } catch (err) {
        console.error('Failed to fetch content:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, []);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <section id="latest-issue" className="py-20 bg-gradient-to-br from-gray-100/70 via-slate-100/80 to-blue-100/90 dark:from-gray-900 dark:to-gray-800 relative overflow-hidden">
      {/* 代码片段背景图案 */}
      <div className="absolute inset-0 opacity-5 dark:opacity-10">
        <div className="absolute top-10 left-10 text-6xl font-mono text-python-blue transform rotate-12">
          def
        </div>
        <div className="absolute top-32 right-20 text-4xl font-mono text-emerald-500 transform -rotate-6">
          import
        </div>
        <div className="absolute bottom-40 left-1/4 text-5xl font-mono text-purple-500 transform rotate-45">
          class
        </div>
        <div className="absolute bottom-20 right-1/3 text-3xl font-mono text-orange-500 transform -rotate-12">
          return
        </div>
        <div className="absolute top-1/2 left-1/2 text-7xl font-mono text-indigo-400 transform -translate-x-1/2 -translate-y-1/2 rotate-6">
          {"{"}
        </div>
        <div className="absolute top-20 left-1/3 text-2xl font-mono text-teal-500 transform rotate-12">
          for
        </div>
        <div className="absolute bottom-32 left-10 text-4xl font-mono text-pink-500 transform -rotate-15">
          if
        </div>
        <div className="absolute top-1/3 right-10 text-3xl font-mono text-cyan-500 transform rotate-20">
          while
        </div>
      </div>
      
      {/* 几何装饰元素 */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Python符号装饰 */}
        <div className="absolute top-16 right-16 text-6xl font-mono text-python-blue/10 transform rotate-12 select-none">
          🐍
        </div>
        <div className="absolute bottom-16 left-16 text-6xl font-mono text-python-blue/10 transform -rotate-12 select-none">
          📊
        </div>
        
        {/* 代码括号装饰 */}
        <div className="absolute top-24 left-1/4 text-8xl font-mono text-python-blue/10 transform rotate-12 select-none">
          {"{"}
        </div>
        <div className="absolute bottom-24 right-1/4 text-8xl font-mono text-python-blue/10 transform -rotate-12 select-none">
          {"}"}
        </div>
        <div className="absolute top-1/3 left-20 text-6xl font-mono text-emerald-400/15 transform rotate-6 select-none">
          {'['}
        </div>
        <div className="absolute bottom-1/3 right-20 text-6xl font-mono text-emerald-400/15 transform -rotate-6 select-none">
          {']'}
        </div>
        
        {/* 连接线装饰 */}
        <svg className="absolute top-0 left-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-python-blue/5 dark:text-blue-400/10"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* 装饰性连接线 */}
          <path d="M100,100 Q200,50 300,100 T500,100" stroke="currentColor" strokeWidth="2" fill="none" className="text-python-blue/10 dark:text-blue-400/20" strokeDasharray="5,5">
            <animate attributeName="stroke-dashoffset" values="0;10" dur="2s" repeatCount="indefinite"/>
          </path>
          <path d="M600,200 Q700,150 800,200 T1000,200" stroke="currentColor" strokeWidth="2" fill="none" className="text-emerald-400/10 dark:text-emerald-400/20" strokeDasharray="3,7">
            <animate attributeName="stroke-dashoffset" values="10;0" dur="3s" repeatCount="indefinite"/>
          </path>
        </svg>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {t('pastIssueExample')}
          </h2>
          <div className="w-24 h-1 bg-gradient-to-r from-python-blue to-deep-green mx-auto rounded-full"></div>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          {/* Main Content */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl border border-gray-200 dark:border-gray-700 relative overflow-hidden">


              
              {/* Markdown Content */}
              <div>
                {loading && (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-python-blue"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">
                      {locale === 'zh' ? '加载中...' : 'Loading...'}
                    </span>
                  </div>
                )}
                
                {error && (
                  <div className="text-center py-12">
                    <p className="text-red-600 dark:text-red-400">
                      {locale === 'zh' ? '加载失败: ' : 'Failed to load: '}{error}
                    </p>
                  </div>
                )}
                
                {!loading && !error && content && (
                  <div className="relative">
                    <button
                      onClick={openModal}
                      className="absolute top-4 right-4 z-10 bg-gradient-to-r from-python-blue to-emerald-500 text-white p-3 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 group"
                      title={locale === 'zh' ? '点击放大查看' : 'Click to enlarge'}
                    >
                      <FaExpand className="w-5 h-5" />
                      <span className="absolute -top-2 -right-2 w-4 h-4 bg-orange-400 rounded-full animate-ping group-hover:animate-pulse"></span>
                    </button>
                    <div className="max-h-96 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-lg p-6 bg-gray-50 dark:bg-gray-900 cursor-pointer relative" onClick={openModal}>
                      <div className="prose prose-lg dark:prose-invert max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            h1: ({ children }) => (
                              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                                {children}
                              </h1>
                            ),
                            h2: ({ children }) => (
                              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-3 mt-6">
                                {children}
                              </h2>
                            ),
                            h3: ({ children }) => (
                              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 mt-4">
                                {children}
                              </h3>
                            ),
                            p: ({ children }) => (
                              <p className="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">
                                {children}
                              </p>
                            ),
                            a: ({ href, children }) => (
                              <a
                                href={href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-python-blue hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 underline"
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                }}
                              >
                                {children}
                              </a>
                            ),
                            ul: ({ children }) => (
                              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-4 space-y-1">
                                {children}
                              </ul>
                            ),
                            ol: ({ children }) => (
                              <ol className="list-decimal list-inside text-gray-700 dark:text-gray-300 mb-4 space-y-1">
                                {children}
                              </ol>
                            ),
                            blockquote: ({ children }) => (
                              <blockquote className="border-l-4 border-python-blue pl-4 italic text-gray-600 dark:text-gray-400 mb-4">
                                {children}
                              </blockquote>
                            ),
                            code: ({ children, className }) => {
                              const isInline = !className;
                              if (isInline) {
                                return (
                                  <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm font-mono text-gray-800 dark:text-gray-200">
                                    {children}
                                  </code>
                                );
                              }
                              return (
                                <pre className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg overflow-x-auto mb-4">
                                  <code className="text-sm font-mono text-gray-800 dark:text-gray-200">
                                    {children}
                                  </code>
                                </pre>
                              );
                            },
                          }}
                        >
                          {content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* 弹窗模态框 */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-75" onClick={closeModal}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-6xl max-h-[90vh] w-full overflow-hidden relative" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                {locale === 'zh' ? (
                  <>
                    往期内容示例（更多示例请查看
                    <a 
                      href="https://github.com/chinesehuazhou/python-weekly" 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="text-blue-600 dark:text-blue-400 hover:underline ml-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Github
                    </a>
                    ）
                  </>
                ) : (
                  <>
                    Past Issues Example (More examples on 
                    <a 
                      href="https://github.com/chinesehuazhou/python-weekly" 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="text-blue-600 dark:text-blue-400 hover:underline ml-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Github
                    </a>
                    )
                  </>
                )}
              </h3>
              
              <button
                onClick={closeModal}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
              >
                <FaTimes className="w-6 h-6 text-gray-600 dark:text-gray-300" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              <div>
                <div className="prose prose-lg dark:prose-invert max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ children }) => (
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                          {children}
                        </h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-3 mt-6">
                          {children}
                        </h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 mt-4">
                          {children}
                        </h3>
                      ),
                      p: ({ children }) => (
                        <p className="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">
                          {children}
                        </p>
                      ),
                      a: ({ href, children }) => (
                        <a
                          href={href}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-python-blue hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 underline"
                        >
                          {children}
                        </a>
                      ),
                      ul: ({ children }) => (
                        <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-4 space-y-1">
                          {children}
                        </ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="list-decimal list-inside text-gray-700 dark:text-gray-300 mb-4 space-y-1">
                          {children}
                        </ol>
                      ),
                      blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-python-blue pl-4 italic text-gray-600 dark:text-gray-400 mb-4">
                          {children}
                        </blockquote>
                      ),
                      code: ({ children, className }) => {
                        const isInline = !className;
                        if (isInline) {
                          return (
                            <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm font-mono text-gray-800 dark:text-gray-200">
                              {children}
                            </code>
                          );
                        }
                        return (
                          <pre className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg overflow-x-auto mb-4">
                            <code className="text-sm font-mono text-gray-800 dark:text-gray-200">
                              {children}
                            </code>
                          </pre>
                        );
                      },
                    }}
                  >
                    {content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}