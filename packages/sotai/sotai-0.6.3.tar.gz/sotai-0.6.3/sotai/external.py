"""This module contains functions for external models to interact with the SOTAI API."""
import os
import pickle
import numpy as np
import pandas as pd
from .utils.shap_utils import (
    calculate_beeswarm,
    calculate_scatter,
    calculate_feature_importance,
)
from .api import post_external_inference


def shap(  # pylint: disable=too-many-locals
    inference_data: pd.DataFrame,
    shapley_values: np.ndarray,
    base_values: np.ndarray,
    name: str,
    target: str,
    dataset_name: str,
) -> str:
    """Uploads the shapley values, base values, and inference data to the SOTAI API.

    Args:
        inference_data: The data used for inference.
        shapley_values: The shapley values for the inference data.
        base_values: The base values for the inference data.
        name: The name of the shapley values.
        target: The target column of the inference data.
        dataset_name: The name of the dataset used for inference.

    Returns:
        The UUID of the uploaded shapley values.
    """

    external_directory = "/tmp/sotai/external/"
    if not os.path.exists(external_directory):
        os.makedirs(external_directory)

    beeswarm_data = calculate_beeswarm(inference_data, shapley_values, target)
    scatter_data = calculate_scatter(inference_data, shapley_values)
    feature_importance = calculate_feature_importance(
        shapley_values, inference_data.columns
    )

    beeswarm_filepath = "/tmp/sotai/external/beeswarm_data.pkl"
    scatter_filepath = "/tmp/sotai/external/scatter_data.pkl"
    feature_importance_filepath = "/tmp/sotai/external/feature_importance_data.pkl"

    with open(beeswarm_filepath, "wb") as beeswarm_file:
        pickle.dump(beeswarm_data, beeswarm_file)
    with open(scatter_filepath, "wb") as scatter_file:
        pickle.dump(scatter_data, scatter_file)
    with open(feature_importance_filepath, "wb") as feature_importance_file:
        pickle.dump(feature_importance, feature_importance_file)

    shapley_values_df = pd.DataFrame(shapley_values)
    base_values_df = pd.DataFrame(base_values)

    shapley_value_filepath = "/tmp/sotai/external/shapley_values.csv"
    base_values_filepath = "/tmp/sotai/external/base_values.csv"
    inference_data_filepath = "/tmp/sotai/external/inference_predictions.csv"

    shapley_values_df.to_csv(shapley_value_filepath, index=False)
    base_values_df.to_csv(
        base_values_filepath,
        index=False,
    )
    inference_data.to_csv(inference_data_filepath, index=False)

    shap_uuid = post_external_inference(
        external_shapley_value_name=name,
        shap_filepath=shapley_value_filepath,
        base_filepath=base_values_filepath,
        inference_filepath=inference_data_filepath,
        beeswarm_filepath=beeswarm_filepath,
        scatter_filepath=scatter_filepath,
        feature_importance_filepath=feature_importance_filepath,
        target=target,
        dataset_name=dataset_name,
    )
    return shap_uuid
