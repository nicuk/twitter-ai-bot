"""
Advanced project analysis system for Elion AI
Uses multi-factor analysis to evaluate crypto projects with extremely high standards
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class ProjectAnalyzer:
    def __init__(self, data_sources, llm):
        self.data_sources = data_sources
        self.llm = llm
        
        # Weights for different categories (total = 100)
        self.weights = {
            'fundamentals': 35,
            'tokenomics': 25,
            'market_metrics': 20,
            'social_signals': 15,
            'early_shill_bonus': 5  # Bonus for early shills
        }
        
        # Minimum thresholds that must ALL be met
        self.minimum_thresholds = {
            'github_commits_week': 10,     # Minimum weekly commits
            'liquidity_ratio': 0.15,       # Liquidity/Market Cap
            'holder_distribution': 0.6,     # Gini coefficient (lower is better)
            'team_tokens_locked': 0.8,      # % of team tokens locked
            'unique_value_prop': 0.7,       # Uniqueness score
            'security_score': 0.8           # Security audit score
        }
        
        # Track shills per project
        self.project_shills = {}  # {project_id: [shill_count, first_shill_position]}

    def analyze_project(self, project_id: str, shill_position: int) -> Dict:
        """Deep analysis of a project using LLM"""
        try:
            # Get project data
            project_data = self.data_sources.get_coin_details(project_id)
            if not project_data:
                return self._format_rejection("Insufficient data available")

            # Check if token is live and tradeable
            if not self._is_token_live(project_data):
                return self._format_rejection("Token not live yet. Come back after launch!")

            # Track shill position
            if project_id not in self.project_shills:
                self.project_shills[project_id] = [1, shill_position]
            else:
                self.project_shills[project_id][0] += 1

            # Use LLM for deep analysis
            analysis_prompt = self._create_analysis_prompt(project_data)
            analysis_result = self.llm.analyze(analysis_prompt)
            
            # Extract scores and insights
            scores = self._parse_llm_analysis(analysis_result)
            
            # Add early shill bonus
            scores['early_shill_bonus'] = self._calculate_early_bonus(shill_position)
            
            # Calculate final score
            final_score = self._calculate_weighted_score(scores)

            return {
                'name': project_data['name'],
                'symbol': project_data['symbol'],
                'score': final_score,
                'detailed_scores': scores,
                'analysis': analysis_result['analysis'],
                'market_data': self._get_market_data(project_data),
                'conviction_level': self._get_conviction_level(final_score),
                'shill_position': shill_position,
                'is_live': True
            }

        except Exception as e:
            print(f"Error analyzing project: {e}")
            return self._format_rejection("Error during analysis")

    def _create_analysis_prompt(self, data: Dict) -> str:
        """Create prompt for LLM analysis"""
        return f"""Analyze this crypto project as an AI trading expert. Score each category from 0-100 and provide detailed reasoning:

Project: {data['name']} (${data['symbol']})

Key Data:
- Market Cap: ${data.get('market_cap', 'N/A')}
- 24h Volume: ${data.get('volume24h', 'N/A')}
- Liquidity: ${data.get('liquidity', 'N/A')}
- Holders: {data.get('holder_count', 'N/A')}
- Contract Verified: {data.get('contract_verified', False)}

Social Metrics:
- Twitter Engagement: {data.get('twitter_engagement', 'N/A')}
- Telegram Growth: {data.get('telegram_growth', 'N/A')}
- Community Sentiment: {data.get('sentiment_score', 'N/A')}

Technical:
- Github Activity: {data.get('github_commits_week', 'N/A')}
- Security Score: {data.get('security_score', 'N/A')}
- Unique Value Prop: {data.get('unique_value_prop', 'N/A')}

Analyze and score:
1. Fundamentals (0-100)
2. Tokenomics (0-100)
3. Market Metrics (0-100)
4. Social Signals (0-100)

