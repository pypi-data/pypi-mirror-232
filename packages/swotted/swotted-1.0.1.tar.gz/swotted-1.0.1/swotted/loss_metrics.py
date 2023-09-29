
import torch


class Loss():
    def compute(self, X, Y):
        return (X-Y).sum()

class Frobenius(Loss):
    def compute(self, X, Y):
        return torch.norm((X-Y), p='fro') 

class Poisson(Loss):
    def compute(self, X, Y):
        return (Y.sum() - (X * torch.log(Y.clamp(min=1e-10))).sum())


class Bernoulli(Loss):
    def compute(self, X, Y):
        return (torch.log(1 + Y.clamp(min=1e-10))).sum() - (X * torch.log(Y.clamp(min=1e-10))).sum() 
