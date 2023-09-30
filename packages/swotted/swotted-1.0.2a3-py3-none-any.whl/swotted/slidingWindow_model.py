# -*- coding: utf-8 -*-
"""Sliding Windows reconstruction module

This module implements the SWoTTeD reconstruction of tensors based
on the temporal convolution of the temporal phenotypes with a pathways.

Example
--------
.. code-block:: python

    from model.slidingWindow_model import SlidingWindow
    from model.loss_metrics import Bernoulli
    import torch

    Ph = torch.rand( (5,10,3) ) # generation of 5 phenotypes with 10 features and 3 timestamps
    Wp = torch.rand( (5,12) )   # generation of a pathway describing the occurrences of the 5 phenotypes across time

    sw=SlidingWindow()
    sw.setMetric(Bernoulli())

    Yp=sw.reconstruct(Wp,Ph)

"""
import torch
import torch.nn as nn
from swotted.loss_metrics import *
from functools import reduce


class SlidingWindow(nn.Module):
    def setMetric(self, dist=Loss()):
        """
        Define the loss used to evaluate the tensor reconstruction.

        Parameters
        -----------
        dist: Loss
            one of the loss metric available in the loss_metric module.
        """
        self.metric = dist

    def reconstruct(self, Wp, Ph):
        """
        Implementation of the SWoTTeD reconstruction scheme (convolutional reconstruction).

        Notes
        -----
        The function does not ensure that the output values belongs to [0,1]


        Parameters
        ----------
        Ph: torch.Tensor
            Phenotypes of size :math:`R * N * \omega`, where :math:`R` is the
            number of phenotypes and :math:`\omega` the length of the temporal window
        Wp: torch.Tensor
            Assignement tensor of size :math:`R * (Tp-\omega+1)` for patient :math:`p`

        Returns
        -------
        torch.Tensor
            the **SWoTTeD** reconstruction of a pathway from :math:`Wp` and :math:`Ph`.
        """
        # create a tensor of windows
        Yp=torch.conv1d(Wp.squeeze(dim=0), Ph.transpose(0,1).flip(2), padding=Ph.shape[2] - 1)
        return Yp

    def loss(self, Xp, Wp, Ph, padding=None):
        """Evaluation of the SWoTTeD reconstruction loss (see reconstruct method).

        Parameters
        -----------
        Xp: torch.Tensor
            A 2nd-order tensor of size :math:`N * Tp`, where :math:`N` is the number
            of drugs and :math:`Tp` is the time of the patient's stay
        Ph: torch.Tensor
            Phenotypes of size :math:`R * N * \omega`, where :math:`R` is the
            number of phenotypes and :math:`\omega` the length of the temporal window
        Wp: torch.Tensor
            Assignement tensor of size :math:`R * Tp` for patient :math:`p`
        padding: None, bool or tuple
            If `padding` is True then the loss is evaluated on the interval :math:`[\omega, L-\omega]` of the pathway.
            If `padding` is a tuple `(a,b)`, then the loss is evaluated on the interval :math:`[a, L-b]`.
            Default is None (no padding)

        Returns
        -------
        float
            the SWoTTeD reconstruction loss of one patient.
        """
        Yp = self.reconstruct(Wp, Ph)
        Twindow = Ph.shape[2]

        if padding is not None:
            if isinstance(padding, bool) and padding:
                Yp = torch.split(
                    Yp,
                    [Twindow - 1, Yp.shape[1] - 2 * (Twindow - 1), Twindow - 1],
                    dim=1,
                )[1]
                Xp = torch.split(
                    Xp,
                    [Twindow - 1, Xp.shape[1] - 2 * (Twindow - 1), Twindow - 1],
                    dim=1,
                )[1]
            elif isinstance(padding, tuple) and len(padding) == 2:
                Yp = torch.split(
                    Yp,
                    [padding[0], Yp.shape[1] - padding[0] - padding[1], padding[1]],
                    dim=1,
                )[1]
                Xp = torch.split(
                    Xp,
                    [padding[0], Xp.shape[1] - padding[0] - padding[1], padding[1]],
                    dim=1,
                )[1]

        # evaluate the loss
        return self.metric.compute(Xp, Yp)

    def forward(self, X, W, Ph, padding=None):
        """Evaluation of the SWoTTeD reconstruction loss for a collection of patients (see reconstruct method).

        Parameters
        ----------
        Xp: list[torch.Tensor]
            A 3nd-order tensor of size :math:`K* N * Tp`, where :math:`K` is the number
            of patients, :math:`N` is the number of drugs and :math:`Tp` is the time of the patient's stay
        Ph: torch.Tensor
            Phenotypes of size :math:`R * N * \omega`, where :math:`R` is the
            number of phenotypes and :math:`\omega` the length of the temporal window
        Wp: list[torch.Tensor]
            Assignement tensor of size :math:`K* R * Tp` for patient :math:`p`
        padding: None, bool or tuple
            If `padding` is True then the loss is evaluated on the interval :math:`[\omega, L-\omega]` of the pathway.
            If `padding` is a tuple `(a,b)`, then the loss is evaluated on the interval :math:`[a, L-b]`.
            Default is `None` (no padding)

        Returns
        -------
        float
            The SWoTTeD reconstruction loss of a collection of patients, that is the sum of
            the losses for all patients.
        """
        return reduce(
            torch.add, [self.loss(Xp, Wp, Ph, padding) for Xp, Wp in zip(X, W)]
        )
