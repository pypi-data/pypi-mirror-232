
import torch
from torch import nn 

class TemporalDependency(nn.Module):
    def __init__(self, rank, nlayers, nhidden, dropout):
        super(TemporalDependency, self).__init__()

        self.nlayers = nlayers
        self.nhid = nhidden

        self.rnn = nn.LSTM(input_size=rank,
                           hidden_size=nhidden,
                           num_layers=nlayers,
                           dropout=dropout,
                           batch_first=True)
        self.decoder = nn.Sequential(
            nn.Linear(nhidden, rank),
            nn.ReLU()
        )
        self.init_weights()

    def init_weights(self):
        init_range = 0.1
        for m in self.modules():
            if isinstance(m, nn.Linear):
                m.weight.data.uniform_(-init_range, init_range)
                m.bias.data.zero_()

    def forward(self, Ws, device):
        train_loss = 0.0
        for Wp in Ws:
            inputs, targets = Wp[:-1, :], Wp[1:, :]  # seq_len x n_dim
            seq_len, n_dims = inputs.size()

            hidden = self.init_hidden(1)
            # seq_len x n_dims --> 1 x seq_len x n_dims
            outputs, _ = self.rnn(inputs.unsqueeze(0), hidden)
            logits = self.decoder(outputs.contiguous().view(-1, self.nhid))
            loss = self.loss(logits, targets)
            train_loss += loss
        return train_loss

    def init_hidden(self, batch_sz):
        size = (self.nlayers, batch_sz, self.nhid)
        weight = next(self.parameters())
        return (weight.new_zeros(*size),
                weight.new_zeros(*size))

    def loss(self, input, target):
        return torch.mean((input - target) ** 2)