Provide a detailed analysis explaining the scores and any potential red flags."""

    def _parse_llm_analysis(self, llm_response: Dict) -> Dict:
        """Parse LLM analysis into structured scores"""
        scores = {
            'fundamentals': llm_response['scores']['fundamentals'],
            'tokenomics': llm_response['scores']['tokenomics'],
            'market_metrics': llm_response['scores']['market_metrics'],
            'social_signals': llm_response['scores']['social_signals']
        }
        return scores

    def _calculate_weighted_score(self, scores: dict) -> float:
        """Calculate weighted final score"""
        final_score = 0.0
        for category, score in scores.items():
            weight = self.weights.get(category, 0)
            final_score += score * (weight / 100)
        return round(final_score, 2)

    def _calculate_early_bonus(self, position: int) -> float:
        """Calculate bonus score for early shills (0-100 scale)"""
        if position == 1:
            return 100  # First shill gets max bonus
        elif position == 2:
            return 60   # Second shill gets 60%
        elif position == 3:
            return 30   # Third shill gets 30%
        return 0        # No bonus after third shill

    def _get_conviction_level(self, score: float) -> str:
        """Get conviction level based on score (0-100 scale)"""
        if score >= 85:
            return "EXTREMELY HIGH"
        elif score >= 75:
            return "HIGH"
        elif score >= 65:
            return "MODERATE"
        else:
            return "LOW"

    def _format_rejection(self, reason: str) -> Dict:
        """Format rejection response"""
        return {
            'score': 0,
            'conviction_level': 'REJECTED',
            'analysis': f"Project rejected - {reason}",
            'detailed_scores': None,
            'market_data': None
        }

    def _generate_analysis_report(self, scores: Dict, data: Dict) -> str:
        """Generate detailed analysis report"""
        strengths = []
        weaknesses = []
        
        # Analyze each category (now on 0-100 scale)
        for category, score in scores.items():
            if score >= 80:
                strengths.append(f"Exceptional {category}: {score}/100")
            elif score <= 50:
                weaknesses.append(f"Concerning {category}: {score}/100")
        
        report = []
        if strengths:
            report.append("Strengths:\n- " + "\n- ".join(strengths))
        if weaknesses:
            report.append("Areas for Improvement:\n- " + "\n- ".join(weaknesses))
            
        # Add shill position context
        if scores.get('early_shill_bonus', 0) > 0:
            report.append(f"\nEarly Shill Bonus: +{scores['early_shill_bonus']}%")
            
        return "\n\n".join(report)

    def _get_market_data(self, data: Dict) -> Dict:
        """Extract relevant market data"""
        return {
            'market_cap': data.get('market_cap', 0),
            'volume': data.get('volume_24h', 0),
            'price_change': data.get('price_change_24h', 0)
        }

    def _is_token_live(self, data: Dict) -> bool:
        """Check if token is live and tradeable"""
        try:
            # Check if token has price data
            if not data.get('values', {}).get('USD', {}).get('price'):
                return False

            # Check if token has trading volume
            if not data.get('values', {}).get('USD', {}).get('volume24h'):
                return False

            # Check if token has liquidity
            if not data.get('values', {}).get('USD', {}).get('liquidity'):
                return False

            # Check if token contract is verified
            if not data.get('contract_verified', False):
                return False

            return True
        except Exception:
            return False

    def _check_red_flags(self, data: Dict) -> List:
        """Check for red flags"""
        red_flags = []
        if data.get('copy_paste_code', False):
            red_flags.append('copy_paste_code')
        if data.get('single_wallet_dominance', False):
            red_flags.append('single_wallet_dominance')
        if data.get('wash_trading', False):
            red_flags.append('wash_trading')
        if data.get('no_security_audit', False):
            red_flags.append('no_security_audit')
        if data.get('anon_team_no_reputation', False):
            red_flags.append('anon_team_no_reputation')
        if data.get('plagiarized_docs', False):
            red_flags.append('plagiarized_docs')
        return red_flags

    def _check_minimum_thresholds(self, data: Dict) -> List:
        """Check minimum thresholds"""
        failed_thresholds = []
        if data.get('github_commits_week', 0) < self.minimum_thresholds['github_commits_week']:
            failed_thresholds.append('github_commits_week')
        if data.get('liquidity_ratio', 0) < self.minimum_thresholds['liquidity_ratio']:
            failed_thresholds.append('liquidity_ratio')
        if data.get('holder_distribution', 0) < self.minimum_thresholds['holder_distribution']:
            failed_thresholds.append('holder_distribution')
        if data.get('team_tokens_locked', 0) < self.minimum_thresholds['team_tokens_locked']:
            failed_thresholds.append('team_tokens_locked')
        if data.get('unique_value_prop', 0) < self.minimum_thresholds['unique_value_prop']:
            failed_thresholds.append('unique_value_prop')
        if data.get('security_score', 0) < self.minimum_thresholds['security_score']:
            failed_thresholds.append('security_score')
        return failed_thresholds

    # Add implementation for all the _analyze_* methods
    # Each should return a score from 0-1 based on sophisticated metrics
