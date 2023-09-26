from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence, TYPE_CHECKING, Union
import uuid

import pandas as pd

from truera.client.column_info import ColumnInfo
from truera.client.column_info import CreateCacheInfo
from truera.client.ingestion.constants import DEFAULT_APPROX_MAX_ROWS
from truera.client.ingestion.constants import DEFAULT_SAMPLE_STRATEGY
from truera.client.ingestion.constants import DEFAULT_SPLIT_MODE
from truera.client.ingestion.constants import DEFAULT_SPLIT_TYPE
from truera.client.ingestion.constants import PROD_DATA_SPLIT_TYPE
from truera.client.ingestion.ingestion_validation_util import \
    validate_column_spec_and_model_output_context
from truera.client.ingestion.ingestion_validation_util import \
    validate_dataframe
from truera.client.ingestion.temporary_file import TemporaryFile
from truera.client.ingestion_client import Table
from truera.client.services.artifactrepo_client import ArtifactType
from truera.client.util.workspace_validation_utils import \
    is_gradient_influence_type
# pylint: disable=no-name-in-module,no-member
from truera.protobuf.public.common.data_kind_pb2 import DATA_KIND_ALL
from truera.protobuf.public.data_service import \
    data_service_messages_pb2 as ds_messages_pb
from truera.protobuf.public.data_service import data_service_pb2 as ds_pb

# pylint: enable=no-name-in-module

if TYPE_CHECKING:
    from truera.client.remote_truera_workspace import RemoteTrueraWorkspace


