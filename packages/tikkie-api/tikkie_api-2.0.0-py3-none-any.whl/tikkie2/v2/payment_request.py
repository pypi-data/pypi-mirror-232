from datetime import date, datetime
from typing import Optional

from tikkie2._session import ApiSession, get_session
from tikkie2._util import JsonDict, format_date
from tikkie2.v2.models import GetAllPaymentRequestsResponse, PaymentRequest


def create(
    *,
    description: str,
    amount_in_cents: Optional[int] = None,
    expiry_date: Optional[date] = None,
    reference_id: Optional[str] = None,
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[ApiSession] = None,
) -> PaymentRequest:
    """
    https://developer.abnamro.com/api-products/tikkie/reference-documentation#operation/createPaymentRequest

    :param description: Description of the payment request, which the payer or payers see.
    :param amount_in_cents: Amount in cents of the payment request (euros). If this value is not specified, an open payment request is created.
    :param expiry_date: Date after the payment request expires and cannot be paid
    :param reference_id: ID for the reference of the API consumer.
    :param app_token: The App Token generated in the Tikkie Business Portal.
    :param api_key: The API Key obtained from the ABN developer portal.
    :param session: An optional API session class. If not passed the global API session will be used
    """
    s = session if session else get_session()
    payload: JsonDict = {"description": description}
    if amount_in_cents is not None:
        payload["amountInCents"] = amount_in_cents
    if expiry_date is not None:
        payload["expiryDate"] = format_date(expiry_date)
    if reference_id is not None:
        payload["referenceId"] = reference_id

    response = s.post("paymentrequests", json=payload, app_token=app_token, api_key=api_key)
    return PaymentRequest.parse_raw(response.content)


def get(
    payment_request_token: str,
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[ApiSession] = None,
) -> PaymentRequest:
    """
    https://developer.abnamro.com/api-products/tikkie/reference-documentation#operation/getPaymentRequest

    :param payment_request_token: Token identifying the payment request.
    :param app_token: The App Token generated in the Tikkie Business Portal.
    :param api_key: The API Key obtained from the ABN developer portal.
    :param session: An optional API session class. If not passed the global API session will be used
    """
    s = session if session else get_session()
    response = s.get(
        f"paymentrequests/{payment_request_token}",
        app_token=app_token,
        api_key=api_key,
    )
    return PaymentRequest.parse_raw(response.content)


def get_all(
    *,
    page_size: int,
    page_number: int,
    from_date_time: Optional[datetime] = None,
    to_date_time: Optional[datetime] = None,
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[ApiSession] = None,
) -> GetAllPaymentRequestsResponse:
    """
    https://developer.abnamro.com/api-products/tikkie/reference-documentation#operation/getPaymentRequestList

    :param page_size: Number of the page to be returned.
    :param page_number: Number of items on a page.
    :param from_date_time:The time you start searching for items. Refers to the creation date for payment requests and iDeal QRs, and refers to the bundle date for transaction bundles.
    :param to_date_time: The time you stop searching for items. Refers to the creation date for payment requests and iDeal QRs, and refers to the bundle date for transaction bundles.
    :param app_token: The App Token generated in the Tikkie Business Portal.
    :param api_key: The API Key obtained from the ABN developer portal.
    :param session: An optional API session class. If not passed the global API session will be used
    """
    s = session if session else get_session()
    params: JsonDict = {
        "pageSize": page_size,
        "pageNumber": page_number,
    }
    if from_date_time is not None:
        params["fromDateTime"] = from_date_time
    if to_date_time is not None:
        params["toDateTime"] = to_date_time

    response = s.get(
        "paymentrequests",
        params=params,
        app_token=app_token,
        api_key=api_key,
    )
    return GetAllPaymentRequestsResponse.parse_raw(response.content)
