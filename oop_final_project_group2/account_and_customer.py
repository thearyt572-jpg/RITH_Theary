import hashlib
from typing import List
from abc import ABC, abstractmethod
from datetime import datetime
from exceptions import *
ADMIN_KEY = "admin123"  # Admin key for unlocking accounts

class Account(ABC):
    """Base class for all account types with PIN protection"""
    
    def __init__(self, account_number: str, owner: 'Customer', initial_balance: float = 0.0):
        self.__account_number = account_number
        self.__balance = initial_balance
        self.__owner = owner
        self.__transactions = []
        self.__date_created = datetime.now()
        self.__requires_pin_for_withdrawal = True
        
    def deposit(self, amount: float, pin: str = None) -> None:
        """Deposit money into account (PIN optional for deposit)"""
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        self.__balance += amount
        self._log_transaction("DEPOSIT", amount)
        
    @abstractmethod
    def withdraw(self, amount: float, pin: str = None) -> None:
        """Abstract method - must be implemented by subclasses"""
        pass

    def transfer(self, target_account: 'Account', amount: float, pin: str = None) -> None:
        """Transfer money to another account"""
        # First check if we have sufficient funds
        if amount > self.__balance:
            if isinstance(self, CheckingAccount):
                if amount > (self.__balance + self.overdraft_limit):
                    raise InsufficientFundsError("Overdraft limit exceeded")
            else:
                raise InsufficientFundsError("Insufficient funds")
        
        # Check PIN for withdrawal if required
        if self.__requires_pin_for_withdrawal:
            if not pin:
                raise InvalidPINError("PIN required for withdrawal")
            if not self.__owner.verify_pin(pin):
                raise InvalidPINError("Invalid PIN for transfer")
        
        # Perform withdrawal and deposit
        self.withdraw(amount, pin)
        target_account.deposit(amount)
        self._log_transaction(f"TRANSFER to {target_account.account_number}", amount)
    
    def verify_owner_pin(self, pin: str) -> bool:
        """Verify owner's PIN"""
        return self.__owner.verify_pin(pin)
    
    def apply_monthly_charges_or_interest(self) -> None:
        """Default implementation (can be overridden)"""
        pass
    
    def get_statement(self) -> dict:
        """Get account statement"""
        return {
            "account_number": self.__account_number,
            "balance": self.__balance,
            "owner": self.__owner.name,
            "account_type": type(self).__name__.replace("Account", ""),
            "transactions": self.__transactions[-10:]  # Last 10 transactions
        }
    
    def _log_transaction(self, transaction_type: str, amount: float) -> None:
        """Log a transaction"""
        self.__transactions.append({
            "date": datetime.now(),
            "type": transaction_type,
            "amount": amount,
            "balance_after": self.__balance
        })
    
    # Protected method for derived classes to access balance
    def _get_balance(self) -> float:
        return self.__balance
    
    def _set_balance(self, amount: float) -> None:
        self.__balance = amount
    
    @property
    def account_number(self) -> str:
        return self.__account_number
    
    @property
    def balance(self) -> float:
        return self.__balance
    
    @property
    def owner(self):
        return self.__owner
    
    @property
    def transactions(self):
        return self.__transactions.copy()


class SavingsAccount(Account):
    """Savings account with interest calculation"""
    
    def __init__(self, account_number: str, owner: 'Customer', 
                 initial_balance: float = 0.0, interest_rate: float = 0.02):
        super().__init__(account_number, owner, initial_balance)
        self.__interest_rate = interest_rate
        self.__minimum_balance = 100.0
        
    def withdraw(self, amount: float, pin: str = None) -> None:
        """Withdraw from savings account with PIN verification"""
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        
        # Check PIN
        if not pin:
            raise InvalidPINError("PIN required for withdrawal")
        if not self.verify_owner_pin(pin):
            raise InvalidPINError("Invalid PIN for withdrawal")
        
        # Check minimum balance
        if self.balance - amount < self.__minimum_balance:
            raise InsufficientFundsError(
                f"Cannot go below minimum balance of ${self.__minimum_balance}"
            )
        
        # Perform withdrawal
        self._set_balance(self._get_balance() - amount)
        self._log_transaction("WITHDRAW", amount)
    
    def apply_monthly_charges_or_interest(self) -> None:
        """Calculate and apply monthly interest"""
        if self._get_balance() >= self.__minimum_balance:
            monthly_interest = (self._get_balance() * self.__interest_rate) / 12
            self._set_balance(self._get_balance() + monthly_interest)
            self._log_transaction("INTEREST", monthly_interest)


