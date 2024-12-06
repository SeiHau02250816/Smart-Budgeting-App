from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from backendTop import BackendTop
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure secret key
backend = BackendTop()

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'receipt' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['receipt']
        
        if file and allowed_file(file.filename):
            try:
                # Process the uploaded file using backend
                filepath = backend.process_uploaded_file(file, app.config['UPLOAD_FOLDER'])

                # Process the receipt using backend
                recognized_text = backend.recognize_text(filepath)
                transaction = backend.extract_transaction_data(recognized_text)
                
                # Store transaction data in session for review
                session['transaction_data'] = {
                    'date': transaction.date,  
                    'business_name': transaction.business_name,
                    'amount': float(transaction.amount),
                    'category': transaction.category.value
                }
                
                return redirect(url_for('review_transaction'))
                
            except Exception as e:
                flash(f'Error processing receipt: {str(e)}')
            
            return redirect(url_for('upload'))
    
    return render_template('upload.html')

@app.route('/review', methods=['GET', 'POST'])
def review_transaction():
    if 'transaction_data' not in session:
        flash('No transaction to review')
        return redirect(url_for('upload'))
    
    if request.method == 'POST':
        # Update transaction data with user edits
        transaction_data = {
            'date': request.form['date'],  
            'business_name': request.form['business_name'],
            'amount': float(request.form['amount']),
            'category': request.form['category']
        }
        
        try:
            # Create transaction object and add to database
            transaction = backend.create_transaction_from_dict(transaction_data)
            backend.add_to_spent_table(transaction)
            
            # Check total spending and trigger alert if needed
            total_spending = backend.database.get_total_spending()
            alert_message = backend.alert_system.check_total_spending(total_spending)
            if alert_message:
                flash(f'Spending Alert: {alert_message}')
            else:
                flash('Transaction added successfully!')
            
            # Clear the session
            session.pop('transaction_data', None)
            return redirect(url_for('transactions'))
        except Exception as e:
            flash(f'Error saving transaction: {str(e)}')
            return redirect(url_for('review_transaction'))
    
    return render_template('review.html', transaction=session['transaction_data'])

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        print(transaction_id)
        print(request.form.get('business_name'))
        if transaction_id:
            try:
                # Find the transaction object by ID
                transaction = next((t for t in backend.database.get_all_transactions() if t.transaction_id == transaction_id), None)
                if transaction:
                    # Delete the transaction using BackendTop
                    message = backend.delete_transaction(transaction)
                    flash(message)
                else:
                    flash('Transaction not found.')
            except Exception as e:
                flash(f'Error deleting transaction: {str(e)}')

    transactions = backend.database.get_all_transactions()
    total_spending = backend.database.get_total_spending()
    return render_template('transactions.html', transactions=transactions, total_spending=total_spending)

if __name__ == '__main__':
    app.run(debug=True)
