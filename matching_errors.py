"""Custom exceptions of the matching system (LostLink)."""


class MatchingError(Exception): pass
class InvalidMatchItemError(MatchingError): pass
class InvalidReportTypeError(MatchingError): pass
class InvalidThresholdError(MatchingError): pass
class InvalidConfigError(MatchingError): pass
class UnsortedDataError(MatchingError): pass