class CheckingAccount(Account):
    """Checking account with overdraft facility"""
    
    def __init__(self, account_number: str, owner: 'Customer', 
                 initial_balance: float = 0.0, overdraft_limit: float = 500.0):
        super().__init__(account_number, owner, initial_balance)
        self.__overdraft_limit = overdraft_limit
        self.__overdraft_fee = 25.0
    
    def withdraw(self, amount: float, pin: str = None) -> None:
        """Withdraw from checking account with overdraft protection"""
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        
        # Check PIN
        if not pin:
            raise InvalidPINError("PIN required for withdrawal")
        if not self.verify_owner_pin(pin):
            raise InvalidPINError("Invalid PIN for withdrawal")
        
        # Check overdraft limit
        if self.balance - amount < -self.__overdraft_limit:
            raise InsufficientFundsError(
                f"Cannot exceed overdraft limit of ${self.__overdraft_limit}"
            )
        
        # Perform withdrawal
        self._set_balance(self._get_balance() - amount)
        self._log_transaction("WITHDRAW", amount)
    
    def apply_monthly_charges_or_interest(self) -> None:
        """Apply overdraft fees if balance is negative"""
        if self._get_balance() < 0:
            self._set_balance(self._get_balance() - self.__overdraft_fee)
            self._log_transaction("OVERDRAFT_FEE", -self.__overdraft_fee)
    
    @property
    def overdraft_limit(self) -> float:
        return self.__overdraft_limit


class Customer:
    """Manages multiple accounts for a single customer with PIN authentication"""
    
    def __init__(self, customer_id: str, name: str, email: str, pin: str):
        self.__customer_id = customer_id
        self.__name = name
        self.__email = email
        self.__pin_hash = self.__hash_pin(pin)
        self.__accounts: List[Account] = []
        self.__failed_attempts = 0
        self.__locked = False
    
    def __hash_pin(self, pin: str) -> str:
        """Hash PIN for security"""
        return hashlib.sha256(pin.encode()).hexdigest()
    
    def verify_pin(self, pin: str) -> bool:
        """Verify PIN with hash"""
        if self.__locked:
            raise AccountLockedError("Account is locked due to too many failed attempts")
        
        if self.__hash_pin(pin) == self.__pin_hash:
            self.__failed_attempts = 0
            return True
        else:
            self.__failed_attempts += 1
            if self.__failed_attempts >= 3:
                self.__locked = True
                raise AccountLockedError("Account locked! Too many failed attempts")
            return False
    
    def reset_pin(self, old_pin: str, new_pin: str) -> bool:
        """Reset customer PIN"""
        if self.verify_pin(old_pin):
            self.__pin_hash = self.__hash_pin(new_pin)
            return True
        return False
    
    def unlock_account(self, admin_key: str = "ADMIN123") -> bool:
        """Unlock account (simplified admin override for demo)"""
        if admin_key == ADMIN_KEY:
            self.__locked = False
            self.__failed_attempts = 0
            return True
        return False
    
    def add_account(self, account: Account) -> None:
        """Add an account to customer's portfolio"""
        if account.owner != self:
            raise ValueError("Account does not belong to this customer")
        self.__accounts.append(account)
    
    def get_account(self, account_number: str) -> Account:
        """Retrieve a specific account by number"""
        for account in self.__accounts:
            if account.account_number == account_number:
                return account
        raise AccountNotFoundError(f"Account {account_number} not found")
    
    def get_total_balance(self) -> float:
        """Calculate total balance across all accounts"""
        return sum(account.balance for account in self.__accounts)
    
    def get_accounts_summary(self) -> List[dict]:
        """Get summary of all accounts"""
        return [{
            "account_number": acc.account_number,
            "type": type(acc).__name__,
            "balance": acc.balance
        } for acc in self.__accounts]
    
    @property
    def customer_id(self) -> str:
        return self.__customer_id
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def email(self) -> str:
        return self.__email
    
    @property
    def accounts(self) -> List[Account]:
        return self.__accounts.copy()
    
    @property
    def is_locked(self) -> bool:
        return self.__locked
    
    @property
    def failed_attempts(self) -> int:
        return self.__failed_attempts