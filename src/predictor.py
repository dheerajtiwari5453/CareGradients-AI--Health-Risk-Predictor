import os
import joblib
import pandas as pd
import numpy as np

class HealthRiskPredictor:
    """
    Main model registry and prediction engine. Loads disease classification models,
    encodes input variables, aligns clinical data schemas, and computes risk probabilities.
    """
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.models = {}
        self.encoders = {}
        self.feature_lists = {}
        
        self._load_artifacts()

    def _load_artifacts(self):
        """
        Loads pre-trained XGBoost classifiers, ordinal category encoders,
        and target feature lists from the joblib binaries.
        """
        diseases = {
            "heart": ("heart_disease_xgb.joblib", "heart_encoder.joblib", "heart_features.joblib"),
            "diabetes": ("diabetes_xgb.joblib", "diabetes_encoder.joblib", "diabetes_features.joblib"),
            "stroke": ("stroke_xgb.joblib", "stroke_encoder.joblib", "stroke_features.joblib")
        }
        
        for key, (model_file, encoder_file, features_file) in diseases.items():
            model_path = os.path.join(self.models_dir, model_file)
            encoder_path = os.path.join(self.models_dir, encoder_file)
            features_path = os.path.join(self.models_dir, features_file)
            
            if not (os.path.exists(model_path) and os.path.exists(encoder_path) and os.path.exists(features_path)):
                raise FileNotFoundError(f"Missing model files for {key} in directory: {self.models_dir}")
                
            self.models[key] = joblib.load(model_path)
            self.encoders[key] = joblib.load(encoder_path)
            self.feature_lists[key] = joblib.load(features_path)

    def preprocess_and_align(self, patient_profile: dict, disease_key: str) -> pd.DataFrame:
        """
        Translates raw input features into the schema and formatting expected by
        each individual classifier. Corrects casing mismatch for the categorical encoder.
        """
        df = pd.DataFrame([patient_profile])
        
        # Normalize BMI category to lowercase as expected by the trained encoder
        if "BMI_cat" in df.columns and isinstance(df["BMI_cat"].values[0], str):
            df["BMI_cat"] = df["BMI_cat"].str.lower()
            
        # Standardize gender format to floats matching the encoder categories [0., 1.]
        if "gender" in df.columns:
            first_val = df["gender"].values[0]
            if isinstance(first_val, str):
                df["gender"] = df["gender"].apply(lambda val: 1.0 if str(val).lower() == "male" else 0.0)
            else:
                df["gender"] = df["gender"].astype(float)
                
        # Transform categorical values
        encoder = self.encoders[disease_key]
        categorical_columns = [col for col in ["gender", "BMI_cat"] if col in df.columns]
        
        df_encoded = df.copy()
        if categorical_columns:
            df_encoded[categorical_columns] = encoder.transform(df_encoded[categorical_columns])
            
        # Re-index to align with model feature schema, filling missing values with 0.0
        model_features = self.feature_lists[disease_key]
        aligned_df = pd.DataFrame(0.0, index=[0], columns=model_features)
        
        for col in df_encoded.columns:
            if col in aligned_df.columns:
                aligned_df[col] = df_encoded[col].values
                
        return aligned_df

    def predict_risk(self, patient_profile: dict, disease_key: str) -> float:
        """
        Scores a clinical patient profile against a specific disease model.
        """
        aligned_df = self.preprocess_and_align(patient_profile, disease_key)
        model = self.models[disease_key]
        probability = model.predict_proba(aligned_df)[:, 1][0]
        return float(probability)

    def calculate_composite_risk(self, heart_prob: float, diabetes_prob: float, stroke_prob: float) -> float:
        """
        Determines the weighted composite health risk index:
        - Heart Disease: 40%
        - Diabetes: 35%
        - Stroke: 25%
        """
        weighted_val = (0.40 * heart_prob) + (0.35 * diabetes_prob) + (0.25 * stroke_prob)
        return round(weighted_val * 100, 2)
