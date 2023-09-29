from typing import Optional

from tikkie2._session import ApiSession, get_session
from tikkie2.v2.models import Refund


def create(
    *,
    payment_request_token: str,
    payment_token: str,
    description: str,
    amount_in_cents: int,
    reference_id: Optional[str] = None,
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[ApiSession] = None,
) -> Refund:
    """
    Creates a refund for a specific payment

    The maximum amount which can be refunded for a payment is the
    amount paid plus €25.00. The application must have payment request
    permission and the refund permission to complete this request.

    https://developer.abnamro.com/api-products/tikkie/reference-documentation#tag/Refund

    :param payment_request_token: Token identifying the payment request.
    :param payment_token: Token identifying one payment of a payment request
    :param description: Description of the payment request, which the payer or payers see.
    :param amount_in_cents: Amount in cents of the payment request (euros). If this value is not specified, an open payment request is created.
    :param reference_id: ID for the reference of the API consumer.
    :param app_token: The App Token generated in the Tikkie Business Portal.
    :param api_key: The API Key obtained from the ABN developer portal.
    :param session: An optional API session class. If not passed the global API session will be used
    """
    s = session if session else get_session()
    payload = {
        "description": description,
        "amountInCents": amount_in_cents,
    }
    if reference_id is not None:
        payload["referenceId"] = reference_id

    response = s.post(
        f"paymentrequests/{payment_request_token}/payments/{payment_token}/refunds",
        json=payload,
        app_token=app_token,
        api_key=api_key,
    )
    return Refund.parse_raw(response.content)


def get(
    *,
    payment_request_token: str,
    payment_token: str,
    refund_token: str,
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[ApiSession] = None,
) -> Refund:
    """
    Retrieves details of a specific refund based on a token value.
    The application must have payment request permission to complete
    this request.

    https://developer.abnamro.com/api-products/tikkie/reference-documentation#operation/getRefund

    :param payment_request_token: Token identifying the payment request.
    :param payment_token: Token identifying one payment of a payment request
    :param refund_token: Token identifying one refund of a payment.
    :param app_token: The App Token generated in the Tikkie Business Portal.
    :param api_key: The API Key obtained from the ABN developer portal.
    :param session: An optional API session class. If not passed the global API session will be used
    """
    s = session if session else get_session()
    response = s.get(
        f"paymentrequests/{payment_request_token}/payments/{payment_token}/refunds/{refund_token}",
        app_token=app_token,
        api_key=api_key,
    )
    return Refund.parse_raw(response.content)
