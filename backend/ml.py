import joblib
import pandas as pd
import numpy as np
import os
import shap

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fraud_detection_artifacts.pkl")

class FraudModel:
    def __init__(self):
        self.model = None
        self.explainer = None
        self.error = None
        
        try:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
                
            loaded_data = joblib.load(MODEL_PATH)
            if isinstance(loaded_data, dict):
                print("Loaded artifacts dict. Keys:", loaded_data.keys())
                # Try to extract the model or pipeline
                self.model = loaded_data.get("model", loaded_data.get("pipeline", None))
                if self.model is None:
                    # Fallback to first item
                    self.model = list(loaded_data.values())[0]
            else:
                self.model = loaded_data
                
            print("Model loaded successfully! Type:", type(self.model))
            
            if hasattr(self.model, "named_steps"):
                steps = list(self.model.named_steps.keys())
                classifier = self.model.named_steps[steps[-1]]
                
                # Monkey-patch XGBoost version mismatch
                if not hasattr(classifier, 'use_label_encoder'):
                    classifier.use_label_encoder = False
                if not hasattr(classifier, 'gpu_id'):
                    classifier.gpu_id = -1
                if not hasattr(classifier, 'interaction_constraints'):
                    classifier.interaction_constraints = None
                if not hasattr(classifier, 'monotone_constraints'):
                    classifier.monotone_constraints = None
                if not hasattr(classifier, 'predictor'):
                    classifier.predictor = None
                if not hasattr(classifier, 'enable_categorical'):
                    classifier.enable_categorical = False
                if not hasattr(classifier, 'callbacks'):
                    classifier.callbacks = None
                if not hasattr(classifier, 'classes_'):
                    classifier.classes_ = np.array([0, 1])
                    
                self.explainer = shap.TreeExplainer(classifier)
            else:
                # Monkey-patch XGBoost version mismatch
                if not hasattr(self.model, 'use_label_encoder'):
                    self.model.use_label_encoder = False
                if not hasattr(self.model, 'gpu_id'):
                    self.model.gpu_id = -1
                if not hasattr(self.model, 'interaction_constraints'):
                    self.model.interaction_constraints = None
                if not hasattr(self.model, 'monotone_constraints'):
                    self.model.monotone_constraints = None
                if not hasattr(self.model, 'predictor'):
                    self.model.predictor = None
                if not hasattr(self.model, 'enable_categorical'):
                    self.model.enable_categorical = False
                if not hasattr(self.model, 'callbacks'):
                    self.model.callbacks = None
                if not hasattr(self.model, 'classes_'):
                    self.model.classes_ = np.array([0, 1])
                    
                self.explainer = shap.TreeExplainer(self.model)
                
        except Exception as e:
            self.error = str(e)
            print("CRITICAL ERROR: Failed to load model or SHAP explainer.", e)
            
    def predict(self, features_dict):
        if self.model is None:
            raise RuntimeError(f"Model is not loaded. Initialization Error: {self.error}")
            
        df = pd.DataFrame([features_dict])
        
        # Ensure all columns exist (V1-V28, Time, Amount)
        for i in range(1, 29):
            col = f"V{i}"
            if col not in df.columns:
                df[col] = 0.0
        if "Time" not in df.columns: df["Time"] = 0.0
        if "Amount" not in df.columns: df["Amount"] = 0.0
            
        # Reorder columns to standard Credit Card Fraud dataset format
        cols = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
        df = df[cols]
        
        # ML Prediction
        prob = float(self.model.predict_proba(df)[0][1])
        pred = int(prob > 0.5)
        
        # SHAP Values
        if self.explainer:
            # Transform df if it's a pipeline
            X_transformed = df.copy()
            if hasattr(self.model, "named_steps"):
                steps = list(self.model.named_steps.keys())
                for name, step in self.model.named_steps.items():
                    if name != steps[-1]:  # Skip the final estimator
                        if hasattr(step, "transform"):
                            X_transformed = step.transform(X_transformed)
            
            shap_values = self.explainer.shap_values(X_transformed)
            # Depending on the XGBoost version/objective, shap_values might be a list or array
            if isinstance(shap_values, list):
                shap_vals = shap_values[1][0] # for binary classification it might be a list of 2 arrays
            else:
                if len(shap_values.shape) == 3:
                    shap_vals = shap_values[0, :, 1]
                else:
                    shap_vals = shap_values[0]
                    
            shap_dict = {cols[i]: float(shap_vals[i]) for i in range(len(cols))}
        else:
            shap_dict = {}
            
        # Sort SHAP dict by absolute value to get top drivers
        sorted_shap = dict(sorted(shap_dict.items(), key=lambda item: abs(item[1]), reverse=True)[:5])
        return prob, pred, sorted_shap

    def predict_batch(self, df):
        if self.model is None:
            raise RuntimeError(f"Model is not loaded. Initialization Error: {self.error}")
        
        # Ensure all columns exist (V1-V28, Time, Amount)
        for i in range(1, 29):
            col = f"V{i}"
            if col not in df.columns:
                df[col] = 0.0
        if "Time" not in df.columns: df["Time"] = 0.0
        if "Amount" not in df.columns: df["Amount"] = 0.0
            
        cols = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
        df = df[cols]
        
        # ML Prediction (Vectorized)
        probs = self.model.predict_proba(df)[:, 1]
        preds = (probs > 0.5).astype(int)
        
        return probs.tolist(), preds.tolist()
