import numpy as np
import torch
import torch.optim as optim
from torch.autograd import Variable
from munkres import Munkres
from swotted.slidingWindow_model import SlidingWindow
from swotted.loss_metrics import *
from swotted.decomposition_contraints import *
from swotted.temporal_regularization import *
from swotted.utils import *
import lightning.pytorch as pl

from omegaconf import DictConfig


class swottedModule(pl.LightningModule):
    def __init__(self, config: DictConfig):
        super().__init__()

        # use config as parameter
        self.params = config

        self.model = SlidingWindow()
        self.model.setMetric(eval(self.params.model.metric)())

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

        self.Ph = torch.nn.Parameter(
            torch.rand(
                (self.params.model.rank, self.params.model.N, self.params.model.twl)
            )
        )

        # Important: Wk is not directly part of the model
        self.Wk = None

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

        if self.adam:
            optimizerW = optim.Adam(self.Wk, lr=self.params.training.lr)
        else:
            optimizerW = optim.SGD(self.Wk, lr=self.params.training.lr, momentum=0.9)

        return optimizerPh, optimizerW

    def forward(self, X):
        """
        This forward function makes the decomposition of the tensor `X`.
        It contains an optimisation stage to find the best decomposition.
        The optimisation does not modifies the phenotypes of the model.

        Parameters
        -----------
        X: torch.Tensor
            tensor of dimension :math:`K * N * T` to decompose according to the phenotype of the model

        Returns
        --------
        torch.Tensor
            A tensor of dimension :math:`K * R * (T-Tw)` that is the decomposition of X according to the :math:`R` phenotypes of the model
        """
        # self.unfreeze()
        K = len(X)  # number of patients
        if self.N != X[0].shape[0]:  # number of medical events
            # TODO throw an error
            return None

        with torch.inference_mode(False):
            # torchlightning activates the inference mode that deeply disable the computation
            # of gradients in the function. This is not sufficient to enable_grad() only.

            Wk_batch = [
                Variable(
                    torch.rand(self.rank, X[Tp].shape[1] - self.twl + 1),
                    requires_grad=True,
                )
                for Tp in range(K)
            ]
            optimizerW = optim.Adam(Wk_batch, lr=self.params["predict"]["lr"])

            n_epochs = self.params["predict"]["nepochs"]
            for epoch in range(n_epochs):

                def closure():
                    optimizerW.zero_grad()
                    loss = self.model(X, Wk_batch, self.Ph.data)
                    if self.pheno_succession:
                        loss += self.beta * phenotypeSuccession_constraint(
                            Wk_batch, self.twl
                        )
                    loss.backward()
                    return loss

                optimizerW.step(closure)
                if self.non_negativity:
                    nonnegative_projection(*Wk_batch)
                if self.normalization:
                    normalization_constraint(*Wk_batch)
            # self.freeze()
        return Wk_batch

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        """
        Parent override.
        """
        return self(batch)  # it only calls the forward function

    def training_step(self, batch, idx):
        """
        Parent override.
        """

        optimizerPh, optimizerW = self.optimizers()

        D, indices = zip(*batch)
        X = D
        Wk_batch = [self.Wk[p] for p in indices]
        Wk_batch_nograd = [self.Wk[p].data for p in indices]

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
                sparsity_loss = sparsity_constraint(self.Ph)
                self.log(
                    "train_sparsity_Ph",
                    sparsity_loss,
                    on_step=True,
                    on_epoch=False,
                    prog_bar=False,
                    logger=True,
                )
                loss+=self.alpha * sparsity_loss
            loss.backward()
            self.log(
                "train_loss_Ph",
                loss,
                on_step=True,
                on_epoch=False,
                prog_bar=False,
                logger=True,
                batch_size=len(indices),

            )
            return loss

        optimizerPh.step(closure)

        if self.non_negativity:
            nonnegative_projection(*self.Ph)  # non-negativity constraint
        if self.normalization:
            normalization_constraint(*self.Ph)  # normalization constraint

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
                nonsucc_loss=phenotypeSuccession_constraint(Wk_batch, self.twl)
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
                logger=True,
                batch_size=len(indices),
            )
            return loss

        optimizerW.step(closure)
        if self.non_negativity:
            nonnegative_projection(*Wk_batch)
        if self.normalization:
            normalization_constraint(*Wk_batch)

    def test_step(self, batch, batch_idx):
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

    def forecast(self, X):
        """
        This function forecasts the next time step using the trained phenotypes.
        This function can be used only with the parameter :math:`$\omega\geq 2` (`twl>=2`)
        (phenotypes with more than two instant).

        This function makes a projection of the data with the phenotypes of the model.

        For computational efficiency, the time dimension of :math:`X` is reduced to
        :math:`\omega`, and then is extended :math:`\omega-1` time steps on the right with
        empty values.

        Parameters
        ----------
        X: torch.Tensor
            tensor of dimension :math:`K* N* T` with :math:`T` to decompose
            according to the phenotype of the model.

        Returns
        --------
        torch.Tensor
            A tensor of dimension :math:`K* N` that is the forecast of the
            next time step of :math:`X`.
        """

        if self.twl < 2:
            # trained with daily phenotypes
            # TODO throw an error
            return None

        K = len(X)  # number of patients
        if self.N != X[0].shape[0]:  # number of medical events
            # TODO throw an error
            return None

        # reduction of the data based on the last "window" of size twl with zeros of length twl (region to predict)
        X = [
            torch.cat(
                (xi[:, -(self.twl - 1) :], torch.zeros((self.N, self.twl))), axis=1
            )
            for xi in X
        ]

        # now, we decompose the tensor ... without considering the last part of the
        # reconstruction, ie the predicted part
        with torch.inference_mode(False):
            # torchlightning activates the inference mode that deeply disable the computation
            # of gradients in the function. This is not sufficient to enable_grad() only.

            Wk_batch = [
                Variable(
                    torch.rand(self.rank, X[Tp].shape[1] - self.twl + 1),
                    requires_grad=True,
                )
                for Tp in range(K)
            ]
            optimizerW = optim.Adam(Wk_batch, lr=self.params["predict"]["lr"])

            n_epochs = self.params["predict"]["nepochs"]
            for _ in range(n_epochs):

                def closure():
                    optimizerW.zero_grad()
                    # evaluate the loss based on the beginning of the reconstruction only
                    loss = self.model(X, Wk_batch, self.Ph.data, padding=(0, self.twl))
                    if self.pheno_succession:
                        loss += self.beta * phenotypeSuccession_constraint(
                            Wk_batch, self.twl
                        )
                    loss.backward()
                    return loss

                optimizerW.step(closure)
                if self.non_negativity:
                    nonnegative_projection(*Wk_batch)
                if self.normalization:
                    normalization_constraint(*Wk_batch)

        # make a reconstruction, and select only the next event
        with torch.no_grad():
            pred = [
                self.model.reconstruct(x, self.Ph.data)[:, self.twl] for x in Wk_batch
            ]
        return pred

    def reorderPhenotypes(self, gen_pheno, Wk=None, tw=2):
        """
        This function outputs reordered internal phenotypes and pathways.

        Parameters
        ----------
        gen_pheno: torch.Tensor
            generated phenotypes of size R x N x Tw, where R is the number of phenotypes, N is the number of drugs and Tw is the length of the temporal window
        Wk: torch.Tensor
            pathway to reorder, if None, it uses the internal pathways
        tw: int
            windows size

        Returns
        -------
        A pair (rPh,rW) with reordered phenotypes (aligned at best with gen_pheno) and the corresponding reodering of the pathways
        """
        if Wk is None:
            Wk = self.Wk

        if tw == 1:
            gen_pheno = torch.unsqueeze(gen_pheno, 2)  # transform into a matrix

        if gen_pheno[0].shape != self.Ph[0].shape:
            raise ValueError(
                f"The generated phenotypes ({gen_pheno[0].shape}) and computed phenotypes ({self.Ph[0].shape}) doesn't have the same shape."
            )

        dic = np.zeros(
            (gen_pheno.shape[0], self.Ph.shape[0])
        )  # construct a cost matrix

        for i in range(gen_pheno.shape[0]):
            for j in range(self.Ph.shape[0]):
                dic[i][j] = torch.norm((gen_pheno[i] - self.Ph[j]), p="fro").item()

        m = Munkres()  # Use of Hungarian Algorithm to find phenotypes correspondances
        indexes = m.compute(dic)

        # Reorder phenotypes
        reordered_pheno = self.Ph.clone()
        for row, column in indexes:
            reordered_pheno[row] = self.Ph[column]

        # Reorder pathways
        reordered_pathways = [Wk[i].clone() for i in range(len(Wk))]
        for i in range(len(Wk)):
            for row, column in indexes:
                reordered_pathways[i][row] = Wk[i][column]

        return reordered_pheno, reordered_pathways


class swottedTrainer(pl.Trainer):
    def fit(
        self,
        model: swottedModule,
        train_dataloaders,
        val_dataloaders=None,
        datamodule=None,
        ckpt_path=None,
    ):
        model.Wk = [
            Variable(
                torch.rand(
                    model.rank, ds[0].shape[1] - model.twl + 1
                ),
                requires_grad=True,
            )
            for ds in train_dataloaders.dataset
        ]
        return super().fit(
            model, train_dataloaders, val_dataloaders, datamodule, ckpt_path
        )
