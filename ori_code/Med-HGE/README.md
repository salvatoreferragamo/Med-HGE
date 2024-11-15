# Med-HGE


## Requirements
* We use Conda python 3.7 and strongly recommend that you create a new environment: `conda create -n dhgn python=3.7`.
* Run the following command: `pip install -r requirements.txt`.
* Download datasets from CBLEU and TIANCHI platform for IMCS-21.

### * pytorch_geometric
* We use [pytorch_geometric](https://github.com/rusty1s/pytorch_geometric) for GNN implementation.
* Download `*.whl` files from https://pytorch-geometric.com/whl/torch-1.4.0.html
* Run following commands:
```
pip install torch_spline_conv-latest+cu100-cp37-cp37m-linux_x86_64.whl
pip install torch_cluster-latest+cu100-cp37-cp37m-linux_x86_64.whl
pip install torch_sparse-latest+cu100-cp37-cp37m-linux_x86_64.whl
pip install torch_scatter-latest+cu100-cp37-cp37m-linux_x86_64.whl
pip install torch-geometric==1.4.3
```

## From Scratch
### * preprocess
(1) Preprocess dataset with DiseaseKG.

```
python imcs_medical.py
```

### * train
```
CUDA_VISIBLE_DEVICES=x python train.py -config ./config/train.yml -save_config ./config/train.txt
CUDA_VISIBLE_DEVICES=x python train.py -config ./config/train.yml

```

### * translate
```
python translate.py \
-src data/test.src.txt \
-edge_index data/test.edge_index.txt \
-edge_type data/test.edge_type.txt \
-node_type data/test.node_type.txt \
-max_length 1000 -min_length 19 -beta 1 -ignore_when_blocking "." "," -stepwise_penalty -coverage_penalty summary -n_best 4 -batch_size 64 -beam_size 10 -dynamic_dict -share_vocab  -block_ngram_repeat 3 -replace_unk \
-model models/xxxx.pt \
-output summaries/xxxx.txt \
-gpu X
```

### * rerank
* `python rerank.py -n 4 -c summaries/xxxx.txt`

### * test rouge score
* `python py_rouge_test.py -c summaries/summary_rerank.txt`
