# Copyright © 2023 ValidMind Inc. All rights reserved.

"""
Metrics functions for any Pandas-compatible datasets
"""

import string
from collections import defaultdict
from dataclasses import dataclass

import matplotlib.pyplot as plt

from validmind.vm_models import Figure, Metric, VMDataset


@dataclass
class Punctuations(Metric):
    """
    Metric that analyses the frequencies of punctuations in a given text dataset
    """

    name = "punctuations"
    required_inputs = ["dataset", "dataset.text_column"]
    metadata = {
        "task_types": ["text_classification", "text_summarization"],
        "tags": ["nlp", "text_data", "visualization", "frequency_analysis"],
    }

    def run(self):
        # Can only run this test if we have a Dataset object
        if not isinstance(self.dataset, VMDataset):
            raise ValueError("Punctuations requires a validmind Dataset object")

        def create_corpus(df, text_column):
            corpus = []
            for x in df[text_column].str.split():
                for i in x:
                    corpus.append(i)
            return corpus

        text_column = self.dataset.text_column
        corpus = create_corpus(self.dataset.df, text_column=text_column)

        dic = defaultdict(int)
        special = string.punctuation
        for i in corpus:
            if i in special:
                dic[i] += 1

        fig = plt.figure()
        x, y = zip(*dic.items())
        plt.bar(x, y, color="#17C37B")

        # Do this if you want to prevent the figure from being displayed
        plt.close("all")

        return self.cache_results(
            figures=[
                Figure(
                    for_object=self,
                    key=self.key,
                    figure=fig,
                )
            ]
        )
