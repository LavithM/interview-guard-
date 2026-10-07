import json
from pathlib import Path

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from xgboost import XGBClassifier


DATASET_FILE = Path(
    "dataset/processed/interviewguard_training.csv"
)

MODEL_DIRECTORY = Path(
    "models"
)

MODEL_FILE = (
    MODEL_DIRECTORY
    / "interviewguard_xgboost.json"
)

FEATURE_FILE = (
    MODEL_DIRECTORY
    / "interviewguard_features.json"
)


FEATURES = [

    "face_present",
    "no_of_face",

    "face_conf",

    "hand_count",
    "hand_obj_interaction",

    "head_pitch",
    "head_yaw",
    "head_roll",

    "phone_present",
    "phone_conf",

    "gaze_on_script",
    "gaze_direction",

    "gazePoint_x",
    "gazePoint_y",

    "pupil_left_x",
    "pupil_left_y",

    "pupil_right_x",
    "pupil_right_y",
]


TARGET = "label"


def main():

    print("Loading dataset...")

    df = pd.read_csv(
        DATASET_FILE
    )

    print(
        "Dataset shape:",
        df.shape
    )

    X = df[FEATURES]

    y = df[TARGET]

    print(
        "Features:",
        len(FEATURES)
    )

    print(
        "Samples:",
        len(df)
    )

    # --------------------------------------------------
    # 80% training
    # 10% validation
    # 10% testing
    # --------------------------------------------------

    X_train, X_temp, y_train, y_temp = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )
    )

    X_validation, X_test, y_validation, y_test = (
        train_test_split(
            X_temp,
            y_temp,
            test_size=0.50,
            random_state=42,
            stratify=y_temp,
        )
    )

    print()
    print("Training samples:", len(X_train))
    print(
        "Validation samples:",
        len(X_validation)
    )
    print(
        "Test samples:",
        len(X_test)
    )

    # --------------------------------------------------
    # Create XGBoost model
    # --------------------------------------------------

    print()
    print("Creating XGBoost model...")

    model = XGBClassifier(

        n_estimators=200,

        max_depth=5,

        learning_rate=0.05,

        subsample=0.8,

        colsample_bytree=0.8,

        objective="binary:logistic",

        eval_metric="logloss",

        random_state=42,

        n_jobs=4,
    )

    # --------------------------------------------------
    # Train
    # --------------------------------------------------

    print()
    print("Training model...")

    model.fit(
        X_train,
        y_train,
        eval_set=[
            (
                X_validation,
                y_validation
            )
        ],
        verbose=False,
    )

    print(
        "Training completed."
    )

    # --------------------------------------------------
    # Validation evaluation
    # --------------------------------------------------

    validation_predictions = (
        model.predict(
            X_validation
        )
    )

    validation_accuracy = (
        accuracy_score(
            y_validation,
            validation_predictions
        )
    )

    validation_precision = (
        precision_score(
            y_validation,
            validation_predictions,
            zero_division=0
        )
    )

    validation_recall = (
        recall_score(
            y_validation,
            validation_predictions,
            zero_division=0
        )
    )

    validation_f1 = (
        f1_score(
            y_validation,
            validation_predictions,
            zero_division=0
        )
    )

    print()
    print("========== VALIDATION ==========")

    print(
        "Accuracy:",
        round(
            validation_accuracy,
            4
        )
    )

    print(
        "Precision:",
        round(
            validation_precision,
            4
        )
    )

    print(
        "Recall:",
        round(
            validation_recall,
            4
        )
    )

    print(
        "F1:",
        round(
            validation_f1,
            4
        )
    )

    # --------------------------------------------------
    # Final test evaluation
    # --------------------------------------------------

    test_predictions = (
        model.predict(
            X_test
        )
    )

    test_accuracy = (
        accuracy_score(
            y_test,
            test_predictions
        )
    )

    test_precision = (
        precision_score(
            y_test,
            test_predictions,
            zero_division=0
        )
    )

    test_recall = (
        recall_score(
            y_test,
            test_predictions,
            zero_division=0
        )
    )

    test_f1 = (
        f1_score(
            y_test,
            test_predictions,
            zero_division=0
        )
    )

    print()
    print("========== TEST ==========")

    print(
        "Accuracy:",
        round(
            test_accuracy,
            4
        )
    )

    print(
        "Precision:",
        round(
            test_precision,
            4
        )
    )

    print(
        "Recall:",
        round(
            test_recall,
            4
        )
    )

    print(
        "F1:",
        round(
            test_f1,
            4
        )
    )

    # --------------------------------------------------
    # Classification report
    # --------------------------------------------------

    print()
    print("========== CLASSIFICATION REPORT ==========")

    print(
        classification_report(
            y_test,
            test_predictions,
            zero_division=0
        )
    )

    # --------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------

    matrix = confusion_matrix(
        y_test,
        test_predictions
    )

    print(
        "========== CONFUSION MATRIX =========="
    )

    print(matrix)

    # --------------------------------------------------
    # Feature importance
    # --------------------------------------------------

    importance = (
        model.feature_importances_
    )

    feature_importance = sorted(
        zip(
            FEATURES,
            importance
        ),
        key=lambda item: item[1],
        reverse=True
    )

    print()
    print(
        "========== FEATURE IMPORTANCE =========="
    )

    for feature, score in feature_importance:

        print(
            f"{feature}: "
            f"{score:.4f}"
        )

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    model.save_model(
        MODEL_FILE
    )

    # Save feature order separately.
    with open(
        FEATURE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            FEATURES,
            file,
            indent=4
        )

    print()
    print(
        "Model saved:"
    )

    print(
        MODEL_FILE
    )

    print()
    print(
        "Feature list saved:"
    )

    print(
        FEATURE_FILE
    )


if __name__ == "__main__":
    main()