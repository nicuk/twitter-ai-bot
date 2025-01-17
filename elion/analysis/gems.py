"""
Gem analysis functionality for Elion
"""

from typing import Dict, List
from datetime import datetime, timedelta

class GemAnalyzer:
    """Analyzes potential gem opportunities"""
    
    def __init__(self):
        """Initialize gem analyzer"""
        self.opportunities = []
        self.min_confidence = 0.8  # Minimum confidence to recommend
        self.max_market_cap = 100000000  # $100M max market cap
        self.min_liquidity = 100000  # $100K min daily volume

    def analyze_opportunity(self, project_data: Dict) -> Dict:
        """Analyze a potential gem opportunity"""
        try:
            # Basic checks
            if not self._passes_basic_checks(project_data):
                return None
                
            # Calculate scores
            tech_score = self._analyze_tech_score(project_data)
            social_score = self._analyze_social_score(project_data)
            market_score = self._analyze_market_score(project_data)
            
            # Calculate overall score
            overall_score = (
                tech_score * 0.4 +
                social_score * 0.3 +
                market_score * 0.3
            )
            
            if overall_score < self.min_confidence:
                return None
                
            analysis = {
                'symbol': project_data.get('symbol'),
                'name': project_data.get('name'),
                'market_cap': project_data.get('market_cap'),
                'volume_24h': project_data.get('volume_24h'),
                'scores': {
                    'technical': tech_score,
                    'social': social_score,
                    'market': market_score,
                    'overall': overall_score
                },
                'analysis': self._generate_analysis(project_data, overall_score),
                'timestamp': datetime.now()
            }
            
            # Track opportunity
            self.opportunities.append(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing gem opportunity: {e}")
            return None

    def get_best_opportunities(self, limit: int = 3) -> List[Dict]:
        """Get best current opportunities"""
        try:
            # Remove old opportunities
            self._cleanup_opportunities()
            
            # Sort by overall score
            sorted_opps = sorted(
                self.opportunities,
                key=lambda x: x['scores']['overall'],
                reverse=True
            )
            
            return sorted_opps[:limit]
            
        except Exception as e:
            print(f"Error getting opportunities: {e}")
            return []

    def _passes_basic_checks(self, data: Dict) -> bool:
        """Check if project passes basic criteria"""
        try:
            market_cap = data.get('market_cap', 0)
            volume_24h = data.get('volume_24h', 0)
            
            return (
                market_cap > 0 and
                market_cap < self.max_market_cap and
                volume_24h >= self.min_liquidity
            )
            
        except Exception as e:
            print(f"Error in basic checks: {e}")
            return False

    def _analyze_tech_score(self, data: Dict) -> float:
        """Analyze technical aspects"""
        try:
            # Get metrics
            github = data.get('github_metrics', {})
            contract = data.get('contract_metrics', {})
            
            # Calculate GitHub score
            github_score = (
                min(github.get('stars', 0) / 1000, 1.0) * 0.3 +
                min(github.get('commits_month', 0) / 100, 1.0) * 0.4 +
                min(github.get('contributors', 0) / 20, 1.0) * 0.3
            )
            
            # Calculate contract score
            contract_score = (
                (1.0 if contract.get('audited') else 0.0) * 0.4 +
                (1.0 if contract.get('proxy') else 0.0) * 0.3 +
                min(contract.get('deployments', 0) / 5, 1.0) * 0.3
            )
            
            return (github_score + contract_score) / 2
            
        except Exception as e:
            print(f"Error analyzing tech score: {e}")
            return 0.0

    def _analyze_social_score(self, data: Dict) -> float:
        """Analyze social metrics"""
        try:
            social = data.get('social_metrics', {})
            
            # Calculate engagement scores
            twitter_score = (
                min(social.get('twitter_followers', 0) / 50000, 1.0) * 0.3 +
                min(social.get('twitter_engagement', 0) / 0.05, 1.0) * 0.7
            )
            
            telegram_score = (
                min(social.get('telegram_members', 0) / 20000, 1.0) * 0.3 +
                min(social.get('telegram_activity', 0) / 1000, 1.0) * 0.7
            )
            
            discord_score = (
                min(social.get('discord_members', 0) / 10000, 1.0) * 0.3 +
                min(social.get('discord_activity', 0) / 500, 1.0) * 0.7
            )
            
            return (
                twitter_score * 0.4 +
                telegram_score * 0.3 +
                discord_score * 0.3
            )
            
        except Exception as e:
            print(f"Error analyzing social score: {e}")
            return 0.0

    def _analyze_market_score(self, data: Dict) -> float:
        """Analyze market metrics"""
        try:
            market = data.get('market_metrics', {})
            
            # Calculate market scores
            liquidity_score = min(
                market.get('volume_24h', 0) / self.min_liquidity,
                1.0
            )
            
            holders_score = min(
                market.get('holders', 0) / 1000,
                1.0
            )
            
            distribution_score = (
                0.0 if market.get('top10_holders_pct', 100) > 80
                else (1.0 if market.get('top10_holders_pct', 100) < 40
                else (80 - market.get('top10_holders_pct', 100)) / 40)
            )
            
            return (
                liquidity_score * 0.4 +
                holders_score * 0.3 +
                distribution_score * 0.3
            )
            
        except Exception as e:
            print(f"Error analyzing market score: {e}")
            return 0.0

    def _generate_analysis(self, data: Dict, score: float) -> str:
        """Generate analysis summary"""
        try:
            strengths = []
            weaknesses = []
            
            # Technical analysis
            if data.get('github_metrics', {}).get('stars', 0) > 500:
                strengths.append("Strong GitHub presence")
            if data.get('contract_metrics', {}).get('audited'):
                strengths.append("Audited contract")
            if not data.get('contract_metrics', {}).get('proxy'):
                weaknesses.append("No upgrade capability")
                
            # Social analysis
            if data.get('social_metrics', {}).get('twitter_followers', 0) > 25000:
                strengths.append("Strong Twitter following")
            if data.get('social_metrics', {}).get('telegram_members', 0) < 5000:
                weaknesses.append("Small community")
                
            # Market analysis
            if data.get('market_metrics', {}).get('holders', 0) > 500:
                strengths.append("Healthy holder base")
            if data.get('market_metrics', {}).get('top10_holders_pct', 0) > 70:
                weaknesses.append("Concentrated holdings")
                
            analysis = f"Overall Score: {score:.2f}\n\n"
            
            if strengths:
                analysis += "Strengths:\n- " + "\n- ".join(strengths) + "\n\n"
            if weaknesses:
                analysis += "Concerns:\n- " + "\n- ".join(weaknesses)
                
            return analysis
            
        except Exception as e:
            print(f"Error generating analysis: {e}")
            return "Error generating analysis"

    def _cleanup_opportunities(self) -> None:
        """Remove old opportunities"""
        try:
            now = datetime.now()
            cutoff = now - timedelta(days=1)  # Remove opportunities older than 1 day
            
            self.opportunities = [
                opp for opp in self.opportunities
                if opp['timestamp'] > cutoff
            ]
            
        except Exception as e:
            print(f"Error cleaning up opportunities: {e}")
