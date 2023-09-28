# Copyright © 2023 ValidMind Inc. All rights reserved.

from dataclasses import dataclass

import plotly.graph_objects as go
from sklearn.inspection import permutation_importance

from validmind.errors import SkipTestError
from validmind.logging import get_logger
from validmind.vm_models import Figure, Metric

logger = get_logger(__name__)


@dataclass
class PermutationFeatureImportance(Metric):
    """
    The Feature Importance plot below calculates a score representing the
    importance of each feature in the model. A higher score indicates
    that the specific input feature will have a larger effect on the
    predictive power of the model.

    The importance score is calculated using Permutation Feature
    Importance. Permutation feature importance measures the decrease of
    model performance after the feature's values have been permuted, which
    breaks the relationship between the feature and the true outcome. A
    feature is "important" if shuffling its values increases the model
    error, because in this case the model relied on the feature for the
    prediction. A feature is "unimportant" if shuffling its values leaves
    the model error unchanged, because in this case the model ignored the
    feature for the prediction.
    """

    name = "pfi"
    required_inputs = ["model", "model.train_ds", "model.test_ds"]
    default_params = {
        "fontsize": None,
        "figure_height": 1000,
    }
    metadata = {
        "task_types": ["classification", "text_classification"],
        "tags": [
            "sklearn",
            "binary_classification",
            "multiclass_classification",
            "feature_importance",
            "visualization",
        ],
    }

    def run(self):
        x = self.model.train_ds.x_df()
        y = self.model.train_ds.y_df()

        model_library = self.model.model_library()
        if (
            model_library == "statsmodels"
            or model_library == "pytorch"
            or model_library == "catboost"
            or model_library == "transformers"
            or model_library == "R"
        ):
            raise SkipTestError(f"Skipping PFI for {model_library} models")

        pfi_values = permutation_importance(
            self.model.model,
            x,
            y,
            random_state=0,
            n_jobs=-2,
        )

        pfi = {}
        for i, column in enumerate(x.columns):
            pfi[column] = [pfi_values["importances_mean"][i]], [
                pfi_values["importances_std"][i]
            ]

        sorted_idx = pfi_values.importances_mean.argsort()

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=x.columns[sorted_idx],
                x=pfi_values.importances[sorted_idx].mean(axis=1).T,
                orientation="h",
            )
        )
        fig.update_layout(
            title_text="Permutation Importances (train set)",
            yaxis=dict(
                tickmode="linear",  # set tick mode to linear
                dtick=1,  # set interval between ticks
                tickfont=dict(
                    size=self.params["fontsize"]
                ),  # set the tick label font size
            ),
            height=self.params["figure_height"],  # use figure_height parameter here
        )

        return self.cache_results(
            metric_value=pfi,
            figures=[
                Figure(
                    for_object=self,
                    key="pfi",
                    figure=fig,
                ),
            ],
        )
