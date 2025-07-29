import json
import os
from collections import defaultdict

class PromptThemeClassifier:
    def __init__(self, keywords_file='theme_keywords.json'):
        self.keywords_file = keywords_file
        self.theme_keywords = self._load_theme_keywords()

    def _load_theme_keywords(self):
        if os.path.exists(self.keywords_file):
            with open(self.keywords_file, 'r') as f:
                return json.load(f)
        # Default keywords if file doesn't exist
        return {
            "trend_following": ["trend", "momentum", "breakout", "continuation", "swing high", "swing low"],
            "mean_reversion": ["mean reversion", "oversold", "overbought", "pullback", "reversal", "bounce"],
            "volatility_breakout": ["volatility", "breakout", "range expansion", "squeeze", "implied volatility"],
            "scalping": ["scalping", "intraday", "fast moves", "quick profit", "small gains"],
            "options_strategy": ["options", "straddle", "strangle", "butterfly", "iron condor", "spread", "premium"],
            "event_driven": ["event", "earnings", "news", "announcement", "catalyst"],
            "technical_analysis": ["RSI", "MACD", "moving average", "Bollinger Bands", "support", "resistance", "chart pattern"],
            "fundamental_analysis": ["fundamental", "earnings", "revenue", "valuation", "balance sheet"],
            "arbitrage": ["arbitrage", "discrepancy", "inefficiency", "spread"],
            "sentiment_based": ["sentiment", "news analysis", "social media", "fear index", "greed index"],
            "nifty": ["Nifty", "NIFTY50", "Indian market", "NSE"],
            "banknifty": ["BankNifty", "BANKNIFTY", "Indian banking sector"],
            "sensex": ["Sensex", "SENSEX", "BSE"],
            "intraday": ["intraday", "day trading", "daily"],
            "positional": ["positional", "swing trading", "long term"],
            "hedging": ["hedging", "risk management", "portfolio protection"],
            "algo_trading": ["algo trading", "algorithmic", "automated", "HFT"],
            "macro_economic": ["macro economic", "interest rates", "inflation", "GDP", "central bank"]
        }

    def classify_prompt(self, prompt_text):
        prompt_text_lower = prompt_text.lower()
        assigned_themes = defaultdict(int)

        for theme, keywords in self.theme_keywords.items():
            for keyword in keywords:
                if keyword.lower() in prompt_text_lower:
                    assigned_themes[theme] += 1
        
        if not assigned_themes:
            return ["unclassified"]

        # Sort themes by count and return the top ones, or all if counts are equal
        sorted_themes = sorted(assigned_themes.items(), key=lambda item: item[1], reverse=True)
        
        top_score = sorted_themes[0][1]
        final_themes = [theme for theme, score in sorted_themes if score == top_score]
        
        return final_themes

    def update_theme_keywords(self, new_keywords):
        # new_keywords should be a dictionary like {"new_theme": ["keyword1", "keyword2"]}
        self.theme_keywords.update(new_keywords)
        with open(self.keywords_file, 'w') as f:
            json.dump(self.theme_keywords, f, indent=4)
        print(f"Updated theme keywords and saved to {self.keywords_file}")

    def get_all_themes(self):
        return list(self.theme_keywords.keys())

if __name__ == "__main__":
    classifier = PromptThemeClassifier()

    # Example usage
    prompt1 = "Develop an intraday scalping strategy for Nifty options using RSI and MACD for quick profits."
    themes1 = classifier.classify_prompt(prompt1)
    print(f"Prompt: '{prompt1}'\nThemes: {themes1}\n")

    prompt2 = "Create a mean reversion strategy for BankNifty when it's oversold, looking for a bounce."
    themes2 = classifier.classify_prompt(prompt2)
    print(f"Prompt: '{prompt2}'\nThemes: {themes2}\n")

    prompt3 = "Design a long-term trend following strategy for Sensex stocks based on moving average crossovers."
    themes3 = classifier.classify_prompt(prompt3)
    print(f"Prompt: '{prompt3}'\nThemes: {themes3}\n")

    prompt4 = "Analyze the impact of central bank announcements on currency pairs using sentiment analysis."
    themes4 = classifier.classify_prompt(prompt4)
    print(f"Prompt: '{prompt4}'\nThemes: {themes4}\n")

    prompt5 = "A simple prompt with no specific keywords."
    themes5 = classifier.classify_prompt(prompt5)
    print(f"Prompt: '{prompt5}'\nThemes: {themes5}\n")

    # Example of updating keywords
    # classifier.update_theme_keywords({"new_trading_style": ["custom_keyword", "another_term"]})
    # print(f"All available themes: {classifier.get_all_themes()}")

    # You can also manually create or edit theme_keywords.json to customize themes and keywords