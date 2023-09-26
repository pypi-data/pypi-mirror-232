from . import TypeModel


class Event(TypeModel):
    base_path = "/events/"
    
    def __init__(
            self,
            title: str,
            additional_data: dict | None = None):
    
        self.title = title
        self.additional_data = additional_data

    @classmethod
    def from_json(cls, event: dict):
        """
            Getting event using json that we get from API
            {
                "title": "str",
                "additional_data": "dict"
            }
        """
        return cls(title=event["title"], additional_data=event["additional_data"])

    @property
    def body(self) -> dict:
        return dict(title=self.title, additional_data=self.additional_data)

    @property
    def params(self) -> dict:
        return {}