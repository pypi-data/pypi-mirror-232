#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Artificial Intelligence & Data Science Studio                                       #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.11                                                                             #
# Filename   : /studioai/stats/inferential/kendallstau.py                                          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/studioai                                           #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday May 29th 2023 03:00:39 am                                                    #
# Modified   : Friday September 29th 2023 05:29:51 pm                                              #
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
    StatTestResult,
    StatAnalysis,
)


# ------------------------------------------------------------------------------------------------ #
#                                 KENDALL'S TAU MEASURE OF CORRELATION                             #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class KendallsTau(StatTestResult):
    data: pd.DataFrame = None
    a: str = None
    b: str = None
    n: int = None
    strength: str = None
    pvalue: float = None
    visualizer: Visualizer = None

    @inject
    def __post_init__(self, visualizer: Visualizer = Provide[StudioAIContainer.visualizer]) -> None:
        self.visualizer = visualizer

    def plot(self) -> None:  # pragma: no cover
        self.visualizer.kendallstau(
            data=self.data,
            a=self.a,
            b=self.b,
            value=self.value,
            thresholds=self.thresholds,
            interpretation=self.interpretation,
        )

    def result(self) -> str:
        return f"Kendall's Tau Test of Association between {self.a.capitalize()} and {self.b.capitalize()} \u03C4={round(self.value,2)},{self._report_pvalue(self.pvalue)}."


# ------------------------------------------------------------------------------------------------ #
#                                   CRAMERS V ANALYSIS                                             #
# ------------------------------------------------------------------------------------------------ #
class KendallsTauAnalysis(StatAnalysis):
    """Kendall's Tau Measures the degree of correlation between two ordinal variables.

    Args:
        data (pd.DataFrame): The DataFrame containing the variables of interest.
        a (str): The name of an ordinal variable in data.
        b (str): The name of an ordinal variable in data.

    """

    __id = "kendallstau"

    @inject
    def __init__(
        self,
        data: pd.DataFrame,
        a: str = None,
        b: str = None,
        variant: str = "c",
        alternative: str = "two-sided",
    ) -> None:
        super().__init__()
        self._data = data
        self._a = a
        self._b = b
        self._variant = variant
        self._alternative = alternative
        self._thresholds = np.array([-1, -0.5, -0.3, 0.0, 0.3, 0.5, 1.0])
        self._labels = [
            "Strong",
            "Moderate",
            "Weak",
            "Weak",
            "Moderate",
            "Strong",
        ]

    @property
    def result(self) -> KendallsTau:
        """Returns the Cramer's V Measure object."""
        return self._result

    def run(self) -> None:
        """Performs the statistical test and creates a result object."""

        a = self._data[self._a].values
        b = self._data[self._b].values

        statistic, pvalue = stats.kendalltau(
            x=a, y=b, variant=self._variant, alternative=self._alternative
        )

        strength = self._labels[np.where(self._thresholds < statistic)[-1][-1]]

        # Create the result object.
        self._result = KendallsTau(
            data=self._data,
            a=self._a,
            b=self._b,
            n=len(a),
            value=statistic,
            strength=strength,
            pvalue=pvalue,
        )
