from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define, field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.metadata_response_200_response_metadata_status_item import (
        MetadataResponse200ResponseMetadataStatusItem,
    )
    from ..models.metadata_response_200_response_result_item import MetadataResponse200ResponseResultItem


T = TypeVar("T", bound="MetadataResponse200Response")


@define
class MetadataResponse200Response:
    """
    Attributes:
        result (Union[Unset, List['MetadataResponse200ResponseResultItem']]):
        metadata_status (Union[Unset, List['MetadataResponse200ResponseMetadataStatusItem']]):
    """

    result: Union[Unset, List["MetadataResponse200ResponseResultItem"]] = UNSET
    metadata_status: Union[Unset, List["MetadataResponse200ResponseMetadataStatusItem"]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.result, Unset):
            result = []
            for result_item_data in self.result:
                result_item = result_item_data.to_dict()

                result.append(result_item)

        metadata_status: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.metadata_status, Unset):
            metadata_status = []
            for metadata_status_item_data in self.metadata_status:
                metadata_status_item = metadata_status_item_data.to_dict()

                metadata_status.append(metadata_status_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if result is not UNSET:
            field_dict["result"] = result
        if metadata_status is not UNSET:
            field_dict["metadataStatus"] = metadata_status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.metadata_response_200_response_metadata_status_item import (
            MetadataResponse200ResponseMetadataStatusItem,
        )
        from ..models.metadata_response_200_response_result_item import MetadataResponse200ResponseResultItem

        d = src_dict.copy()
        result = []
        _result = d.pop("result", UNSET)
        for result_item_data in _result or []:
            result_item = MetadataResponse200ResponseResultItem.from_dict(result_item_data)

            result.append(result_item)

        metadata_status = []
        _metadata_status = d.pop("metadataStatus", UNSET)
        for metadata_status_item_data in _metadata_status or []:
            metadata_status_item = MetadataResponse200ResponseMetadataStatusItem.from_dict(metadata_status_item_data)

            metadata_status.append(metadata_status_item)

        metadata_response_200_response = cls(
            result=result,
            metadata_status=metadata_status,
        )

        metadata_response_200_response.additional_properties = d
        return metadata_response_200_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
