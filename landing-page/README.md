# Python 潮流周刊 Landing Page

这是 Python 潮流周刊的官方 Landing Page，使用 Next.js 15 和 TypeScript 构建，支持中英文双语。

## 🚀 特性

- **现代化设计**: 使用 Tailwind CSS 构建的响应式设计
- **国际化支持**: 支持中文和英文双语切换
- **深色模式**: 完整的深色/浅色主题支持
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
│   ├── HeroSection.tsx    # 首屏：价值主张 + 累计体量
│   ├── WhySection.tsx     # 六条理由
│   ├── SampleIssueSection.tsx # 第 100 期全文样例
│   ├── SocialProofSection.tsx # 读者留言截图（可点开大图）
│   ├── SubscriptionSection.tsx # 订阅转化
│   ├── FAQSection.tsx     # 常见问题
│   └── Footer.tsx         # 页脚
├── messages/              # 各语言的通用文案（站名、页脚、价格、FAQ）
├── public/               # 静态资源
│   ├── stats.json        # 累计期数/文章/项目/音视频，随发刊更新
│   ├── testimonials/     # 读者留言截图（自持，不热链图床）
│   ├── logo_pythonlink.svg # Logo 文件
│   └── wechat_pythoncat.jpg # 微信二维码
├── i18n/                 # 国际化配置
│   └── request.ts        # next-intl 请求配置
├── lib/                  # 数据与文案
│   ├── landing-copy.ts   # 首页文案唯一来源（中/英）
│   ├── sample-issue.ts   # 解析第 100 期全文
│   ├── inline-markdown.tsx # 正文行内标记渲染（链接/代码/加粗）
│   └── stats.ts          # 读 public/stats.json
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

首页的营销文案在 `lib/landing-copy.ts`（目前只有中英两套，其余语言回落英文）；
站名、页脚、价格、FAQ 等通用文案在 `messages/`。

## 📄 样例期为什么固定在第 100 期

样例区（`lib/sample-issue.ts`）固定渲染 `docs/2025-05-03-weekly.md` 的全文：

- 最新一期是付费内容，首页给不出可点的全文；
- 若跟着最新一期走，每发一期都要重建一次 landing，维护成本不对等；
- 第 100 期发布已满一年，按 FAQ 里的承诺全文免费公开。

换期只改 `lib/sample-issue.ts` 顶部的两个常量，期数不符会在构建时抛错。

## 📱 响应式设计

项目完全响应式，支持以下断点:

- `sm`: 640px+
- `md`: 768px+
- `lg`: 1024px+
- `xl`: 1280px+
- `2xl`: 1536px+

**Python 潮流周刊** - 由 Python猫 出品的高质量技术周刊，发布地址：https://weekly.pythoncat.top
