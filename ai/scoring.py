from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def score_job(job_text, user_profile):

    job_emb = model.encode(job_text, convert_to_tensor=True)

    user_emb = model.encode(user_profile, convert_to_tensor=True)

    score = util.cos_sim(job_emb, user_emb).item()

    return round(score * 100, 2)