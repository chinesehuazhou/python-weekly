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

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
        <LatestIssueSection />

        <SubscriptionSection />

        <SocialProofSection />
        <FAQSection />

      </main>
      <Footer />
    </div>
  );
}