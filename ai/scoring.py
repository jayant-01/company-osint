"""Semantic similarity between a job and the user profile. The embedding model
is loaded lazily on first use."""

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def score_job(job_text, user_profile):
    from sentence_transformers import util

    model = _get_model()
    job_emb = model.encode(job_text, convert_to_tensor=True)
    user_emb = model.encode(user_profile, convert_to_tensor=True)
    score = util.cos_sim(job_emb, user_emb).item()
    return round(score * 100, 2)
