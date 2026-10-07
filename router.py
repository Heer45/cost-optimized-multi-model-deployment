import numpy as np
from typing import Any, cast
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split


class SmartRouter:
    """
    Automatically determines request complexity and selects
    Model A, Model B, or Model C.

    Routing:
        Simple   -> Model A
        Medium   -> Model B
        Complex  -> Model C
    """

    def __init__(self):

        # ----------------------------------------------------
        # Load dataset used by the project
        # ----------------------------------------------------

        data = cast(Any, load_breast_cancer())

        X = data.data
        y = data.target

        # ----------------------------------------------------
        # Recreate training split
        # ----------------------------------------------------

        X_train, _, _, _ = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        # ----------------------------------------------------
        # Training-data statistics
        # ----------------------------------------------------

        self.feature_means = np.mean(
            X_train,
            axis=0,
        )

        self.feature_stds = np.std(
            X_train,
            axis=0,
        )

        # Prevent division by zero
        self.feature_stds = np.where(
            self.feature_stds == 0,
            1.0,
            self.feature_stds,
        )

        # ----------------------------------------------------
        # Calculate training complexity scores
        # ----------------------------------------------------

        training_scores = self._calculate_scores(
            X_train
        )

        # ----------------------------------------------------
        # Data-driven thresholds
        # ----------------------------------------------------

        self.simple_threshold = float(
            np.quantile(
                training_scores,
                0.33,
            )
        )

        self.complex_threshold = float(
            np.quantile(
                training_scores,
                0.66,
            )
        )

    # ========================================================
    # COMPLEXITY CALCULATION
    # ========================================================

    def _calculate_scores(self, X):
        """
        Calculate complexity scores for one or more samples.
        """

        X = np.asarray(
            X,
            dtype=float,
        )

        # Make sure a single sample becomes 2D
        if X.ndim == 1:
            X = X.reshape(1, -1)

        z_scores = np.abs(
            (
                X - self.feature_means
            )
            / self.feature_stds
        )

        scores = np.mean(
            z_scores,
            axis=1,
        )

        return scores

    # ========================================================
    # SINGLE REQUEST COMPLEXITY
    # ========================================================

    def calculate_complexity(self, input_data):
        """
        Calculate the complexity score for one patient.

        Accepts:
            [30 values]

        or:

            [[30 values]]
        """

        # ----------------------------------------------------
        # Convert everything to NumPy
        # ----------------------------------------------------

        X = np.asarray(
            input_data,
            dtype=float,
        )

        # ----------------------------------------------------
        # Flatten nested input
        # ----------------------------------------------------

        X = X.reshape(-1)

        # ----------------------------------------------------
        # Validate feature count
        # ----------------------------------------------------

        if X.size != 30:

            raise ValueError(
                f"Expected 30 features, "
                f"but received {X.size}."
            )

        # ----------------------------------------------------
        # Calculate standardized deviation
        # ----------------------------------------------------

        z_scores = np.abs(
            (
                X - self.feature_means
            )
            / self.feature_stds
        )

        # ----------------------------------------------------
        # Average deviation = complexity score
        # ----------------------------------------------------

        complexity_score = float(
            np.mean(z_scores)
        )

        return complexity_score

    # ========================================================
    # AUTOMATIC ROUTING
    # ========================================================

    def route(self, input_data):
        """
        Automatically select a model based on
        the patient's input complexity.
        
        Returns a dictionary containing:
        
            complexity
            complexity_score
            selected_model
            reason
        """
        complexity_score = self.calculate_complexity(
            input_data
        )

        if complexity_score < self.simple_threshold:
            complexity = "Simple"
            selected_model = "Model A"
        elif complexity_score < self.complex_threshold:
            complexity = "Medium"
            selected_model = "Model B"
        else:
            complexity = "Complex"
            selected_model = "Model C"

        reason = (
            f"Input complexity score is "
            f"{complexity_score:.2f}. "
            f"The request was automatically classified "
            f"as {complexity}, so {selected_model} "
            f"was selected."
        )

        return {
            "complexity": complexity,
            "complexity_score": complexity_score,
            "selected_model": selected_model,
            "reason": reason,
        }

