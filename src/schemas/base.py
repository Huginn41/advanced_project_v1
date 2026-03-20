

from pydantic import BaseModel


class Base(BaseModel):

    model_config = {"from_attributes": True}


class ResultResponse(Base):

    result: bool = True
