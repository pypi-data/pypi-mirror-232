from . import TypeModel


class Seat(TypeModel):
    base_path = "/seats/"

    def __init__(
            self,
            row: int,
            column: int,
            number: int,
            booked: bool = False,
            additional_data: dict | None = None):

        self.row = row
        self.column = column
        self.number = number
        self.booked = booked
        self.additional_data = additional_data

    @classmethod
    def from_json(cls, seat: dict):
        """
            Getting seat using json that we get from API
        """
        return cls(
            row=seat["row"], 
            column=seat["column"], 
            number=seat["number"], 
            booked=seat["booked"], 
            additional_data=seat["additional_data"]
        )

    @property
    def room(self):
        """
            TODO: Getting room by it id in the database and return it
        """
        pass

    def book(self):
        """
            TODO: booking seat in the database
        """
        if self.booked:
            raise ValueError("The seat have already booked")
        self.booked = True
        pass

    def unbook(self, strict: bool = False):
        """
            TODO: unbooking seat in the database
        """
        self.booked = False
        pass

    @property
    def body(self) -> dict:
        return dict(
            row=self.row,
            column=self.column, 
            number=self.number, 
            booked=self.booked, 
            additional_data=self.additional_data
        )

    @property
    def params(self) -> dict:
        return {}