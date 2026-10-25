// 首页文案的唯一来源。组件只渲染，不写死句子。
// 2026-10-25 用户定稿：首屏保留「高质量的信息筛选器…」与「在信息洪流中淘金太累…」两段，
// 「为什么选择」的六条理由沿用旧站原文，读者反馈用截图证据（此前用改写过的引文，属编造）。
// 同日第二轮：删掉 why / sample / faq 三处「解释性提示」，用户认为多余。

export type WhyItem = {title: string; body: string};

const GITHUB_URL = 'https://github.com/chinesehuazhou/python-weekly';

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
        title: ['少刷一点，', '多读点有用的。'],
        tagline: '高质量的信息筛选器，为你开阔视野的一扇明窗',
        description:
          '在信息洪流中淘金太累？Python 潮流周刊人工为你打捞出最硬核、最前沿的技术干货。告别信息过载，精准捕获最新趋势与深度洞察。',
        subscribe: '订阅周刊',
        sample: '看一整期长什么样',
        // 四格体量的名词标签（数字在下面），单位词另给 sample.counts
        stats: {
          issues: '期数',
          articles: '文章',
          projects: '开源项目',
          media: '音视频',
        },
      },
      why: {
        kicker: 'WHY THIS WEEKLY',
        title: ['信息不缺，', '缺的是判断。'],
        items: [
          {
            title: '全球信息源覆盖',
            body: '精选中英文 400+ 优质信息源，涵盖官方文档、技术博客、开源社区、学术论文，确保内容前沿权威。',
          },
          {
            title: '内容形式多样',
            body: '深度技术文章、开源项目、音视频资源、热门话题、技术书籍一应俱全，满足不同学习需求。',
          },
          {
            title: '内容体量丰富',
            body: '每期精选 12 篇技术文章 + 12 个开源项目，配套音视频资源和热门讨论，构建全方位技术资讯生态。',
          },
          {
            title: 'AI + 人工精选',
            body: 'AI 技术高效抓取海量信息，人工高标准精选优质内容，确保每篇推荐都有学习价值。',
          },
          {
            title: '内容深度解读',
            body: '每篇内容都有精心整理的摘要和推荐语，不是简单照搬原文，更有相关附录内容补充。',
          },
          {
            title: '展示要素丰富',
            body: '图文并茂的精美展示，star 数超 1000 的开源项目特别标注，助你快速识别优质资源。',
          },
        ] as WhyItem[],
      },
      sample: {
        kicker: 'PAST ISSUES',
        title: '往期内容示例',
        more: '更多示例请查看',
        moreLink: 'GitHub',
        moreUrl: GITHUB_URL,
        backToTop: '回到开头',
        counts: {
          articles: '篇文章',
          projects: '个项目',
          media: '个音视频',
        },
      },
      proof: {
        kicker: 'FROM READERS',
        // 2026-10-25 用户定稿：标题与导语改回旧站原文，不再自拟。
        title: '深受开发者信赖',
        intro:
          'Python 潮流周刊通过人工精选的高质量内容和持续稳定的交付，帮助读者缓解了他们的信息焦虑问题，帮助他们在职业发展中保持技术敏感度。',
        caption: '读者留言',
        // 截图收在 public/testimonials/ 里，不再热链 img.pythoncat.top：
        // 图床慢一点，「证据」区就是三个空白框，而这一块的唯一价值就是能看见。
        images: [
          {
            src: '/testimonials/reader-01.png',
            width: 2314,
            height: 2160,
            alt: '读者留言截图：基本每一期都有看，国内认真做 Python 高质量信息源的真的不多',
          },
          {
            src: '/testimonials/reader-02.png',
            width: 804,
            height: 600,
            alt: '读者留言截图：相比自己去到处翻网页，直接看你总结的体验好很多',
          },
          {
            src: '/testimonials/reader-03.png',
            width: 502,
            height: 439,
            alt: '付费读者留言截图：每一期总有一两篇文章能直接用到工作中',
          },
        ],
      },
      subscription: {
        kicker: 'SUBSCRIBE',
        introMulti: '选一个适合你的付款方式。两档内容一致，区别只在登录与支付渠道。',
        introSingle: '一个订阅，解锁全部往期与电子书。随时可退订。',
      },
      faq: {
        kicker: 'BEFORE YOU SUBSCRIBE',
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
      title: ['Spend less time scrolling.', 'Read what actually matters.'],
      tagline: 'A high-quality information filter — a bright window onto a wider world.',
      description:
        'Panning for gold in the information flood is exhausting. Python Trending Weekly hand-picks the most substantial, most current technical material for you: no more information overload, just the trends and the depth that matter.',
      subscribe: 'Subscribe',
      sample: 'See a full issue',
      stats: {
        issues: 'issues',
        articles: 'articles',
        projects: 'projects',
        media: 'audio/video',
      },
    },
    why: {
      kicker: 'WHY THIS WEEKLY',
      title: ['Information is cheap.', 'Judgment is not.'],
      items: [
        {
          title: 'Comprehensive global coverage',
          body: 'Handpicked from 400+ premium sources across Chinese and English ecosystems, spanning official documentation, technical blogs, open-source communities and academic publications.',
        },
        {
          title: 'Multi-format content',
          body: 'In-depth articles, open-source projects, audio and video, trending topics and technical books — enough range for different learning needs.',
        },
        {
          title: 'Substantial volume',
          body: 'Each issue carries 12 selected articles and 12 open-source projects, plus audio/video and trending discussions.',
        },
        {
          title: 'AI + human curation',
          body: 'AI aggregates the flood efficiently; a human applies a high bar, so every recommendation earns its place.',
        },
        {
          title: 'In-depth analysis',
          body: 'Every item comes with a written summary and editorial note — never a bare repost — plus relevant supplementary material.',
        },
        {
          title: 'Rich presentation',
          body: 'Careful visual layout, with projects above 1,000 stars flagged so you can spot top-tier resources fast.',
        },
      ] as WhyItem[],
    },
    sample: {
      kicker: 'PAST ISSUES',
      title: 'What an issue looks like',
      more: 'More examples on',
      moreLink: 'GitHub',
      moreUrl: GITHUB_URL,
      backToTop: 'Back to top',
      counts: {
        articles: 'articles',
        projects: 'projects',
        media: 'audio/video',
      },
    },
    proof: {
      kicker: 'FROM READERS',
      title: 'Trusted by Developers',
      intro:
        'Python Trending Weekly helps readers alleviate information anxiety and maintain technical sensitivity in their career development through manually curated high-quality content and consistent, stable delivery.',
      caption: 'Reader comment',
      images: [
        {
          src: '/testimonials/reader-01.png',
          width: 2314,
          height: 2160,
          alt: 'Reader comment screenshot: I read almost every issue',
        },
        {
          src: '/testimonials/reader-02.png',
          width: 804,
          height: 600,
          alt: 'Reader comment screenshot: much better than browsing around myself',
        },
        {
          src: '/testimonials/reader-03.png',
          width: 502,
          height: 439,
          alt: 'Paying reader comment screenshot: there is always something I can use at work',
        },
      ],
    },
    subscription: {
      kicker: 'SUBSCRIBE',
      introMulti: 'Two payment channels, identical content. Pick whichever is easier for you.',
      introSingle: 'One subscription, the full archive and every e-book. Cancel anytime.',
    },
    faq: {
      kicker: 'BEFORE YOU SUBSCRIBE',
    },
  };
}
