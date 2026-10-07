import json
from pathlib import Path

import pandas as pd
from xgboost import XGBClassifier


class ModelPredictionService:

    def __init__(self):

        model_path = Path(
            "models/interviewguard_xgboost.json"
        )

        feature_path = Path(
            "models/interviewguard_features.json"
        )

        self.model = XGBClassifier()

        self.model.load_model(
            model_path
        )

        with open(
            feature_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.features = json.load(file)

    def predict(self, features):

        missing_features = [
            feature
            for feature in self.features
            if feature not in features
        ]

        if missing_features:

            return {
                "prediction_available": False,

                "reason": "missing_features",

                "missing_features": (
                    missing_features
                ),
            }

        dataframe = pd.DataFrame(
            [
                {
                    feature: features[feature]
                    for feature in self.features
                }
            ],
            columns=self.features,
        )

        prediction = int(
            self.model.predict(
                dataframe
            )[0]
        )

        probabilities = (
            self.model.predict_proba(
                dataframe
            )[0]
        )

        return {

            "prediction_available": True,

            "prediction": prediction,

            "probability_normal": round(
                float(probabilities[0]),
                4
            ),

            "probability_suspicious": round(
                float(probabilities[1]),
                4
            ),
        }