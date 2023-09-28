# Copyright © 2023 ValidMind Inc. All rights reserved.

from dataclasses import dataclass

from statsmodels.tsa.stattools import adfuller

from validmind.vm_models import TestResult, ThresholdTest


@dataclass
class ADFTest(ThresholdTest):
    """
    Augmented Dickey-Fuller Metric for establishing the order of integration of
    time series
    """

    category = "model_performance"  # right now we support "model_performance" and "data_quality"
    name = "adf_test"
    default_params = {"threshold": 0.05}
    metadata = {
        "task_types": ["regression"],
        "tags": [
            "time_series_data",
            "statsmodels",
            "forecasting",
            "statistical_test",
            "stationarity",
        ],
    }

    def run(self):
        x_train = self.train_ds.raw_dataset

        results = []
        for col in x_train.columns:
            # adf_values[col] = adfuller(x_train[col].values)
            adf, pvalue, usedlag, nobs, critical_values, icbest = adfuller(
                x_train[col].values
            )

            col_passed = pvalue < self.params["threshold"]
            results.append(
                TestResult(
                    column=col,
                    passed=col_passed,
                    values={
                        "adf": adf,
                        "pvalue": pvalue,
                        "usedlag": usedlag,
                        "nobs": nobs,
                        "icbest": icbest,
                    },
                )
            )

        return self.cache_results(results, passed=all([r.passed for r in results]))
