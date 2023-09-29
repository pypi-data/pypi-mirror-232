# -*- coding: utf-8 -*-
"""This module implements the FastSWoTTeD reconstruction of tensors based
on the temporal convolution of the temporal phenotypes with a pathways.

This fast implementation decomposes collection of pathway all having the 
same length.
"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

from munkres import Munkres
from swotted.loss_metrics import *
from swotted.temporal_regularization import *
from swotted.utils import *
import lightning.pytorch as pl

from omegaconf import DictConfig


class fastSWoTTeDDataset(Dataset):
    """Implementation of a dataset class for `FastSwotted`.

    The dataset uses a 3D tensors with dimensions :math:`K * N * T` where
    :math:`K` is the number of individuals, :math:`N` the number of features
    and :math:`T` the shared duration.

    *FastSwotted* requires the pathways to be of same length.
    """

    def __init__(self, dataset: torch.Tensor):
        """
        Parameters
        ----------
        dataset: torch.Tensor
            3D Tensor with dimensions :math:`K * N * T` where
            :math:`K` is the number of individuals, :math:`N` the number of features
            and :math:`T` the shared duration.
        """
        if not isinstance(dataset, torch.Tensor) or len(dataset.shape) != 3:
            raise TypeError(
                "Invalid type for dataset: excepted a tensor of 3D dimension"
            )

        self.dataset = dataset

    def __getitem__(self, idx: int):
        return self.dataset[idx, :, :], idx

    def __len__(self):
        return self.dataset.shape[0]



class SlidingWindowConv(nn.Module):
    def __init__(self, dist=Loss()):
        super().__init__()
        self.setMetric(dist)

    def setMetric(self, dist):
        """Setter for the metric property

        Parameters
        ----------
        dist: Loss
            Selection of one loss metric used to evaluate the quality of the reconstruction

        See
        ---
        loss_metric.py"""
        self.metric = dist

    def reconstruct(self, W: torch.Tensor, Ph: torch.Tensor) -> torch.Tensor:
        """Reconstruction function based on a convolution operator

        Parameters
        ----------
        W: torch.Tensor
            Pathway containing all occurrences of the phenotypes
        Ph: torch.Tensor
            Description of the phenotypes

        Returns
        -------
        torch.Tensor
            The reconstructed pathway that combines all occurrences of the phenotypes
            along time."""
        Y = torch.conv1d(W, Ph.transpose(0, 1), padding=Ph.shape[2] - 1).squeeze(dim=0)

        if W.shape[0]:
            Y = Y.unsqueeze(0)
        return Y

    def loss(self, Xp: torch.Tensor, Wp: torch.Tensor, Ph: torch.Tensor) -> float:
        """
        Parameters
        ----------
        Xp: torch.Tensor
            a 2nd-order tensor of size :math:`N * Tp`, where :math:`N` is the number of
            drugs and :math:`Tp` is the time of the patient's stay
        Ph: torch.Tensor
            phenotypes of size :math:`R * N * \omega`, where :math:`R` is the number of
            phenotypes and :math:`\omega` the length of the temporal window
        Wp: torch.Tensor
            assignement tensor of size :math:`R * Tp` for patient :math:`p`
        """
        Yp = self.reconstruct(Wp.unsqueeze(dim=0), Ph)
        # evaluate the loss
        return self.metric.compute(Xp, Yp)

    def forward(
        self, X: torch.Tensor, W: torch.Tensor, Ph: torch.Tensor, padding: bool = None
    ) -> float:
        """
        Parameters
        ----------
        X: torch.Tensor
            a 3rd-order tensor of size :math:`K * N * Tp`, where :math:`N` is the number of
            drugs and :math:`Tp` is the time of the patients' stays
        Ph: torch.Tensor
            phenotypes of size :math:`R * N * \omega`, where :math:`R` is the number of
            phenotypes and :math:`\omega` the length of the temporal window
        W: torch.Tensor
            assignement tensor of size :math:`K * R * Tp` for all patients
        """
        # W is a tensor of size K x N x Tp
        Y = self.reconstruct(W, Ph)

        if padding is not None:
            if isinstance(padding, tuple) and len(padding) == 2:
                return self.metric.compute(
                    torch.split(
                        X,
                        [padding[0], X.shape[1] - padding[0] - padding[1], padding[1]],
                        dim=1,
                    )[1],
                    torch.split(
                        Y,
                        [padding[0], Y.shape[1] - padding[0] - padding[1], padding[1]],
                        dim=1,
                    )[1],
                )
            else:
                raise ValueError(
                    f"error in padding parameter, got {padding} and expected the tuple of length 2."
                )
        else:
            return self.metric.compute(X, Y)


class fastSWoTTeDModule(pl.LightningModule):
    """

    Warning
    -------
    The fastSwottedModule has to be used with a fastSwottedTrainer. This trainer
    ensures the initialisation of the internal :math:`W` and :math:`O` tensors, 
    when the dataset is known.

    Warning
    -------
    The phenotypes that are discovered by this module have to be flipped to
    correspond to the correct temporal order!

    .. code-block:: python

        swotted = fastSwottedModule()
        ...
        swotted.fit()
        ...
        Ph = swotted.Ph
        Ph = Ph.flip(2)
    """

    def __init__(self, config: DictConfig):
        """
        Parameters
        ----------
        config: (omegaconf.DictConfig)
            Configuration of the model, training parameters and prediction parameters
            see FastswoTTed_test.py for the list of required parameters.
        """
        super().__init__()

        # use config as parameter
        self.params = config

        self.model = SlidingWindowConv(eval(self.params.model.metric)())

        try:
            self.alpha = self.params.model.sparsity  # sparsity
            self.beta = self.params.model.non_succession  # non-succession
            self.adam = True

            self.sparsity = self.params.model.sparsity > 0
            self.pheno_succession = self.params.model.non_succession > 0
            self.non_negativity = True
            self.normalization = True

            self.rank = self.params.model.rank
            self.N = self.params.model.N
            self.twl = self.params.model.twl
        except:
            raise ValueError("Missing mandatory model parameters in the configuration")

        self.Ph = torch.nn.Parameter(
            torch.rand(
                (self.params.model.rank, self.params.model.N, self.params.model.twl)
            )
        )

        # Important: Wk is not directly part of the model. This torch variable is initialized in the trainer.
        self.Wk = None

        # O is a tool tensor for non-succession constraint. It is initialized in the trainer.
        self.O = None

        # Important: This property activates manual optimization.
        self.automatic_optimization = False

    def configure_optimizers(self):
        """
        Parent override.
        """

        if self.adam:
            optimizerPh = optim.Adam([self.Ph], lr=self.params.training.lr)
        else:
            optimizerPh = optim.SGD([self.Ph], lr=self.params.training.lr, momentum=0.9)

        return optimizerPh

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        """This forward function makes the decomposition of the tensor `X`.
        It contains an optimisation stage to find the best decomposition.
        The optimisation does not modifies the phenotypes of the model.

        Parameters
        -----------
        X: (torch.Tensor)
            tensor of dimension :math:`K * N * T` to decompose according to the phenotype of the model

        Returns
        --------
        torch.Tensor
            A tensor of dimension :math:`K * R * (T-\omega)` that is the decomposition of X according
            to the :math:`R` phenotypes of the model
        """

        K = X.shape[0]  # number of patients
        if self.N != X.shape[1]:  # number of medical events
            raise ValueError(
                f"The second dimension of X (number of features) is invalid (expected {self.N})."
            )

        with torch.inference_mode(False):
            # torchlightning activates the inference mode that deeply disable the computation
            # of gradients in the function. This is not sufficient to enable_grad() only.
            Wk_batch = Variable(
                torch.rand(K, self.rank, X.shape[2] - self.twl + 1), requires_grad=True
            )
            optimizerW = optim.Adam([Wk_batch], lr=self.params["predict"]["lr"])

            n_epochs = self.params["predict"]["nepochs"]
            for _ in range(n_epochs):

                def closure():
                    optimizerW.zero_grad()
                    loss = self.model(X, Wk_batch, self.Ph.data)
                    if self.pheno_succession:
                        loss += self.beta * self.phenotypeNonSuccession_loss(
                            Wk_batch, self.twl
                        )
                    loss.backward()
                    return loss

                optimizerW.step(closure)
                if self.non_negativity:
                    Wk_batch.data[Wk_batch.data < 0] = 0
                if self.normalization:
                    Wk_batch.data = torch.clamp(Wk_batch.data, 0, 1)
        return Wk_batch

    def predict_step(self, batch, batch_idx, dataloader_idx=0) -> float:
        """
        Parent override.
        """
        return self(batch)  # it only calls the forward function

    def training_step(self, batch, idx):
        """
        Parent override.
        """

        optimizerPh = self.optimizers()

        D, indices = zip(*batch)
        X = torch.stack(D, dim=0)

        Wk_batch = self.Wk[indices, :, :].detach()
        Wk_batch.requires_grad_(True)
        Wk_batch_nograd = self.Wk[indices, :, :].data

        if self.adam:
            optimizerW = optim.Adam([Wk_batch], lr=self.params.training.lr)
        else:
            optimizerW = optim.SGD([Wk_batch], lr=self.params.training.lr, momentum=0.9)

        def closure():
            optimizerPh.zero_grad()
            loss = self.model(X, Wk_batch_nograd, self.Ph)
            self.log(
                "train_reconstr_Ph",
                loss,
                on_step=True,
                on_epoch=False,
                prog_bar=False,
                logger=True,
            )
            if self.sparsity:
                sparsity_loss=torch.norm(self.Ph, 1)
                self.log(
                    "train_sparsity_Ph",
                    sparsity_loss,
                    on_step=True,
                    on_epoch=False,
                    prog_bar=False,
                    logger=True,
                )
                loss += self.alpha * sparsity_loss
            loss.backward()
            self.log(
                "train_loss_Ph",
                loss,
                on_step=True,
                on_epoch=False,
                prog_bar=False,
                logger=True,
            )
            return loss

        optimizerPh.step(closure)

        if self.non_negativity:
            self.Ph.data[self.Ph.data < 0] = 0
        if self.normalization:
            self.Ph.data = torch.clamp(self.Ph.data, 0, 1)

        # update W
        def closure():
            optimizerW.zero_grad()
            loss = self.model(X, Wk_batch, self.Ph.data)
            self.log(
                "train_reconstr_W",
                loss,
                on_step=True,
                on_epoch=False,
                prog_bar=False,
                logger=True,
            )
            if self.pheno_succession:
                nonsucc_loss=self.phenotypeNonSuccession_loss(Wk_batch, self.twl)
                self.log(
                    "train_nonsucc_W",
                    nonsucc_loss,
                    on_step=True,
                    on_epoch=False,
                    prog_bar=False,
                    logger=True,
                )
                loss += self.beta * nonsucc_loss
            loss.backward()
            self.log(
                "train_loss_W",
                loss,
                on_step=True,
                on_epoch=False,
                prog_bar=False,
                logger=True
            )
            return loss

        optimizerW.step(closure)
        if self.non_negativity:
            Wk_batch.data[Wk_batch.data < 0] = 0
        if self.normalization:
            Wk_batch.data = torch.clamp(Wk_batch.data, 0, 1)

        self.Wk[indices, :, :] = Wk_batch

    def test_step(self, batch, batch_idx) -> float:
        X, _ = zip(*batch)
        W_hat = self(X)
        loss = self.model(X, W_hat, self.Ph)
        #self.log("test_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        """
        Parent override.

        ***This function has not been tested***
        """
        X, y = zip(*batch)
        W_hat = self(
            X
        )  # Apply the model on the data (requires optimisation of local W)
        loss = self.model(X, W_hat, self.Ph)
        #self.log("val_loss", loss)

    def forecast(self, X: torch.Tensor) -> torch.Tensor:
        """This function forecasts the next time step using the trained phenotypes.
        This function can be used only with the parameter :math:`\omega\geq 2` (`twl>=2`)
        (phenotypes with more than two instant).

        This function makes a projection of the data with the phenotypes of the model.

        For computational efficiency, the time dimension of :math:`X` is reduced to
        :math:`\omega`, and then is extended :math:`\omega-1` time steps on the right with
        empty values.

        Parameters
        ----------
        X: (torch.Tensor)
            tensor of dimension :math:`K* N* T` with :math:`T` to decompose
            according to the phenotype of the model.

        Returns
        --------
        torch.Tensor
            A tensor of dimension :math:`K * N` that is the forecast of the
            next time step of :math:`X`.
        """

        if self.twl < 2:
            # trained with daily phenotypes
            raise ValueError(
                f"The width of the phenotype does not always to make forecasts. \
                It is possible only with phenotype having a width>1."
            )

        K = X.shape[0]  # number of patients
        if self.N != X.shape[1]:  # number of medical events
            raise ValueError(
                f"The second dimension of X (number of features) is invalid (expected {self.N})."
            )

        # reduction of the data based on the last "window" of size twl with zeros of length twl (region to predict)
        X = torch.cat(
            (X[:, :, -(self.twl - 1) :], torch.zeros((K, self.N, self.twl))), axis=2
        )

        # now, we decompose the tensor ... without considering the last part of the
        # reconstruction, ie the predicted part
        with torch.inference_mode(False):
            # torchlightning activates the inference mode that deeply disable the computation
            # of gradients in the function. This is not sufficient to enable_grad() only.

            Wk_batch = Variable(
                torch.rand(K, self.rank, X.shape[2] - self.twl + 1), requires_grad=True
            )
            optimizerW = optim.Adam([Wk_batch], lr=self.params["predict"]["lr"])

            n_epochs = self.params["predict"]["nepochs"]
            for _ in range(n_epochs):

                def closure():
                    optimizerW.zero_grad()
                    # evaluate the loss based on the beginning of the reconstruction only
                    loss = self.model(X, Wk_batch, self.Ph.data, padding=(0, self.twl))
                    if self.pheno_succession:
                        loss += self.beta * self.phenotypeNonSuccession_loss(
                            Wk_batch, self.twl
                        )
                    loss.backward()
                    return loss

                optimizerW.step(closure)
                if self.non_negativity:
                    Wk_batch.data[Wk_batch.data < 0] = 0
                if self.normalization:
                    Wk_batch.data = torch.clamp(Wk_batch.data, 0, 1)

        # make a reconstruction, and select only the next event
        with torch.no_grad():
            pred = self.model.reconstruct(Wk_batch, self.Ph.data)[:, :, self.twl]
        return pred
    

    def phenotypeNonSuccession_loss(self, Wk: torch.Tensor, Tw: torch.Tensor):
        """Definition of a loss that pushes the decomposition to add the
        description in phenotypes preferably to in the pathways.

        Parameters
        ----------
        Wk: torch.Tensor
            A 3rd order tensor of size :math:`K * R * (T-\omega+1)`
        """
        return torch.sum(torch.clamp(Wk * torch.log(10e-8 + torch.conv1d(Wk, self.O, padding=Tw)),min=0))


    def reorderPhenotypes(
        self, gen_pheno: torch.Tensor, Wk: torch.Tensor = None, tw: int = 2
    ) -> torch.Tensor:
        """
        This function outputs reordered internal phenotypes and pathways.

        Parameters
        ----------
        gen_pheno: (torch.Tensor)
            generated phenotypes of size :math:`R * N * \omega`, where :math:`R` is the number of
            phenotypes, :math:`N` is the number of drugs and :math:`\omega` is the length of the
            temporal window
        Wk: (torch.Tensor)
            pathway to reorder. If None, the function uses the internal pathways
        tw: (int)
            windows size (:math:`\omega`)

        Returns
        -------
        torch.Tensor
            A pair `(rPh,rW)` with reordered phenotypes (aligned at best with `gen_pheno`) and
            the corresponding reodering of the pathways
        """
        if Wk is None:
            Wk = self.Wk

        if tw == 1:
            gen_pheno = torch.unsqueeze(gen_pheno, 2)  # transform into a matrix

        if gen_pheno[0].shape != self.Ph[0].shape:
            raise ValueError(
                "The generated phenotypes and computed phenotypes doesn't have the same shape"
            )

        dic = np.zeros(
            (gen_pheno.shape[0], self.Ph.shape[0])
        )  # construct a cost matrix

        Ph = self.Ph.flip(2)

        for i in range(gen_pheno.shape[0]):
            for j in range(Ph.shape[0]):
                dic[i][j] = torch.norm((gen_pheno[i] - Ph[j]), p="fro").item()

        m = Munkres()  # Use of Hungarian Algorithm to find phenotypes correspondances
        indexes = m.compute(dic)

        # Reorder phenotypes
        reordered_pheno = Ph.clone()
        for row, column in indexes:
            reordered_pheno[row] = Ph[column]

        # Reorder pathways
        reordered_pathways = Wk.clone()
        for row, column in indexes:
            reordered_pathways[:, row] = Wk[:, column]

        return reordered_pheno, reordered_pathways


class fastSWoTTeDTrainer(pl.Trainer):
    def fit(
        self,
        model: fastSWoTTeDModule,
        train_dataloaders,
        val_dataloaders=None,
        datamodule=None,
        ckpt_path=None,
    ):
        model.Wk = Variable(
            torch.rand(
                len(train_dataloaders.dataset),
                model.rank,
                train_dataloaders.dataset[0][0].shape[1] - model.twl + 1,
            ),
            requires_grad=False,
        )

        # O is a matrix used for the non-succession constraint
        model.O = torch.transpose(
            #torch.stack([torch.zeros(model.Wk.shape[1], model.Wk.shape[1])]* (model.twl+1) + [torch.eye(model.Wk.shape[1])]* (model.twl)), 0, 2
            torch.stack([torch.eye(model.Wk.shape[1])]* (2*model.twl+1)), 0, 2
        )
        ret = super().fit(
            model, train_dataloaders, val_dataloaders, datamodule, ckpt_path
        )
    
        return ret
