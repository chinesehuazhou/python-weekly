# Python 潮流周刊 Landing Page

这是 Python 潮流周刊的官方 Landing Page，使用 Next.js 15 和 TypeScript 构建，支持中英文双语。

## 🚀 特性

- **现代化设计**: 使用 Tailwind CSS 构建的响应式设计
- **国际化支持**: 支持中文和英文双语切换
- **深色模式**: 完整的深色/浅色主题支持
- **动画效果**: 使用 Framer Motion 实现流畅的动画
- **性能优化**: 基于 Next.js 15 的静态站点生成
- **SEO 友好**: 完整的 meta 标签和支持多语言的 Open Graph 图片

## 🛠️ 技术栈

- **框架**: Next.js 15 (App Router)
- **语言**: TypeScript (ES2022)
- **样式**: Tailwind CSS, PostCSS
- **国际化**: next-intl
- **图标**: React Icons
- **打包分析**: webpack-bundle-analyzer
- **代码规范**: ESLint, Prettier

## 📦 安装

1. 安装依赖:
```bash
npm install
# 或
yarn install
# 或
pnpm install
```

2. 启动开发服务器:
```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

3. 在浏览器中打开 [http://localhost:3000](http://localhost:3000)

4. 构建静态站点:
```bash
npm run build
# 或
yarn build
# 或
pnpm build
```
构建完成后，静态文件将输出到 `out/` 目录。

## 📁 项目结构

```
landing-page/
├── app/                    # Next.js App Router
│   ├── [locale]/          # 国际化路由
│   │   ├── layout.tsx     # 语言布局
│   │   └── page.tsx       # 主页
│   ├── api/               # API 路由
│   │   └── analytics/     # 分析相关 API
│   ├── globals.css        # 全局样式
│   ├── layout.tsx         # 根布局
│   ├── robots.txt/        # 搜索引擎爬虫配置
│   └── sitemap.xml/       # 网站地图
├── components/            # React 组件
│   ├── Header.tsx         # 导航栏
│   ├── HeroSection.tsx    # 英雄区域
│   ├── FeaturesSection.tsx # 特性展示
│   ├── SubscriptionSection.tsx # 订阅转化
│   ├── LatestIssueSection.tsx # 最新期刊展示
│   ├── FAQSection.tsx     # 常见问题
│   ├── SocialProofSection.tsx # 社交证明
│   └── Footer.tsx         # 页脚
├── messages/              # 国际化文本
│   ├── zh.json           # 简体中文
│   ├── zh-TW.json        # 繁体中文
│   └── en.json           # 英文
├── public/               # 静态资源
│   ├── docs/             # 示例文档
│   │   ├── example_zh.md # 中文示例周刊
│   │   └── example_en.md # 英文示例周刊
│   ├── logo_pythonlink.svg # Logo 文件
│   ├── python_cat.jpg    # 作者头像
│   └── wechat_pythoncat.jpg # 微信二维码
├── i18n/                 # 国际化配置
│   └── request.ts        # next-intl 请求配置
├── lib/                  # 工具库 (例如 `metadata.ts`)
├── i18n.ts              # 国际化主配置
├── middleware.ts        # 中间件
├── next.config.js       # Next.js 配置 (包含静态导出 `output: 'export'`)
├── tailwind.config.js   # Tailwind CSS 配置
├── tsconfig.json        # TypeScript 配置 (目标 ES2022, 严格模式)
└── .eslintrc.json       # ESLint 配置
```

## 🌍 国际化

项目支持多语言:

- 简体中文: `/zh` 或 `/` (默认)
- 繁体中文: `/zh-TW`
- 英文: `/en`

语言文件位于 `messages/` 目录下，可以通过修改这些文件来更新文本内容。示例周刊内容位于 `public/docs/` 目录，根据用户语言自动加载对应的示例文件。

## 📱 响应式设计

项目完全响应式，支持以下断点:

- `sm`: 640px+
- `md`: 768px+
- `lg`: 1024px+
- `xl`: 1280px+
- `2xl`: 1536px+

**Python 潮流周刊** - 由 Python猫 出品的高质量技术周刊，发布地址：https://weekly.pythoncat.top
