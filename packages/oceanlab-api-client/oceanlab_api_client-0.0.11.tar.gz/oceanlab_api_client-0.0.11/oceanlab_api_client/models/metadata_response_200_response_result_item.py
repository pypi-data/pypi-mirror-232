import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define, field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="MetadataResponse200ResponseResultItem")


@define
class MetadataResponse200ResponseResultItem:
    """
    Attributes:
        name (Union[Unset, str]):
        source (Union[Unset, str]):
        collection (Union[Unset, str]):
        description (Union[Unset, str]):
        maxvalue (Union[Unset, str]):
        min_value (Union[Unset, str]):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):
    """

    name: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    collection: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    maxvalue: Union[Unset, str] = UNSET
    min_value: Union[Unset, str] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    end_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        source = self.source
        collection = self.collection
        description = self.description
        maxvalue = self.maxvalue
        min_value = self.min_value
        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if source is not UNSET:
            field_dict["source"] = source
        if collection is not UNSET:
            field_dict["collection"] = collection
        if description is not UNSET:
            field_dict["description"] = description
        if maxvalue is not UNSET:
            field_dict["maxvalue"] = maxvalue
        if min_value is not UNSET:
            field_dict["minValue"] = min_value
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        source = d.pop("source", UNSET)

        collection = d.pop("collection", UNSET)

        description = d.pop("description", UNSET)

        maxvalue = d.pop("maxvalue", UNSET)

        min_value = d.pop("minValue", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _end_date = d.pop("endDate", UNSET)
        end_date: Union[Unset, datetime.datetime]
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        metadata_response_200_response_result_item = cls(
            name=name,
            source=source,
            collection=collection,
            description=description,
            maxvalue=maxvalue,
            min_value=min_value,
            start_date=start_date,
            end_date=end_date,
        )

        metadata_response_200_response_result_item.additional_properties = d
        return metadata_response_200_response_result_item

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
