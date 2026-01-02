# Requirements:
#  - User
#  - Payment type - CC or UPI
#  - Transaction
#  - Payment processor - CC or UPI
#  - Payment service
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import uuid


class CreditCard:
    """Class representing a credit payment"""

    def __init__(
        self, card_number: str, cvv: str, expiration_date: str, name_on_card: str
    ):
        self.card_number = card_number
        self.cvv = cvv
        self.expiration_date = expiration_date
        self.name_on_card = name_on_card


class UPI:
    """Class representing a upi type"""

    def __init__(self, upi_id: str):
        self.upi_id = upi_id


class PaymentType(Enum):
    """Class representing a payment method type"""

    CREDIT_CARD = "credit_card"
    UPI = "upi"


class PaymentStatus(Enum):
    """Class representing a payment status"""

    INITIATED = "initiated"
    PROCESSING = "processing"
    SUCCESS = "SUCCESS"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundStatus(Enum):
    """Class representing a refund status"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "SUCCESS"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User:
    """Class representing a user info"""

    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name


# class Transaction:
class Transaction:
    """Class representing a transaction"""

    def __init__(
        self,
        transaction_id: str | None = None,
        amount: float = 0.0,
        payment_type: PaymentType | None = None,
        status: PaymentStatus | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.amount = amount
        self.payment_type = payment_type
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()


# class Refund:
class Refund:
    """class showing refund"""

    def __init__(
        self,
        refund_id: str,
        amount: int,
        payment_type: PaymentType | None,
        status: RefundStatus,
    ):
        self.refund_id = refund_id
        self.amount = amount
        self.payment_type = payment_type
        self.status = status


# -----


class PaymentProcessor(ABC):
    """Class representing a payment processor"""

    def __init__(self):
        pass

    @abstractmethod
    def validate_payment(self, payment_type: PaymentType, method: UPI | CreditCard):
        pass


class CreditCardProcessor(PaymentProcessor):
    def validate_payment(self, payment_type: PaymentType, method: CreditCard) -> bool:
        return payment_type == PaymentType.CREDIT_CARD and is_valid_credit_card(
            method.card_number
        )


class UPIProcessor(PaymentProcessor):
    """Class representing a upi payment"""

    def validate_payment(self, payment_type: PaymentType, method: UPI) -> bool:
        return payment_type == PaymentType.UPI and is_valid_upi(method.upi_id)


class PaymentService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor

    def process_payment(
        self, transaction: Transaction, method: CreditCard | UPI
    ) -> Transaction | bool:
        if self.payment_processor.validate_payment(transaction.payment_type, method):
            processed_transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                amount=transaction.amount,
                payment_type=transaction.payment_type,
                status=PaymentStatus.SUCCESS,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            return processed_transaction
        return False


# Util methods
def is_valid_credit_card(card_number: str) -> bool:
    digits = [int(d) for d in card_number if d.isdigit()]
    checksum = 0
    reverse_digits = digits[::-1]

    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    return checksum % 10 == 0


def is_valid_upi(upi_id: str) -> bool:
    return "@" in upi_id and len(upi_id) >= 5


if __name__ == "__main__":
    credit_card_processor = CreditCardProcessor()
    upi_processor = UPIProcessor()
    payment_service = PaymentService(credit_card_processor)
    result = payment_service.process_payment(
        Transaction(
            amount=100,
            payment_type=PaymentType.CREDIT_CARD,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        CreditCard(
            card_number="4539148803436467",
            cvv="123",
            expiration_date="12/2025",
            name_on_card="John Doe",
        ),
    )
    if result:
        print(f"Transaction ID: {result.transaction_id}")
        print(f"Amount: {result.amount}")
        print(f"Status: {result.status}")
    else:
        print("Payment processing failed")
