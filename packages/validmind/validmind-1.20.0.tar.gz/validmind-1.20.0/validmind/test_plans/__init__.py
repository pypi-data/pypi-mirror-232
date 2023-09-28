# Copyright © 2023 ValidMind Inc. All rights reserved.

"""
Test Plans entry point
"""
import pandas as pd

from ..logging import get_logger
from ..tests import list_tests as real_list_tests
from ..tests import load_test
from ..utils import format_dataframe
from .classifier import ClassifierDiagnosis, ClassifierMetrics, ClassifierPerformance
from .llm import PromptValidation
from .statsmodels_timeseries import (
    RegressionModelDescription,
    RegressionModelsEvaluation,
)
from .summarization import SummarizationMetrics
from .tabular_datasets import (
    TabularDataQuality,
    TabularDatasetDescription,
    TimeSeriesDataQuality,
)
from .text_data import TextDataQuality
from .time_series import (
    TimeSeriesForecast,
    TimeSeriesMultivariate,
    TimeSeriesSensitivity,
    TimeSeriesUnivariate,
)

logger = get_logger(__name__)

core_test_plans = {
    "classifier_metrics": ClassifierMetrics,
    "classifier_validation": ClassifierPerformance,
    "classifier_model_diagnosis": ClassifierDiagnosis,
    "prompt_validation": PromptValidation,
    "tabular_dataset_description": TabularDatasetDescription,
    "tabular_data_quality": TabularDataQuality,
    "time_series_data_quality": TimeSeriesDataQuality,
    "time_series_univariate": TimeSeriesUnivariate,
    "time_series_multivariate": TimeSeriesMultivariate,
    "time_series_forecast": TimeSeriesForecast,
    "time_series_sensitivity": TimeSeriesSensitivity,
    "regression_model_description": RegressionModelDescription,
    "regression_models_evaluation": RegressionModelsEvaluation,
    "text_data_quality": TextDataQuality,
    "summarization_metrics": SummarizationMetrics,
}

# These test plans can be added by the user
custom_test_plans = {}

# TODO: remove this... here for backwards compatibility
list_tests = real_list_tests


def _get_all_test_plans():
    """
    Returns a dictionary of all test plans.

    Merge the core and custom test plans, with the custom plans
    taking precedence, i.e. allowing overriding of core test plans
    """
    return {**core_test_plans, **custom_test_plans}


def list_plans(pretty: bool = True):
    """
    Returns a list of all available test plans
    """

    all_test_plans = _get_all_test_plans()

    if not pretty:
        return list(all_test_plans.keys())

    table = []
    for name, test_plan in all_test_plans.items():
        table.append(
            {
                "ID": name,
                "Name": test_plan.__name__,
                "Description": test_plan.__doc__.strip(),
            }
        )

    return format_dataframe(pd.DataFrame(table))


def get_by_id(test_plan_id: str):
    """
    Returns the test plan by ID
    """
    try:
        return _get_all_test_plans()[test_plan_id]
    except KeyError:
        raise ValueError(f"Test plan with name: '{test_plan_id}' not found")


def describe_plan(plan_id: str, style=True):
    """
    Returns a description of the test plan
    """
    plan = get_by_id(plan_id)

    tests = []
    for test_id in plan.tests:
        test = load_test(test_id)
        tests.append(f"{test.__name__} ({test.test_type})")

    df = pd.DataFrame(
        [
            {
                "ID": plan.name,
                "Name": plan.__name__,
                "Description": plan.__doc__.strip(),
                "Tests": "<br>".join(tests),
            }
        ]
    )

    return format_dataframe(df) if style else df


def register_test_plan(plan_id: str, plan):
    """
    Registers a custom test plan
    """
    # TODO: for this and other registration functions, we should
    # use Protocols instead of making the user inherit from a base class
    custom_test_plans[plan_id] = plan
    logger.info(f"Registered test plan: {plan_id}")
