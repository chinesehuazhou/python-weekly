export function getLandingCopy(locale: string) {
  const chinese = locale === 'zh' || locale === 'zh-TW';

  if (chinese) {
    return {
      nav: {
        why: '为什么订阅',
        pricing: '价格与平台',
        faq: '常见问题',
      },
      hero: {
        eyebrow: '每周六更新 · 人工筛选',
        title: ['少刷一点，', '多读点有用的。'],
        lede:
          '从 400+ 中英文信息源里，人工筛出值得你花时间的 Python 文章、开源项目与社区讨论。每期约 25 条，读完只要一杯咖啡的时间。',
        subscribe: '订阅周刊',
        preview: '先看本期精选',
        proof: [
          ['已连载', ''],
          ['更新频率', '每周六'],
          ['内容来源', '400+ 信息源'],
        ],
      },
      issue: {
        latest: '最新一期',
        articles: '篇文章',
        projects: '个项目',
        readFull: '阅读完整版',
      },
      principles: {
        kicker: 'WHY THIS WEEKLY',
        title: ['信息不缺，', '缺的是判断。'],
        intro:
          '一份周刊的价值不在于收录多少链接，而在于替你放弃了什么。这三件事，是我们每周真正花时间做的。',
        items: [
          {
            title: '不是聚合，是筛选',
            body: '先从 400+ 信息源里粗筛，再由人工判断什么值得读。标题党、重复内容和低信噪比讨论会停在门外。',
            note: '每周约 25 条',
          },
          {
            title: '每一条都给出理由',
            body: '不只丢一个链接。每篇文章和项目都有摘要与推荐语，告诉你它解决了什么问题、为什么现在值得看。',
            note: '摘要 + 推荐语',
          },
          {
            title: '覆盖正在发生的变化',
            body: '从 CPython 新提案、框架演进，到 AI 工具链和社区争论，把零散动态放回一条可追踪的技术脉络里。',
            note: '文章 · 项目 · 播客 · 讨论',
          },
        ],
      },
      issueIndex: {
        kicker: "WHAT'S INSIDE",
        title: '这一期，具体有什么。',
        intro: '完整目录来自仓库里的第 {number} 期原文，不再维护一份会过期的示例。',
        articles: '文章 & 教程',
        projects: '项目 & 资源',
        cta: '阅读第 {number} 期完整版',
      },
      testimonials: {
        kicker: 'FROM READERS',
        title: '不是我们自说自话。',
        intro: '这些话来自公众号留言和付费读者反馈，原文未改写核心意思。',
        items: [
          {
            quote: '基本每一期都有看……国内认真做 Python 高质量信息源真的不多，支持！',
            source: '微信公众号读者 · 浙江',
            date: '2024.05',
          },
          {
            quote: '相比自己去到处翻网页，直接看你总结的体验真的好很多！！！',
            source: '微信公众号读者 · 江苏',
            date: '2024.05',
          },
          {
            quote:
              '每一期总有那么一两篇文章让我眼前一亮，学到新的知识或技巧，甚至能直接应用到我的工作中。',
            source: '付费订阅读者 · 软件开发',
            date: '2024.06',
          },
        ],
      },
    };
  }

  return {
    nav: {
      why: 'Why subscribe',
      pricing: 'Pricing',
      faq: 'FAQ',
    },
    hero: {
      eyebrow: 'NEW EVERY SATURDAY · HUMAN CURATED',
      title: ['Spend less time scrolling.', 'Read what actually matters.'],
      lede:
        'A human-curated Python weekly covering the articles, open-source projects and community debates worth your time, selected from 400+ Chinese and English sources.',
      subscribe: 'Subscribe',
      preview: "See what's inside",
      proof: [
        ['Issues', ''],
        ['Cadence', 'Every Saturday'],
        ['Sources', '400+ curated'],
      ],
    },
    issue: {
      latest: 'Latest issue',
      articles: 'articles',
      projects: 'projects',
      readFull: 'Read the full issue',
    },
    principles: {
      kicker: 'WHY THIS WEEKLY',
      title: ['Information is cheap.', 'Judgment is not.'],
      intro:
        'A weekly is defined by what it leaves out. These are the three things we spend real time on every week.',
      items: [
        {
          title: 'Curation, not aggregation',
          body: 'We scan 400+ sources first, then make a human call on what deserves your attention. Clickbait and low-signal noise stop at the door.',
          note: 'About 25 items a week',
        },
        {
          title: 'Every link comes with a reason',
          body: 'No naked links. Every article and project gets a summary and editorial note explaining the problem it solves and why it matters now.',
          note: 'Summary + editorial note',
        },
        {
          title: 'A view of what is changing',
          body: 'From CPython proposals and framework shifts to AI tooling and community debates, scattered updates become a trackable technical narrative.',
          note: 'Articles · Projects · Podcasts · Debates',
        },
      ],
    },
    issueIndex: {
      kicker: "WHAT'S INSIDE",
      title: 'Exactly what is in this issue.',
      intro:
        'This index is generated from issue {number} in the repository. Item titles keep the language used in the source draft.',
      articles: 'Articles & tutorials',
      projects: 'Projects & resources',
      cta: 'Read issue {number}',
    },
    testimonials: {
      kicker: 'FROM READERS',
      title: 'Readers, not marketing copy.',
      intro: 'Quotes from public comments and paying subscribers, lightly trimmed without changing the meaning.',
      items: [
        {
          quote:
            'I read almost every issue. There are very few people in China doing high-quality Python curation this consistently.',
          source: 'WeChat reader · Zhejiang',
          date: '2024.05',
        },
        {
          quote:
            'Compared with browsing around myself, reading your summary is a much better experience.',
          source: 'WeChat reader · Jiangsu',
          date: '2024.05',
        },
        {
          quote:
            'There is always one or two pieces that surprise me, teach me something new, or go straight into my work.',
          source: 'Paid subscriber · Software developer',
          date: '2024.06',
        },
      ],
    },
  };
}
