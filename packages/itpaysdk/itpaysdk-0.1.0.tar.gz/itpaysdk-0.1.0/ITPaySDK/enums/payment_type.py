from enum import Enum


class PaymentType(Enum):
    one_time = "normal"
    multiple_times = "multi"
