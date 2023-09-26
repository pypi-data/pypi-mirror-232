from typing import Sequence, TYPE_CHECKING

import pandas as pd

from truera.client.column_info import validate_column_input
from truera.client.util import workspace_validation_utils
# pylint: disable=no-name-in-module,no-member
from truera.protobuf.public import metadata_message_types_pb2 as md_pb

# pylint: enable=no-name-in-module
if TYPE_CHECKING:
    from truera.client.ingestion import ModelOutputContext
    from truera.client.ingestion import ColumnSpec

from truera.client.ingestion.constants import PROD_DATA_SPLIT_TYPE
from truera.client.ingestion.constants import SPECIAL_COLUMN_NAMES


def validate_column_spec_and_model_output_context(
    column_spec: 'ColumnSpec',
    model_output_context: 'ModelOutputContext',
    *,
    split_name: str,
    existing_models: Sequence[str],
    existing_splits: Sequence[str],
    project_influence_type: str,
    target_split_metadata=md_pb.DataSplitMetadata
):

    # Validate columns
    if not column_spec.id_col_name:
        raise ValueError("`id_col_name` is required in `column_spec`.")
    for column_type, column_names in column_spec.to_dict().items():
        if column_names:
            for column_name in validate_column_input(column_names):
                if column_name in SPECIAL_COLUMN_NAMES:
                    raise ValueError(
                        f"Column name '{column_name}' from `{column_type}` can not be used as it is reserved for use by TruEra services."
                    )

    # Validate target split
    is_appending = split_name in existing_splits and (
        column_spec.pre_data_col_names or column_spec.post_data_col_names
    )
    if is_appending:
        if target_split_metadata.split_type != PROD_DATA_SPLIT_TYPE:
            raise ValueError(
                f"Data split '{split_name}' already exists. Appending data is supported only for production monitoring data splits created by add_production_data_split."
            )
        if not column_spec.timestamp_col_name:
            raise ValueError(
                "Production monitoring data requires `timestamp_col_name` in `column_spec`."
            )

    # Validate model_output_context
    if column_spec.prediction_col_names or column_spec.feature_influence_col_names:
        if not model_output_context:
            raise ValueError(
                "`model_output_context` is required when ingesting predictions or feature influences."
            )

        # Validate model
        if not model_output_context.model_name:
            raise ValueError(
                "`model_name` is required in model output context when ingesting predictions or feature influences."
            )
        if model_output_context.model_name not in existing_models:
            raise ValueError(
                f"Model '{model_output_context.model_name}' does not exist among available models: {existing_models}"
            )

        # Validate score_type
        if not model_output_context.score_type:
            raise ValueError(
                f"`score_type` is required in model output context when ingesting predictions or feature influences."
            )

        if column_spec.feature_influence_col_names:
            if not workspace_validation_utils.is_gradient_influence_type(
                model_output_context.influence_type
            ):
                # Validate background_split_name
                if not model_output_context.background_split_name:
                    raise ValueError(
                        "`background_split_name` is required in model output context when ingesting feature influences."
                    )
                if model_output_context.background_split_name not in existing_splits:
                    raise ValueError(
                        f"Data split '{model_output_context.background_split_name}' does not exist among available splits: {existing_splits}"
                    )

            # Validate influence_type
            if not model_output_context.influence_type:
                raise ValueError(
                    "`influence_type` is required in model output context when ingesting feature influences."
                )
            workspace_validation_utils.validate_influence_type_str_for_virtual_model_upload(
                model_output_context.influence_type, project_influence_type
            )


def validate_dataframe(
    data: pd.DataFrame, column_spec: 'ColumnSpec', input_type: str
):
    # Validate data against columns
    for column_type, column_names in column_spec.to_dict().items():
        if column_names:
            for column_name in validate_column_input(column_names):
                if column_name not in data:
                    raise ValueError(
                        f"Column name '{column_name}' was provided though `{column_type}`, but not found in data."
                    )

    # Validate id column is string
    try:
        data[column_spec.id_col_name].astype("string")
    except Exception as exc:
        raise ValueError(
            f"`id_col_name` '{column_spec.id_col_name}' column must be convertible into string type. Could not convert column to string; error: {exc}"
        )

    # Validate timestamp is datetime
    if column_spec.timestamp_col_name:
        try:
            pd.to_datetime(data[column_spec.timestamp_col_name])
        except Exception as exc:
            raise ValueError(
                f"`timestamp_col_name` column '{column_spec.timestamp_col_name}' must have valid datetime format. Could not convert column to datetime; "
                f"error: {exc}"
            )

    # Validate feature influence columns for non-NLP ColumnSpec
    if column_spec.feature_influence_col_names:
        for col_name in column_spec.feature_influence_col_names:
            if input_type == "tabular":
                if not pd.api.types.is_float_dtype(data[col_name].dtype):
                    raise ValueError(
                        f"`feature_influence_data` column '{col_name}' must have float dtype, but was '{data[col_name].dtype}'"
                    )
            elif input_type == "text":
                if data[col_name].apply(
                    lambda x: not (
                        pd.api.types.is_array_like(x) or
                        isinstance(x, Sequence)
                    )
                ).any():
                    raise ValueError(
                        f"`feature_influence_data` column '{col_name}' must contain only array-like elements"
                    )
            else:
                raise ValueError(f"Invalid `input_type` specified {input_type}")


def get_all_col_names_in_column_spec(
    column_spec: 'ColumnSpec'
) -> Sequence[str]:
    all_col_names = []
    for _, col_names in column_spec.to_dict().items():
        if col_names:
            all_col_names.extend(
                [col_names] if isinstance(col_names, str) else col_names
            )
    return all_col_names
