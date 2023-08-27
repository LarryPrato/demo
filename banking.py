import mysql.connector
import pytest

class Budget:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.transactions = []

        self._create_table()

    def _create_table(self):
        conn = mysql.connector.connect(
            host="localhost",
            user="username",
            password="password",
            database="budget_db"
        )
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS transactions (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), amount DECIMAL(10, 2), note TEXT)"
        )
        conn.commit()
        conn.close()

    def deposit(self, amount, note=""):
        self.balance += amount
        self.transactions.append((amount, note))
        self._save_transaction(amount, note)

    def withdraw(self, amount, note=""):
        if self.check_funds(amount):
            self.balance -= amount
            self.transactions.append((-amount, note))
            self._save_transaction(-amount, note)
            return True
        else:
            return False

    def get_balance(self):
        return self.balance

    def check_funds(self, amount):
        return amount <= self.balance

    def get_transactions(self):
        return self.transactions

    def delete_transaction(self, transaction_index):
        if 0 <= transaction_index < len(self.transactions):
            amount, _ = self.transactions[transaction_index]
            del self.transactions[transaction_index]
            self.balance -= amount
            self._delete_transaction_from_db(transaction_index)

    def get_transactions_by_type(self, transaction_type):
        transactions_by_type = []
        for amount, note in self.transactions:
            if note == transaction_type:
                transactions_by_type.append((amount, note))
        return transactions_by_type

    def display_transactions(self):
        for amount, note in self.transactions:
            print(f"{note}: {amount}")

    def calculate_average_income(self):
        total_income = sum(amount for amount, note in self.transactions if amount > 0)
        num_income_transactions = len([amount for amount, note in self.transactions if amount > 0])
        if num_income_transactions > 0:
            return total_income / num_income_transactions
        return 0

    def calculate_average_expenses(self):
        total_expenses = sum(amount for amount, note in self.transactions if amount < 0)
        num_expenses_transactions = len([amount for amount, note in self.transactions if amount < 0])
        if num_expenses_transactions > 0:
            return total_expenses / num_expenses_transactions
        return 0

    def print_budget_summary(self):
        print(f"Budget Summary for {self.name}")
        print(f"Current Balance: {self.balance}")
        print(f"Average Income: {self.calculate_average_income()}")
        print(f"Average Expenses: {self.calculate_average_expenses()}")

    def _save_transaction(self, amount, note):
        conn = mysql.connector.connect(
            host="localhost",
            user="username",
            password="password",
            database="budget_db"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (name, amount, note) VALUES (%s, %s, %s)",
                       (self.name, amount, note))
        conn.commit()
        conn.close()

    def _delete_transaction_from_db(self, transaction_index):
        conn = mysql.connector.connect(
            host="localhost",
            user="username",
            password="password",
            database="budget_db"
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_index + 1,))
        conn.commit()
        conn.close()

class TestBudget:
    @pytest.fixture
    def budget(self):
        return Budget("Test Budget", 100)

    def test_deposit(self, budget):
        budget.deposit(50)
        assert budget.get_balance() == 150

    def test_withdraw(self, budget):
        budget.withdraw(30)
        assert budget.get_balance() == 70

    def test_check_funds(self, budget):
        assert budget.check_funds(50)
        assert not budget.check_funds(150)

    def test_get_transactions(self, budget):
        budget.deposit(50, "Income")
        budget.withdraw(30, "Groceries")
        transactions = budget.get_transactions()
        assert len(transactions) == 2
        assert transactions[0] == (50, "Income")
        assert transactions[1] == (-30, "Groceries")

    def test_delete_transaction(self, budget):
        budget.deposit(50, "Income")
        budget.delete_transaction(0)
        assert len(budget.get_transactions()) == 0
        assert budget.get_balance() == 100

    def test_get_transactions_by_type(self, budget):
        budget.deposit(50, "Income")
        budget.withdraw(30, "Groceries")
        income_transactions = budget.get_transactions_by_type("Income")
        assert len(income_transactions) == 1
        assert income_transactions[0] == (50, "Income")
        grocery_transactions = budget.get_transactions_by_type("Groceries")
        assert len(grocery_transactions) == 1
        assert grocery_transactions[0] == (-30, "Groceries")

if __name__ == '__main__':
    pytest.main()