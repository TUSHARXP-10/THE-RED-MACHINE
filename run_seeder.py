import argparse
from prompt_seeder import PromptSeeder
from gpt_strategy_suggestor import GPTStrategySuggestor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate prompt seeding and GPT strategy suggestion.")
    parser.add_argument('--num_prompts', type=int, default=5, help='Number of top prompts to use for seeding.')
    parser.add_argument('--sort_by', type=str, default='avg_sharpe', help='Metric to sort prompts by (e.g., avg_sharpe, cumulative_pnl, victory_rate).')
    parser.add_argument('--min_strategies', type=int, default=1, help='Minimum number of strategies a prompt must have to be considered.')
    parser.add_argument('--gpt_prompt', type=str, default="Generate a new, innovative trading strategy.", help='The prompt to send to the GPT model.')
    parser.add_argument('--include_themes', type=str, help='Comma-separated list of themes to include (e.g., "sensex,intraday").')
    parser.add_argument('--exclude_themes', type=str, help='Comma-separated list of themes to exclude (e.g., "nifty,scalping").')
    parser.add_argument('--filter_regime', type=str, help='Filter prompts by a specific market regime (e.g., "uptrend", "rangebound").')

    args = parser.parse_args()

    # Process theme arguments
    include_themes_list = [theme.strip() for theme in args.include_themes.split(',')] if args.include_themes else None
    exclude_themes_list = [theme.strip() for theme in args.exclude_themes.split(',')] if args.exclude_themes else None

    # Initialize PromptSeeder and GPTStrategySuggestor
    seeder = PromptSeeder()
    suggestor = GPTStrategySuggestor(prompt_seeder=seeder)

    print(f"\n--- Running Seeder with {args.num_prompts} top prompts sorted by {args.sort_by} ---")
    if include_themes_list:
        print(f"Including themes: {', '.join(include_themes_list)}")
    if exclude_themes_list:
        print(f"Excluding themes: {', '.join(exclude_themes_list)}")

    # Generate strategy suggestion using the seeded prompt
    suggestion = suggestor.generate_strategy_suggestion(
        prompt=args.gpt_prompt,
        num_seed_prompts=args.num_prompts,
        seed_sort_by=args.sort_by,
        min_seed_strategies=args.min_strategies,
        include_themes=include_themes_list,
        exclude_themes=exclude_themes_list,
        filter_regime=args.filter_regime
    )

    if suggestion and suggestion["parsed_suggestion"]:
        print("\nParsed Suggestion:")
        for key, value in suggestion["parsed_suggestion"].items():
            print(f"  {key}: {value}")
    else:
        print("\nFailed to generate or parse suggestion.")