from sklearn.ensemble import IsolationForest
import numpy as np

class AdvancedHealthMonitor:
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.metrics_history = []

    def train_detector(self):
        if len(self.metrics_history) < 100:
            return False

        data = np.array(self.metrics_history)
        self.isolation_forest.fit(data)
        return True

    def detect_anomalies(self, new_metrics):
        if not self.metrics_history:
            return False

        prediction = self.isolation_forest.predict([new_metrics])
        return prediction[0] == -1  # -1 indicates anomaly

    async def predict_failures(self, time_window=3600):
        #"""Predict potential failures in next hour#"""
        recent_data = self.metrics_history[-100:]  # Last 100 readings
        anomaly_scores = self.isolation_forest.score_samples(recent_data)

        # Trending towards failure if scores decreasing
        trend = np.polyfit(range(len(anomaly_scores)), anomaly_scores, 1)[0]
        return trend < -0.1  # Negative trend indicates increasing anomalies


