"""
Testing utilities for the banking system
"""
from account_and_customer import *
from bank import *
from exceptions import *

def create_test_bank() -> Bank:
    """Create a bank with test customers and accounts"""
    bank = Bank("Test Bank")
    
    # Create test customers
    customer1 = Customer("cust001", "John Doe", "john@example.com", "1234")
    customer2 = Customer("cust002", "Jane Smith", "jane@example.com", "5678")
    
    bank.add_customer(customer1)
    bank.add_customer(customer2)
    
    # Create accounts for customer1
    savings1 = bank.create_account("cust001", "SAVINGS", 1000.0)
    checking1 = bank.create_account("cust001", "CHECKING", 500.0)
    
    # Create accounts for customer2
    savings2 = bank.create_account("cust002", "SAVINGS", 1500.0)
    checking2 = bank.create_account("cust002", "CHECKING", 300.0)
    
    print("✓ Test bank created with 2 customers and 4 accounts")
    print(f"  - {customer1.name}: {len(customer1.accounts)} accounts")
    print(f"  - {customer2.name}: {len(customer2.accounts)} accounts")
    
    return bank

def quick_test():
    """Run a quick test of the banking system"""
    print("\n" + "="*60)
    print("QUICK TEST MODE")
    print("="*60)
    
    bank = create_test_bank()
    customer1 = bank.get_customer("cust001")
    customer2 = bank.get_customer("cust002")
    
    # Get accounts
    savings1 = customer1.get_account("cust001-001")
    checking1 = customer1.get_account("cust001-002")
    savings2 = customer2.get_account("cust002-001")
    
    print("\nInitial Balances:")
    print(f"John's Savings: ${savings1.balance:.2f}")
    print(f"John's Checking: ${checking1.balance:.2f}")
    print(f"Jane's Savings: ${savings2.balance:.2f}")
    
    # Test 1: Deposit
    print("\nTest 1: Deposit $200 to John's Savings")
    savings1.deposit(200)
    print(f"New balance: ${savings1.balance:.2f}")
    
    # Test 2: Withdraw with correct PIN
    print("\nTest 2: Withdraw $100 from John's Checking (PIN: 1234)")
    try:
        checking1.withdraw(100, "1234")
        print(f"Withdrawal successful! New balance: ${checking1.balance:.2f}")
    except Exception as e:
        print(f"Withdrawal failed: {e}")
    
    # Test 3: Withdraw with wrong PIN
    print("\nTest 3: Withdraw $50 from John's Checking (wrong PIN: 9999)")
    try:
        checking1.withdraw(50, "9999")
    except InvalidPINError as e:
        print(f"Expected error: {e}")
    
    # Test 4: Transfer with PIN
    print("\nTest 4: Transfer $150 from John's Savings to Jane's Savings")
    try:
        bank.transfer(savings1.account_number, savings2.account_number, 150, "1234")
        print(f"Transfer successful!")
        print(f"John's Savings: ${savings1.balance:.2f}")
        print(f"Jane's Savings: ${savings2.balance:.2f}")
    except Exception as e:
        print(f"Transfer failed: {e}")
    
    # Test 5: Test overdraft
    print("\nTest 5: Test checking account overdraft")
    print(f"John's Checking balance: ${checking1.balance:.2f}")
    print(f"Overdraft limit: ${checking1.overdraft_limit:.2f}")
    
    try:
        checking1.withdraw(600, "1234")
        print(f"Withdrew $600. New balance: ${checking1.balance:.2f}")
    except InsufficientFundsError as e:
        print(f"Expected overdraft limit error: {e}")
    
    # Test 6: Monthly updates
    print("\nTest 6: Apply monthly updates")
    bank.apply_monthly_updates()
    print("Monthly updates applied")
    print(f"John's Savings: ${savings1.balance:.2f} (should have interest if > $100)")
    print(f"John's Checking: ${checking1.balance:.2f}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    summary = bank.get_bank_summary()
    print(f"Bank: {summary['bank_name']}")
    print(f"Total Customers: {summary['total_customers']}")
    print(f"Total Accounts: {summary['total_accounts']}")
    print(f"Total Deposits: ${summary['total_deposits']:.2f}")
    
    return bank

def create_demo_bank():
    """Create a demo bank with pre-populated data"""
    bank = Bank("Demo Bank")
    
    # Demo customers
    customers = [
        ("alice01", "Alice Johnson", "alice@example.com", "1111"),
        ("bob02", "Bob Williams", "bob@example.com", "2222"),
        ("charlie03", "Charlie Brown", "charlie@example.com", "3333"),
    ]
    
    for cust_id, name, email, pin in customers:
        customer = Customer(cust_id, name, email, pin)
        bank.add_customer(customer)
        
        # Create 1-2 accounts for each
        bank.create_account(cust_id, "SAVINGS", 1000.0)
        bank.create_account(cust_id, "CHECKING", 500.0)
    
    print("Demo bank created with 3 customers and 6 accounts")
    print("Login credentials:")
    print("  Customer ID: alice01, PIN: 1111")
    print("  Customer ID: bob02, PIN: 2222")
    print("  Customer ID: charlie03, PIN: 3333")
    print("\nEmployee PIN: 1111")
    print("Admin Key: admin123")
    
    return bank

def stress_test(num_customers=10):
    """Stress test the system with many customers"""
    print(f"\nCreating stress test with {num_customers} customers...")
    bank = Bank("Stress Test Bank")
    
    for i in range(num_customers):
        cust_id = f"test{i:03d}"
        customer = Customer(cust_id, f"Test User {i}", f"test{i}@example.com", "1234")
        bank.add_customer(customer)
        
        # Create accounts
        bank.create_account(cust_id, "SAVINGS", 500.0 + i*100)
        bank.create_account(cust_id, "CHECKING", 200.0 + i*50)
    
    # Run some transactions
    for i in range(min(5, num_customers)):
        cust_id = f"test{i:03d}"
        customer = bank.get_customer(cust_id)
        if customer.accounts:
            account = customer.accounts[0]
            account.deposit(100)
            try:
                account.withdraw(50, "1234")
            except:
                pass
    
    summary = bank.get_bank_summary()
    print(f"\nStress test completed:")
    print(f"  Customers: {summary['total_customers']}")
    print(f"  Accounts: {summary['total_accounts']}")
    print(f"  Total deposits: ${summary['total_deposits']:.2f}")
    
    return bank

if __name__ == "__main__":
    print("Banking System Test Utilities")
    print("Run one of the following:")
    print("1. quick_test() - Basic functionality test")
    print("2. create_demo_bank() - Create pre-populated demo bank")
    print("3. stress_test(20) - Stress test with many customers")