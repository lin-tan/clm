from transformers import AutoTokenizer, AutoModelForCausalLM

if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained('/local2/jiang719/language_models/incoder/incoder-1B/')
    model = AutoModelForCausalLM.from_pretrained('/local2/jiang719/language_models/incoder/incoder-1B-finetune/')

    text = \
"""public static int bitcount(int n) {
    int count = 0;
    while (n != 0) {
// buggy lines start:        
        n = n ^ (n - 1);
// buggy lines end
        count++;
    }
    return count;
}
// fixed lines:\n"""

    input_ids = tokenizer(text, return_tensors="pt").input_ids
    print(input_ids)
    print(tokenizer.decode(input_ids[0], skip_special_tokens=False))

    eos_id = tokenizer.convert_tokens_to_ids('<|endofmask|>')
    generated_ids = model.generate(
        input_ids, max_new_tokens=128, num_beams=3, num_return_sequences=3, early_stopping=True,
        pad_token_id=eos_id, eos_token_id=eos_id
    )

    for i, generated_id in enumerate(generated_ids):
        print('patch', i + 1)
        print(tokenizer.decode(generated_id, skip_special_tokens=False, clean_up_tokenization_spaces=False))
