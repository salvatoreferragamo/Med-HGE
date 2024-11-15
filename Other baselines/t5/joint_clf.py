from msilib.schema import Class
import torch
import torch.nn as nn


class jointClf(nn.Module):
    def __init__(self, args):
        super(jointClf, self).__init__()
        self.args = args

        # attention部分，encoder与decoder分别模拟的transformer的，故不必再写
        # self.attention = AttentionNet(args)

    def forward(self, dif_type_ent_lists, token_rep, sent_mask)


