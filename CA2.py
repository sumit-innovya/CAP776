import csv
import re
import hashlib
import requests
from datetime import datetime
import sys

REGNO_FILE_PATH = 'regno.csv'
USER_ACTIVITY_LOG_PATH = 'user_activity_log.csv'


COMPANY_TICKER_MAP = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Alphabet": "GOOGL",
    "Meta": "META"
}

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False
    special_characters = re.compile('[@$!%*?&]')
    return bool(special_characters.search(password))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup(email, password, security_question, correct_answer):
    hashed_password = hash_password(password)
    with open(REGNO_FILE_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email, hashed_password, security_question, correct_answer])
    print("Signup successful!")

def login(email, password):
    hashed_password = hash_password(password)
    try:
        with open(REGNO_FILE_PATH, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == email and row[1] == hashed_password:
                    return True
        print("Invalid email or password.")
        return False
    except FileNotFoundError:
        print("User database not found.")
        return False

def reset_password(email):
    try:
        with open(REGNO_FILE_PATH, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == email:
                    security_question = row[2]
                    correct_answer = row[3]
                    answer = input(f"Security Question: {security_question}\nYour Answer: ")
                    if answer == correct_answer:
                        new_password = input("Enter your new password: ")
                        if validate_password(new_password):
                            hashed_password = hash_password(new_password)
                            update_password(email, hashed_password)
                            print("Password updated successfully.")
                            return True
                        else:
                            print("New password does not meet criteria.")
                    else:
                        print("Incorrect answer to the security question.")
                    return False
        print("Email not found.")
        return False
    except FileNotFoundError:
        print("User database not found.")

def update_password(email, new_password):
    rows = []
    with open(REGNO_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == email:
                row[1] = new_password
            rows.append(row)

    with open(REGNO_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def log_activity(email, company_name, stock_data):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    with open(USER_ACTIVITY_LOG_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email, date_str, time_str, company_name, stock_data['symbol'], stock_data['currentPrice'], 
                         stock_data['openPrice'], stock_data['highPrice'], stock_data['lowPrice'], stock_data['previousClose'], stock_data['volume']])

def fetch_stock_data(ticker):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey=2LYW83QDKHE80TXV'
    response = requests.get(url)
    data = response.json()
    
    if 'Time Series (1min)' in data:
        latest_time = sorted(data['Time Series (1min)'].keys())[0]
        stock_info = data['Time Series (1min)'][latest_time]
        
        stock_data = {
            'symbol': ticker,
            'currentPrice': stock_info['1. open'],
            'openPrice': stock_info['1. open'],
            'highPrice': stock_info['2. high'],
            'lowPrice': stock_info['3. low'],
            'previousClose': stock_info['4. close'],
            'volume': stock_info['5. volume']
        }
        return stock_data
    else:
        print("Failed to retrieve stock data. Please check the ticker symbol.")
        return None

def application_functionality(email):
    company_name = input("Enter the company name for which you want to retrieve stock data: ")
    ticker = COMPANY_TICKER_MAP.get(company_name)
    if ticker:
        stock_data = fetch_stock_data(ticker)
        if stock_data:
            print(f"Current Price: {stock_data['currentPrice']}")
            print(f"Open Price: {stock_data['openPrice']}")
            print(f"High Price: {stock_data['highPrice']}")
            print(f"Low Price: {stock_data['lowPrice']}")
            print(f"Previous Close: {stock_data['previousClose']}")
            print(f"Volume: {stock_data['volume']}")
            log_activity(email, company_name, stock_data)
        else:
            print("Could not retrieve stock data.")
    else:
        print("Company not found.")

def main():
    print("--------------------------Get your stocks detail right away---------------------------")
    while True:
        print("Pick an option:")
        print("1. Signup")
        print("2. Login")
        print("3. Reset Password")
        choice = input("Enter your choice: ")

        if choice == "1":
            email = input("Enter your email: ")

           
            if not validate_email(email):
                print("Invalid email format. Please try again.")
                continue  

            password = input("Enter your password: ")

            
            if not validate_password(password):
                print("Invalid password format. Password must be at least 8 characters long and contain at least one special character.")
                continue 

            security_question = input("Enter a security question: ")
            correct_answer = input("Enter the answer to the security question: ")
            signup(email, password, security_question, correct_answer)
            print("Signup successful!")

        elif choice == "2":
            email = input("Enter your email: ")

            if not validate_email(email):
                print("Invalid email format. Please try again.")
                continue 

            try:
                with open(REGNO_FILE_PATH, mode='r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row[0] == email:
                          
                            login_attempts = 0
                            while login_attempts < 5:
                                password = input("Enter your password: ")
                                if login(email, password):
                                    print("Login successful!")
                                    application_functionality(email)
                                    return
                                else:
                                    login_attempts += 1
                                    print(f"Attempt {login_attempts} of 5.")

                            
                            if login_attempts >= 3:
                                reset_choice = input("Too many failed attempts. Would you like to reset your password? (yes/no): ")
                                if reset_choice.lower() == 'yes':
                                    if reset_password(email):
                                        print("Password reset successful. Please log in again.")
                                        main()  
                                    else:
                                        print("Password reset failed.")
                                else:
                                    print("Exiting application.")
                                    return
                            return 
                    else:
                        print("New user, please sign up first.")
            except FileNotFoundError:
                print("User database not found. Please sign up first.")

        elif choice == "3":
            email = input("Enter your email for password reset: ")

          
            if not validate_email(email):
                print("Invalid email format. Please try again.")
                continue  

            reset_password(email)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
      main()

# Once the user signs up and after getting the output of Stocks to download that data, please uncomment the below code. 
# from google.colab import files
# files.download('regno.csv')
# files.download('user_activity_log.csv')
