"""Tests for api."""
from unittest.mock import patch
import pandas as pd
import numpy as np

from sotai.external import shap


@patch("builtins.open")
@patch("pickle.dump", return_value="test")
@patch("pandas.DataFrame.to_csv", return_value="test")
@patch("sotai.external.post_external_inference", return_value="test_uuid")
def test_shap(mock_post_external_inference, mock_to_csv, mock_dump, mock_open_data):
    """Tests that a pipeline is posted correctly."""

    mock_open_data.return_value.__enter__.return_value = "data"
    test_inference_data = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["a", "b", "c"])

    test_shap_values = np.array([[1, 2, 3], [4, 5, 6]])
    test_base_values = np.array([[1, 2, 3], [4, 5, 6]])

    shap(
        test_inference_data,
        test_shap_values,
        test_base_values,
        "test",
        "target",
        "test",
    )

    mock_post_external_inference.assert_called_with(
        external_shapley_value_name="test",
        shap_filepath="/tmp/sotai/external/shapley_values.csv",
        base_filepath="/tmp/sotai/external/base_values.csv",
        inference_filepath="/tmp/sotai/external/inference_predictions.csv",
        beeswarm_filepath="/tmp/sotai/external/beeswarm_data.pkl",
        scatter_filepath="/tmp/sotai/external/scatter_data.pkl",
        feature_importance_filepath="/tmp/sotai/external/feature_importance_data.pkl",
        target="target",
        dataset_name="test",
    )
    mock_to_csv.assert_called()
    mock_dump.assert_called()
    mock_open_data.assert_called()
