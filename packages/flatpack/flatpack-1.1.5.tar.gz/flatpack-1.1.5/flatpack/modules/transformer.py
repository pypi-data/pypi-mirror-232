import torch
import torch.nn as nn
from torch.nn.functional import pad
from torch.utils.data import DataLoader
import torch.optim as optim
from flatpack.datasets import TextDataset
from .base import Base


class Transformer(Base):
    def __init__(self, d_model, nhead, num_encoder_layers, num_decoder_layers, vocab_size=None):
        super(Transformer, self).__init__(d_model, vocab_size)
        self.nhead = nhead
        self.num_encoder_layers = num_encoder_layers
        self.num_decoder_layers = num_decoder_layers
        self.transformer = nn.Transformer(d_model, nhead, num_encoder_layers, num_decoder_layers)

    def forward(self, src, tgt):
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
        sos_token_index = 0

        dataset = TextDataset(indexed_text, seq_length=seq_length)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        for epoch in range(epochs):
            total_loss = 0.0
            total_accuracy = 0.0
            total_batches = 0

            for inputs, targets in dataloader:
                inputs = inputs.to(device)
                targets = targets.to(device)

                sos_token = torch.full((1, targets.size(1)), sos_token_index, dtype=torch.long, device=device)
                src = pad(targets[:-1], (0, 0, 1, 0), value=sos_token_index)
                src = torch.cat((sos_token, src), dim=0)
                outputs = model(src, targets)

                loss = criterion(outputs.view(-1, vocab_size), targets.view(-1))
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)
                optimizer.step()

                _, predicted = torch.max(outputs.data, 1)
                correct = (predicted == targets.view(-1))
                accuracy = correct.sum().item() / (targets.size(0) * targets.size(1))

                total_loss += loss.item()
                total_accuracy += accuracy
                total_batches += 1

            average_loss = total_loss / total_batches
            average_accuracy = total_accuracy / total_batches
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {average_loss:.4f}, Accuracy: {average_accuracy:.4f}")

        return {'model': model}
