import hashlib
import getpass
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from account_and_customer import *
from exceptions import *
from bank import *
# ==================== CONSTANTS ====================

EMPLOYEE_PIN = "1111"  # Universal employee PIN
ADMIN_KEY = "admin123"  # Admin key for unlocking accounts

# ==================== CLI INTERFACE ====================

def customer_login_flow(bank):
    """Handle customer login and subsequent operations"""
    
    print("\n" + "="*50)
    print("CUSTOMER LOGIN")
    print("="*50)
    
    customer = None
    attempts = 0
    
    while attempts < 3:
        customer_id = input("Customer ID: ").strip()
        
        try:
            customer = bank.get_customer(customer_id)
            
            if customer.is_locked:
                print("✗ Account is locked! Contact employee for unlock.")
                input("\nPress Enter to return to main menu...")
                return
            
            pin = getpass.getpass(f"PIN for {customer.name}: ")
            
            if customer.verify_pin(pin):
                print(f"\n✓ Welcome, {customer.name}!")
                customer_menu(bank, customer)
                return
            else:
                attempts += 1
                remaining = 3 - attempts
                print(f"✗ Invalid PIN. {remaining} attempt(s) remaining.")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            break
    
    if attempts >= 3:
        print("✗ Too many failed attempts. Account may be locked.")
    input("\nPress Enter to return to main menu...")

def employee_login_flow(bank):
    """Handle employee login with universal PIN"""
    
    print("\n" + "="*50)
    print("EMPLOYEE LOGIN")
    print("="*50)
    
    attempts = 0
    while attempts < 3:
        pin = getpass.getpass("Employee PIN: ")
        
        if pin == EMPLOYEE_PIN:
            print("\n✓ Employee access granted!")
            employee_menu(bank)
            return
        else:
            attempts += 1
            remaining = 3 - attempts
            print(f"✗ Invalid PIN. {remaining} attempt(s) remaining.")
    
    print("✗ Too many failed attempts. Access denied.")
    input("\nPress Enter to return to main menu...")

def sign_up_flow(bank):
    """Handle new customer registration"""
    
    print("\n" + "="*50)
    print("NEW CUSTOMER REGISTRATION")
    print("="*50)
    
    customer_id = input("Choose Customer ID: ").strip()
    name = input("Full Name: ").strip()
    email = input("Email: ").strip()
    
    while True:
        pin1 = getpass.getpass("Create 4-digit PIN: ").strip()
        if len(pin1) != 4 or not pin1.isdigit():
            print("PIN must be 4 digits!")
            continue
        
        pin2 = getpass.getpass("Confirm PIN: ").strip()
        if pin1 == pin2:
            break
        else:
            print("PINs don't match! Try again.")
    
    try:
        customer = Customer(customer_id, name, email, pin1)
        bank.add_customer(customer)
        print(f"\n✓ Registration successful!")
        print(f"  Customer: {name} (ID: {customer_id})")
        print(f"  Please login with your credentials.")
        
        create_now = input("\nCreate an account now? (yes/no): ").strip().lower()
        if create_now in ['yes', 'y']:
            create_account_flow(bank, customer)
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    input("\nPress Enter to return to main menu...")

def customer_menu(bank, customer):
    """Menu for authenticated customers"""
    
    customer = bank.get_customer(customer.customer_id)
    
    while True:
        print("\n" + "="*50)
        print(f"CUSTOMER MENU - Welcome, {customer.name}")
        print("="*50)
        print("1. Select Account")
        print("2. Create New Account")
        print("3. Reset PIN")
        print("4. View My Summary")
        print("5. Logout")
        print("-"*50)
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            account = select_account(customer)
            if account:
                account_operations(bank, customer, account)
        elif choice == "2":
            create_account_flow(bank, customer)
        elif choice == "3":
            reset_pin_flow(customer)
        elif choice == "4":
            view_customer_summary(customer)
        elif choice == "5":
            print(f"\n✓ Logged out from {customer.name}")
            break
        else:
            print("✗ Invalid choice!")

def select_account(customer):
    """Let customer select from their accounts"""
    
    if not customer.accounts:
        print("\n✗ You have no accounts. Create one first!")
        return None
    
    print("\nYour Accounts:")
    for i, acc in enumerate(customer.accounts, 1):
        account_type = type(acc).__name__.replace("Account", "")
        print(f"{i}. {acc.account_number} ({account_type}): ${acc.balance:.2f}")
    
    try:
        choice = int(input(f"\nSelect account (1-{len(customer.accounts)}): ").strip())
        if 1 <= choice <= len(customer.accounts):
            return customer.accounts[choice-1]
        else:
            print("✗ Invalid choice!")
            return None
    except ValueError:
        print("✗ Please enter a number!")
        return None

def account_operations(bank, customer, account):
    """Operations for a specific account"""
    
    while True:
        account_type = type(account).__name__.replace("Account", "")
        print(f"\n" + "="*50)
        print(f"ACCOUNT: {account.account_number} ({account_type})")
        print(f"Balance: ${account.balance:.2f}")
        print("="*50)
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Transfer")
        print("4. View Statement")
        print("5. Back to Customer Menu")
        print("-"*50)
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            deposit_flow(account)
        elif choice == "2":
            withdraw_flow(account)
        elif choice == "3":
            transfer_flow(bank, account)
        elif choice == "4":
            view_statement(account)
        elif choice == "5":
            break
        else:
            print("✗ Invalid choice!")

