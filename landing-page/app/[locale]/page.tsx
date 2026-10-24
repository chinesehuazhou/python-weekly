import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import SubscriptionSection from '@/components/SubscriptionSection';
import LatestIssueSection from '@/components/LatestIssueSection';
import SocialProofSection from '@/components/SocialProofSection';
import FAQSection from '@/components/FAQSection';
import Footer from '@/components/Footer';
import {setRequestLocale} from 'next-intl/server';
import {locales} from '../../i18n';
import {getLatestIssue} from '../../lib/latest-issue';
import {getLandingCopy} from '../../lib/landing-copy';

// 为静态导出生成所有语言参数
export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

type Props = {
  params: Promise<{locale: string}>;
};

export default async function HomePage({ params }: Props) {
  const { locale } = await params;
  
  // Enable static rendering
  setRequestLocale(locale);
  const issue = getLatestIssue(locale);
  const copy = getLandingCopy(locale);

  return (
    <div className="site">
      <Header navLabels={copy.nav} />
      <main>
        <HeroSection issue={issue} copy={copy.hero} issueLabels={copy.issue} />
        <FeaturesSection copy={copy.principles} />
        <LatestIssueSection issue={issue} copy={copy.issueIndex} />
        <SubscriptionSection />
        <SocialProofSection copy={copy.testimonials} />
        <FAQSection />
      </main>
      <Footer />
    </div>
  );
}
