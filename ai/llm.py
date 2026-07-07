from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="google/flan-t5-base"
)


def generate(prompt, max_length=256):

    result = generator(
        prompt,
        max_new_tokens=max_length,
        do_sample=True,
        temperature=0.7
    )

    return result[0]["generated_text"]