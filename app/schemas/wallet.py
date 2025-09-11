from typing import Literal
from pydantic import BaseModel


class AddFundsRequest(BaseModel):
    user_id: str
    amount: float
    currency: Literal['AED','USD']
    payment_method: str