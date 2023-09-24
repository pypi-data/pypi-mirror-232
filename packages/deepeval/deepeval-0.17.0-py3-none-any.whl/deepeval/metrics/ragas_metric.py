"""An implementation of the Ragas metric
"""
import os
import numpy as np
from deepeval.metrics.metric import Metric
from deepeval.test_case import LLMTestCase
from typing import List


class ContextualRelevancyRagasMetric(Metric):
    """This metric checks the contextual relevancy using Ragas"""

    def __init__(
        self,
        minimum_score: float = 0.3,
    ):
        self.minimum_score = minimum_score
        try:
            # Adding a list of metrics
            from ragas.metrics import context_relevancy

            self.metrics = [context_relevancy]

        except ModuleNotFoundError as e:
            print(
                "Please install ragas to use this metric. `pip install ragas`."
            )

    def measure(self, test_case: LLMTestCase):
        # sends to server
        try:
            from ragas import evaluate
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Please install ragas to use this metric. `pip install ragas`."
            )

        try:
            from datasets import Dataset
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Please install dataset")

        # Create a dataset from the test case
        data = {
            "ground_truths": [[test_case.expected_output]],
            "contexts": [[test_case.context]],
            "question": [test_case.query],
            "answer": [test_case.output],
            "id": [[test_case.id]],
        }
        dataset = Dataset.from_dict(data)

        # Evaluate the dataset using Ragas
        scores = evaluate(dataset, metrics=self.metrics)

        # Ragas only does dataset-level comparisons
        context_relevancy_score = scores["context_relevancy"]
        self.success = context_relevancy_score >= self.minimum_score
        self.score = context_relevancy_score
        return context_relevancy_score

    def is_successful(self):
        return self.success

    @property
    def __name__(self):
        return "Contextual Relevancy Ragas Score"


class AnswerRelevancyRagasMetric(Metric):
    """This metric checks the answer relevancy using Ragas"""

    def __init__(
        self,
        minimum_score: float = 0.3,
    ):
        self.minimum_score = minimum_score
        try:
            from ragas.metrics import answer_relevancy

            self.metrics = [answer_relevancy]
        except ModuleNotFoundError as e:
            print(
                "Please install ragas to use this metric. `pip install ragas`."
            )

    def measure(self, test_case: LLMTestCase):
        # sends to server
        try:
            from ragas import evaluate
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Please install ragas to use this metric. `pip install ragas`."
            )

        try:
            from datasets import Dataset
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Please install dataset")

        data = {
            "ground_truths": [[test_case.expected_output]],
            "contexts": [[test_case.context]],
            "question": [test_case.query],
            "answer": [test_case.output],
            "id": [[test_case.id]],
        }
        dataset = Dataset.from_dict(data)
        scores = evaluate(dataset, metrics=self.metrics)
        answer_relevancy_score = scores["answer_relevancy"]
        self.success = answer_relevancy_score >= self.minimum_score
        self.score = answer_relevancy_score
        return answer_relevancy_score

    def is_successful(self):
        return self.success

    @property
    def __name__(self):
        return "Answer Relevancy Ragas Score"


class FaithfulnessRagasMetric(Metric):
    def __init__(
        self,
        minimum_score: float = 0.3,
    ):
        self.minimum_score = minimum_score
        try:
            from ragas.metrics import faithfulness

            self.metrics = [faithfulness]
        except ModuleNotFoundError as e:
            print(
                "Please install ragas to use this metric. `pip install ragas`."
            )

    def measure(self, test_case: LLMTestCase):
        # sends to server
        try:
            from ragas import evaluate
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Please install ragas to use this metric. `pip install ragas`."
            )

        try:
            from datasets import Dataset
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Please install dataset")

        data = {
            "ground_truths": [[test_case.expected_output]],
            "contexts": [[test_case.context]],
            "question": [test_case.query],
            "answer": [test_case.output],
            "id": [[test_case.id]],
        }
        dataset = Dataset.from_dict(data)
        scores = evaluate(dataset, metrics=self.metrics)
        faithfulness_score = scores["faithfulness"]
        self.success = faithfulness_score >= self.minimum_score
        self.score = faithfulness_score
        return faithfulness_score

    def is_successful(self):
        return self.success

    @property
    def __name__(self):
        return "Faithfulness Ragas Score"


