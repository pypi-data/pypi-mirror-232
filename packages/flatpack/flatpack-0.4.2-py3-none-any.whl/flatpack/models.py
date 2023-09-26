import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader


class RNNLM(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size, num_layers):
        super(RNNLM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.rnn = nn.RNN(embed_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.rnn(x)
        out = self.fc(out)
        return out

    @staticmethod
    def train_model(dataset, vocab_size, embed_size, hidden_size, num_layers, epochs, batch_size):
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        model = RNNLM(vocab_size, embed_size, hidden_size, num_layers)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        for epoch in range(epochs):
            total_loss = 0.0
            total_accuracy = 0.0
            total_batches = 0

            for inputs, targets in dataloader:
                inputs = inputs.long()
                outputs = model(inputs)
                loss = criterion(outputs.view(-1, vocab_size), targets.view(-1))

                _, predicted = torch.max(outputs.data, 2)
                correct = (predicted == targets)
                accuracy = correct.sum().item() / (targets.size(0) * targets.size(1))

                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)
                optimizer.step()

                total_loss += loss.item()
                total_accuracy += accuracy
                total_batches += 1

            # Print epoch-wise progress
            average_loss = total_loss / total_batches
            average_accuracy = total_accuracy / total_batches
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {average_loss:.4f}, Accuracy: {average_accuracy:.4f}")

        return {'model': model}

    def generate_text(model, tokenizer, detokenizer, start_sequence="In the beginning", generate_length=1024,
                 temperature=1.0):
        input_tensor = tokenizer(start_sequence)
        generated_text = start_sequence

        model.eval()

        with torch.no_grad():
            for _ in range(generate_length):
                output = model(input_tensor)
                probabilities = F.softmax(output[0, -1] / temperature, dim=0)
                next_index = torch.multinomial(probabilities, 1).item()
                next_token = detokenizer(next_index)

                generated_text += next_token
                input_tensor = tokenizer(generated_text[-model.input_size:])

        return generated_text
