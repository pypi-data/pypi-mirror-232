"""
Type annotations for textract service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_textract/type_defs/)

Usage::

    ```python
    from mypy_boto3_textract.type_defs import DocumentMetadataTypeDef

    data: DocumentMetadataTypeDef = ...
    ```
"""
import sys
from typing import IO, Any, Dict, List, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    BlockTypeType,
    ContentClassifierType,
    EntityTypeType,
    FeatureTypeType,
    JobStatusType,
    RelationshipTypeType,
    SelectionStatusType,
    TextTypeType,
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
    "DocumentMetadataTypeDef",
    "HumanLoopActivationOutputTypeDef",
    "ResponseMetadataTypeDef",
    "NormalizedValueTypeDef",
    "BlobTypeDef",
    "QueryTypeDef",
    "RelationshipTypeDef",
    "BoundingBoxTypeDef",
    "DetectedSignatureTypeDef",
    "SplitDocumentTypeDef",
    "UndetectedSignatureTypeDef",
    "S3ObjectTypeDef",
    "ExpenseCurrencyTypeDef",
    "ExpenseGroupPropertyTypeDef",
    "ExpenseTypeTypeDef",
    "PointTypeDef",
    "GetDocumentAnalysisRequestRequestTypeDef",
    "WarningTypeDef",
    "GetDocumentTextDetectionRequestRequestTypeDef",
    "GetExpenseAnalysisRequestRequestTypeDef",
    "GetLendingAnalysisRequestRequestTypeDef",
    "GetLendingAnalysisSummaryRequestRequestTypeDef",
    "HumanLoopDataAttributesTypeDef",
    "NotificationChannelTypeDef",
    "OutputConfigTypeDef",
    "PredictionTypeDef",
    "StartDocumentAnalysisResponseTypeDef",
    "StartDocumentTextDetectionResponseTypeDef",
    "StartExpenseAnalysisResponseTypeDef",
    "StartLendingAnalysisResponseTypeDef",
    "AnalyzeIDDetectionsTypeDef",
    "QueriesConfigTypeDef",
    "DocumentGroupTypeDef",
    "DocumentLocationTypeDef",
    "DocumentTypeDef",
    "GeometryTypeDef",
    "HumanLoopConfigTypeDef",
    "PageClassificationTypeDef",
    "IdentityDocumentFieldTypeDef",
    "LendingSummaryTypeDef",
    "StartDocumentAnalysisRequestRequestTypeDef",
    "StartDocumentTextDetectionRequestRequestTypeDef",
    "StartExpenseAnalysisRequestRequestTypeDef",
    "StartLendingAnalysisRequestRequestTypeDef",
    "AnalyzeExpenseRequestRequestTypeDef",
    "AnalyzeIDRequestRequestTypeDef",
    "DetectDocumentTextRequestRequestTypeDef",
    "BlockTypeDef",
    "ExpenseDetectionTypeDef",
    "LendingDetectionTypeDef",
    "SignatureDetectionTypeDef",
    "AnalyzeDocumentRequestRequestTypeDef",
    "GetLendingAnalysisSummaryResponseTypeDef",
    "AnalyzeDocumentResponseTypeDef",
    "DetectDocumentTextResponseTypeDef",
    "GetDocumentAnalysisResponseTypeDef",
    "GetDocumentTextDetectionResponseTypeDef",
    "IdentityDocumentTypeDef",
    "ExpenseFieldTypeDef",
    "LendingFieldTypeDef",
    "AnalyzeIDResponseTypeDef",
    "LineItemFieldsTypeDef",
    "LendingDocumentTypeDef",
    "LineItemGroupTypeDef",
    "ExpenseDocumentTypeDef",
    "AnalyzeExpenseResponseTypeDef",
    "ExtractionTypeDef",
    "GetExpenseAnalysisResponseTypeDef",
    "LendingResultTypeDef",
    "GetLendingAnalysisResponseTypeDef",
)

DocumentMetadataTypeDef = TypedDict(
    "DocumentMetadataTypeDef",
    {
        "Pages": NotRequired[int],
    },
)