class ContextRecallRagasMetric(Metric):
    """This metric checks the context recall using Ragas"""

    def __init__(
        self,
        minimum_score: float = 0.3,
    ):
        self.minimum_score = minimum_score
        try:
            from ragas.metrics import context_recall

            self.metrics = [context_recall]
        except ModuleNotFoundError as e:
            print(
                "Please install ragas to use this metric. `pip install ragas`."
            )

    def measure(self, test_case: LLMTestCase):
        # sends to server
        try:
            from ragas import evaluate
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Please install ragas to use this metric. `pip install ragas`."
            )

        try:
            from datasets import Dataset
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Please install dataset")

        data = {
            "ground_truths": [[test_case.expected_output]],
            "contexts": [[test_case.context]],
            "question": [test_case.query],
            "answer": [test_case.output],
            "id": [[test_case.id]],
        }
        dataset = Dataset.from_dict(data)
        scores = evaluate(dataset, metrics=self.metrics)
        context_recall_score = scores["context_recall"]
        self.success = context_recall_score >= self.minimum_score
        self.score = context_recall_score
        return context_recall_score

    def is_successful(self):
        return self.success

    @property
    def __name__(self):
        return "Context Recall Ragas Score"


class HarmfulnessRagasMetric(Metric):
    """This metric checks the harmfulness using Ragas"""

    def __init__(
        self,
        minimum_score: float = 0.3,
    ):
        self.minimum_score = minimum_score
        try:
            from ragas.metrics.critique import harmfulness

            self.metrics = [harmfulness]
        except ModuleNotFoundError as e:
            print(
                "Please install ragas to use this metric. `pip install ragas`."
            )

    def measure(self, test_case: LLMTestCase):
        # sends to server
        try:
            from ragas import evaluate
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Please install ragas to use this metric. `pip install ragas`."
            )

        try:
            from datasets import Dataset
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Please install dataset")

        data = {
            "ground_truths": [[test_case.expected_output]],
            "contexts": [[test_case.context]],
            "question": [test_case.query],
            "answer": [test_case.output],
            "id": [[test_case.id]],
        }
        dataset = Dataset.from_dict(data)
        scores = evaluate(dataset, metrics=self.metrics)
        harmfulness_score = scores["harmfulness"]
        self.success = harmfulness_score >= self.minimum_score
        self.score = harmfulness_score
        return harmfulness_score

    def is_successful(self):
        return self.success

    @property
    def __name__(self):
        return "Harmfulness Ragas Score"


class RagasMetric(Metric):
    """This metric checks if the output is more than 3 letters"""

    def __init__(
        self,
        metrics: List[Metric] = None,
        minimum_score: float = 0.3,
    ):
        self.minimum_score = minimum_score
        if metrics is None:
            self.metrics = [
                HarmfulnessRagasMetric,
                ContextRecallRagasMetric,
                FaithfulnessRagasMetric,
                AnswerRelevancyRagasMetric,
                ContextualRelevancyRagasMetric,
            ]
        else:
            self.metrics = metrics

    def measure(self, test_case: LLMTestCase):
        # sends to server
        try:
            from ragas import evaluate
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Please install ragas to use this metric. `pip install ragas`."
            )

        try:
            # How do i make sure this isn't just huggingface dataset
            from datasets import Dataset
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Please install dataset")

        # Create a dataset from the test case
        # Convert the LLMTestCase to a format compatible with Dataset
        scores = []
        for metric in self.metrics:
            m = metric()
            score = m.measure(test_case)
            scores.append(score)

        # ragas score is harmonic mean of all the scores
        if len(scores) > 0:
            ragas_score = len(scores) / sum(
                1.0 / score for score in scores if score != 0
            )
        else:
            ragas_score = 0

        # Ragas only does dataset-level comparisons
        # >>> print(result["ragas_score"])
        # {'ragas_score': 0.860, 'context_relevancy': 0.817, 'faithfulness': 0.892,
        # 'answer_relevancy': 0.874}
        self.success = ragas_score >= self.minimum_score
        self.score = ragas_score
        return ragas_score

    def is_successful(self):
        return self.success

    @property
    def __name__(self):
        return "Ragas Score"


def assert_ragas(
    test_case: LLMTestCase,
    metrics: List[str] = None,
    minimum_score: float = 0.3,
):
    """Asserts if the Ragas score is above the minimum score"""
    metric = RagasMetric(metrics, minimum_score)
    score = metric.measure(test_case)
    assert (
        score >= metric.minimum_score
    ), f"Ragas score {score} is below the minimum score {metric.minimum_score}"
