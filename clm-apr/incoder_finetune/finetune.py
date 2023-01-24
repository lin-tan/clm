import time
import traceback
import torch
import torch.nn as nn
from dataset import Dataset, custom_collate
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import get_cosine_schedule_with_warmup, Adafactor


def validation_step(model, validation_loader, save_dir, parallel=False):
    print('start validation')
    validation_loss = []
    model.eval()
    with torch.no_grad():
        try:
            for i, data in enumerate(validation_loader):
                data = {
                    'input_ids': data['input_ids'].to(device_ids[0]),
                    'labels': data['labels'].to(device_ids[0]),
                    'attention_mask': data['attention_mask'].to(device_ids[0])
                }
                output = model(input_ids=data['input_ids'], labels=data['labels'], attention_mask=data['attention_mask'], return_dict=True)
                loss = output.loss
                validation_loss.append(loss.mean().item())
        except Exception as e:
            torch.cuda.empty_cache()
            pass
    print('validation loss:', round(sum(validation_loss) / len(validation_loss), 4))
    if not parallel:
        model.module.save_pretrained(save_dir)
    else:
        model.save_pretrained(save_dir)
    print('checkpoint saved')
    model.train()


def fine_tune(training_file, validation_file, epochs, batch_size, save_dir, parallel=False, load_range=None):
    tokenizer = AutoTokenizer.from_pretrained(vocabulary_file)
    model = AutoModelForCausalLM.from_pretrained(pretrained_file)
    print('model parameters:', sum(param.numel() for param in model.parameters()))
    if not parallel:
        model = nn.DataParallel(model, device_ids=device_ids).to(device_ids[0])
    else:
        if 'incoder-1B' in pretrained_file:
            device_map = {
                0: [_ for _ in range(0, 5)],
                1: [_ for _ in range(5, 12)],
                2: [_ for _ in range(12, 19)],
                3: [_ for _ in range(19, 24)]
            }
        else:
            device_map = {
                0: [_ for _ in range(0, 4)], 
                1: [_ for _ in range(4, 8)],
                2: [_ for _ in range(8, 12)],
                3: [_ for _ in range(12, 16)],
                4: [_ for _ in range(16, 20)],
                5: [_ for _ in range(20, 24)],
                6: [_ for _ in range(24, 28)],
                7: [_ for _ in range(28, 32)]
            }
        model.parallelize(device_map=device_map)

    training_dataset = Dataset(training_file, tokenizer, max_length=1024, shuffle=False, load_range=load_range)
    validation_dataset = Dataset(validation_file, tokenizer, max_length=1024, load_range=[0, 1000])
    training_sampler = torch.utils.data.SequentialSampler(training_dataset)
    validation_sampler = torch.utils.data.SequentialSampler(validation_dataset)
    training_loader = torch.utils.data.DataLoader(
        dataset=training_dataset, batch_size=batch_size, shuffle=False,
        num_workers=0, pin_memory=True, sampler=training_sampler, collate_fn=custom_collate
    )
    validation_loader = torch.utils.data.DataLoader(
        dataset=validation_dataset, batch_size=3*batch_size, shuffle=False,
        num_workers=0, pin_memory=True, sampler=validation_sampler, collate_fn=custom_collate
    )

    # optimizer = torch.optim.SGD(model.parameters(), lr=2.5e-4, momentum=0.9)
    optimizer = Adafactor(model.parameters(), lr=1e-5, scale_parameter=False, relative_step=False)
    scheduler = get_cosine_schedule_with_warmup(
        optimizer=optimizer, num_warmup_steps=0, num_training_steps=int(epochs * len(training_loader))
    )
    for epoch in range(epochs):
        model.train()
        training_loss = []
        start_time = time.time()
        oom = 0
        for i, data in enumerate(training_loader):
            data = {
                'input_ids': data['input_ids'].to(device_ids[0]),
                'labels': data['labels'].to(device_ids[0]),
                'attention_mask': data['attention_mask'].to(device_ids[0])
            }
            try:
                optimizer.zero_grad()
                output = model(input_ids=data['input_ids'], labels=data['labels'], attention_mask=data['attention_mask'], return_dict=True)
                loss = output.loss
                
                loss.mean().backward()
                nn.utils.clip_grad_value_(model.parameters(), 0.3)
                optimizer.step()
                scheduler.step()
                training_loss.append(loss.mean().item())
            except Exception as e:
                print(str(e))
                if 'out of memory' in str(e):
                    oom += 1
                model.zero_grad()
                optimizer.zero_grad()
                scheduler.step()
                del data

                torch.cuda.empty_cache()

            if i % 1000 == 0:
                print('epoch: {}, step: {}/{}, loss: {}, lr: {}, oom: {}, time: {}s'.format(
                    epoch + 1, i, len(training_loader),
                    round(sum(training_loss) / len(training_loss), 4),
                    round(scheduler.get_last_lr()[0], 7), oom,
                    int(time.time() - start_time)
                ))
                start_time = time.time()
                oom = 0
            if i % 10000 == 0 and i > 0:
                validation_step(model, validation_loader, save_dir, parallel=parallel)
        validation_step(model, validation_loader, save_dir, parallel=parallel)


if __name__ == '__main__':
    device_ids = [0, 1, 2, 3]
    training_file = ''      # change to fine-tuning data path
    validation_file = ''    # change to fine-tuning data path
    vocabulary_file = 'incoder-1B/'
    pretrained_file = 'incoder-1B/'

    fine_tune(
        training_file, validation_file, epochs=1, batch_size=1, save_dir='../../models/incoder-1B-finetune/', 
        parallel=False, load_range=None
    )