def employee_menu(bank):
    """Menu for authenticated employees"""
    
    while True:
        print("\n" + "="*50)
        print("EMPLOYEE MENU")
        print("="*50)
        print("1. View Account Statement")
        print("2. Apply Monthly Updates")
        print("3. View Bank Summary")
        print("4. Unlock Account")
        print("5. Logout")
        print("-"*50)
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            view_account_statement_employee(bank)
        elif choice == "2":
            apply_monthly_updates(bank)
        elif choice == "3":
            view_bank_summary(bank)
        elif choice == "4":
            unlock_account_flow(bank)
        elif choice == "5":
            print("\n✓ Employee logged out")
            break
        else:
            print("✗ Invalid choice!")

def create_account_flow(bank, customer):
    """Create a new account for a customer"""
    
    print("\n" + "="*50)
    print("CREATE NEW ACCOUNT")
    print("="*50)
    print("1. Savings Account (2% interest, $100 min balance)")
    print("2. Checking Account ($500 overdraft)")
    
    choice = input("\nSelect account type (1 or 2): ").strip()
    
    try:
        initial_balance = 0.0
        initial_input = input("Initial deposit (press Enter for $0): $").strip()
        if initial_input:
            initial_balance = float(initial_input)
            if initial_balance < 0:
                print("✗ Cannot deposit negative amount!")
                return
    except ValueError:
        print("✗ Invalid amount! Using $0")
    
    try:
        if choice == "1":
            account = bank.create_account(
                customer.customer_id, 
                "SAVINGS", 
                initial_balance,
                interest_rate=0.02
            )
            print(f"\n✓ Savings Account created!")
            print(f"  Account #: {account.account_number}")
        elif choice == "2":
            account = bank.create_account(
                customer.customer_id,
                "CHECKING",
                initial_balance,
                overdraft_limit=500.0
            )
            print(f"\n✓ Checking Account created!")
            print(f"  Account #: {account.account_number}")
        else:
            print("✗ Invalid choice!")
    except Exception as e:
        print(f"✗ Error: {e}")

def deposit_flow(account):
    """Handle deposit operation"""
    
    try:
        amount = float(input("\nDeposit amount: $").strip())
        if amount <= 0:
            print("✗ Amount must be positive!")
            return
        
        account.deposit(amount)
        print(f"✓ Deposit successful! New balance: ${account.balance:.2f}")
    except ValueError:
        print("✗ Invalid amount!")
    except Exception as e:
        print(f"✗ Error: {e}")

def withdraw_flow(account):
    """Handle withdrawal with PIN confirmation"""
    
    try:
        amount = float(input("Withdrawal amount: $").strip())
        pin = getpass.getpass("Enter PIN to confirm withdrawal: ")
        if amount <= 0:
            print("✗ Amount must be positive!")
            return
        account.withdraw(amount, pin)
        print(f"✓ Withdrawal successful! New balance: ${account.balance:.2f}")
    except InvalidPINError:
        print("✗ Invalid PIN! Withdrawal cancelled.")
    except ValueError:
        print("✗ Invalid amount!")
    except Exception as e:
        print(f"✗ Error: {e}")

def transfer_flow(bank, from_account):
    """Handle transfer between accounts"""
    
    try:
        to_acc_num = input("\nRecipient Account Number: ").strip()
        to_account = bank.get_account(to_acc_num)
        
        amount = float(input("Transfer amount: $").strip())
        
        if amount <= 0:
            print("✗ Amount must be positive!")
            return
        
        pin = getpass.getpass("Enter PIN to confirm transfer: ")
        
        # Fixed: Pass PIN to bank.transfer()
        bank.transfer(from_account.account_number, to_acc_num, amount, pin)
        print(f"✓ Transfer successful!")
        print(f"  Your new balance: ${from_account.balance:.2f}")
        
    except (InvalidPINError, InsufficientFundsError) as e:
        print(f"✗ {e}")
    except ValueError:
        print("✗ Invalid amount!")
    except Exception as e:
        print(f"✗ Error: {e}")

def reset_pin_flow(customer):
    """Reset customer PIN"""
    
    print("\n" + "="*50)
    print("RESET PIN")
    print("="*50)
    
    old_pin = getpass.getpass("Current PIN: ")
    
    try:
        if not customer.verify_pin(old_pin):
            print("✗ Current PIN is incorrect!")
            return
        
        while True:
            new_pin1 = getpass.getpass("New 4-digit PIN: ")
            if len(new_pin1) != 4 or not new_pin1.isdigit():
                print("PIN must be 4 digits!")
                continue
            
            new_pin2 = getpass.getpass("Confirm new PIN: ")
            if new_pin1 == new_pin2:
                if customer.reset_pin(old_pin, new_pin1):
                    print("✓ PIN reset successful!")
                    break
                else:
                    print("✗ PIN reset failed!")
                    break
            else:
                print("PINs don't match!")
                
    except Exception as e:
        print(f"✗ Error: {e}")

