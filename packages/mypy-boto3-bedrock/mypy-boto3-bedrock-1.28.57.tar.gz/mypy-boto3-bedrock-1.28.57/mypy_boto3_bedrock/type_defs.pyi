"""
Type annotations for bedrock service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_bedrock/type_defs/)

Usage::

    ```python
    from mypy_boto3_bedrock.type_defs import S3ConfigTypeDef

    data: S3ConfigTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    FineTuningJobStatusType,
    InferenceTypeType,
    ModelCustomizationJobStatusType,
    ModelModalityType,
    SortOrderType,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "S3ConfigTypeDef",
    "OutputDataConfigTypeDef",
    "TagTypeDef",
    "TrainingDataConfigTypeDef",
    "VpcConfigTypeDef",
    "ResponseMetadataTypeDef",
    "CustomModelSummaryTypeDef",
    "DeleteCustomModelRequestRequestTypeDef",
    "FoundationModelDetailsTypeDef",
    "FoundationModelSummaryTypeDef",
    "GetCustomModelRequestRequestTypeDef",
    "TrainingMetricsTypeDef",
    "ValidatorMetricTypeDef",
    "GetFoundationModelRequestRequestTypeDef",
    "GetModelCustomizationJobRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "TimestampTypeDef",
    "ListFoundationModelsRequestRequestTypeDef",
    "ModelCustomizationJobSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "StopModelCustomizationJobRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "ValidatorTypeDef",
    "CloudWatchConfigTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateModelCustomizationJobResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ListCustomModelsResponseTypeDef",
    "GetFoundationModelResponseTypeDef",
    "ListFoundationModelsResponseTypeDef",
    "ListCustomModelsRequestListCustomModelsPaginateTypeDef",
    "ListCustomModelsRequestRequestTypeDef",
    "ListModelCustomizationJobsRequestListModelCustomizationJobsPaginateTypeDef",
    "ListModelCustomizationJobsRequestRequestTypeDef",
    "ListModelCustomizationJobsResponseTypeDef",
    "ValidationDataConfigTypeDef",
    "LoggingConfigTypeDef",
    "CreateModelCustomizationJobRequestRequestTypeDef",
    "GetCustomModelResponseTypeDef",
    "GetModelCustomizationJobResponseTypeDef",
    "GetModelInvocationLoggingConfigurationResponseTypeDef",
    "PutModelInvocationLoggingConfigurationRequestRequestTypeDef",
)

S3ConfigTypeDef = TypedDict(
    "S3ConfigTypeDef",
    {
        "bucketName": str,
        "keyPrefix": NotRequired[str],
    },
)

OutputDataConfigTypeDef = TypedDict(
    "OutputDataConfigTypeDef",
    {
        "s3Uri": str,
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "key": str,
        "value": str,
    },
)

TrainingDataConfigTypeDef = TypedDict(
    "TrainingDataConfigTypeDef",
    {
        "s3Uri": str,
    },
)

VpcConfigTypeDef = TypedDict(
    "VpcConfigTypeDef",
    {
        "securityGroupIds": Sequence[str],
        "subnetIds": Sequence[str],
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

CustomModelSummaryTypeDef = TypedDict(
    "CustomModelSummaryTypeDef",
    {
        "baseModelArn": str,
        "baseModelName": str,
        "creationTime": datetime,
        "modelArn": str,
        "modelName": str,
    },
)

DeleteCustomModelRequestRequestTypeDef = TypedDict(
    "DeleteCustomModelRequestRequestTypeDef",
    {
        "modelIdentifier": str,
    },
)

FoundationModelDetailsTypeDef = TypedDict(
    "FoundationModelDetailsTypeDef",
    {
        "modelArn": str,
        "modelId": str,
        "customizationsSupported": NotRequired[List[Literal["FINE_TUNING"]]],
        "inferenceTypesSupported": NotRequired[List[InferenceTypeType]],
        "inputModalities": NotRequired[List[ModelModalityType]],
        "modelName": NotRequired[str],
        "outputModalities": NotRequired[List[ModelModalityType]],
        "providerName": NotRequired[str],
        "responseStreamingSupported": NotRequired[bool],
    },
)

FoundationModelSummaryTypeDef = TypedDict(
    "FoundationModelSummaryTypeDef",
    {
        "modelArn": str,
        "modelId": str,
        "customizationsSupported": NotRequired[List[Literal["FINE_TUNING"]]],
        "inferenceTypesSupported": NotRequired[List[InferenceTypeType]],
        "inputModalities": NotRequired[List[ModelModalityType]],
        "modelName": NotRequired[str],
        "outputModalities": NotRequired[List[ModelModalityType]],
        "providerName": NotRequired[str],
        "responseStreamingSupported": NotRequired[bool],
    },
)

GetCustomModelRequestRequestTypeDef = TypedDict(
    "GetCustomModelRequestRequestTypeDef",
    {
        "modelIdentifier": str,
    },
)

TrainingMetricsTypeDef = TypedDict(
    "TrainingMetricsTypeDef",
    {
        "trainingLoss": NotRequired[float],
    },
)

ValidatorMetricTypeDef = TypedDict(
    "ValidatorMetricTypeDef",
    {
        "validationLoss": NotRequired[float],
    },
)

GetFoundationModelRequestRequestTypeDef = TypedDict(
    "GetFoundationModelRequestRequestTypeDef",
    {
        "modelIdentifier": str,
    },
)

GetModelCustomizationJobRequestRequestTypeDef = TypedDict(
    "GetModelCustomizationJobRequestRequestTypeDef",
    {
        "jobIdentifier": str,
    },
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)

TimestampTypeDef = Union[datetime, str]
ListFoundationModelsRequestRequestTypeDef = TypedDict(
    "ListFoundationModelsRequestRequestTypeDef",
    {
        "byCustomizationType": NotRequired[Literal["FINE_TUNING"]],
        "byInferenceType": NotRequired[InferenceTypeType],
        "byOutputModality": NotRequired[ModelModalityType],
        "byProvider": NotRequired[str],
    },
)

ModelCustomizationJobSummaryTypeDef = TypedDict(
    "ModelCustomizationJobSummaryTypeDef",
    {
        "baseModelArn": str,
        "creationTime": datetime,
        "jobArn": str,
        "jobName": str,
        "status": ModelCustomizationJobStatusType,
        "customModelArn": NotRequired[str],
        "customModelName": NotRequired[str],
        "endTime": NotRequired[datetime],
        "lastModifiedTime": NotRequired[datetime],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
    },
)

StopModelCustomizationJobRequestRequestTypeDef = TypedDict(
    "StopModelCustomizationJobRequestRequestTypeDef",
    {
        "jobIdentifier": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
        "tagKeys": Sequence[str],
    },
)

ValidatorTypeDef = TypedDict(
    "ValidatorTypeDef",
    {
        "s3Uri": str,
    },
)

CloudWatchConfigTypeDef = TypedDict(
    "CloudWatchConfigTypeDef",
    {
        "logGroupName": str,
        "roleArn": str,
        "largeDataDeliveryS3Config": NotRequired[S3ConfigTypeDef],
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
        "tags": Sequence[TagTypeDef],
    },
)

CreateModelCustomizationJobResponseTypeDef = TypedDict(
    "CreateModelCustomizationJobResponseTypeDef",
    {
        "jobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListCustomModelsResponseTypeDef = TypedDict(
    "ListCustomModelsResponseTypeDef",
    {
        "modelSummaries": List[CustomModelSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetFoundationModelResponseTypeDef = TypedDict(
    "GetFoundationModelResponseTypeDef",
    {
        "modelDetails": FoundationModelDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListFoundationModelsResponseTypeDef = TypedDict(
    "ListFoundationModelsResponseTypeDef",
    {
        "modelSummaries": List[FoundationModelSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListCustomModelsRequestListCustomModelsPaginateTypeDef = TypedDict(
    "ListCustomModelsRequestListCustomModelsPaginateTypeDef",
    {
        "baseModelArnEquals": NotRequired[str],
        "creationTimeAfter": NotRequired[TimestampTypeDef],
        "creationTimeBefore": NotRequired[TimestampTypeDef],
        "foundationModelArnEquals": NotRequired[str],
        "nameContains": NotRequired[str],
        "sortBy": NotRequired[Literal["CreationTime"]],
        "sortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListCustomModelsRequestRequestTypeDef = TypedDict(
    "ListCustomModelsRequestRequestTypeDef",
    {
        "baseModelArnEquals": NotRequired[str],
        "creationTimeAfter": NotRequired[TimestampTypeDef],
        "creationTimeBefore": NotRequired[TimestampTypeDef],
        "foundationModelArnEquals": NotRequired[str],
        "maxResults": NotRequired[int],
        "nameContains": NotRequired[str],
        "nextToken": NotRequired[str],
        "sortBy": NotRequired[Literal["CreationTime"]],
        "sortOrder": NotRequired[SortOrderType],
    },
)

ListModelCustomizationJobsRequestListModelCustomizationJobsPaginateTypeDef = TypedDict(
    "ListModelCustomizationJobsRequestListModelCustomizationJobsPaginateTypeDef",
    {
        "creationTimeAfter": NotRequired[TimestampTypeDef],
        "creationTimeBefore": NotRequired[TimestampTypeDef],
        "nameContains": NotRequired[str],
        "sortBy": NotRequired[Literal["CreationTime"]],
        "sortOrder": NotRequired[SortOrderType],
        "statusEquals": NotRequired[FineTuningJobStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelCustomizationJobsRequestRequestTypeDef = TypedDict(
    "ListModelCustomizationJobsRequestRequestTypeDef",
    {
        "creationTimeAfter": NotRequired[TimestampTypeDef],
        "creationTimeBefore": NotRequired[TimestampTypeDef],
        "maxResults": NotRequired[int],
        "nameContains": NotRequired[str],
        "nextToken": NotRequired[str],
        "sortBy": NotRequired[Literal["CreationTime"]],
        "sortOrder": NotRequired[SortOrderType],
        "statusEquals": NotRequired[FineTuningJobStatusType],
    },
)

ListModelCustomizationJobsResponseTypeDef = TypedDict(
    "ListModelCustomizationJobsResponseTypeDef",
    {
        "modelCustomizationJobSummaries": List[ModelCustomizationJobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ValidationDataConfigTypeDef = TypedDict(
    "ValidationDataConfigTypeDef",
    {
        "validators": Sequence[ValidatorTypeDef],
    },
)

LoggingConfigTypeDef = TypedDict(
    "LoggingConfigTypeDef",
    {
        "cloudWatchConfig": NotRequired[CloudWatchConfigTypeDef],
        "embeddingDataDeliveryEnabled": NotRequired[bool],
        "imageDataDeliveryEnabled": NotRequired[bool],
        "s3Config": NotRequired[S3ConfigTypeDef],
        "textDataDeliveryEnabled": NotRequired[bool],
    },
)

CreateModelCustomizationJobRequestRequestTypeDef = TypedDict(
    "CreateModelCustomizationJobRequestRequestTypeDef",
    {
        "baseModelIdentifier": str,
        "customModelName": str,
        "hyperParameters": Mapping[str, str],
        "jobName": str,
        "outputDataConfig": OutputDataConfigTypeDef,
        "roleArn": str,
        "trainingDataConfig": TrainingDataConfigTypeDef,
        "clientRequestToken": NotRequired[str],
        "customModelKmsKeyId": NotRequired[str],
        "customModelTags": NotRequired[Sequence[TagTypeDef]],
        "jobTags": NotRequired[Sequence[TagTypeDef]],
        "validationDataConfig": NotRequired[ValidationDataConfigTypeDef],
        "vpcConfig": NotRequired[VpcConfigTypeDef],
    },
)

GetCustomModelResponseTypeDef = TypedDict(
    "GetCustomModelResponseTypeDef",
    {
        "baseModelArn": str,
        "creationTime": datetime,
        "hyperParameters": Dict[str, str],
        "jobArn": str,
        "jobName": str,
        "modelArn": str,
        "modelKmsKeyArn": str,
        "modelName": str,
        "outputDataConfig": OutputDataConfigTypeDef,
        "trainingDataConfig": TrainingDataConfigTypeDef,
        "trainingMetrics": TrainingMetricsTypeDef,
        "validationDataConfig": ValidationDataConfigTypeDef,
        "validationMetrics": List[ValidatorMetricTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetModelCustomizationJobResponseTypeDef = TypedDict(
    "GetModelCustomizationJobResponseTypeDef",
    {
        "baseModelArn": str,
        "clientRequestToken": str,
        "creationTime": datetime,
        "endTime": datetime,
        "failureMessage": str,
        "hyperParameters": Dict[str, str],
        "jobArn": str,
        "jobName": str,
        "lastModifiedTime": datetime,
        "outputDataConfig": OutputDataConfigTypeDef,
        "outputModelArn": str,
        "outputModelKmsKeyArn": str,
        "outputModelName": str,
        "roleArn": str,
        "status": ModelCustomizationJobStatusType,
        "trainingDataConfig": TrainingDataConfigTypeDef,
        "trainingMetrics": TrainingMetricsTypeDef,
        "validationDataConfig": ValidationDataConfigTypeDef,
        "validationMetrics": List[ValidatorMetricTypeDef],
        "vpcConfig": VpcConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetModelInvocationLoggingConfigurationResponseTypeDef = TypedDict(
    "GetModelInvocationLoggingConfigurationResponseTypeDef",
    {
        "loggingConfig": LoggingConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutModelInvocationLoggingConfigurationRequestRequestTypeDef = TypedDict(
    "PutModelInvocationLoggingConfigurationRequestRequestTypeDef",
    {
        "loggingConfig": LoggingConfigTypeDef,
    },
)
