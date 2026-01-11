"""
Developer menu for quick testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test import *
from main import interactive_main

def dev_menu():
    """Developer menu for testing"""
    bank = None
    
    while True:
        print("\n" + "="*60)
        print("DEVELOPER TEST MENU")
        print("="*60)
        print("1. Quick Test (basic functionality)")
        print("2. Create Demo Bank (pre-populated)")
        print("3. Stress Test (many customers)")
        print("4. Run Normal Interactive System")
        print("5. Reset Bank")
        print("6. Exit")
        print("-"*60)
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            bank = quick_test()
        elif choice == "2":
            bank = create_demo_bank()
        elif choice == "3":
            try:
                num = int(input("Number of customers (default 10): ") or "10")
                bank = stress_test(num)
            except ValueError:
                print("Invalid number!")
        elif choice == "4":
            interactive_main()
        elif choice == "5":
            bank = None
            print("Bank reset. Create a new one.")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    dev_menu()