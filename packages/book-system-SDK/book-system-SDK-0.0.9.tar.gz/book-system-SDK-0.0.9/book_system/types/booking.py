import datetime

from . import TypeModel
from .events import Event
from .rooms import Room


class Booking(TypeModel):
    base_path = "/booking/"
    def __init__(
            self, 
            time_start: datetime.datetime,
            time_finish: datetime.datetime, 
            event_id: int | None = None,
            room_id: int | None = None,
            event: Event | None = None,
            room: Room | None = None,
            id: int | None = None,
            additional_data: dict | None = None):
        
        self.id = id
        if (not event or not room) and (not event_id or not room_id):
            raise ValueError("You should pass ids event and room or its instance")
        self.event = event
        self.room = room
        self.event_id = event_id
        self.room_id = room_id
        self.time_start = time_start
        self.time_finish = time_finish
        self.additional_data = additional_data

    @classmethod
    def from_json(cls, booking: dict):
        return cls(event_id=booking["event_id"], room_id=booking["room_id"], time_start=booking["time_start"], time_finish=booking["time_finish"], additional_data=booking["additional_data"])

    @property
    def body(self):
        """
            It can cause error when room or event didn't save in the database
        """
        return dict(
            time_start=self.time_start,
            time_finish=self.time_finish, 
            additional_data=self.additional_data,
            room_id=self.room.id,
            event_id=self.event.id)

    @property
    def params(self) -> dict:
        return {}