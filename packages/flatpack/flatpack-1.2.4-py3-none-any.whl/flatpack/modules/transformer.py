import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from flatpack.datasets import TextDataset
import json
import os


class Transformer(nn.Module):
    def __init__(self, vocab_size, d_model=512, nhead=8, num_encoder_layers=6, num_decoder_layers=6,
                 dim_feedforward=2048, dropout=0.1, activation='relu'):
        super(Transformer, self).__init__()
        self.vocab_size = vocab_size
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.transformer = nn.Transformer(d_model, nhead, num_encoder_layers, num_decoder_layers,
                                          dim_feedforward, dropout, activation)
        self.fc = nn.Linear(d_model, vocab_size)

    def forward(self, src, tgt, src_mask=None, tgt_mask=None, memory_mask=None,
                src_key_padding_mask=None, tgt_key_padding_mask=None, memory_key_padding_mask=None):
        src = self.embedding(src)
        tgt = self.embedding(tgt)
        out = self.transformer(src, tgt, src_mask, tgt_mask, memory_mask,
                               src_key_padding_mask, tgt_key_padding_mask, memory_key_padding_mask)
        out = self.fc(out)
        return out

    @staticmethod
    def generate_square_subsequent_mask(sz):
        return torch.triu(torch.ones(sz, sz), diagonal=1).bool()


def train_model(model, indexed_text, seq_length, epochs, batch_size, device):
    dataset = TextDataset(indexed_text, seq_length=seq_length)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    model.to(device)

    for epoch in range(epochs):
        total_loss = 0
        total_batches = 0

        for inputs, targets in dataloader:
            inputs = inputs.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()

            outputs = model(inputs, inputs)
            loss = criterion(outputs.view(-1, model.vocab_size), targets.view(-1))

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)
            optimizer.step()

            total_loss += loss.item()
            total_batches += 1

        average_loss = total_loss / total_batches
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {average_loss:.4f}")


def generate_text(model, char_to_index, index_to_char, start_sequence="To be, or not to be", generate_length=1024,
                  device=None):
    model.eval()
    input_sequence = [char_to_index[char] for char in start_sequence]
    input_tensor = torch.tensor(input_sequence).long().unsqueeze(0).to(device)
    generated_text = start_sequence

    with torch.no_grad():
        for _ in range(generate_length):
            output = model(input_tensor, input_tensor)
            probabilities = torch.nn.functional.softmax(output[0, -1], dim=0)
            next_index = torch.multinomial(probabilities, 1).item()
            next_char = index_to_char[str(next_index)]
            generated_text += next_char
            input_tensor = torch.cat([input_tensor[:, 1:], torch.tensor([[next_index]], device=device)], dim=1)

    return generated_text
