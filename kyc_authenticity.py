"""
Pramaan Backend — KYC authenticity scoring

IMPORTANT — read before the code walkthrough:
This is NOT a trained deepfake detector. It computes a simple image
sharpness/noise heuristic (Laplacian variance) so the demo produces
some real, image-dependent variation instead of a hardcoded constant.
It has no relationship to actual deepfake-detection accuracy and must
not be presented as one in front of the jury.

The honest line to say out loud: "This endpoint is a structural
placeholder — same input/output shape our trained DeepWatch model would
use (patch-wise CNN inference -> calibrated risk score -> accept/review/
block). Swapping in the real model is a model-loading change, not an
architecture change."
"""

import io
import numpy as np
from PIL import Image


def score_image(image_bytes: bytes) -> tuple[float, str, str]:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        arr = np.asarray(img, dtype=np.float64)

        # Laplacian (edge/sharpness) variance — a crude, non-ML signal.
        laplacian_kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        from scipy.signal import convolve2d
        lap = convolve2d(arr, laplacian_kernel, mode="valid")
        sharpness = float(lap.var())

        # Map sharpness into a [0,1] "risk" score for demo purposes only.
        # Lower sharpness (over-smoothed) -> nudges risk score up.
        # This mapping is arbitrary and illustrative — not a validated model.
        risk_score = float(np.clip(1.0 - min(sharpness, 800.0) / 800.0, 0.02, 0.95))

    except Exception:
        risk_score = 0.5  # unreadable/corrupt image -> send to human review, don't guess

    if risk_score >= 0.65:
        verdict = "flagged"
    elif risk_score >= 0.35:
        verdict = "needs_review"
    else:
        verdict = "authentic"

    note = "Placeholder heuristic (image sharpness), not a trained detector."
    return round(risk_score, 3), verdict, note
