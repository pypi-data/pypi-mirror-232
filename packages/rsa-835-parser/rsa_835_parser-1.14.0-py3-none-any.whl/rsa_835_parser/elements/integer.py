""" Integer Element """
from typing import Optional, Union

from rsa_835_parser.elements import Element


class Integer(Element):
    """Integer Element Class"""

    def parser(self, value: str) -> Optional[Union[int, float]]:
        if value == "":
            return None

        try:
            return int(value)
        except ValueError:
            pass

        return value
