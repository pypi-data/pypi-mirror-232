""" Dollars """
from typing import Optional

from rsa_835_parser.elements import Element

class Dollars(Element):
    """ Dollars Class """

    def parser(self, value: str) -> Optional[float]:
        if value != "":
            return float(value)
