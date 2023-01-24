from transformers import AutoTokenizer, AutoModelForCausalLM


if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained('codegen-350M-multi')
    model = AutoModelForCausalLM.from_pretrained('codegen-350M-multi')

    print("Num of parameters:", sum(p.numel() for p in model.parameters() if p.requires_grad))

    text = """
public static int bitcount(int n) {
    int count = 0;
    while (n != 0) {
"""
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    print(input_ids)
    print(tokenizer.decode(input_ids[0], skip_special_tokens=True))

    eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
    generated_ids = model.generate(
        input_ids, max_length=128, num_beams=10, num_return_sequences=10, 
        pad_token_id=eos_id, eos_token_id=eos_id, early_stopping=True
    )
    for i, generated_id in enumerate(generated_ids):
        print('output', i + 1)
        print(tokenizer.decode(generated_id, skip_special_tokens=True))
