import torch
import torch.nn as nn
from torch.nn.functional import pad
from .base import Base


class Transformer(Base):
    def __init__(self, d_model, nhead, num_encoder_layers, num_decoder_layers, vocab_size=None):
        super(Transformer, self).__init__(d_model, vocab_size)
        self.nhead = nhead
        self.num_encoder_layers = num_encoder_layers
        self.num_decoder_layers = num_decoder_layers
        self.transformer = nn.Transformer(d_model, nhead, num_encoder_layers, num_decoder_layers)
        self.sos_token_index = 0

    def forward(self, tgt):
        sos_token = torch.full((1, tgt.size(1)), self.sos_token_index, dtype=torch.long, device=tgt.device)
        src = pad(tgt[:-1], (0, 0, 1, 0), value=self.sos_token_index)
        src = torch.cat((sos_token, src), dim=0)

        src = self.embedding(src)
        tgt = self.embedding(tgt)
        out = self.transformer(src, tgt)
        out = out.reshape(out.size(0) * out.size(1), -1)
        out = self.fc(out)
        return out

    @classmethod
    def train_model(cls, indexed_text, seq_length, vocab_size, epochs=100, batch_size=64, device='cpu', **kwargs):
        model = cls(**kwargs, vocab_size=vocab_size)
        model.to(device)

        base_result = super(Transformer, cls).train_model(indexed_text, seq_length, vocab_size, epochs, batch_size,
                                                          device, **kwargs)

        return base_result
