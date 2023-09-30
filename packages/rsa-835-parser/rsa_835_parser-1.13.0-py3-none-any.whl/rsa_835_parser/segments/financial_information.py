""" Financial Information segment """
from rsa_835_parser.elements.identifier import Identifier
from rsa_835_parser.elements.payment_method import PaymentMethod
from rsa_835_parser.elements.dollars import Dollars
from rsa_835_parser.elements.integer import Integer
from rsa_835_parser.elements.date import Date
from rsa_835_parser.segments.utilities import split_segment


class FinancialInformation:
    """Financial Information Class segment"""

    identification = "BPR"

    identifier = Identifier()
    amount_paid = Dollars()
    payment_method = PaymentMethod()
    rounting_number = Integer()
    transaction_date = Date()

    def __init__(self, segment: str):
        self.segment = segment
        segment = split_segment(segment)

        self.identifier = segment[0]
        self.amount_paid = segment[2]
        self.payment_method = segment[4]
        self.rounting_number = segment[13]
        self.transaction_date = segment[16]

    def __repr__(self) -> str:
        return "\n".join(str(item) for item in self.__dict__.items())


# End-of-Class (FinancialInformation)
if __name__ == "__main__":
    pass

# End-of-file (EOF)
