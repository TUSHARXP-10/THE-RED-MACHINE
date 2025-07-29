import pandas as pd
import argparse
from imblearn.over_sampling import SMOTE

def balance_data(df):
    """
    Applies SMOTE for class balancing on the input DataFrame.
    Assumes 'target' is the column to be balanced.
    """
    if 'target' not in df.columns:
        print("Error: 'target' column not found in the DataFrame.")
        return pd.DataFrame()

    X = df.drop('target', axis=1)
    y = df['target']

    # Drop non-numeric columns before applying SMOTE
    X = X.select_dtypes(include=['number'])

    print(f"Original class distribution: {pd.Series(y).value_counts(normalize=True)}")

    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)

    balanced_df = pd.concat([X_res, y_res.rename('target')], axis=1)
    print(f"After SMOTE, new sample size: {len(balanced_df)}")
    print(f"Balanced class distribution: {pd.Series(y_res).value_counts(normalize=True)}")

    return balanced_df

def main():
    parser = argparse.ArgumentParser(description="Data Balancing Script using SMOTE")
    parser.add_argument('--input', type=str, required=True, help='Path to the input CSV file (e.g., augmented_data.csv).')
    parser.add_argument('--output', type=str, default='balanced_data.csv', help='Path to save the balanced data CSV file.')
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.input)
        print(f"Loaded {len(df)} samples from {args.input}")
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        return
    except Exception as e:
        print(f"Error loading input file: {e}")
        return

    balanced_df = balance_data(df)

    if not balanced_df.empty:
        balanced_df.to_csv(args.output, index=False)
        print(f"Balanced data saved to {args.output}.")
    else:
        print("No balanced data generated.")

if __name__ == "__main__":
    main()