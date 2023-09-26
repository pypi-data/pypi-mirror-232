import requests
from typing import Literal

from .types import TypeModel
from .types.rooms import Room
from .types.events import Event
from .types.booking import Booking


class BookSystemSDK:
    def __init__(
            self,
            api_url: str,
            rooms: list[Room] | None = None,
            events: list[Event] | None = None,
            booking: list[Booking] | None = None):
        self.api_url = api_url
        self._rooms = rooms
        self._events = events
        self._booking = booking
    
    @property
    def rooms(self) -> list[Room]:
        if not self._rooms:
            url = f"{self.api_url}/rooms/"
            self._rooms = [Room.from_json(room) for room in self._make_request(url=url, method="GET")]
        return self._rooms

    @property
    def events(self) -> list[Event]:
        if not self._events:
            url = f"{self.api_url}/events/"
            self._events = [Event.from_json(event) for event in self._make_request(url=url, method="GET")]
        return self._events
    
    @property
    def booking(self) -> list[Booking]:
        if not self._booking:
            url = f"{self.api_url}/booking/"
            self._booking = [Booking.from_json(booking) for booking in self._make_request(url=url, method="GET")]
        return self._booking

    def _make_request(
            self,
            url: str,
            method: Literal["GET", "POST", "PATCH", "DELETE"],
            body: dict | None = None,
            params: dict | None = None) -> dict:
        response = requests.request(method=method, url=url, json=body, params=params)
        json = response.json()
        if response.status_code not in [200, 201, 204]:
            raise ValueError(json["detail"])
        return json
    
    def create(self, obj: TypeModel) -> TypeModel:
        url = f"{self.api_url}{obj.base_path}"
        return obj.from_json(self._make_request(url=url, method="POST", body=obj.body, params=obj.params))
    
    def refresh(self, obj: TypeModel) -> TypeModel:
        url = f"{self.api_url}{obj.base_path}{obj.id}"
        return obj.from_json(self._make_request(url=url, method="PATCH", body=obj.body, params=obj.params))

    def delete(self, obj: TypeModel | list[TypeModel]) -> None:
        url = f"{self.api_url}{obj.base_path}{obj.id}"
        self._make_request(url=url, method="DELETE")

    def get(self, model, **kwargs) -> TypeModel:
        url = f"{self.api_url}{model.base_path}"
        json = self._make_request(url=url, method="GET", params=kwargs)
        return model.from_json(json)