from transformers import PLBartForConditionalGeneration, PLBartTokenizer

if __name__ == '__main__':
    tokenizer = PLBartTokenizer.from_pretrained("plbart-base", src_lang="java", tgt_lang="java")
    model = PLBartForConditionalGeneration.from_pretrained("plbart-large")
    print('model parameters:', sum(param.numel() for param in model.parameters()))

    text = text = """<s>
public static int bitcount(int n) {
    int count = 0;
    while (n != 0) {
        <mask>
        count++;
    }
    return count;
} </s> java
"""
    input_ids = tokenizer(text, add_special_tokens=False, return_tensors="pt").input_ids
    print(input_ids)
    generated_ids = model.generate(
        input_ids, max_length=128, num_beams=1, num_return_sequences=1, decoder_start_token_id=tokenizer.lang_code_to_id["java"]
    )
    for i, generated_id in enumerate(generated_ids):
        print('patch', i + 1)
        print(generated_id)
        print(tokenizer.decode(generated_id, skip_special_tokens=False))
