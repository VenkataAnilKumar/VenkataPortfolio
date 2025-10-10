# ai_adapter.py
"""
This module provides AI/ML utilities for text classification using scikit-learn.
"""
from typing import List
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

# Paths for model persistence (for MVP, models can be trained on startup or loaded if available)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_models")
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "text_classifier.joblib")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# --- Text Classification ---
class TextClassifier:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(CLASSIFIER_PATH) and os.path.exists(VECTORIZER_PATH):
            self.model = joblib.load(CLASSIFIER_PATH)
            self.vectorizer = joblib.load(VECTORIZER_PATH)
        else:
            # For MVP: train on dummy data
            self._train_on_dummy()

    def _train_on_dummy(self):
        texts = ["fraudulent transaction", "customer dispute", "merchant error", "legitimate purchase"]
        labels = [1, 1, 1, 0]  # 1=dispute, 0=not dispute
        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression()
        self.model.fit(X, labels)
        joblib.dump(self.model, CLASSIFIER_PATH)
        joblib.dump(self.vectorizer, VECTORIZER_PATH)

    def predict(self, texts: List[str]) -> List[int]:
        X = self.vectorizer.transform(texts)
        return self.model.predict(X).tolist()

    def retrain(self, texts: List[str], labels: List[int]):
        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression()
        self.model.fit(X, labels)
        joblib.dump(self.model, CLASSIFIER_PATH)
        joblib.dump(self.vectorizer, VECTORIZER_PATH)

    def evaluate(self, texts: List[str], labels: List[int]) -> dict:
        X = self.vectorizer.transform(texts)
        preds = self.model.predict(X)
        accuracy = (preds == labels).mean()
        return {"accuracy": float(accuracy)}

    def is_healthy(self) -> bool:
        return self.model is not None and self.vectorizer is not None

# Singleton instance for use in API
text_classifier = TextClassifier()