def view_customer_summary(customer):
    """Display customer summary"""
    
    print(f"\n" + "="*50)
    print(f"CUSTOMER SUMMARY: {customer.name}")
    print("="*50)
    print(f"Customer ID: {customer.customer_id}")
    print(f"Email: {customer.email}")
    print(f"Status: {'LOCKED 🔒' if customer.is_locked else 'ACTIVE ✓'}")
    print(f"Total Balance: ${customer.get_total_balance():.2f}")
    
    if customer.accounts:
        print("\nAccounts:")
        print("-"*50)
        print(f"{'Account #':<15} {'Type':<15} {'Balance':<15}")
        print("-"*50)
        for acc in customer.accounts:
            account_type = type(acc).__name__.replace("Account", "")
            print(f"{acc.account_number:<15} {account_type:<15} ${acc.balance:<14.2f}")
    else:
        print("\nNo accounts yet.")

def view_statement(account):
    """View account statement"""
    
    try:
        statement = account.get_statement()
        print(f"\n" + "="*60)
        print(f"STATEMENT: {statement['account_number']}")
        print("="*60)
        print(f"Owner: {statement['owner']}")
        print(f"Balance: ${statement['balance']:.2f}")
        print(f"Type: {statement['account_type']}")
        
        if statement['transactions']:
            print("\nRecent Transactions:")
            print("-"*70)
            print(f"{'Date':<20} {'Type':<15} {'Amount':<15} {'Balance':<15}")
            print("-"*70)
            for tx in statement['transactions'][-10:]:
                date_str = tx['date'].strftime("%Y-%m-%d %H:%M")
                amount = f"${tx['amount']:.2f}"
                balance = f"${tx['balance_after']:.2f}"
                
                if tx['type'] == 'DEPOSIT':
                    amount = f"+{amount}"
                elif tx['type'] == 'WITHDRAW':
                    amount = f"-{amount}"
                
                print(f"{date_str:<20} {tx['type']:<15} {amount:<15} {balance:<15}")
        else:
            print("\nNo transactions yet.")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def view_account_statement_employee(bank):
    """Employee can view any account statement"""
    
    account_num = input("\nEnter Account Number: ").strip()
    
    try:
        account = bank.get_account(account_num)
        view_statement(account)
    except Exception as e:
        print(f"✗ Error: {e}")

def apply_monthly_updates(bank):
    """Apply monthly interest/charges"""
    
    confirm = input("\nApply monthly updates to ALL accounts? (yes/no): ").strip().lower()
    if confirm in ['yes', 'y']:
        bank.apply_monthly_updates()
        print("✓ Monthly updates applied to all accounts.")
    else:
        print("✗ Monthly updates cancelled.")

def view_bank_summary(bank):
    """Display bank-wide summary"""
    
    summary = bank.get_bank_summary()
    print(f"\n" + "="*50)
    print("BANK SUMMARY")
    print("="*50)
    print(f"Total Customers: {summary.get('total_customers', 0)}")
    print(f"Total Accounts: {summary.get('total_accounts', 0)}")
    print(f"Total Deposits: ${summary.get('total_deposits', 0):.2f}")
    
    if 'accounts_by_type' in summary:
        print("\nAccounts by Type:")
        for acc_type, count in summary['accounts_by_type'].items():
            print(f"  {acc_type}: {count}")

def unlock_account_flow(bank):
    """Unlock a customer account"""
    
    customer_id = input("\nEnter Customer ID to unlock: ").strip()
    
    try:
        customer = bank.get_customer(customer_id)
        print(f"\nCustomer: {customer.name}")
        print(f"Status: {'LOCKED' if customer.is_locked else 'Already ACTIVE'}")
        
        if customer.is_locked:
            admin_key = getpass.getpass("Enter Admin Key: ")
            if customer.unlock_account(admin_key):
                print(f"✓ Account for {customer.name} unlocked!")
            else:
                print("✗ Invalid admin key!")
    except Exception as e:
        print(f"✗ Error: {e}")

# ==================== MAIN FUNCTION ====================

def interactive_main():
    """Main function to run the banking system"""
    
    my_bank = Bank("Secure Python Bank")
    
    while True:
        print("\n" + "="*50)
        print("MAIN MENU - SECURE BANKING SYSTEM")
        print("="*50)
        print("1. Login as Customer")
        print("2. Login as Employee")
        print("3. Sign Up (New Customer)")
        print("4. Exit")
        print("-"*50)
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            customer_login_flow(my_bank)
        elif choice == "2":
            employee_login_flow(my_bank)
        elif choice == "3":
            sign_up_flow(my_bank)
        elif choice == "4":
            print("\nThank you for using the Secure Banking System. Goodbye!")
            break
        else:
            print("✗ Invalid choice!")

# ==================== RUN THE SYSTEM ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("WELCOME TO PYTHON BANKING SYSTEM")
    print("\nStarting system...")
    
    interactive_main()