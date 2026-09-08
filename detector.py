import time
import numpy as np
from collections import deque


class ModelVaultDetector:

    def __init__(self, max_history=100):
        self.history = deque(maxlen=max_history)

    # --------------------------------------------------
    # Calculate cosine similarity
    # --------------------------------------------------

    def cosine_similarity(self, a, b):

        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)

        denominator = np.linalg.norm(a) * np.linalg.norm(b)

        if denominator == 0:
            return 0.0

        return float(np.dot(a, b) / denominator)

    # --------------------------------------------------
    # 1. BEHAVIORAL ANALYSIS
    # --------------------------------------------------

    def behavioral_score(self):

        if len(self.history) < 2:
            return 5.0

        timestamps = [
            request["timestamp"]
            for request in self.history
        ]

        intervals = np.diff(timestamps)

        if len(intervals) == 0:
            return 5.0

        avg_interval = np.mean(intervals)

        # ----------------------------------------------
        # Request frequency
        # ----------------------------------------------

        if avg_interval < 0.5:
            frequency_score = 100

        elif avg_interval < 1:
            frequency_score = 80

        elif avg_interval < 2:
            frequency_score = 60

        elif avg_interval < 5:
            frequency_score = 30

        else:
            frequency_score = 10

        # ----------------------------------------------
        # Request regularity
        # ----------------------------------------------

        if np.mean(intervals) == 0:
            regularity_score = 100
        else:

            coefficient_variation = (
                np.std(intervals) /
                np.mean(intervals)
            )

            if coefficient_variation < 0.1:
                regularity_score = 90

            elif coefficient_variation < 0.25:
                regularity_score = 60

            elif coefficient_variation < 0.5:
                regularity_score = 30

            else:
                regularity_score = 5

        # ----------------------------------------------
        # Combined behavioral score
        # ----------------------------------------------

        score = (
            0.6 * frequency_score +
            0.4 * regularity_score
        )

        return round(float(score), 2)

    # --------------------------------------------------
    # 2. QUERY SIMILARITY
    # --------------------------------------------------

    def similarity_score(self, features):

        if len(self.history) == 0:
            return 5.0

        recent_requests = list(self.history)[-20:]

        similarities = []

        for request in recent_requests:

            similarity = self.cosine_similarity(
                features,
                request["features"]
            )

            similarities.append(similarity)

        if not similarities:
            return 5.0

        max_similarity = max(similarities)

        # ----------------------------------------------
        # Convert similarity to suspiciousness
        # ----------------------------------------------

        if max_similarity >= 0.99:
            score = 100

        elif max_similarity >= 0.97:
            score = 90

        elif max_similarity >= 0.95:
            score = 75

        elif max_similarity >= 0.90:
            score = 50

        elif max_similarity >= 0.80:
            score = 25

        else:
            score = 5

        return round(float(score), 2)

    # --------------------------------------------------
    # 3. DECISION-BOUNDARY PROBING
    # --------------------------------------------------

    def boundary_score(self, features, prediction):

        if len(self.history) == 0:
            return 5.0

        recent_requests = list(self.history)[-20:]

        highest_score = 5.0

        for request in recent_requests:

            similarity = self.cosine_similarity(
                features,
                request["features"]
            )

            previous_prediction = request["prediction"]

            # ------------------------------------------
            # Highly similar input + prediction flip
            # = possible boundary probing
            # ------------------------------------------

            if (
                similarity >= 0.95
                and
                previous_prediction != prediction
            ):

                score = similarity * 100

                highest_score = max(
                    highest_score,
                    score
                )

        return round(float(highest_score), 2)

    # --------------------------------------------------
    # 4. RISK FUSION
    # --------------------------------------------------

    def calculate_risk(
        self,
        behavioral,
        similarity,
        boundary
    ):

        risk = (
            0.30 * behavioral +
            0.35 * similarity +
            0.35 * boundary
        )

        return round(float(risk), 2)

    # --------------------------------------------------
    # 5. SECURITY POLICY
    # --------------------------------------------------

    def security_policy(self, risk):

        if risk < 30:

            return {
                "status": "TRUSTED",
                "action": "ALLOW"
            }

        elif risk < 50:

            return {
                "status": "MONITORED",
                "action": "ALLOW"
            }

        elif risk < 70:

            return {
                "status": "SUSPICIOUS",
                "action": "RATE_LIMIT"
            }

        elif risk < 85:

            return {
                "status": "HIGH_RISK",
                "action": "BLOCK"
            }

        else:

            return {
                "status": "CRITICAL",
                "action": "BLOCK"
            }

    # --------------------------------------------------
    # MAIN PROCESSING FUNCTION
    # --------------------------------------------------

    def process(self, features, prediction):

        # ----------------------------------------------
        # Calculate security signals
        # ----------------------------------------------

        behavioral = self.behavioral_score()

        similarity = self.similarity_score(
            features
        )

        boundary = self.boundary_score(
            features,
            prediction
        )

        # ----------------------------------------------
        # Calculate final extraction risk
        # ----------------------------------------------

        risk = self.calculate_risk(
            behavioral,
            similarity,
            boundary
        )

        # ----------------------------------------------
        # Determine action
        # ----------------------------------------------

        policy = self.security_policy(risk)

        # ----------------------------------------------
        # Store request for future analysis
        # ----------------------------------------------

        self.history.append({

            "timestamp": time.time(),

            "features": list(features),

            "prediction": prediction

        })

        # ----------------------------------------------
        # Return security information
        # ----------------------------------------------

        return {

            "risk_score": risk,

            "behavioral_score": behavioral,

            "similarity_score": similarity,

            "boundary_score": boundary,

            "status": policy["status"],

            "action": policy["action"]

        }