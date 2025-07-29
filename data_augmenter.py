import pandas as pd
import numpy as np
import argparse

def augment_data(df, scale_factor=10):
    """
    Augments the dataset by generating synthetic samples.
    """
    if df.empty:
        print("Input DataFrame is empty. Cannot augment data.")
        return pd.DataFrame()

    augmented_data = []
    for _ in range(scale_factor):
        for index, row in df.iterrows():
            # Add small random noise to numerical features
            new_row = row.copy()
            # Augment numerical features, but keep 'target' column as is
            for col in df.select_dtypes(include=[np.number]).columns:
                if col != 'target': # Exclude target from augmentation
                    noise = np.random.normal(0, 0.01 * df[col].std() if df[col].std() > 0 else 0.01, 1)[0]
                    new_row[col] = row[col] + noise
                else:
                    new_row[col] = row[col] # Keep target column unchanged
            augmented_data.append(new_row)

    augmented_df = pd.DataFrame(augmented_data)

    # Reset index to avoid duplicate label issues
    df = df.reset_index(drop=True)
    augmented_df = augmented_df.reset_index(drop=True)

    # Ensure 'last_traded_price' is present for target calculation
    if 'last_traded_price' in df.columns:
        # Calculate target for the original data if not present
        if 'target' not in df.columns:
            df['target'] = (df['last_traded_price'].shift(-1) > df['last_traded_price']).astype(int)
            df = df.dropna(subset=['target'])

        # Calculate target for augmented data
        if 'target' not in augmented_df.columns and 'last_traded_price' in augmented_df.columns:
            augmented_df['target'] = (augmented_df['last_traded_price'].shift(-1) > augmented_df['last_traded_price']).astype(int)
            augmented_df = augmented_df.dropna(subset=['target'])

    return pd.concat([df, augmented_df], ignore_index=True)

def main():
    parser = argparse.ArgumentParser(description="Data Augmentation Script")
    parser.add_argument('--input', type=str, required=True, help='Path to the input historical data CSV file.')
    parser.add_argument('--output', type=str, default='augmented_data.csv', help='Path to save the augmented data CSV file.')
    parser.add_argument('--scale', type=int, default=10, help='Scale factor for data augmentation (e.g., 10x synthetic samples).')
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

    augmented_df = augment_data(df, args.scale)

    if not augmented_df.empty:
        augmented_df.to_csv(args.output, index=False)
        print(f"Augmented data saved to {args.output} with {len(augmented_df)} samples.")
    else:
        print("No augmented data generated.")

if __name__ == "__main__":
    main()