import torch
from torch.utils.data import Dataset


class Subset(Dataset):
    def __init__(self, dataset, indices):
        self.dataset = dataset
        self.indices = indices

    def __getitem__(self, idx):
        return self.dataset[self.indices[idx]], idx

    def __len__(self):
        return len(self.indices)


def transform3DTensorTo4D(dataset, twl):
    dataset = [torch.t(dataset[i]) for i in range(len(dataset))]
    tensor4D = torch.stack(
        [
            torch.zeros((int(dataset[Tp].shape[0] / twl), twl, dataset[Tp].shape[1]))
            for Tp in range(len(dataset))
        ]
    )
    for i in range(len(dataset)):
        for j in range(int(dataset[i].shape[0] / twl)):
            tensor4D[i][j] = dataset[i][(j * twl) : (j + 1) * twl]
    return torch.transpose(tensor4D, 2, 3)


def success_rate(base, result):
    """
    Parameters
    -----------
    base: torch.Tensor
        phenotypes, pathways or patients matrices
    result: torch.Tensor
        tensor with the same shape as base
    """
    dis = 0
    max = 0
    for i in range(len(base)):
        dis += torch.norm((base[i] - result[i]), p="fro").item()
        max += torch.norm(base[i], p="fro").item()

    try:
        return 1 - dis / max
    except ZeroDivisionError:
        return 0
