from torch.utils.data import Dataset


class TextDataset(Dataset):
    def __init__(self, indexed_text, seq_length):
        self.indexed_text = indexed_text
        self.seq_length = seq_length

    def __len__(self):
        return len(self.indexed_text) - self.seq_length

    def __getitem__(self, idx):
        return (self.indexed_text[idx:idx + self.seq_length], self.indexed_text[idx + 1:idx + self.seq_length + 1])
