import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertSystem:
    def __init__(self, threshold=3000.0, recipient_email=None):
        """
        Initialize the alert system with a default threshold.

        :param threshold: The spending threshold to trigger alerts.
        :param recipient_email: Email address to send alerts to.
        """
        self.threshold = threshold
        self.recipient_email = recipient_email
        # Email configuration from environment variables
        self.sender_email = os.getenv('PERSONAL_GMAIL')
        self.email_password = os.getenv('PERSONAL_GMAIL_APP_PW')
        if not self.sender_email or not self.email_password:
            raise EnvironmentError("Email credentials not found in environment variables. "
                                 "Please set PERSONAL_GMAIL and PERSONAL_GMAIL_APP_PW.")

    def check_total_spending(self, total_amount):
        """
        Check if the total amount exceeds the threshold and trigger an alert.

        :param total_amount: The total amount to check.
        :return: Alert message if threshold is exceeded, else None.
        """
        if total_amount > self.threshold:
            alert_message = self.create_alert_message(total_amount)
            if self.recipient_email:
                self.send_email_alert(alert_message)
            return alert_message
        return None

    def create_alert_message(self, total_amount):
        """
        Create the alert message.

        :param total_amount: The total amount that triggered the alert.
        :return: A string message for the alert.
        """
        return (f"Alert: Total spending exceeds the monthly threshold of RM{self.threshold}! "
                f"Current total spending: RM{total_amount:.2f}")

    def send_email_alert(self, alert_message):
        """
        Send an email alert using SMTP.

        :param alert_message: The alert message to send.
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = "Spending Alert - Monthly Threshold Exceeded"

            # Add body
            body = f"""
Dear User,

{alert_message}

This is an automated alert from your Smart Budgeting App.
Please review your spending and take necessary actions.

Best regards,
Smart Budgeting App Team
            """
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.email_password)
                text = msg.as_string()
                server.sendmail(self.sender_email, self.recipient_email, text)
                print("Email alert sent successfully!")
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        # Initialize the alert system with recipient email
        alert_system = AlertSystem(
            threshold=3000.0,
            recipient_email="seihauteo0225@gmail.com"  # Replace with recipient's email
        )

        # Check total amount
        total_amount = 3500.0
        alert_message = alert_system.check_total_spending(total_amount)
        if alert_message:
            print(alert_message)
    except EnvironmentError as e:
        print(f"Error: {e}")
