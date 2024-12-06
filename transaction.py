from datetime import datetime
from enum import Enum
from typing import Optional

class TransactionCategory(Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    LIFESTYLE_ENTERTAINMENT = "Lifestyle & Entertainment"
    RENT = "Rent"
    UTILITIES = "Utilities"
    OTHERS = "Others"

    @classmethod
    def from_string(cls, category_str: str) -> 'TransactionCategory':
        """Convert string to TransactionCategory, case-insensitive"""
        clean_str = category_str.lower().replace('&', '').replace(' ', '_')
        for category in cls:
            if category.name.lower() == clean_str:
                return category
        return cls.OTHERS

class Transaction:
    def __init__(
        self,
        date: str,
        amount: float,
        business_name: str,
        category: str,
        transaction_id: Optional[str] = None
    ):
        """
        Initialize a Transaction object.

        Args:
            date (str): Transaction date in YYYY-MM-DD format
            amount (float): Transaction amount in RM
            business_name (str): Name of the business
            category (str): Transaction category
            transaction_id (Optional[str]): Unique transaction identifier
        """
        self.transaction_id = transaction_id if transaction_id else self._generate_transaction_id()
        self._set_date(date)
        self._set_amount(amount)
        self.business_name = business_name.strip()
        self.category = TransactionCategory.from_string(category)

    def _generate_transaction_id(self) -> str:
        """Generate a unique transaction ID based on timestamp"""
        return datetime.now().strftime("%Y%m%d%H%M%S%f")

    def _set_date(self, date_str: str) -> None:
        """Validate and set the transaction date"""
        try:
            # Parse the date string to ensure it's valid
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            self.date = parsed_date.strftime("%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD, got: {date_str}") from e

    def _set_amount(self, amount: float) -> None:
        """Validate and set the transaction amount"""
        try:
            self.amount = float(amount)
            if self.amount < 0:
                raise ValueError("Amount cannot be negative")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid amount value: {amount}") from e

    def to_csv_row(self) -> str:
        """Convert transaction to CSV row format"""
        return f"{self.date},{self.amount:.2f},{self.business_name},{self.category.value}"

    @classmethod
    def from_csv_row(cls, csv_row: str) -> 'Transaction':
        """Create a Transaction object from a CSV row"""
        try:
            date, amount, business_name, category = csv_row.strip().split(',')
            return cls(
                date=date,
                amount=float(amount),
                business_name=business_name,
                category=category
            )
        except ValueError as e:
            raise ValueError(f"Invalid CSV format. Expected: date,amount,business,category. Got: {csv_row}") from e

    def __str__(self):
        return "{:<22} {:<12} {:<10.2f} {:<20} {:<15}".format(
            self.transaction_id,
            self.date,
            self.amount,
            self.business_name,
            self.category.value
        )

if __name__ == "__main__":
    # Example usage
    try:
        # Create a transaction from direct values
        t1 = Transaction(
            date="2024-03-15",
            amount=25.90,
            business_name="Restaurant ABC",
            category="Food"
        )
        print("\nTransaction 1:")
        print(t1)
        print("As CSV:", t1.to_csv_row())

        # Create a transaction from CSV
        csv_data = "2024-03-15,42.50,Grab,Transport"
        t2 = Transaction.from_csv_row(csv_data)
        print("\nTransaction 2:")
        print(t2)
        print("As dict:", t2.to_dict())

    except ValueError as e:
        print(f"Error: {e}")
