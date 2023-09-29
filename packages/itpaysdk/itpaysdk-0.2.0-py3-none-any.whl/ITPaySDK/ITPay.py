import aiohttp
from types import NoneType
from typing import Optional

from ITPaySDK import ITPayStatusException
from enums import Currency, PaymentType


class ITPayAPI:
    def __init__(self, shop_id: str, token: str):
        self.base_url = "https://itpay.app/api/v1/"
        self.shop_id = shop_id
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    async def _send_request(self, endpoint: str, method: str = "GET", data: Optional[dict | NoneType] = None) -> dict:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(self.base_url + endpoint, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise ITPayStatusException(f"Request failed with status {response.status}")
            elif method == "POST":
                if data is None:
                    raise ValueError("You must provide data for a POST request.")

                async with session.post(self.base_url + endpoint, headers=self.headers, data=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise ITPayStatusException(f"Request failed with status {response.status}")

    async def balance(self):
        return await self._send_request(endpoint="merchant/balance/")

    async def create_bill(
            self,
            amount: float,
            order_id: Optional[int] = None,
            description: Optional[str] = None,
            type: Optional[PaymentType] = None,
            currency_in: Optional[Currency] = None,
            payer_pays_commission: Optional[bool] = None
    ) -> dict:
        """
        Create payment bill
        :param float amount: Amount of payment
        :param Optional[int] order_id: Unique order identifier. Will be returned in postback
        :param Optional[str] description: Description of payment
        :param Optional[PaymentType] type: Payment type. Onetime or multiple.
        If you select a one-time payment, you will not be able to pay a second time
        :param Optional[Currency] currency_in: Currency in which the invoice is paid.
        If not transferred, then the store currency is used
        :param Optional[bool] payer_pays_commission: Who pays the commission. 1 or 0
        :return dict: API Response
        """
        payload = {
            "amount": amount,
            "shop_id": self.shop_id
        }

        if order_id is not None:
            payload["order_id"] = order_id
        if description is not None:
            payload["description"] = description
        if type is not None:
            payload["type"] = type.value
        if currency_in is not None:
            payload["currency_in"] = currency_in.value
        if payer_pays_commission is not None:
            payload["payer_pays_commission"] = 1 if payer_pays_commission is True else 0

        return await self._send_request(
            endpoint="bill/create",
            method="POST",
            data=payload
        )

    async def bill_status(self, bill_id: int) -> dict:
        """
        Get bill status and related info
        :param int bill_id: Unique identifier of the bill
        :return dict: API Response
        """
        return await self._send_request(
            endpoint=f"bill/status?id={bill_id}",
            method="GET",
        )

    async def toggle_activity(self, bill_id: str, active: bool) -> dict:
        """
        Activate or deactivate the bill
        :param str bill_id:
        :param bool active:
        :return dict: API Response
        """
        payload = {"id": bill_id, "active": 1 if active is True else 0}
        return await self._send_request(
            method="POST",
            endpoint="bill/toggle_activity",
            data=payload
        )
