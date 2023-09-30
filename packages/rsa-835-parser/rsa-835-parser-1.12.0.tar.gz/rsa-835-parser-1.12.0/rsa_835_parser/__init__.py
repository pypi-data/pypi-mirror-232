""" rsa-835-parser package """
# Importing standard libraries
import os
from tkinter import E
from typing import List
from warnings import warn


# Local imports
from rsa_835_parser.transaction_set.transaction_set import TransactionSet
from rsa_835_parser.transaction_set.transaction_sets import TransactionSets

def parse(path: str, debug: bool = False) -> TransactionSets:
    """Parse EDI 835 files from a directory or a single file path"""
    if path[0] == "~":
        path = os.path.expanduser(path)

    transaction_sets = []

    if os.path.isdir(path):
        files = _find_edi_835_files(path)
        for file in files:
            file_path = f"{path}/{file}"
            if debug:
                transaction_set = TransactionSet.build(file_path)
                transaction_sets.append(transaction_set)
            else:
                try:
                    transaction_set = TransactionSet.build(file_path)
                    transaction_sets.append(transaction_set)
                except (FileNotFoundError, ValueError):
                    warn(f"Failed to build a transaction set from {file_path}")
    else:
        transaction_set = TransactionSet.build(path)
        transaction_sets.append(transaction_set)

    return TransactionSets(transaction_sets)


def _find_edi_835_files(path: str) -> List[str]:
    files = []
    for file in os.listdir(path):
        # Sometime EDI_835 files come with extension .txt and other with .835
        if file.endswith(".txt") or file.endswith(".835"):
            files.append(file)

    return files


if __name__ == "__main__":
    pass
