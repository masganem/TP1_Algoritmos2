import pandas as pd

INPUT_PATH = 'data/geocoded_bars_and_restaurants.csv'
OUTPUT_PATH = 'data/geocoded_bars_and_restaurants_dedup.csv'


def main() -> None:
    # Load dataset
    df = pd.read_csv(INPUT_PATH, sep=';')

    # Drop duplicate names (case-sensitive comparison)
    dedup_df = df.drop_duplicates(subset='NOME', keep='first')

    # Save result
    dedup_df.to_csv(OUTPUT_PATH, sep=';', index=False)
    print(f'Deduplicated file saved to {OUTPUT_PATH} (rows reduced from {len(df)} to {len(dedup_df)}).')


if __name__ == '__main__':
    main()
 