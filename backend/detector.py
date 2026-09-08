"""
ModelVault — Adaptive AI-Security Middleware
=============================================
Core extraction-detection engine for protecting the ARGUS predictive-maintenance
Random Forest classifier against model-extraction attacks.

Review 1 features
------------------
1. Behavioral Fingerprinting          (per-client temporal analysis)
2. Query Trajectory Analysis          (sequential feature-delta patterns)
3. Query Similarity Analysis          (normalized feature distance)
4. Decision-Boundary Probing Detection(small perturbation + prediction flip)
5. Input-Space Coverage Analysis      (sparse binned region tracking)
6. Multi-Signal Risk Fusion           (weighted combination)
7. Adaptive Security Policy           (risk → status/action mapping)
8. Persistent Request / Fingerprint Logging (JSON Lines append-only log)

Design constraints
-------------------
- Python 3.12, numpy + stdlib only
- Deterministic (no randomness)
- Thread-safe (threading.Lock on all mutable state)
- Cold-start safe (low scores until sufficient evidence)
- Does NOT load or execute the ARGUS model
"""

from __future__ import annotations

import json
import math
import os
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration dataclasses
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FeatureConfig:
    """Per-feature normalization ranges for the 8 ARGUS engine features.

    Using domain-informed ranges prevents high-magnitude features (e.g. RPM)
    from dominating distance calculations.
    """
    names: tuple[str, ...] = (
        "engine_rpm",
        "lub_oil_pressure",
        "fuel_pressure",
        "coolant_pressure",
        "lub_oil_temp",
        "coolant_temp",
        "pressure_ratio",
        "temp_diff",
    )
    # (min, max) per feature — conservative engine operating envelope
    ranges: tuple[tuple[float, float], ...] = (
        (0.0, 3000.0),       # engine_rpm
        (0.0, 10.0),         # lub_oil_pressure (bar)
        (0.0, 25.0),         # fuel_pressure (bar)
        (0.0, 10.0),         # coolant_pressure (bar)
        (0.0, 200.0),        # lub_oil_temp (°C)
        (0.0, 200.0),        # coolant_temp (°C)
        (0.0, 2.0),          # pressure_ratio
        (-50.0, 50.0),       # temp_diff (°C)
    )
    num_bins: int = 10  # bins per feature for coverage tracking


@dataclass
class FusionWeights:
    """Weights for multi-signal risk fusion.  Must sum to 1.0."""
    behavioral: float = 0.20
    trajectory: float = 0.20
    similarity: float = 0.20
    boundary: float = 0.25
    coverage: float = 0.15


@dataclass
class PolicyThresholds:
    """Risk-score thresholds for security status transitions."""
    monitored: float = 30.0
    suspicious: float = 35.0
    high_risk: float = 42.0
    critical: float = 46.0


@dataclass
class DetectorConfig:
    """Top-level detector configuration — every knob in one place."""
    max_history_per_client: int = 200
    behavioral_window_sec: float = 60.0
    similarity_lookback: int = 30
    trajectory_lookback: int = 20
    boundary_lookback: int = 30
    high_similarity_threshold: float = 0.92
    boundary_distance_threshold: float = 0.08
    small_perturbation_threshold: float = 0.05
    log_dir: str = "logs"
    log_file: str = "requests.jsonl"
    feature_config: FeatureConfig = field(default_factory=FeatureConfig)
    fusion_weights: FusionWeights = field(default_factory=FusionWeights)
    policy_thresholds: PolicyThresholds = field(default_factory=PolicyThresholds)


# ═══════════════════════════════════════════════════════════════════════════════
# Per-client state container
# ═══════════════════════════════════════════════════════════════════════════════

class _ClientState:
    """Isolated mutable state for a single client / session."""

    __slots__ = ("history", "coverage_regions", "boundary_events")

    def __init__(self, maxlen: int) -> None:
        self.history: deque[dict[str, Any]] = deque(maxlen=maxlen)
        self.coverage_regions: set[tuple[int, ...]] = set()
        self.boundary_events: deque[dict[str, Any]] = deque(maxlen=maxlen)


# ═══════════════════════════════════════════════════════════════════════════════
# Main detector class
# ═══════════════════════════════════════════════════════════════════════════════