@dataclass(eq=True, frozen=True)
class ColumnSpec:
    '''Parameter data class mapping column names to data kinds

    Args:
        id_col_name: Name of the id column
        timestamp_col_name: Name of the timestamp column
        pre_data_col_names: Name(s) of pre-transform data column(s)
        post_data_col_names: Name(s) of post-transform data column(s)
        prediction_col_names: Name(s) of prediction column(s)
        label_col_names: Name(s) of ground truth label column(s)
        extra_data_col_names: Name(s) of extra data column(s)
        feature_influence_col_names: Name(s) of feature influences column(s)

        # NLP
        token_col_name: Name of the token column
        embeddings_col_name: Name of the embeddings column
    '''
    id_col_name: str
    timestamp_col_name: str = None
    pre_data_col_names: Sequence[str] = tuple()
    post_data_col_names: Sequence[str] = tuple()
    prediction_col_names: Sequence[str] = tuple()
    label_col_names: Sequence[str] = tuple()
    extra_data_col_names: Sequence[str] = tuple()
    feature_influence_col_names: Sequence[str] = tuple()

    # NLP
    tokens_col_name: str = None
    embeddings_col_name: str = None

    def to_column_info(self) -> ColumnInfo:
        return ColumnInfo(
            pre=self.pre_data_col_names,
            post=self.post_data_col_names,
            label=self.label_col_names,
            prediction=self.prediction_col_names,
            extra=self.extra_data_col_names,
            feature_influences=self.feature_influence_col_names,
            # System columns
            id_column=self.id_col_name,
            timestamp_column=self.timestamp_col_name,
            tokens_column=self.tokens_col_name,
            embeddings_column=self.embeddings_col_name
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(eq=True, frozen=True)
class ModelOutputContext:
    '''Parameter data class representing context for model predictions and feature influences

    Args:
        model_name: Name of the model corresponding to the data
        score_type: Score type of the data
        background_split_name: Name of the split that feature influences are computed against. Feature influences only.
        influence_type: Type of algorithm used to compute influence. Feature influences only.
    '''
    model_name: str
    score_type: str
    background_split_name: str = ""
    influence_type: str = ""

    def __post_init__(self):
        if is_gradient_influence_type(
            self.influence_type
        ) and self.background_split_name:
            raise ValueError(
                f"`background_split_name` cannot be used with influence_type `{self.influence_type}`"
            )

    def clone(
        self,
        model_name: str = None,
        score_type: str = None,
        background_split_name: str = None,
        influence_type: str = None
    ) -> ModelOutputContext:
        '''Return new ModelOutputContext with any provided parameter replaced'''
        return ModelOutputContext(
            model_name=model_name or self.model_name,
            score_type=score_type or self.score_type,
            background_split_name=background_split_name or
            self.background_split_name,
            influence_type=influence_type or self.influence_type
        )


def add_data(
    remote_workspace: 'RemoteTrueraWorkspace',
    data: Union[pd.DataFrame, 'Table'],
    *,
    split_name: str,
    column_spec: Union[ColumnSpec, Mapping[str, Union[str, Sequence[str]]]],
    model_output_context: Optional[Union[ModelOutputContext, dict]] = None,
    is_production_data: bool = False
):
    if column_spec and not isinstance(column_spec, ColumnSpec):
        column_spec = ColumnSpec(**column_spec)
    if model_output_context and not isinstance(
        model_output_context, ModelOutputContext
    ):
        model_output_context = ModelOutputContext(**model_output_context)

    # Validation
    remote_workspace._ensure_project()
    remote_workspace._ensure_data_collection()

    project_id = remote_workspace.project.id
    project_influence_type = remote_workspace.cs_client.get_influence_algorithm_type(
        project_id
    )
    existing_splits = remote_workspace.get_data_splits()
    existing_models = remote_workspace.get_models()

    if split_name not in existing_splits:
        target_split_metadata = None
    else:
        target_split_metadata = remote_workspace.ar_client.get_datasplit_metadata(
            project_id=project_id,
            datasplit_name=split_name,
            data_collection_name=remote_workspace.data_collection.name
        )

    validate_column_spec_and_model_output_context(
        column_spec,
        model_output_context,
        split_name=split_name,
        existing_models=existing_models,
        existing_splits=existing_splits,
        project_influence_type=project_influence_type,
        target_split_metadata=target_split_metadata
    )

    rowset_id = None
    load_data_request = None
    if isinstance(data, Table):
        rowset_id = data._rowset_id
    elif isinstance(data, pd.DataFrame):
        validate_dataframe(
            data=data,
            column_spec=column_spec,
            input_type=remote_workspace._get_input_type()
        )

        # Convert id column to string
        data = data.copy()
        data[column_spec.id_col_name
            ] = data[column_spec.id_col_name].astype("string")

        # Upload DataFrame as parquet
        with TemporaryFile(mode="w+", suffix=".parquet") as file:
            data.to_parquet(path=file.name, index=False)
            uri = remote_workspace.artifact_interaction_client.ar_client.upload_artifact(
                src=file.name,
                project_id=project_id,
                artifact_type=ArtifactType.data_source,
                artifact_id=str(uuid.uuid4()),
                intra_artifact_path="",
                scoping_artifact_ids=[],
                stream=False
            )

        # Build load request
        load_data_request = ds_pb.LoadDataRequest(
            data_source_info=ds_messages_pb.LoadDataInfo(
                project_id=project_id,
                describes_file_kind=DATA_KIND_ALL,
                creation_reason=ds_messages_pb.DS_CR_SYSTEM_REQUESTED,
                type=ds_messages_pb.DS_LOCAL,
                uri=uri,
                format=ds_messages_pb.Format(
                    file_type=ds_messages_pb.FT_PARQUET
                )
            )
        )
    else:
        raise ValueError(
            f"`data` must be either a pd.DataFrame or Table, instead received '{type(data)}'"
        )

    # Build materialize request
    split_type = PROD_DATA_SPLIT_TYPE if is_production_data else DEFAULT_SPLIT_TYPE
    materialize_request = _build_materialize_request(
        remote_workspace,
        split_name,
        column_spec,
        model_output_context,
        split_already_exists=split_name in existing_splits,
        rowset_id=rowset_id,
        split_type=split_type
    )

    # Submit request(s)
    materialize_operation_id = _submit_data_service_requests(
        remote_workspace, materialize_request, load_data_request
    )

    # Wait for materialize to succeed
    remote_workspace.logger.info("Waiting for data split to materialize...")
    remote_workspace.get_ingestion_client(
    )._wait_for_materialize_operation(materialize_operation_id)
    remote_workspace.data_service_client.get_materialize_data_status(
        project_id=project_id,
        materialize_operation_id=materialize_operation_id,
        throw_on_error=True
    )

    # Set datasplit in current context
    remote_workspace.data_split_name = split_name


def _build_materialize_request(
    remote_workspace: 'RemoteTrueraWorkspace',
    split_name: str,
    column_spec: ColumnSpec,
    model_output_context: ModelOutputContext,
    split_already_exists: bool = False,
    rowset_id: str = None,
    split_type: str = DEFAULT_SPLIT_TYPE
) -> ds_pb.MaterializeDataRequest:
    # Create model cache info
    if model_output_context is None:
        model_cache = None
    else:
        model_metadata = remote_workspace.artifact_interaction_client.ar_client.get_model_metadata(
            project_id=remote_workspace.project.id,
            model_name=model_output_context.model_name
        )
        background_split_id = None
        if len(column_spec.feature_influence_col_names
              ) > 0 and not is_gradient_influence_type(
                  model_output_context.influence_type
              ):
            background_split_id = remote_workspace.ar_client.get_datasplit_metadata(
                project_id=remote_workspace.project.id,
                data_collection_name=remote_workspace.data_collection.name,
                datasplit_name=model_output_context.background_split_name
            ).id
        model_cache = CreateCacheInfo(
            model_id=model_metadata.id,
            score_type=model_output_context.score_type,
            background_split_id=background_split_id,
            explanation_algorithm_type=model_output_context.influence_type
        ).build_create_cache_info()

    # Create split info
    existing_split_id, create_split_info = None, None
    if split_already_exists:
        existing_split_id = remote_workspace.artifact_interaction_client.ar_client.get_datasplit_metadata(
            project_id=remote_workspace.project.id,
            data_collection_name=remote_workspace.data_collection.name,
            datasplit_name=split_name,
        ).id
    else:
        create_split_info = ds_messages_pb.CreateSplitInfo(
            output_split_name=split_name,
            output_split_type=split_type,
            # TODO: Check if DEFAULT_SPLIT_MODE is required for all scenarios or in some we might have to change
            output_split_mode=DEFAULT_SPLIT_MODE
        )

    # Create materialize request
    column_info = column_spec.to_column_info()
    materialize_request = ds_pb.MaterializeDataRequest(
        rowset_id=rowset_id,
        data_info=ds_messages_pb.MaterializeDataInfo(
            project_id=remote_workspace.project.id,
            output_data_collection_id=remote_workspace.data_collection.id,
            cache_info=model_cache,
            existing_split_id=existing_split_id,
            create_split_info=create_split_info,
            projections=column_info.get_projections(),
            system_columns=column_info.get_system_column_details()
        ),
        sample_strategy=DEFAULT_SAMPLE_STRATEGY,
        approx_max_rows=DEFAULT_APPROX_MAX_ROWS,
    )
    return materialize_request


def _submit_data_service_requests(
    remote_workspace: 'RemoteTrueraWorkspace',
    materialize_request: ds_pb.MaterializeDataRequest,
    load_data_request: ds_pb.LoadDataRequest = None
) -> str:
    if load_data_request:
        rowset_id, _ = remote_workspace.data_service_client.load_data_source_from_request(
            load_data_request
        )
        materialize_request.rowset_id = rowset_id

    response = remote_workspace.data_service_client.materialize_data_from_request(
        materialize_request=materialize_request
    )
    return response.materialize_operation_id
