"""Zero-shot job-role classification. The model is loaded lazily on first use
so importing this module stays cheap and does not require transformers/torch
unless AI is actually enabled."""

_classifier = None

LABELS = [
    "backend engineer",
    "frontend engineer",
    "data scientist",
    "devops",
    "security engineer",
    "mobile developer",
    "internship",
    "non-technical",
]


def _get_classifier():
    global _classifier
    if _classifier is None:
        from transformers import pipeline
        _classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
        )
    return _classifier


def classify_job(text):
    result = _get_classifier()(text, candidate_labels=LABELS)
    return {
        "label": result["labels"][0],
        "score": float(result["scores"][0]),
    }
