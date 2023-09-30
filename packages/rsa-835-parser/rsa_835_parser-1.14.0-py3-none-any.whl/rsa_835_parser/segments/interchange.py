""" Interchange Segment """

# Local Imports
from rsa_835_parser.elements.authorization_information_qualifier import (
    AuthorizationInformationQualifier,
)
from rsa_835_parser.elements.organization import Organization
from rsa_835_parser.elements.date import Date
from rsa_835_parser.elements.identifier import Identifier
from rsa_835_parser.segments.utilities import split_segment


class Interchange:
    # Iterchange Segment Class Definition
    """Interchange Segment Class"""
    identification = "ISA"

    identifier = Identifier()
    autorization_information_qualifier = AuthorizationInformationQualifier()
    sender = Organization()
    receiver = Organization()
    transimission_date = Date()

    def __init__(self, segment: str):
        self.segment = segment
        segment = split_segment(segment)

        self.identifier = segment[0]
        self.autorization_information_qualifier = segment[1]
        self.sender = segment[6]
        self.receiver = segment[8]
        self.transimission_date = segment[9] + segment[10]

    def __repr__(self) -> str:
        return "\n".join(str(item) for item in self.__dict__.items())


if __name__ == "__main__":
    pass
