"""
AI-Based Automatic Antenna Designer
Module: Machine Learning RF Surrogate Model Engine
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import os
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

class RFSurrogateModel:
    def __init__(self, dataset_path=None):
        if dataset_path is None:
            dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "microstrip_rf_dataset.csv")
        
        self.dataset_path = dataset_path
        self.feature_names = ['patch_length_mm', 'patch_width_mm', 'feed_offset_mm', 'substrate_er', 'substrate_height_mm']
        self.model_f_res = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model_s11 = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model_gain = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model_bw = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False
        
        self.train()

    def train(self):
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"RF Dataset not found at {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)
        X = df[self.feature_names]

        self.model_f_res.fit(X, df['f_res_ghz'])
        self.model_s11.fit(X, df['s11_db'])
        self.model_gain.fit(X, df['gain_dbi'])
        self.model_bw.fit(X, df['bandwidth_mhz'])
        self.is_trained = True

    def predict(self, patch_length_mm, patch_width_mm, feed_offset_mm, substrate_er=4.4, substrate_h_mm=1.6):
        """
        Predicts RF parameters (f_res, S11, Gain, BW, VSWR) in < 1ms using trained ML Surrogate.
        """
        X_test = pd.DataFrame([[patch_length_mm, patch_width_mm, feed_offset_mm, substrate_er, substrate_h_mm]], columns=self.feature_names)
        
        f_res = float(self.model_f_res.predict(X_test)[0])
        s11 = float(self.model_s11.predict(X_test)[0])
        gain = float(self.model_gain.predict(X_test)[0])
        bw = float(self.model_bw.predict(X_test)[0])

        # VSWR calculation formula from S11 DB
        gamma = 10.0 ** (s11 / 20.0)
        vswr = (1.0 + gamma) / (1.0 - gamma) if gamma < 1.0 else 1.05

        return {
            "predicted_f_res_ghz": round(f_res, 3),
            "predicted_s11_db": round(s11, 2),
            "predicted_gain_dbi": round(gain, 2),
            "predicted_bandwidth_mhz": round(bw, 1),
            "predicted_vswr": round(vswr, 2)
        }
