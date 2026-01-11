class InsufficientFundsError(Exception):
    """Raised when account has insufficient funds for withdrawal"""
    pass

class InvalidAmountError(Exception):
    """Raised when transaction amount is invalid"""
    pass

class AccountNotFoundError(Exception):
    """Raised when account is not found"""
    pass

class InvalidPINError(Exception):
    """Raised when PIN is incorrect"""
    pass

class AccountLockedError(Exception):
    """Raised when account is locked due to too many failed attempts"""
    pass