#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Artificial Intelligence & Data Science Studio                                       #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.11                                                                             #
# Filename   : /studioai/stats/inferential/cramersv.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/studioai                                           #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday May 29th 2023 03:00:39 am                                                    #
# Modified   : Monday September 18th 2023 05:21:37 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass

import pandas as pd
import numpy as np
from scipy import stats
from dependency_injector.wiring import inject, Provide

from studioai.container import StudioAIContainer
from studioai.visual.visualizer import Visualizer
from studioai.stats.inferential.base import (
    StatMeasure,
    StatAnalysis,
)


# ------------------------------------------------------------------------------------------------ #
#                                 CRAMERS V MEASURE OF ASSOCIATION                                 #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class CramersV(StatMeasure):
    name: str = "Cramer's V"
    data: pd.DataFrame = None
    dof: int = None
    thresholds: np.array = None
    interpretation: str = None
    x2alpha: float = None
    x2: float = None
    x2dof: float = None
    pvalue: float = None
    expected_freq: np.array = None
    x2result: str = None
    visualizer: Visualizer = None

    @inject
    def __post_init__(self, visualizer: Visualizer = Provide[StudioAIContainer.visualizer]) -> None:
        self.visualizer = visualizer

    def plot(self) -> None:  # pragma: no cover
        self.visualizer.cramersv(
            data=self.data,
            value=self.value,
            thresholds=self.thresholds,
            interpretation=self.interpretation,
        )

    def plot_x2(self) -> None:  # pragma: no cover
        self.visualizer.x2testplot(
            statistic=self.x2,
            dof=self.x2dof,
            result=self.x2result,
            alpha=self.x2alpha,
        )


# ------------------------------------------------------------------------------------------------ #
#                                   CRAMERS V ANALYSIS                                             #
# ------------------------------------------------------------------------------------------------ #
class CramersVAnalysis(StatAnalysis):
    """Cramer's V Analysis of the Association between two Nominal Variables.

    The CramersVAnalysis class provides the association between two nominal variables.

    Args:
        data (pd.DataFrame): The DataFrame containing the variables of interest.
        x (str): The name of the independent variable in data.
        y (str): The name of the dependent variable in data.
        alpha (float): The level of significance for the independence hypothesis test. Default = 0.05
    """

    __id = "cramersv"

    @inject
    def __init__(
        self, data: pd.DataFrame, x: str = None, y: str = None, alpha: float = 0.05
    ) -> None:
        super().__init__()
        self._data = data
        self._x = x
        self._y = y
        self._alpha = alpha
        self._thresholds = {
            1: [0.0, 0.1, 0.3, 0.5, 1.0],
            2: [0.0, 0.07, 0.21, 0.35, 1.0],
            3: [0.0, 0.06, 0.17, 0.29, 1.0],
            4: [0.0, 0.05, 0.15, 0.25, 1.0],
            5: [0.0, 0.05, 0.13, 0.22, 1.0],
            6: [0.0, 0.05, 0.13, 0.22, 1.0],
            7: [0.0, 0.05, 0.13, 0.22, 1.0],
            8: [0.0, 0.05, 0.13, 0.22, 1.0],
            9: [0.0, 0.05, 0.13, 0.22, 1.0],
            10: [0.0, 0.05, 0.13, 0.22, 1.0],
        }
        self._labels = ["Negligible", "Small", "Moderate", "Large"]

    @property
    def measure(self) -> CramersV:
        """Returns the Cramer's V Measure object."""
        return self._measure

    def run(self) -> None:
        """Performs the statistical test and creates a result object."""

        n = len(self._data)

        crosstab = pd.crosstab(self._data[self._x], self._data[self._y])

        dof = min(crosstab.shape[0], crosstab.shape[1]) - 1

        cv = stats.contingency.association(crosstab.values, method="cramer")

        statistic, pvalue, x2dof, exp = stats.chi2_contingency(crosstab.values)

        thresholds = np.array(self._thresholds[dof])

        interpretation = self._labels[np.where(thresholds < cv)[-1][-1]]

        # Create the result object.
        self._measure = CramersV(
            data=crosstab,
            dof=dof,
            value=cv,
            interpretation=interpretation,
            thresholds=thresholds,
            x2alpha=self._alpha,
            x2=statistic,
            x2dof=x2dof,
            pvalue=pvalue,
            expected_freq=exp,
            x2result=self._report_results(statistic=statistic, pvalue=pvalue, dof=x2dof, n=n),
        )

    def _report_results(self, statistic: float, pvalue: float, dof: float, n: int) -> str:
        return f"X\u00b2 Test of Independence\n{self._x.capitalize()} and {self._y.capitalize()}\nX\u00b2({dof}, N={n})={round(statistic,2)}, {self._report_pvalue(pvalue)}."
