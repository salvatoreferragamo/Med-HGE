import json
import os
import numpy as np
from collections import defaultdict


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


# data_dir = '../../../dataset'
data_dir = '../dataset'
train_set = load_json(os.path.join(data_dir, 'train.json'))
dev_set = load_json(os.path.join(data_dir, 'dev.json'))
test_set = load_json(os.path.join(data_dir, 'test.json'))

# save_path = '../ernie_predictions.npz'
# test_prediction = np.load(save_path)['test_prediction']


def process(title):
    x = []
    for key, value in title.items():
        x.append(key + '：' + value)
    return ''.join(x)


def label2id(samples):
    label2id = defaultdict()
    labels = []
    for pid, sample in samples.items():
        for sent in sample['dialogue']:
            if sent['dialogue_act'] not in labels:
                labels.append(sent['dialogue_act'])
    for i, label in enumerate(labels):
        label2id[label] = i

    return label2id


def make_data(samples, path, label2id, mode='train'):
    lines = ''
    i = 0
    # if not os.path.exists(path):
    #     os.mkfile(path)
    with open(path, 'w', encoding='utf-8') as f:
        for pid, sample in samples.items():
            content = []
            if mode == 'test1':
                for sent in sample['dialogue']:
                    if test_prediction[i] != 15:
                        content.append(sent['speaker'] + sent['sentence'])
                    i += 1
            else:
                for sent in sample['dialogue']:
                    if sent['dialogue_act'] != 'Other':
                        content.append(sent['speaker'] + sent['sentence'])
                        title1, title2 = process(sample['report'][0]), process(sample['report'][1])
            content = ''.join(content)
            # title1, title2 = process(sample['report'][0]), process(sample['report'][1])
            if mode == 'train':
                lines += title1 + '\t' + content + '\n'
                lines += title2 + '\t' + content + '\n'
            elif mode == 'dev':
                lines += title1 + '\t' + content + '\n'
            elif mode == 'dev_for_test':
                lines += title1 + '\t' + content + '\n'
            else:
                lines += content + '\n'
        f.write(lines)
    if mode == 'test1':
        assert i == len(test_prediction)


# label2id =label2id(train_set)
# print(label2id)

make_data(train_set, 'data/train.tsv', None, mode='train')
make_data(dev_set, 'data/dev.tsv', None, mode='dev')

make_data(dev_set, 'data/dev_predict.tsv',  None, mode='test')
# make_data(test_set, 'data/predict.tsv', None, mode='test')
