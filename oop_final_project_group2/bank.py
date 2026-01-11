from typing import Dict, List
from exceptions import *
from account_and_customer import *

class Bank:
    """Manages collections of customers and implements transaction logic"""
    
    def __init__(self, bank_name: str):
        self.__bank_name = bank_name
        self.__customers: Dict[str, Customer] = {}
        self.__accounts: Dict[str, Account] = {}
    
    def add_customer(self, customer: Customer) -> None:
        """Add a new customer to the bank"""
        if customer.customer_id in self.__customers:
            raise ValueError(f"Customer {customer.customer_id} already exists")
        self.__customers[customer.customer_id] = customer
    
    def get_customer(self, customer_id: str) -> Customer:
        """Retrieve customer by ID"""
        if customer_id not in self.__customers:
            raise ValueError(f"Customer {customer_id} not found")
        return self.__customers[customer_id]
    
    def create_account(self, customer_id: str, account_type: str, 
                       initial_balance: float = 0.0, **kwargs) -> Account:
        """Create a new account for a customer"""
        customer = self.get_customer(customer_id)
        
        account_number = f"{customer_id}-{len(customer.accounts) + 1:03d}"
        
        if account_type.upper() == "SAVINGS":
            account = SavingsAccount(
                account_number, customer, initial_balance, 
                kwargs.get('interest_rate', 0.02)
            )
        elif account_type.upper() == "CHECKING":
            account = CheckingAccount(
                account_number, customer, initial_balance,
                kwargs.get('overdraft_limit', 500.0)
            )
        else:
            raise ValueError(f"Unknown account type: {account_type}")
        
        customer.add_account(account)
        self.__accounts[account_number] = account
        return account
    
    def get_account(self, account_number: str) -> Account:
        """Retrieve account by number"""
        if account_number not in self.__accounts:
            raise AccountNotFoundError(f"Account {account_number} not found")
        return self.__accounts[account_number]
    
    def transfer(self, from_account_num: str, to_account_num: str, amount: float, pin: str) -> None:
        """Transfer money between accounts with PIN verification"""
        from_account = self.get_account(from_account_num)
        to_account = self.get_account(to_account_num)
        
        try:
            from_account.transfer(to_account, amount, pin)
            print(f"Transfer successful: {amount} from {from_account_num} to {to_account_num}")
        except (InsufficientFundsError, InvalidPINError) as e:
            print(f"Transfer failed: {e}")
            raise
    
    def apply_monthly_updates(self) -> None:
        """Apply monthly charges/interest to all accounts"""
        for account in self.__accounts.values():
            account.apply_monthly_charges_or_interest()
    
    def get_bank_summary(self) -> dict:
        """Get summary of bank's status"""
        total_customers = len(self.__customers)
        total_accounts = len(self.__accounts)
        total_deposits = sum(acc.balance for acc in self.__accounts.values())
        
        return {
            "bank_name": self.__bank_name,
            "total_customers": total_customers,
            "total_accounts": total_accounts,
            "total_deposits": total_deposits,
            "accounts_by_type": self._get_accounts_by_type()
        }
    
    def _get_accounts_by_type(self) -> Dict[str, int]:
        """Private method to count accounts by type"""
        counts = {"SavingsAccount": 0, "CheckingAccount": 0}
        for account in self.__accounts.values():
            counts[type(account).__name__] += 1
        return counts
    
    @property
    def bank_name(self) -> str:
        return self.__bank_name