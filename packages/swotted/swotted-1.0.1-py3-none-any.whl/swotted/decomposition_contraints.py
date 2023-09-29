from math import log
import torch
from functools import reduce


def sparsity_constraint(var):
    return torch.norm(var, 1)


def nonnegative_projection(*var):
    for X in var:
        X.data[X.data < 0] = 0


def normalization_constraint(*var):
    for X in var:
        X.data = torch.clamp(X.data, 0, 1)


def phenotypeSuccession_constraint(Wk, Tw):
    """
    Parameters
    ----------
    Wk: torch.Tensor
        A 3rd order tensor of size :math:`K * rank * (T-Tw+1)`
    """
    O = torch.transpose( torch.stack([ torch.eye(Wk[0].shape[0])]*(2 * Tw + 1) ), 0, 2 )
    penalisation = reduce(
        torch.add, [torch.sum(torch.clamp(Wp * torch.log(10e-8 + torch.conv1d(Wp, O, padding=Tw)),min=0)) for Wp in Wk]
    )
    return penalisation


def phenotype_uniqueness(Ph):
    Ph = torch.transpose(Ph, 1, 2)
    ps = 0
    for i in range(Ph.shape[0]):
        for p1 in range(Ph.shape[1]):
            for j in range(i + 1, Ph.shape[0]):
                for p2 in range(Ph.shape[1]):
                    ps += torch.dot(Ph[i][p1], Ph[j][p2])
                    # print("(i, p1) : ", i, p1, "(j, p2) : ", j, p2)

    return ps.data
