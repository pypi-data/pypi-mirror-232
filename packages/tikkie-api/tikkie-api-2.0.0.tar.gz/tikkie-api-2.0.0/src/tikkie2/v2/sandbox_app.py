from typing import Optional

from tikkie2._session import ApiSession, get_session
from tikkie2.v2.models import CreateSandboxApplicationResponse


def create_application(
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[ApiSession] = None,
) -> CreateSandboxApplicationResponse:
    """
    Creates an app in the sandbox for you to use with this API. This
    operation does not work in the production environment.

    https://developer.abnamro.com/api-products/tikkie/reference-documentation#tag/Sandbox-app

    :param app_token: The App Token generated in the Tikkie Business Portal.
    :param api_key: The API Key obtained from the ABN developer portal.
    :param session: An optional API session class. If not passed the global API session will be used
    """
    s = session if session else get_session()
    response = s.post(
        "sandboxapps",
        app_token=app_token,
        api_key=api_key,
    )
    return CreateSandboxApplicationResponse.parse_raw(response.content)
