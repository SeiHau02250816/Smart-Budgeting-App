import cv2
import sys
from databaseHandler import ExcelDatabase
from imagePostProcessing import ImagePostProcessing
from transaction import Transaction, TransactionCategory
from chatCompletion import ClaudeClient
from alertSystem import AlertSystem
import os
from werkzeug.utils import secure_filename

class BackendTop:
    def __init__(self):
        self.database = ExcelDatabase('database.xlsx')
        self.database.create_spent_table()
        self.image_processor = ImagePostProcessing()
        self.alert_system = AlertSystem(threshold=3000.0, recipient_email="seihauteo0225@gmail.com")

    def recognize_text(self, image_path):
        result = self.image_processor.extract_text_from_image(image_path)
        if result['success']:
            return result['text']
        else:
            raise Exception("Failed to recognize text from image.")

    def extract_transaction_data(self, text):
        """
        Extract transaction data from text and return a Transaction object.
        """
        try:
            # Create a Transaction object from the CSV text
            transaction = Transaction.from_csv_row(text)
            return transaction
        except ValueError as e:
            raise Exception(f"Failed to extract transaction data: {e}")

    def create_transaction_from_dict(self, transaction_data):
        """
        Create a Transaction object from a dictionary of transaction data.
        
        Args:
            transaction_data (dict): Dictionary containing transaction information
                                   (date, business_name, amount, category)
        
        Returns:
            Transaction: A new Transaction object with the provided data
        """
        from datetime import datetime
        
        # Date should already be in YYYY-MM-DD format from the form
        date = transaction_data['date']

        return Transaction(
            date=date,  # Transaction class will handle date validation
            business_name=transaction_data['business_name'],
            amount=float(transaction_data['amount']),
            category=transaction_data['category']
        )

    def add_to_spent_table(self, transaction):
        # Add the transaction to the 'Spent' table
        self.database.add_data_to_sheet('Spent', [transaction])

    def process_uploaded_file(self, file, upload_folder):
        """
        Process the uploaded file by checking if it is allowed and saving it.
        
        Args:
            file: The uploaded file object
            upload_folder: The folder path where the file should be saved
        
        Returns:
            filepath: The path where the file is saved
        """
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            return filepath
        else:
            raise ValueError('Invalid file or file type not allowed')

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}