HumanLoopActivationOutputTypeDef = TypedDict(
    "HumanLoopActivationOutputTypeDef",
    {
        "HumanLoopArn": NotRequired[str],
        "HumanLoopActivationReasons": NotRequired[List[str]],
        "HumanLoopActivationConditionsEvaluationResults": NotRequired[str],
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

NormalizedValueTypeDef = TypedDict(
    "NormalizedValueTypeDef",
    {
        "Value": NotRequired[str],
        "ValueType": NotRequired[Literal["DATE"]],
    },
)

BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
QueryTypeDef = TypedDict(
    "QueryTypeDef",
    {
        "Text": str,
        "Alias": NotRequired[str],
        "Pages": NotRequired[Sequence[str]],
    },
)

RelationshipTypeDef = TypedDict(
    "RelationshipTypeDef",
    {
        "Type": NotRequired[RelationshipTypeType],
        "Ids": NotRequired[List[str]],
    },
)

BoundingBoxTypeDef = TypedDict(
    "BoundingBoxTypeDef",
    {
        "Width": NotRequired[float],
        "Height": NotRequired[float],
        "Left": NotRequired[float],
        "Top": NotRequired[float],
    },
)

DetectedSignatureTypeDef = TypedDict(
    "DetectedSignatureTypeDef",
    {
        "Page": NotRequired[int],
    },
)

SplitDocumentTypeDef = TypedDict(
    "SplitDocumentTypeDef",
    {
        "Index": NotRequired[int],
        "Pages": NotRequired[List[int]],
    },
)

UndetectedSignatureTypeDef = TypedDict(
    "UndetectedSignatureTypeDef",
    {
        "Page": NotRequired[int],
    },
)

S3ObjectTypeDef = TypedDict(
    "S3ObjectTypeDef",
    {
        "Bucket": NotRequired[str],
        "Name": NotRequired[str],
        "Version": NotRequired[str],
    },
)

ExpenseCurrencyTypeDef = TypedDict(
    "ExpenseCurrencyTypeDef",
    {
        "Code": NotRequired[str],
        "Confidence": NotRequired[float],
    },
)

ExpenseGroupPropertyTypeDef = TypedDict(
    "ExpenseGroupPropertyTypeDef",
    {
        "Types": NotRequired[List[str]],
        "Id": NotRequired[str],
    },
)

ExpenseTypeTypeDef = TypedDict(
    "ExpenseTypeTypeDef",
    {
        "Text": NotRequired[str],
        "Confidence": NotRequired[float],
    },
)

PointTypeDef = TypedDict(
    "PointTypeDef",
    {
        "X": NotRequired[float],
        "Y": NotRequired[float],
    },
)

GetDocumentAnalysisRequestRequestTypeDef = TypedDict(
    "GetDocumentAnalysisRequestRequestTypeDef",
    {
        "JobId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

WarningTypeDef = TypedDict(
    "WarningTypeDef",
    {
        "ErrorCode": NotRequired[str],
        "Pages": NotRequired[List[int]],
    },
)

GetDocumentTextDetectionRequestRequestTypeDef = TypedDict(
    "GetDocumentTextDetectionRequestRequestTypeDef",
    {
        "JobId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

GetExpenseAnalysisRequestRequestTypeDef = TypedDict(
    "GetExpenseAnalysisRequestRequestTypeDef",
    {
        "JobId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

GetLendingAnalysisRequestRequestTypeDef = TypedDict(
    "GetLendingAnalysisRequestRequestTypeDef",
    {
        "JobId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

GetLendingAnalysisSummaryRequestRequestTypeDef = TypedDict(
    "GetLendingAnalysisSummaryRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

HumanLoopDataAttributesTypeDef = TypedDict(
    "HumanLoopDataAttributesTypeDef",
    {
        "ContentClassifiers": NotRequired[Sequence[ContentClassifierType]],
    },
)

NotificationChannelTypeDef = TypedDict(
    "NotificationChannelTypeDef",
    {
        "SNSTopicArn": str,
        "RoleArn": str,
    },
)

OutputConfigTypeDef = TypedDict(
    "OutputConfigTypeDef",
    {
        "S3Bucket": str,
        "S3Prefix": NotRequired[str],
    },
)

PredictionTypeDef = TypedDict(
    "PredictionTypeDef",
    {
        "Value": NotRequired[str],
        "Confidence": NotRequired[float],
    },
)

StartDocumentAnalysisResponseTypeDef = TypedDict(
    "StartDocumentAnalysisResponseTypeDef",
    {
        "JobId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartDocumentTextDetectionResponseTypeDef = TypedDict(
    "StartDocumentTextDetectionResponseTypeDef",
    {
        "JobId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartExpenseAnalysisResponseTypeDef = TypedDict(
    "StartExpenseAnalysisResponseTypeDef",
    {
        "JobId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartLendingAnalysisResponseTypeDef = TypedDict(
    "StartLendingAnalysisResponseTypeDef",
    {
        "JobId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AnalyzeIDDetectionsTypeDef = TypedDict(
    "AnalyzeIDDetectionsTypeDef",
    {
        "Text": str,
        "NormalizedValue": NotRequired[NormalizedValueTypeDef],
        "Confidence": NotRequired[float],
    },
)

QueriesConfigTypeDef = TypedDict(
    "QueriesConfigTypeDef",
    {
        "Queries": Sequence[QueryTypeDef],
    },
)

DocumentGroupTypeDef = TypedDict(
    "DocumentGroupTypeDef",
    {
        "Type": NotRequired[str],
        "SplitDocuments": NotRequired[List[SplitDocumentTypeDef]],
        "DetectedSignatures": NotRequired[List[DetectedSignatureTypeDef]],
        "UndetectedSignatures": NotRequired[List[UndetectedSignatureTypeDef]],
    },
)

DocumentLocationTypeDef = TypedDict(
    "DocumentLocationTypeDef",
    {
        "S3Object": NotRequired[S3ObjectTypeDef],
    },
)

DocumentTypeDef = TypedDict(
    "DocumentTypeDef",
    {
        "Bytes": NotRequired[BlobTypeDef],
        "S3Object": NotRequired[S3ObjectTypeDef],
    },
)

GeometryTypeDef = TypedDict(
    "GeometryTypeDef",
    {
        "BoundingBox": NotRequired[BoundingBoxTypeDef],
        "Polygon": NotRequired[List[PointTypeDef]],
    },
)

HumanLoopConfigTypeDef = TypedDict(
    "HumanLoopConfigTypeDef",
    {
        "HumanLoopName": str,
        "FlowDefinitionArn": str,
        "DataAttributes": NotRequired[HumanLoopDataAttributesTypeDef],
    },
)

PageClassificationTypeDef = TypedDict(
    "PageClassificationTypeDef",
    {
        "PageType": List[PredictionTypeDef],
        "PageNumber": List[PredictionTypeDef],
    },
)

IdentityDocumentFieldTypeDef = TypedDict(
    "IdentityDocumentFieldTypeDef",
    {
        "Type": NotRequired[AnalyzeIDDetectionsTypeDef],
        "ValueDetection": NotRequired[AnalyzeIDDetectionsTypeDef],
    },
)

LendingSummaryTypeDef = TypedDict(
    "LendingSummaryTypeDef",
    {
        "DocumentGroups": NotRequired[List[DocumentGroupTypeDef]],
        "UndetectedDocumentTypes": NotRequired[List[str]],
    },
)

StartDocumentAnalysisRequestRequestTypeDef = TypedDict(
    "StartDocumentAnalysisRequestRequestTypeDef",
    {
        "DocumentLocation": DocumentLocationTypeDef,
        "FeatureTypes": Sequence[FeatureTypeType],
        "ClientRequestToken": NotRequired[str],
        "JobTag": NotRequired[str],
        "NotificationChannel": NotRequired[NotificationChannelTypeDef],
        "OutputConfig": NotRequired[OutputConfigTypeDef],
        "KMSKeyId": NotRequired[str],
        "QueriesConfig": NotRequired[QueriesConfigTypeDef],
    },
)

StartDocumentTextDetectionRequestRequestTypeDef = TypedDict(
    "StartDocumentTextDetectionRequestRequestTypeDef",
    {
        "DocumentLocation": DocumentLocationTypeDef,
        "ClientRequestToken": NotRequired[str],
        "JobTag": NotRequired[str],
        "NotificationChannel": NotRequired[NotificationChannelTypeDef],
        "OutputConfig": NotRequired[OutputConfigTypeDef],
        "KMSKeyId": NotRequired[str],
    },
)

StartExpenseAnalysisRequestRequestTypeDef = TypedDict(
    "StartExpenseAnalysisRequestRequestTypeDef",
    {
        "DocumentLocation": DocumentLocationTypeDef,
        "ClientRequestToken": NotRequired[str],
        "JobTag": NotRequired[str],
        "NotificationChannel": NotRequired[NotificationChannelTypeDef],
        "OutputConfig": NotRequired[OutputConfigTypeDef],
        "KMSKeyId": NotRequired[str],
    },
)

StartLendingAnalysisRequestRequestTypeDef = TypedDict(
    "StartLendingAnalysisRequestRequestTypeDef",
    {
        "DocumentLocation": DocumentLocationTypeDef,
        "ClientRequestToken": NotRequired[str],
        "JobTag": NotRequired[str],
        "NotificationChannel": NotRequired[NotificationChannelTypeDef],
        "OutputConfig": NotRequired[OutputConfigTypeDef],
        "KMSKeyId": NotRequired[str],
    },
)

AnalyzeExpenseRequestRequestTypeDef = TypedDict(
    "AnalyzeExpenseRequestRequestTypeDef",
    {
        "Document": DocumentTypeDef,
    },
)

AnalyzeIDRequestRequestTypeDef = TypedDict(
    "AnalyzeIDRequestRequestTypeDef",
    {
        "DocumentPages": Sequence[DocumentTypeDef],
    },
)

DetectDocumentTextRequestRequestTypeDef = TypedDict(
    "DetectDocumentTextRequestRequestTypeDef",
    {
        "Document": DocumentTypeDef,
    },
)

BlockTypeDef = TypedDict(
    "BlockTypeDef",
    {
        "BlockType": NotRequired[BlockTypeType],
        "Confidence": NotRequired[float],
        "Text": NotRequired[str],
        "TextType": NotRequired[TextTypeType],
        "RowIndex": NotRequired[int],
        "ColumnIndex": NotRequired[int],
        "RowSpan": NotRequired[int],
        "ColumnSpan": NotRequired[int],
        "Geometry": NotRequired[GeometryTypeDef],
        "Id": NotRequired[str],
        "Relationships": NotRequired[List[RelationshipTypeDef]],
        "EntityTypes": NotRequired[List[EntityTypeType]],
        "SelectionStatus": NotRequired[SelectionStatusType],
        "Page": NotRequired[int],
        "Query": NotRequired[QueryTypeDef],
    },
)

ExpenseDetectionTypeDef = TypedDict(
    "ExpenseDetectionTypeDef",
    {
        "Text": NotRequired[str],
        "Geometry": NotRequired[GeometryTypeDef],
        "Confidence": NotRequired[float],
    },
)

LendingDetectionTypeDef = TypedDict(
    "LendingDetectionTypeDef",
    {
        "Text": NotRequired[str],
        "SelectionStatus": NotRequired[SelectionStatusType],
        "Geometry": NotRequired[GeometryTypeDef],
        "Confidence": NotRequired[float],
    },
)

SignatureDetectionTypeDef = TypedDict(
    "SignatureDetectionTypeDef",
    {
        "Confidence": NotRequired[float],
        "Geometry": NotRequired[GeometryTypeDef],
    },
)

AnalyzeDocumentRequestRequestTypeDef = TypedDict(
    "AnalyzeDocumentRequestRequestTypeDef",
    {
        "Document": DocumentTypeDef,
        "FeatureTypes": Sequence[FeatureTypeType],
        "HumanLoopConfig": NotRequired[HumanLoopConfigTypeDef],
        "QueriesConfig": NotRequired[QueriesConfigTypeDef],
    },
)

GetLendingAnalysisSummaryResponseTypeDef = TypedDict(
    "GetLendingAnalysisSummaryResponseTypeDef",
    {
        "DocumentMetadata": DocumentMetadataTypeDef,
        "JobStatus": JobStatusType,
        "Summary": LendingSummaryTypeDef,
        "Warnings": List[WarningTypeDef],
        "StatusMessage": str,
        "AnalyzeLendingModelVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AnalyzeDocumentResponseTypeDef = TypedDict(
    "AnalyzeDocumentResponseTypeDef",
    {
        "DocumentMetadata": DocumentMetadataTypeDef,
        "Blocks": List[BlockTypeDef],
        "HumanLoopActivationOutput": HumanLoopActivationOutputTypeDef,
        "AnalyzeDocumentModelVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DetectDocumentTextResponseTypeDef = TypedDict(
    "DetectDocumentTextResponseTypeDef",
    {
        "DocumentMetadata": DocumentMetadataTypeDef,
        "Blocks": List[BlockTypeDef],
        "DetectDocumentTextModelVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDocumentAnalysisResponseTypeDef = TypedDict(
    "GetDocumentAnalysisResponseTypeDef",
    {
        "DocumentMetadata": DocumentMetadataTypeDef,
        "JobStatus": JobStatusType,
        "NextToken": str,
        "Blocks": List[BlockTypeDef],
        "Warnings": List[WarningTypeDef],
        "StatusMessage": str,
        "AnalyzeDocumentModelVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDocumentTextDetectionResponseTypeDef = TypedDict(
    "GetDocumentTextDetectionResponseTypeDef",
    {
        "DocumentMetadata": DocumentMetadataTypeDef,
        "JobStatus": JobStatusType,
        "NextToken": str,
        "Blocks": List[BlockTypeDef],
        "Warnings": List[WarningTypeDef],
        "StatusMessage": str,
        "DetectDocumentTextModelVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IdentityDocumentTypeDef = TypedDict(
    "IdentityDocumentTypeDef",
    {
        "DocumentIndex": NotRequired[int],
        "IdentityDocumentFields": NotRequired[List[IdentityDocumentFieldTypeDef]],
        "Blocks": NotRequired[List[BlockTypeDef]],
    },
)

ExpenseFieldTypeDef = TypedDict(
    "ExpenseFieldTypeDef",
    {
        "Type": NotRequired[ExpenseTypeTypeDef],
        "LabelDetection": NotRequired[ExpenseDetectionTypeDef],
        "ValueDetection": NotRequired[ExpenseDetectionTypeDef],
        "PageNumber": NotRequired[int],
        "Currency": NotRequired[ExpenseCurrencyTypeDef],
        "GroupProperties": NotRequired[List[ExpenseGroupPropertyTypeDef]],
    },
)

LendingFieldTypeDef = TypedDict(
    "LendingFieldTypeDef",
    {
        "Type": NotRequired[str],
        "KeyDetection": NotRequired[LendingDetectionTypeDef],
        "ValueDetections": NotRequired[List[LendingDetectionTypeDef]],
    },
)

AnalyzeIDResponseTypeDef = TypedDict(
    "AnalyzeIDResponseTypeDef",
    {
        "IdentityDocuments": List[IdentityDocumentTypeDef],
        "DocumentMetadata": DocumentMetadataTypeDef,
        "AnalyzeIDModelVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LineItemFieldsTypeDef = TypedDict(
    "LineItemFieldsTypeDef",
    {
        "LineItemExpenseFields": NotRequired[List[ExpenseFieldTypeDef]],
    },
)

LendingDocumentTypeDef = TypedDict(
    "LendingDocumentTypeDef",
    {
        "LendingFields": NotRequired[List[LendingFieldTypeDef]],
        "SignatureDetections": NotRequired[List[SignatureDetectionTypeDef]],
    },
)

LineItemGroupTypeDef = TypedDict(
    "LineItemGroupTypeDef",
    {
        "LineItemGroupIndex": NotRequired[int],
        "LineItems": NotRequired[List[LineItemFieldsTypeDef]],
    },
)

ExpenseDocumentTypeDef = TypedDict(
    "ExpenseDocumentTypeDef",
    {
        "ExpenseIndex": NotRequired[int],
        "SummaryFields": NotRequired[List[ExpenseFieldTypeDef]],
        "LineItemGroups": NotRequired[List[LineItemGroupTypeDef]],
        "Blocks": NotRequired[List[BlockTypeDef]],
    },
)

AnalyzeExpenseResponseTypeDef = TypedDict(
    "AnalyzeExpenseResponseTypeDef",
    {
        "DocumentMetadata": DocumentMetadataTypeDef,
        "ExpenseDocuments": List[ExpenseDocumentTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExtractionTypeDef = TypedDict(
    "ExtractionTypeDef",
    {
        "LendingDocument": NotRequired[LendingDocumentTypeDef],
        "ExpenseDocument": NotRequired[ExpenseDocumentTypeDef],
        "IdentityDocument": NotRequired[IdentityDocumentTypeDef],
    },
)

GetExpenseAnalysisResponseTypeDef = TypedDict(
    "GetExpenseAnalysisResponseTypeDef",
    {
        "DocumentMetadata": DocumentMetadataTypeDef,
        "JobStatus": JobStatusType,
        "NextToken": str,
        "ExpenseDocuments": List[ExpenseDocumentTypeDef],
        "Warnings": List[WarningTypeDef],
        "StatusMessage": str,
        "AnalyzeExpenseModelVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LendingResultTypeDef = TypedDict(
    "LendingResultTypeDef",
    {
        "Page": NotRequired[int],
        "PageClassification": NotRequired[PageClassificationTypeDef],
        "Extractions": NotRequired[List[ExtractionTypeDef]],
    },
)

GetLendingAnalysisResponseTypeDef = TypedDict(
    "GetLendingAnalysisResponseTypeDef",
    {
        "DocumentMetadata": DocumentMetadataTypeDef,
        "JobStatus": JobStatusType,
        "NextToken": str,
        "Results": List[LendingResultTypeDef],
        "Warnings": List[WarningTypeDef],
        "StatusMessage": str,
        "AnalyzeLendingModelVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
