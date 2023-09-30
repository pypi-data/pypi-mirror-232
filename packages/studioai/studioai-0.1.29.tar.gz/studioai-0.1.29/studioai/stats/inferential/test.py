#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Artificial Intelligence & Data Science Studio                                       #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.12                                                                             #
# Filename   : /studioai/stats/inferential/test.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/studioai                                           #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 29th 2023 10:45:53 am                                              #
# Modified   : Friday September 29th 2023 11:15:27 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
import pandas as pd
import numpy as np
from typing import Union

from studioai.stats.inferential.chisquare import (
    ChiSquareIndependenceTest,
    ChiSquareIndependenceResult,
)
from studioai.stats.inferential.cramersv import CramersVAnalysis, CramersV
from studioai.stats.inferential.kendallstau import KendallsTauAnalysis, KendallsTau
from studioai.stats.inferential.kstest import KSTest, KSTestResult
from studioai.stats.inferential.pearson import PearsonCorrelationTest, PearsonCorrelationResult
from studioai.stats.inferential.spearman import SpearmanCorrelationTest, SpearmanCorrelationResult
from studioai.stats.inferential.ttest import TTest, TTestResult


# ------------------------------------------------------------------------------------------------ #
class Inference:
    """Bundles hypothesis testing into a single class."""

    def chisquare(
        self, data: pd.DataFrame, a: str = None, b: str = None, alpha: float = 0.05
    ) -> ChiSquareIndependenceResult:
        test = ChiSquareIndependenceTest(data=data, a=a, b=b, alpha=alpha)
        test.run()
        return test.result

    def cramersv(
        self, data: pd.DataFrame, x: str = None, y: str = None, alpha: float = 0.05
    ) -> CramersV:
        test = CramersVAnalysis(data=data, x=x, y=y, alpha=alpha)
        test.run()
        return test.result

    def kendallstau(
        self,
        data: pd.DataFrame,
        a: str = None,
        b: str = None,
        variant: str = "c",
        alternative: str = "two-sided",
    ) -> KendallsTau:
        test = KendallsTauAnalysis(data=data, a=a, b=b, variant=variant, alternative=alternative)
        test.run()
        return test.result

    def kstest(self, a: np.ndarray, b: Union[str, np.ndarray], alpha: float = 0.05) -> KSTestResult:
        test = KSTest(a=a, b=b, alpha=alpha)
        test.run()
        return test.result

    def pearson(
        self,
        data: pd.DataFrame = None,
        a: Union[str, np.ndarray, pd.Series] = None,
        b: Union[str, np.ndarray, pd.Series] = None,
        alpha: float = 0.05,
    ) -> PearsonCorrelationResult:
        test = PearsonCorrelationTest(data=data, a=a, b=b, alpha=alpha)
        test.run()
        return test.result

    def spearman(
        self,
        data: pd.DataFrame = None,
        a: Union[str, np.ndarray, pd.Series] = None,
        b: Union[str, np.ndarray, pd.Series] = None,
        alpha: float = 0.05,
    ) -> SpearmanCorrelationResult:
        test = SpearmanCorrelationTest(data=data, a=a, b=b, alpha=alpha)
        test.run()
        return test.result

    def ttest(
        self,
        a: np.ndarray,
        b: np.ndarray,
        varname: str = None,
        a_name: str = None,
        b_name: str = None,
        alpha: float = 0.05,
        homoscedastic: bool = True,
    ) -> TTestResult:
        test = TTest(
            a=a,
            b=b,
            varname=varname,
            a_name=a_name,
            b_name=b_name,
            alpha=alpha,
            homoscedastic=homoscedastic,
        )
        test.run()
        return test.result
