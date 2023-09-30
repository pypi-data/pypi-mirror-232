from enum import StrEnum


class Status(StrEnum):
    PASSED = "PASSED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    YET_TO_CALCULATE = "YET_TO_CALC"  # needs to be updated by our server to either passed or failed
    # yet_to_calc is mostly seen for the suite


class SuiteType(StrEnum):
    TEST = "TEST"
    SUITE = "SUITE"


class AttachmentType(StrEnum):
    LABEL = "LABEL"
    ENV = "ENV"
    IMAGE = "IMAGE"
    CONFIG = "CONFIG"
    VIDEO = "VIDEO"
    ERROR = "ERROR"


class PrunedRecords(StrEnum):
    RUN = "RUN"
