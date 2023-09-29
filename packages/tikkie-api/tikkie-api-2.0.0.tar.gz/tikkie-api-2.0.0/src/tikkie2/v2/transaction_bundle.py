from datetime import datetime
from typing import Optional

from tikkie2._session import ApiSession, get_session
from tikkie2._util import JsonDict
from tikkie2.v2.models import Bundle, GetAllBundlesResponse


def get(
    bundle_id: str,
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[ApiSession] = None,
) -> Bundle:
    """
    Retrieves a specific bundle based on a bundle identifier. The
    application must have transactions permission to complete this
    request.

    https://developer.abnamro.com/api-products/tikkie/reference-documentation#operation/getBundle

    :param bundle_id: Identifier for the bundle.
    :param app_token: The App Token generated in the Tikkie Business Portal.
    :param api_key: The API Key obtained from the ABN developer portal.
    :param session: An optional API session class. If not passed the global API session will be used
    """
    s = session if session else get_session()
    response = s.get(
        f"transactionbundles/{bundle_id}",
        app_token=app_token,
        api_key=api_key,
    )
    return Bundle.parse_raw(response.content)


def get_all(
    *,
    page_size: int,
    page_number: int,
    from_date_time: Optional[datetime] = None,
    to_date_time: Optional[datetime] = None,
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[ApiSession] = None,
) -> GetAllBundlesResponse:
    """
    Retrieves a list of bundles based on the parameters provided. The
    application must have transactions permission to complete this request.

    https://developer.abnamro.com/api-products/tikkie/reference-documentation#operation/getBundleList

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
        "transactionbundles",
        params=params,
        app_token=app_token,
        api_key=api_key,
    )
    return GetAllBundlesResponse.parse_raw(response.content)
