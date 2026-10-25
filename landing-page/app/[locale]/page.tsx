import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import WhySection from '@/components/WhySection';
import SampleIssueSection from '@/components/SampleIssueSection';
import SocialProofSection from '@/components/SocialProofSection';
import SubscriptionSection from '@/components/SubscriptionSection';
import FAQSection from '@/components/FAQSection';
import Footer from '@/components/Footer';
import {setRequestLocale} from 'next-intl/server';
import {locales} from '../../i18n';
import {getLandingCopy} from '../../lib/landing-copy';
import {getSampleIssue} from '../../lib/sample-issue';
import {getSiteStats} from '../../lib/stats';

// 为静态导出生成所有语言参数
export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

type Props = {
  params: Promise<{locale: string}>;
};

// 版式（2026-10-25 用户定稿）：
// 首屏只讲价值主张 + 累计体量 → 六条理由 → 第 100 期完整样例 → 读者截图 → 价格 → FAQ。
// 「本期精选」与「这一期有什么」原本是同一期的两份列表，现已合并成中间那一个样例区。
export default async function HomePage({ params }: Props) {
  const { locale } = await params;

  // Enable static rendering
  setRequestLocale(locale);
  const copy = getLandingCopy(locale);
  const issue = getSampleIssue(locale);
  const stats = getSiteStats();

  return (
    <div className="site">
      <Header navLabels={copy.nav} />
      <main>
        <HeroSection copy={copy.hero} stats={stats} />
        <WhySection copy={copy.why} />
        <SampleIssueSection issue={issue} copy={copy.sample} />
        <SocialProofSection copy={copy.proof} />
        <SubscriptionSection copy={copy.subscription} />
        <FAQSection kicker={copy.faq.kicker} />
      </main>
      <Footer />
    </div>
  );
}
