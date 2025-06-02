import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import SubscriptionSection from '@/components/SubscriptionSection';
import LatestIssueSection from '@/components/LatestIssueSection';
import SocialProofSection from '@/components/SocialProofSection';
import FAQSection from '@/components/FAQSection';

import Footer from '@/components/Footer';

export default function HomePage() {
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