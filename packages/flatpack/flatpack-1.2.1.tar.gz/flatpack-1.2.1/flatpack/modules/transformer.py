import torch
import torch.nn as nn
from transformers import GPT2LMHeadModel, GPT2Config
from .base import Base


class Transformer(Base):
    def __init__(self, d_model, nhead, num_encoder_layers, num_decoder_layers, vocab_size=None):
        super(Transformer, self).__init__(d_model, vocab_size)

        config = GPT2Config(
            vocab_size=vocab_size,
            n_positions=d_model,
            n_ctx=d_model,
            n_embd=d_model,
            n_layer=num_encoder_layers,
            n_head=nhead,
        )

        self.transformer = GPT2LMHeadModel(config)

    def forward(self, input_ids):
        outputs = self.transformer(input_ids, return_dict=True)
        return outputs.logits

    @classmethod
    def train_model(cls, indexed_text, seq_length, vocab_size, epochs=100, batch_size=64, device='cpu', **kwargs):
        model = cls(**kwargs, vocab_size=vocab_size)
        model.to(device)

        base_result = super(Transformer, cls).train_model(indexed_text, seq_length, vocab_size, epochs, batch_size,
                                                          device, **kwargs)

        return base_result
