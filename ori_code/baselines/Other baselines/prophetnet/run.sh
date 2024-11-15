export CUDA_VISIBLE_DEVICES=0,1

# pre-process
fairseq-preprocess \
--user-dir prophetnet \
--task translation_prophetnet \
--source-lang src --target-lang tgt \
--trainpref data/tokenized_train --validpref data/tokenized_dev --testpref data/tokenized_dev \
--destdir processed --srcdict vocab.txt --tgtdict vocab.txt \
--workers 20

# train
DATA_DIR=processed/
ARCH=ngram_transformer_prophet_large
CRITERION=ngram_language_loss
SAVE_DIR=models/
USER_DIR=./prophetnet
PRETRAINED_CHECKPOINT=./pretrained_checkpoint/prophetnet_zh.pt

fairseq-train $DATA_DIR \
--ngram 2 \
--user-dir $USER_DIR --task translation_prophetnet --arch $ARCH \
--optimizer adam --adam-betas '(0.9, 0.999)' --clip-norm 0.1 \
--lr 0.0001 --min-lr 1e-09 \
--lr-scheduler inverse_sqrt --warmup-init-lr 1e-07 --warmup-updates 1000 \
--dropout 0.1 --attention-dropout 0.1 --weight-decay 0.01 \
--criterion $CRITERION --label-smoothing 0.1 \
--update-freq 4 --max-sentences 1 \
--num-workers 0  \
--ddp-backend=no_c10d --max-epoch 10 \
--max-source-positions 512 --max-target-positions 256 \
--truncate-source --load-from-pretrained-model $PRETRAINED_CHECKPOINT \
--empty-cache-freq 64 \
--save-dir $SAVE_DIR \
--distributed-no-spawn \
--skip-invalid-size-inputs-valid-test


# BEAM=5
# CHECK_POINT=./models/checkpoint10.pt
# TEMP_FILE=fairseq_outputs.txt
# OUTPUT_FILE=sorted_outputs.txt

# fairseq-generate processed --path $CHECK_POINT --user-dir prophetnet --task translation_prophetnet --batch-size 80 --gen-subset test --beam $BEAM --num-workers 4 --no-repeat-ngram-size 3  2>&1 > $TEMP_FILE
# grep ^H $TEMP_FILE | cut -c 3- | sort -n | cut -f3- | sed "s/ ##//g" > $OUTPUT_FILE
