"""Local text generation via a seq2seq model (flan-t5). Loaded lazily on first
use. flan-t5 is a text2text-generation model, not text-generation."""

_generator = None


def _get_generator():
    global _generator
    if _generator is None:
        from transformers import pipeline
        _generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
        )
    return _generator


def generate(prompt, max_new_tokens=256):
    result = _get_generator()(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7,
    )
    return result[0]["generated_text"]
