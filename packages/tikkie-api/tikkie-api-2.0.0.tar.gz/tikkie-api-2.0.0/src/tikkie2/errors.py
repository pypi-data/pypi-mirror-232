import logging
from typing import Any

from requests import Response


class BaseError(Exception):
    response: Response
    code: str
    message: str
    reference: str
    trace_id: str
    status: int

    def __init__(
        self,
        message: str,
        *,
        response: Response,
        code: str,
        reference: str,
        trace_id: str,
        status: int,
    ):
        super().__init__(message)
        self.response = response
        self.code = code
        self.reference = reference
        self.trace_id = trace_id
        self.status = status

    @classmethod
    def from_response(cls, response: Any) -> "BaseError":
        payload = response.json()

        # Tikkie returns multiple errors, but that makes for an weird error
        # handling system. So let's just use the first error
        error = payload["errors"][0]

        for ErrorClass in BaseError.__subclasses__():
            if error["code"] == ErrorClass.code:
                return ErrorClass(
                    error["message"],
                    response=response,
                    code=error["code"],
                    reference=error["reference"],
                    trace_id=error["traceId"],
                    status=error["status"],
                )

        # Not implemented exception found, just raise the base class
        logging.warning(
            f"Unknow Tikkie response found: code={error['code']!r} message={error['message']!r}"
        )
        return cls(
            error["message"],
            response=response,
            code=error["code"],
            reference=error["reference"],
            trace_id=error["traceId"],
            status=error["status"],
        )


class AmountChangeableInvalid(BaseError):
    code = "AMOUNT_CHANGEABLE_INVALID"


class AmountChangeableParametersInvalid(BaseError):
    code = "AMOUNT_CHANGEABLE_PARAMETERS_INVALID"


class AmountInCentsInvalid(BaseError):
    code = "AMOUNT_IN_CENTS_INVALID"


class AmountInCentsMissing(BaseError):
    code = "AMOUNT_IN_CENTS_MISSING"


class AppTokenAlreadyInUse(BaseError):
    code = "APP_TOKEN_ALREADY_IN_USE"


class AppTokenDisabled(BaseError):
    code = "APP_TOKEN_DISABLED"


class AppTokenInvalid(BaseError):
    code = "APP_TOKEN_INVALID"


class BundleIDInvalid(BaseError):
    code = "BUNDLE_ID_INVALID"


class BundleNotFound(BaseError):
    code = "BUNDLE_NOT_FOUND"


class BundledPayoutNotEnabled(BaseError):
    code = "BUNDLED_PAYOUT_NOT_ENABLED"


class DescriptionInvalid(BaseError):
    code = "DESCRIPTION_INVALID"


class DescriptionMaxLengthExceeded(BaseError):
    code = "DESCRIPTION_MAX_LENGTH_EXCEEDED"


class DescriptionMissing(BaseError):
    code = "DESCRIPTION_MISSING"


class ExpiryDateInvalid(BaseError):
    code = "EXPIRY_DATE_INVALID"


class ExpiryDateNotAllowed(BaseError):
    code = "EXPIRY_DATE_NOT_ALLOWED"


class ExpiryDateTimeInvalid(BaseError):
    code = "EXPIRY_DATE_TIME_INVALID"


class ExpiryDateTimeMissing(BaseError):
    code = "EXPIRY_DATE_TIME_MISSING"


class ExpiryDateTimeNotAllowed(BaseError):
    code = "EXPIRY_DATE_TIME_NOT_ALLOWED"


class FromDateTimeInvalid(BaseError):
    code = "FROM_DATE_TIME_INVALID"


class IdealQrNotFound(BaseError):
    code = "IDEAL_QR_NOT_FOUND"


class IdealqrForbidden(BaseError):
    code = "IDEALQR_FORBIDDEN"


class ImageSizeInvalid(BaseError):
    code = "IMAGE_SIZE_INVALID"


class ImageSizeTooLarge(BaseError):
    code = "IMAGE_SIZE_TOO_LARGE"


class ImageSizeTooSmall(BaseError):
    code = "IMAGE_SIZE_TOO_SMALL"


class InternalServerError(BaseError):
    code = "INTERNAL_SERVER_ERROR"


class MaxAmountInCentsInvalid(BaseError):
    code = "MAX_AMOUNT_IN_CENTS_INVALID"


class MaxAmountInCentsMissing(BaseError):
    code = "MAX_AMOUNT_IN_CENTS_MISSING"


class MinAmountInCentsInvalid(BaseError):
    code = "MIN_AMOUNT_IN_CENTS_INVALID"


class PageNumberInvalid(BaseError):
    code = "PAGE_NUMBER_INVALID"


class PageNumberMissing(BaseError):
    code = "PAGE_NUMBER_MISSING"


class PageSizeInvalid(BaseError):
    code = "PAGE_SIZE_INVALID"


class PageSizeMissing(BaseError):
    code = "PAGE_SIZE_MISSING"


class PageSizeTooLarge(BaseError):
    code = "PAGE_SIZE_TOO_LARGE"


class PaymentNotFound(BaseError):
    code = "PAYMENT_NOT_FOUND"


class PaymentRequestForbidden(BaseError):
    code = "PAYMENT_REQUEST_FORBIDDEN"


class PaymentRequestMaxAmountExceeded(BaseError):
    code = "PAYMENT_REQUEST_MAX_AMOUNT_EXCEEDED"


class PaymentRequestNotFound(BaseError):
    code = "PAYMENT_REQUEST_NOT_FOUND"


class PaymentRequestTokenInvalid(BaseError):
    code = "PAYMENT_REQUEST_TOKEN_INVALID"


class PaymentTokenInvalid(BaseError):
    code = "PAYMENT_TOKEN_INVALID"


class QrIDInvalid(BaseError):
    code = "QR_ID_INVALID"


class ReferenceIDInvalid(BaseError):
    code = "REFERENCE_ID_INVALID"


class ReferenceIDMaxLengthExceeded(BaseError):
    code = "REFERENCE_ID_MAX_LENGTH_EXCEEDED"


class RefundAmountIsTooHigh(BaseError):
    code = "REFUND_AMOUNT_IS_TOO_HIGH"


class RefundForbidden(BaseError):
    code = "REFUND_FORBIDDEN"


class RefundNotFound(BaseError):
    code = "REFUND_NOT_FOUND"


class RefundTokenInvalid(BaseError):
    code = "REFUND_TOKEN_INVALID"


class SinglePayInvalid(BaseError):
    code = "SINGLE_PAY_INVALID"


class TimeRangeInvalid(BaseError):
    code = "TIME_RANGE_INVALID"


class ToDateTimeInvalid(BaseError):
    code = "TO_DATE_TIME_INVALID"


class TransactionsForbidden(BaseError):
    code = "TRANSACTIONS_FORBIDDEN"


class URLDisallowed(BaseError):
    code = "URL_DISALLOWED"


class URLInvalid(BaseError):
    code = "URL_INVALID"


class URLMissing(BaseError):
    code = "URL_MISSING"
