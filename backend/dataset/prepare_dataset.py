import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    "dataset/raw/Students suspicious behaviors detection dataset_V1.csv"
)

OUTPUT_FILE = Path(
    "dataset/processed/interviewguard_training.csv"
)


def main():

    print("Loading dataset...")

    df = pd.read_csv(INPUT_FILE)

    print("Original shape:", df.shape)

    # Convert categorical columns into numeric values.
    head_pose_mapping = {
        "forward": 0,
        "left": -1,
        "right": 1,
        "down": 2,
    }

    gaze_direction_mapping = {
        "center": 0,
        "top_left": 1,
        "top_right": 2,
        "bottom_left": 3,
        "bottom_right": 4,
    }

    df["head_pose"] = (
        df["head_pose"]
        .map(head_pose_mapping)
        .fillna(-1)
    )

    df["gaze_direction"] = (
        df["gaze_direction"]
        .map(gaze_direction_mapping)
        .fillna(-1)
    )

    # Fill remaining missing numeric values
    # using the median of each column.
    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for column in numeric_columns:

        if column == "label":
            continue

        median_value = df[column].median()

        df[column] = df[column].fillna(
            median_value
        )

    # Make sure the label is numeric.
    df["label"] = df["label"].astype(int)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Processed dataset created.")
    print("Output:", OUTPUT_FILE)
    print("Shape:", df.shape)

    print()
    print("Missing values after preprocessing:")

    missing = df.isnull().sum()

    remaining_missing = (
        missing[missing > 0]
    )

    if len(remaining_missing) == 0:
        print("None")
    else:
        print(remaining_missing)

    print()
    print("Label distribution:")
    print(df["label"].value_counts())


if __name__ == "__main__":
    main()