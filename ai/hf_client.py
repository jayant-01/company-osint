from transformers import pipeline


# Lightweight model for classification
classifier = pipeline(
    "text-classification",
    model="facebook/bart-large-mnli"
)


def classify_job(text):

    labels = [
        "backend engineer",
        "frontend engineer",
        "data scientist",
        "devops",
        "security engineer",
        "mobile developer",
        "internship",
        "non-technical"
    ]

    result = classifier(text, candidate_labels=labels)

    return {
        "label": result["labels"][0],
        "score": result["scores"][0]
    }