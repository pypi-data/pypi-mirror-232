from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field

from tikkie2._util import CamelCaseModel


class PaymentRequestStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    MAX_YIELD_REACHED = "MAX_YIELD_REACHED"
    MAX_SUCCESSFUL_PAYMENTS_REACHED = "MAX_SUCCESSFUL_PAYMENTS_REACHED"


class PaymentRequest(CamelCaseModel):
    payment_request_token: str
    description: str
    url: str
    expiry_date: date
    created_date_time: datetime
    status: PaymentRequestStatus
    number_of_payments: int
    total_amount_paid_in_cents: int
    amount_in_cents: Optional[int] = None
    reference_id: Optional[str] = None


class GetAllPaymentRequestsResponse(CamelCaseModel):
    payment_requests: List[PaymentRequest]
    total_element_count: int


class Refund(CamelCaseModel):
    refund_token: str
    amount_in_cents: int
    description: str
    created_date_time: datetime
    status: str  # TODO: Fill all statuses (PENDING, ?)
    reference_id: Optional[str] = None


class Payment(CamelCaseModel):
    payment_token: str
    tikkie_id: int
    counter_party_name: str
    counter_party_account_number: str
    amount_in_cents: int
    description: str
    created_date_time: datetime
    refunds: List[Refund]


class GetAllPaymentsResponse(CamelCaseModel):
    payments: List[Payment]
    total_element_count: int


class SubscribeResponse(CamelCaseModel):
    subscription_id: str


class CreateSandboxApplicationResponse(CamelCaseModel):
    app_token: str


class File(CamelCaseModel):
    type: str
    url: str


class Bundle(CamelCaseModel):
    bundle_id: str
    reference: str
    files: List[File]
    start_date_time: datetime
    end_date_time: datetime


class GetAllBundlesResponse(CamelCaseModel):
    bundles: List[Bundle]
    total_element_count: int


class IdealQr(CamelCaseModel):
    qr_id: str
    url: str
    description: str
    amount_changeable: bool
    created_date_time: datetime
    expiry_date_time: datetime
    single_pay: bool
    number_of_payments: int
    total_amount_paid_in_cents: int
    status: str  # TODO: Find all statuses (OPEN, ?)
    image_size: int
    reference_id: Optional[str] = None
    amount_in_cents: Optional[int] = None
    max_amount_in_cents: Optional[int] = None
    min_amount_in_cents: Optional[int] = None


class GetAllIdealQrResponse(CamelCaseModel):
    ideal_qrs: List[IdealQr] = Field(None, alias="idealQRs")
    total_element_count: int


class IdealQrPayment(CamelCaseModel):
    payment_token: str
    tikkie_id: int
    counter_party_name: str
    counter_party_account_number: str
    amount_in_cents: int
    description: str
    created_date_time: datetime


class GetAllIdealQrPaymentsResponse(CamelCaseModel):
    payments: List[IdealQrPayment]
    total_element_count: int