class ModelVaultDetector:
    """Stateful extraction-detection engine.

    Thread-safe.  One instance is shared across all FastAPI workers.

    Usage::

        detector = ModelVaultDetector()
        result   = detector.process(
            features   = [700, 2.5, 11.8, 3.2, 80, 82, 0.78, -2],
            prediction = 0,
            confidence = 0.94,
            client_id  = "user-abc",
        )
    """

    # ── construction ────────────────────────────────────────────────────────

    def __init__(self, config: DetectorConfig | None = None,
                 max_history: int | None = None) -> None:
        self._cfg = config or DetectorConfig()
        # Backwards-compat: the old prototype accepted max_history directly.
        if max_history is not None:
            self._cfg.max_history_per_client = max_history
        self._lock = threading.Lock()
        self._clients: dict[str, _ClientState] = {}
        self._feature_ranges = np.array(
            self._cfg.feature_config.ranges, dtype=np.float64
        )  # shape (8, 2)
        self._feature_spans = (
            self._feature_ranges[:, 1] - self._feature_ranges[:, 0]
        )
        # Avoid division by zero for any degenerate range
        self._feature_spans[self._feature_spans == 0] = 1.0
        self._num_bins = self._cfg.feature_config.num_bins
        # Ensure log directory exists
        self._log_path = Path(self._cfg.log_dir) / self._cfg.log_file
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

    # ── public API ──────────────────────────────────────────────────────────

    def process(
        self,
        features: list[float],
        prediction: int,
        confidence: float | None = None,
        client_id: str = "default",
    ) -> dict[str, Any]:
        """Analyse a single request and return a JSON-serializable security verdict.

        Parameters
        ----------
        features : list[float]
            Exactly 8 numerical engine features in ARGUS order.
        prediction : int
            Model output (0 or 1).
        confidence : float | None
            Optional class probability from ``predict_proba``.
        client_id : str
            Caller identifier for per-session isolation.

        Returns
        -------
        dict
            Contains *risk_score*, *scores*, *status*, *action*,
            *evidence*, and *reasons*.
        """
        # 1. validate
        feat_array = self._validate_input(features, prediction, confidence)
        norm_feat = self._normalize(feat_array)
        request_id = uuid.uuid4().hex
        ts = time.time()

        with self._lock:
            state = self._get_client_state(client_id)
            history_list = list(state.history)

            # 2. component scores
            beh_score, beh_diag = self._calculate_behavioral_fingerprint(
                history_list, ts
            )
            traj_score, traj_diag = self._calculate_trajectory(
                history_list, norm_feat
            )
            sim_score, sim_diag = self._calculate_query_similarity(
                history_list, norm_feat
            )
            bnd_score, bnd_diag = self._calculate_boundary_probing(
                history_list, norm_feat, prediction, state
            )
            cov_score, cov_diag, new_region = self._calculate_coverage(
                state, norm_feat, history_list
            )

            # 3. fuse
            risk_score = self._fuse_risk(
                beh_score, traj_score, sim_score, bnd_score, cov_score
            )

            # 4. policy
            status, action = self._apply_policy(risk_score)

            # 5. reasons
            reasons = self._generate_reasons(
                beh_score, traj_score, sim_score, bnd_score, cov_score,
                beh_diag, traj_diag, sim_diag, bnd_diag, cov_diag,
            )

            # 6. persist into in-memory history
            record: dict[str, Any] = {
                "request_id": request_id,
                "timestamp": ts,
                "client_id": client_id,
                "features": feat_array.tolist(),
                "normalized_features": norm_feat.tolist(),
                "prediction": prediction,
                "confidence": confidence,
                "scores": {
                    "behavioral": beh_score,
                    "trajectory": traj_score,
                    "similarity": sim_score,
                    "boundary": bnd_score,
                    "coverage": cov_score,
                },
                "risk_score": risk_score,
                "status": status,
                "action": action,
            }
            state.history.append(record)

        # 7. build response
        result: dict[str, Any] = {
            "request_id": request_id,
            "risk_score": risk_score,
            "scores": {
                "behavioral": beh_score,
                "trajectory": traj_score,
                "similarity": sim_score,
                "boundary": bnd_score,
                "coverage": cov_score,
            },
            "status": status,
            "action": action,
            "evidence": {
                **beh_diag,
                **sim_diag,
                **traj_diag,
                **bnd_diag,
                **cov_diag,
            },
            "reasons": reasons,
        }

        # 8. persistent log (outside lock — append-only, non-blocking)
        self._persist_request(record, result)

        return result

    # ── input validation ────────────────────────────────────────────────────

    @staticmethod
    def _validate_input(
        features: list[float],
        prediction: int,
        confidence: float | None,
    ) -> np.ndarray:
        """Validate & coerce raw inputs.  Raises ``ValueError`` on bad data."""
        if not isinstance(features, (list, tuple)):
            raise ValueError(
                f"features must be a list or tuple, got {type(features).__name__}"
            )
        if len(features) != 8:
            raise ValueError(
                f"Exactly 8 features required, got {len(features)}"
            )
        try:
            arr = np.array(features, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"All feature values must be numeric: {exc}") from exc
        if np.any(np.isnan(arr)):
            raise ValueError("Feature vector contains NaN values")
        if np.any(np.isinf(arr)):
            raise ValueError("Feature vector contains infinite values")
        if int(prediction) not in (0, 1):
            raise ValueError(
                f"prediction must be 0 or 1, got {prediction}"
            )
        if confidence is not None:
            conf = float(confidence)
            if not (0.0 <= conf <= 1.0):
                raise ValueError(
                    f"confidence must be between 0 and 1, got {conf}"
                )
        return arr

    # ── normalisation helpers ───────────────────────────────────────────────

    def _normalize(self, feat: np.ndarray) -> np.ndarray:
        """Min-max normalise a raw feature vector to [0, 1] per feature."""
        return np.clip(
            (feat - self._feature_ranges[:, 0]) / self._feature_spans,
            0.0, 1.0,
        )

    @staticmethod
    def _euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
        """Euclidean distance in normalised space."""
        return float(np.linalg.norm(a - b))

    # ── per-client state ────────────────────────────────────────────────────

    def _get_client_state(self, client_id: str) -> _ClientState:
        """Return (or lazily create) the per-client state container.

        Must be called under ``self._lock``.
        """
        if client_id not in self._clients:
            self._clients[client_id] = _ClientState(
                maxlen=self._cfg.max_history_per_client
            )
        return self._clients[client_id]

    # ════════════════════════════════════════════════════════════════════════
    #  3. BEHAVIORAL FINGERPRINTING
    # ════════════════════════════════════════════════════════════════════════

    def _calculate_behavioral_fingerprint(
        self,
        history: list[dict[str, Any]],
        current_ts: float,
    ) -> tuple[float, dict[str, Any]]:
        """Score temporal request patterns on a 0–100 scale.

        Cold start:  ≤2 prior requests → score capped at 5.
        """
        request_count = len(history)
        diag: dict[str, Any] = {
            "request_count": request_count,
            "avg_interval": None,
            "median_interval": None,
            "interval_cv": None,
            "burst_ratio": None,
        }

        if request_count < 2:
            return 0.0, diag

        # ── gather timestamps ──────────────────────────────────────────────
        timestamps = [r["timestamp"] for r in history] + [current_ts]
        intervals = np.diff(timestamps)

        avg_interval = float(np.mean(intervals))
        sorted_intervals = np.sort(intervals)
        median_interval = float(sorted_intervals[len(sorted_intervals) // 2])
        std_interval = float(np.std(intervals))
        cv = std_interval / avg_interval if avg_interval > 0 else 0.0

        # ── burst ratio: fraction of intervals < 1 s ──────────────────────
        burst_threshold = 1.0  # seconds
        burst_count = int(np.sum(intervals < burst_threshold))
        burst_ratio = burst_count / len(intervals)

        # ── requests inside the recent window ─────────────────────────────
        window = self._cfg.behavioral_window_sec
        recent_count = int(np.sum(
            np.array(timestamps) >= (current_ts - window)
        ))

        diag.update({
            "avg_interval": round(avg_interval, 4),
            "median_interval": round(median_interval, 4),
            "interval_cv": round(cv, 4),
            "burst_ratio": round(burst_ratio, 4),
            "recent_window_count": recent_count,
        })

        # ── sub-scores ────────────────────────────────────────────────────
        # A. Frequency (how fast requests arrive)
        if avg_interval <= 0.0:
            freq_score = 100.0
        else:
            # Sigmoid-like: score rises sharply when avg_interval drops < 1 s
            freq_score = 100.0 / (1.0 + math.exp(2.0 * (avg_interval - 1.0)))

        # B. Regularity (low CV ⇒ machine-like)
        if avg_interval <= 0.0:
            reg_score = 100.0
        elif cv < 0.05:
            reg_score = 95.0
        elif cv < 0.15:
            reg_score = 70.0
        elif cv < 0.30:
            reg_score = 40.0
        elif cv < 0.60:
            reg_score = 15.0
        else:
            reg_score = 0.0

        # C. Burst ratio
        burst_score = burst_ratio * 100.0

        # D. Volume in recent window (relative to expected human pace)
        # 10 requests/minute is heavy but plausible; 60+ is scripted
        volume_score = min(100.0, (recent_count / 60.0) * 100.0)

        # ── combine (weighted) ────────────────────────────────────────────
        raw = (
            0.30 * freq_score
            + 0.25 * reg_score
            + 0.25 * burst_score
            + 0.20 * volume_score
        )

        # Cold-start damping: ramp linearly from 0 → 1 over first 5 requests
        ramp = min(1.0, request_count / 5.0)
        score = round(float(np.clip(raw * ramp, 0.0, 100.0)), 2)
        return score, diag

    # ════════════════════════════════════════════════════════════════════════
    #  4. QUERY SIMILARITY ANALYSIS
    # ════════════════════════════════════════════════════════════════════════

    def _calculate_query_similarity(
        self,
        history: list[dict[str, Any]],
        norm_feat: np.ndarray,
    ) -> tuple[float, dict[str, Any]]:
        """Compare the current (normalised) query against recent queries.

        Uses Euclidean distance in normalised feature space so that no single
        feature dominates due to scale.
        """
        diag: dict[str, Any] = {
            "nearest_distance": None,
            "nearest_similarity": None,
            "high_similarity_count": 0,
            "high_similarity_fraction": 0.0,
        }

        if len(history) == 0:
            return 0.0, diag

        lookback = self._cfg.similarity_lookback
        recent = history[-lookback:]

        distances: list[float] = []
        for rec in recent:
            prev_norm = np.array(rec["normalized_features"], dtype=np.float64)
            d = self._euclidean_distance(norm_feat, prev_norm)
            distances.append(d)

        nearest_dist = min(distances)
        # Map distance → similarity in [0, 1].  Max possible distance in unit
        # hypercube is sqrt(8) ≈ 2.83.
        max_dist = math.sqrt(8.0)
        nearest_sim = 1.0 - (nearest_dist / max_dist)

        threshold = self._cfg.high_similarity_threshold
        high_sim_count = sum(
            1 for d in distances if (1.0 - d / max_dist) >= threshold
        )
        high_sim_frac = high_sim_count / len(distances)

        diag.update({
            "nearest_distance": round(nearest_dist, 6),
            "nearest_similarity": round(nearest_sim, 6),
            "high_similarity_count": high_sim_count,
            "high_similarity_fraction": round(high_sim_frac, 4),
        })

        # ── suspicion scoring ─────────────────────────────────────────────
        # A single similar query is mildly interesting; *repeated* high
        # similarity is the real signal.
        if nearest_sim >= 0.99:
            peak = 60.0
        elif nearest_sim >= 0.97:
            peak = 40.0
        elif nearest_sim >= 0.94:
            peak = 25.0
        elif nearest_sim >= 0.90:
            peak = 12.0
        else:
            peak = 0.0

        # Amplify by the *fraction* of recent queries that are highly similar
        repetition_amp = min(1.0, high_sim_frac * 2.5)  # saturates at 40%
        pattern_score = peak + 40.0 * repetition_amp

        # Cold-start damping
        ramp = min(1.0, len(history) / 5.0)
        score = round(float(np.clip(pattern_score * ramp, 0.0, 100.0)), 2)
        return score, diag

    # ════════════════════════════════════════════════════════════════════════
    #  5. QUERY TRAJECTORY ANALYSIS
    # ════════════════════════════════════════════════════════════════════════

    def _calculate_trajectory(
        self,
        history: list[dict[str, Any]],
        norm_feat: np.ndarray,
    ) -> tuple[float, dict[str, Any]]:
        """Detect systematic, monotonic, or oscillating feature perturbations."""
        diag: dict[str, Any] = {
            "average_delta": None,
            "normalized_delta": None,
            "directional_consistency": None,
            "monotonic_feature_count": 0,
            "small_perturbation_ratio": 0.0,
        }

        if len(history) < 2:
            return 0.0, diag

        lookback = self._cfg.trajectory_lookback
        recent = history[-lookback:]

        # Build sequence of normalised feature vectors including current
        seq: list[np.ndarray] = [
            np.array(r["normalized_features"], dtype=np.float64) for r in recent
        ]
        seq.append(norm_feat)

        # Consecutive deltas: shape (N-1, 8)
        deltas = np.diff(np.array(seq), axis=0)  # type: ignore[arg-type]
        n_steps = deltas.shape[0]

        magnitudes = np.linalg.norm(deltas, axis=1)
        avg_delta = float(np.mean(magnitudes))

        # ── directional consistency per feature ───────────────────────────
        # For each feature, what fraction of steps move in the same direction?
        signs = np.sign(deltas)  # -1, 0, +1
        consistency_per_feat = np.zeros(8)
        for f_idx in range(8):
            col = signs[:, f_idx]
            nonzero = col[col != 0]
            if len(nonzero) >= 2:
                # fraction agreeing with majority direction
                pos = np.sum(nonzero > 0)
                neg = np.sum(nonzero < 0)
                consistency_per_feat[f_idx] = max(pos, neg) / len(nonzero)
            else:
                consistency_per_feat[f_idx] = 0.0

        directional_consistency = float(np.mean(consistency_per_feat))

        # ── monotonic features (same sign ≥80% of steps) ─────────────────
        monotonic_count = int(np.sum(consistency_per_feat >= 0.80))

        # ── small perturbation ratio ──────────────────────────────────────
        small_thresh = self._cfg.small_perturbation_threshold
        small_steps = int(np.sum(magnitudes < small_thresh))
        small_ratio = small_steps / n_steps

        diag.update({
            "average_delta": round(avg_delta, 6),
            "normalized_delta": round(avg_delta / math.sqrt(8.0), 6),
            "directional_consistency": round(directional_consistency, 4),
            "monotonic_feature_count": monotonic_count,
            "small_perturbation_ratio": round(small_ratio, 4),
        })

        # ── scoring ──────────────────────────────────────────────────────
        # Sub-scores for: monotonicity, small perturbations, consistency
        mono_score = min(100.0, (monotonic_count / 4.0) * 100.0)
        small_score = small_ratio * 100.0
        consist_score = max(0.0, (directional_consistency - 0.5) * 200.0)

        raw = 0.35 * mono_score + 0.35 * small_score + 0.30 * consist_score

        # Cold-start ramp: need ≥5 history entries for meaningful trajectory
        ramp = min(1.0, len(history) / 5.0)
        score = round(float(np.clip(raw * ramp, 0.0, 100.0)), 2)
        return score, diag

    # ════════════════════════════════════════════════════════════════════════
    #  6. DECISION-BOUNDARY PROBING
    # ════════════════════════════════════════════════════════════════════════

    def _calculate_boundary_probing(
        self,
        history: list[dict[str, Any]],
        norm_feat: np.ndarray,
        prediction: int,
        state: _ClientState,
    ) -> tuple[float, dict[str, Any]]:
        """Detect repeated close-query prediction flips."""
        diag: dict[str, Any] = {
            "prediction_flip": False,
            "closest_previous_prediction": None,
            "distance_to_flip": None,
            "recent_boundary_flips": len(state.boundary_events),
            "boundary_event_count": len(state.boundary_events),
        }

        if len(history) == 0:
            return 0.0, diag

        lookback = self._cfg.boundary_lookback
        recent = history[-lookback:]
        dist_thresh = self._cfg.boundary_distance_threshold

        # Find the closest previous query
        closest_dist = float("inf")
        closest_pred: int | None = None
        flip_detected = False
        flip_distance: float | None = None

        for rec in recent:
            prev_norm = np.array(rec["normalized_features"], dtype=np.float64)
            d = self._euclidean_distance(norm_feat, prev_norm)
            if d < closest_dist:
                closest_dist = d
                closest_pred = rec["prediction"]

        if closest_pred is not None:
            diag["closest_previous_prediction"] = closest_pred

        # Check for prediction flips among nearby queries
        for rec in recent:
            prev_norm = np.array(rec["normalized_features"], dtype=np.float64)
            d = self._euclidean_distance(norm_feat, prev_norm)
            if d <= dist_thresh and rec["prediction"] != prediction:
                flip_detected = True
                if flip_distance is None or d < flip_distance:
                    flip_distance = d

        if flip_detected:
            state.boundary_events.append({
                "timestamp": time.time(),
                "distance": flip_distance,
            })

        diag.update({
            "prediction_flip": flip_detected,
            "distance_to_flip": (
                round(flip_distance, 6) if flip_distance is not None else None
            ),
            "recent_boundary_flips": len(state.boundary_events),
            "boundary_event_count": len(state.boundary_events),
        })

        # ── scoring ──────────────────────────────────────────────────────
        n_flips = len(state.boundary_events)

        if n_flips == 0:
            return 0.0, diag

        # Single flip: mild concern.  Repeated flips: escalate.
        # Map flip count through a saturating curve (cap at ~95).
        flip_score = 95.0 * (1.0 - math.exp(-0.35 * n_flips))

        # Boost when current request itself triggered a flip
        if flip_detected and flip_distance is not None:
            # Closer distance ⇒ more suspicious (inversely proportional)
            proximity_boost = max(0.0, 1.0 - (flip_distance / dist_thresh))
            flip_score = min(100.0, flip_score + 10.0 * proximity_boost)

        # Cold-start damping
        ramp = min(1.0, len(history) / 4.0)
        score = round(float(np.clip(flip_score * ramp, 0.0, 100.0)), 2)
        return score, diag

    # ════════════════════════════════════════════════════════════════════════
    #  7. INPUT-SPACE COVERAGE
    # ════════════════════════════════════════════════════════════════════════

    def _calculate_coverage(
        self,
        state: _ClientState,
        norm_feat: np.ndarray,
        history: list[dict[str, Any]],
    ) -> tuple[float, dict[str, Any], bool]:
        """Track exploration across the 8-D normalised feature space.

        Uses sparse bin-tuple tracking instead of a dense 10^8 array.
        """
        # Compute bin tuple for current query
        bins = tuple(
            int(min(self._num_bins - 1, max(0, v * self._num_bins)))
            for v in norm_feat
        )
        new_region = bins not in state.coverage_regions
        state.coverage_regions.add(bins)
        unique_regions = len(state.coverage_regions)

        # Feature-wise min/max from history + current
        all_feats = [
            np.array(r["normalized_features"], dtype=np.float64)
            for r in history
        ]
        all_feats.append(norm_feat)
        stacked = np.array(all_feats)
        feat_mins = stacked.min(axis=0).tolist()
        feat_maxs = stacked.max(axis=0).tolist()
        feat_ranges = [
            round(mx - mn, 4) for mn, mx in zip(feat_mins, feat_maxs)
        ]

        # Exploration rate: new regions per request (recent window)
        n_requests = len(history) + 1
        exploration_rate = unique_regions / n_requests if n_requests > 0 else 0.0

        diag: dict[str, Any] = {
            "unique_regions": unique_regions,
            "new_region": new_region,
            "exploration_rate": round(exploration_rate, 4),
            "feature_ranges": feat_ranges,
        }

        # ── scoring ──────────────────────────────────────────────────────
        # More unique regions relative to request count ⇒ more suspicious.
        # But only if there is enough history to be meaningful.
        if n_requests <= 3:
            return 0.0, diag, new_region

        # Expected unique regions for purely random exploration grows slower
        # than linearly.  We flag when coverage grows *linearly* (or faster).
        expected_for_normal = math.sqrt(n_requests) * 1.5
        coverage_ratio = unique_regions / max(expected_for_normal, 1.0)
        region_score = min(100.0, coverage_ratio * 40.0)

        # Average feature range (0-1 normalised); wide range ⇒ exploring
        avg_range = float(np.mean(feat_ranges))
        range_score = min(100.0, avg_range * 120.0)

        raw = 0.55 * region_score + 0.45 * range_score

        # Cold-start ramp
        ramp = min(1.0, n_requests / 8.0)
        score = round(float(np.clip(raw * ramp, 0.0, 100.0)), 2)
        return score, diag, new_region

    # ════════════════════════════════════════════════════════════════════════
    #  8. MULTI-SIGNAL RISK FUSION
    # ════════════════════════════════════════════════════════════════════════

    def _fuse_risk(
        self,
        behavioral: float,
        trajectory: float,
        similarity: float,
        boundary: float,
        coverage: float,
    ) -> float:
        """Weighted linear combination, clamped to [0, 100]."""
        w = self._cfg.fusion_weights
        raw = (
            w.behavioral * behavioral
            + w.trajectory * trajectory
            + w.similarity * similarity
            + w.boundary * boundary
            + w.coverage * coverage
        )
        return round(float(np.clip(raw, 0.0, 100.0)), 2)

    # ════════════════════════════════════════════════════════════════════════
    #  9. ADAPTIVE SECURITY POLICY
    # ════════════════════════════════════════════════════════════════════════

    def _apply_policy(self, risk: float) -> tuple[str, str]:
        """Map a risk score to (status, action)."""
        t = self._cfg.policy_thresholds
        if risk < t.monitored:
            return "TRUSTED", "ALLOW"
        if risk < t.suspicious:
            return "MONITORED", "ALLOW"
        if risk < t.high_risk:
            return "SUSPICIOUS", "RATE_LIMIT"
        if risk < t.critical:
            return "HIGH_RISK", "RESTRICT"
        return "CRITICAL", "BLOCK"

    # ════════════════════════════════════════════════════════════════════════
    #  11. SECURITY EXPLANATION
    # ════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _generate_reasons(
        beh: float, traj: float, sim: float, bnd: float, cov: float,
        beh_d: dict, traj_d: dict, sim_d: dict, bnd_d: dict, cov_d: dict,
    ) -> list[str]:
        """Produce human-readable reasons derived *only* from actual evidence."""
        reasons: list[str] = []

        # Behavioral
        if beh >= 60:
            reasons.append("High-frequency, regular query pattern consistent with automated scripting")
        elif beh >= 35:
            reasons.append("Moderately elevated request rate with some regularity")

        if beh_d.get("burst_ratio") is not None and beh_d["burst_ratio"] >= 0.6:
            reasons.append(
                f"Burst activity detected — {beh_d['burst_ratio']:.0%} of intervals under 1 s"
            )

        # Trajectory
        if traj >= 55:
            reasons.append("Repeated small, systematic input perturbations detected")
        elif traj >= 30:
            reasons.append("Some directional consistency in sequential feature changes")

        mc = traj_d.get("monotonic_feature_count", 0)
        if mc >= 3:
            reasons.append(
                f"{mc} features show monotonic sweeping behaviour"
            )

        # Similarity
        if sim >= 55:
            reasons.append(
                "Multiple recent queries are highly similar in normalised feature space"
            )
        elif sim >= 30:
            reasons.append("Several recent queries are moderately similar")

        # Boundary
        if bnd >= 55:
            reasons.append(
                "Multiple prediction flips between highly similar inputs — "
                "strong boundary probing evidence"
            )
        elif bnd >= 25:
            if bnd_d.get("prediction_flip"):
                reasons.append(
                    "Prediction flip detected between close queries — possible boundary probing"
                )

        flips = bnd_d.get("recent_boundary_flips", 0)
        if flips >= 3:
            reasons.append(
                f"{flips} boundary-probing events recorded in session"
            )

        # Coverage
        if cov >= 55:
            reasons.append(
                "Rapid expansion of explored input regions suggests systematic space exploration"
            )
        elif cov >= 30:
            reasons.append("Gradual expansion into new input-space regions observed")

        if not reasons:
            reasons.append("No significant extraction indicators detected")

        return reasons

    # ════════════════════════════════════════════════════════════════════════
    #  PERSISTENT LOGGING
    # ════════════════════════════════════════════════════════════════════════

    def _persist_request(
        self, record: dict[str, Any], result: dict[str, Any]
    ) -> None:
        """Append a single JSON line to the request log file.

        Failures are silently swallowed so logging never crashes the API.
        """
        entry = {
            "request_id": record["request_id"],
            "timestamp": record["timestamp"],
            "client_id": record["client_id"],
            "features": record["features"],
            "prediction": record["prediction"],
            "confidence": record["confidence"],
            "scores": record["scores"],
            "risk_score": record["risk_score"],
            "status": record["status"],
            "action": record["action"],
            "evidence": result.get("evidence", {}),
            "reasons": result.get("reasons", []),
        }
        try:
            with open(self._log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, default=str) + "\n")
        except Exception:
            # Logging must never crash the API
            pass