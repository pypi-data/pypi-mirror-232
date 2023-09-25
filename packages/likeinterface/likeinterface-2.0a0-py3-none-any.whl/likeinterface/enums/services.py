from enum import Enum


class Services(str, Enum):
    AUTH = "auth"
    BALANCE = "balance"
    COLLECTION = "collection"
    FILE = "file"
    LIKE = "like"
