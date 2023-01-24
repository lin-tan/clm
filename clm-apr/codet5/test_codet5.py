from transformers import RobertaTokenizer, T5ForConditionalGeneration


if __name__ == '__main__':
    tokenizer = RobertaTokenizer.from_pretrained('codet5-small')
    model = T5ForConditionalGeneration.from_pretrained('codet5-small')

    print("Num of parameters:", sum(p.numel() for p in model.parameters() if p.requires_grad))

    text = """
public static int bitcount(int n) {
    int count = 0;
    while (n != 0) {
        <extra_id_0>
        count++;
    }
    return count;
}
"""
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    print(input_ids)
    print(tokenizer.decode(input_ids[0], skip_special_tokens=True))

    generated_ids = model.generate(input_ids, max_length=128, num_beams=10, num_return_sequences=10)
    for i, generated_id in enumerate(generated_ids):
        print('patch', i + 1)
        print(tokenizer.decode(generated_id, skip_special_tokens=False))
