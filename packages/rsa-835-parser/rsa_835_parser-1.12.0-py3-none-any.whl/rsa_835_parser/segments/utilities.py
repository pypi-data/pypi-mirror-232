""" Utilities for working with segments """
from typing import List, Optional

## from pytz import NonExistentTimeError


def split_segment(segment: str) -> List[str]:
    """different payers use different characters to delineate elements"""
    asterisk = "*"
    pipe = "|"

    asterisk_segment_count = len(segment.split(asterisk))
    pipe_segment_count = len(segment.split(pipe))

    if asterisk_segment_count > pipe_segment_count:
        return segment.split(asterisk)
    else:
        return segment.split(pipe)


# end def split_segment


def find_identifier(segment) -> str:
    """find the identifier for the segment"""
    segment = split_segment(segment)
    return segment[0]


def get_element(segment: list[str], index: int, default=None) -> Optional[str]:
    """get the element at the given index"""
    element = default
    if index < len(segment):
        element = segment[index]

    return element
