# Copyright © 2023 ValidMind Inc. All rights reserved.

from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
from scipy import stats

from validmind.vm_models import Figure, Metric


@dataclass
class RegressionCoeffsPlot(Metric):
    """
    Regression Coefficients with Confidence Intervals Plot

    This class is used to generate a visualization of the coefficients from a regression model, as well as their corresponding
    confidence intervals. It serves as a useful diagnostic tool for statistical analysis and model interpretation. The visualization
    displays each of the predictor variables on the x-axis, with their associated regression coefficients on the y-axis. Error bars
    are used to indicate the range of the confidence intervals, providing an understanding of the variability and uncertainty
    associated with the model's estimates.
    """

    name = "regression_coeffs_plot"
    required_inputs = ["models"]
    metadata = {
        "task_types": ["regression"],
        "tags": ["tabular_data", "visualization", "model_interpretation"],
    }

    @staticmethod
    def plot_coefficients_with_ci(model, model_name):
        # Extract estimated coefficients and standard errors
        coefficients = model.regression_coefficients()
        coef = pd.to_numeric(coefficients["coef"])
        std_err = pd.to_numeric(coefficients["std err"])

        # Calculate confidence intervals
        confidence_level = 0.95  # 95% confidence interval
        z_value = stats.norm.ppf((1 + confidence_level) / 2)  # Calculate Z-value
        lower_ci = coef - z_value * std_err
        upper_ci = coef + z_value * std_err

        # Create a bar plot with confidence intervals
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=list(coefficients["Feature"].values),
                y=coef,
                name="Estimated Coefficients",
                error_y=dict(
                    type="data",
                    symmetric=False,
                    arrayminus=lower_ci,
                    array=upper_ci,
                    visible=True,
                ),
            )
        )

        fig.update_layout(
            title=f"{model_name} Coefficients with Confidence Intervals",
            xaxis_title="Predictor Variables",
            yaxis_title="Coefficients",
        )

        return fig, {
            "values": list(coef),
            "lower_ci": list(lower_ci),
            "upper_ci": list(upper_ci),
        }

    def run(self):
        # Check models list is not empty
        if not self.models:
            raise ValueError("List of models must be provided in the models parameter")

        all_models = []
        all_figures = []
        all_metric_values = []

        if self.models is not None:
            all_models.extend(self.models)

        for i, model in enumerate(all_models):
            model_name = f"Model {i+1}"

            fig, metric_values = self.plot_coefficients_with_ci(model, model_name)
            all_figures.append(
                Figure(
                    for_object=self,
                    key=f"{model_name}_coefficients_ci_plot",
                    figure=fig,
                )
            )
            all_metric_values.append({"name": model_name, "metrics": metric_values})

        return self.cache_results(
            metric_value=all_metric_values,
            figures=all_figures,
        )
