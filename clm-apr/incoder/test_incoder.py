from transformers import AutoTokenizer, AutoModelForCausalLM


if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained("incoder-1B")
    model = AutoModelForCausalLM.from_pretrained("incoder-1B")

    print("Num of parameters:", sum(p.numel() for p in model.parameters() if p.requires_grad))

    text = ""
    
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    print(input_ids)
    print(tokenizer.decode(input_ids[0], skip_special_tokens=False))

    eos_id = tokenizer.convert_tokens_to_ids('</code>')

    generated_ids = model.generate(
        input_ids, max_new_tokens=128, num_beams=10, num_return_sequences=10, early_stopping=True, # num_beam_groups=1, diversity_penalty=0.,
        output_scores=True, return_dict_in_generate=True, pad_token_id=eos_id, eos_token_id=eos_id
    )
    
    for i in range(generated_ids.sequences.size(0)):
        print('patch', i + 1)

        patch = generated_ids.sequences[i][input_ids.size(1): ]
        print(tokenizer.decode(patch, skip_special_tokens=False, clean_up_tokenization_spaces=False))
