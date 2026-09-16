# imports
from flask import Flask, render_template, request, redirect, url_for, session
from database import database
from helper import helper

import csv

app = Flask(__name__)

# import csv
# from helper import helper
# from database import database


# Global database object
db_ops = database("cafe.db")

# Initialize database tables
@app.route('/initialize', methods=['GET'])
def initialize_database():
    db_ops.drop_table("Customers")
    db_ops.drop_table("BoardGames")
    db_ops.drop_table("MenuItems")
    db_ops.drop_table("Reservations")
    db_ops.drop_table("BoardGameOrders")
    db_ops.drop_table("MenuOrders")

    db_ops.create_Customers_table()
    db_ops.create_BoardGames_table()
    db_ops.create_MenuItems_table()
    db_ops.create_Reservations_table()
    db_ops.create_BoardGameOrders_table()
    db_ops.create_MenuOrders_table()
    db_ops.populate_table("Customers", "Customers.csv")
    db_ops.populate_table("BoardGames", "BoardGames.csv")
    db_ops.populate_table("MenuItems", "MenuItems.csv")
    db_ops.populate_table("Reservations", "Reservations.csv")
    db_ops.populate_table("BoardGameOrders", "BoardGameOrders.csv")
    db_ops.populate_table("MenuOrders", "MenuOrders.csv")
    print ("Database initialized and populated!")
    return "Database initialized and populated!"

@app.route('/')
def main():
        return render_template('sign-in.html')


# user wants to create an account
@app.route('/create-account', methods = ['GET','POST'])
def create_account():
    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']
        db_ops.create_new_customer(new_name, new_email)
        customer_id = db_ops.get_customer_id(new_name, new_email)
        return jsonify({
            "message": "Account created successfully!",
            "customer_id": customer_id
        })
    return render_template('create-account.html')

# @app.route('/reserve', methods=['POST'])
# def make_reservation():
#     customer_id = request.form['customer_id']
#     reserve_date = request.form['date']
#     reserve_time = request.form['time']
#     guest_count = request.form['guest_count']

#     # Print debug info to confirm input data
#     print(f"Reservation received: Customer ID = {customer_id}, Date = {reserve_date}, Time = {reserve_time}, Guests = {guest_count}")

#     db_ops.create_new_reservation(customer_id, reserve_date, reserve_time, guest_count)
#     return jsonify({"message": "Reservation created successfully!"})


    # local implementation
    # def options():
    #     print('''Would you like to
    #             1. Sign In
    #             2. Create Account
    #             3. Exit''')
    #     return helper.get_choice([1,2,3])

    # new_name = input("Please enter your name:\n")
    # new_email = input("Please enter you email:\n")
    # db_ops.create_new_customer(new_name, new_email)
    # print("Your ID is: " + str(db_ops.get_id()))
    # print("Save this!! You will use it to log in!")




# Sign in
@app.route('/', methods=['GET', 'POST'])
def sign_in():
    print("sign in method called")
    if request.method == 'POST':
        entered_id = request.form['customer_id']
        IDvalidity = db_ops.check_customer_id(entered_id)
        if IDvalidity:
            return redirect(url_for('menu', user_id=entered_id))
        else:
            return render_template('sign-in.html', error="Invalid ID. Please try again!")
    return render_template('sign-in.html')

# Sign-In Route
# @app.route('/sign-in', methods=['POST'])
# def sign_in():
#     user_email = request.form['email']
#     user_password = request.form['password']

#     # Check user credentials in the database
#     user_id = db_ops.check_user_credentials(user_email, user_password)
#     if user_id:
#         # Redirect to menu page with the user ID as a query parameter
#         return redirect(url_for('menu', user_id=user_id))
#     else:
#         # Show an error message or redirect to the sign-in page
#         return render_template('sign-in.html', error="Invalid credentials")


    #local implementation: 
    # # user wants to sign in
    # def user_menu():
    #     # Ask for ID and email to log in
    #     print("What is your ID number?")
    #     entered_id = input("ID Number: ")

    # # Check to see if ID number is valid and log in
    # IDvalidity = db_ops.check_id(entered_id)

    # if IDvalidity:
    #     signed_in = True
    #     while signed_in:
    #         choice = menu_options()
    #         if choice == 1:
    #             view_menu()
    #         if choice == 2:
    #             view_board_games()
    #         if choice == 3:
    #             make_reservation(entered_id)
    #         if choice == 4:
    #             view_reservations(entered_id)
    #         if choice == 5:
    #             account_info(entered_id)
    # else:
    #     print("Not a valid ID number. Try logging in with a valid one.")

# options on main screen


# User menu
# @app.route('/menu/<customer_id>')
# def user_menu(customer_id):
#     return render_template('menu.html', customer_id=customer_id)

# User Menu Route
@app.route('/menu', methods=['GET'])
def menu():
    user_id = request.args.get('user_id')
    if user_id:
        print(f"User ID received in menu route: {user_id}")
        return render_template('menu.html', user_id=user_id)
    else:
        print("No user_id found, redirecting to sign-in")
        return redirect(url_for('sign_in'))
    
# def menu_options():
#     print('''Where would you like to go?
#             1. Menu
#             2. Board Games
#             3. Reserve
#             4. Reservations
#             5. Account
#         ''')
#     return helper.get_choice([1,2,3,4.5])


# View menu
@app.route('/view-menu', methods=['GET'])
def view_menu():
    menuItems = db_ops.view_menu_items()
    menuItems_list = [list(menuItem) for menuItem in menuItems]
    return {"menuItems": menuItems_list}

# # user wants to view_menu
# def view_menu():
#     print("Here is a list of all our drinks!")
#     # show the menu
#     food_menu_query = f"""
#     SELECT *
#     FROM MenuItems;
#     """
#     items = db_ops.select_query(food_menu_query)
#     helper.pretty_print(items)


# View board games
@app.route('/board-games', methods=['GET'])
def view_board_games():
    games = db_ops.view_board_games()
    games_list = [list(game) for game in games]  # Convert rows to lists
    return {"games": games_list}


# # user wants to view board games
# def view_board_games():
#     print("Here is a list of all our games!")
#     # show board game menu
#     game_menu_query = f"""
#     SELECT *
#     FROM BoardGames;
#     """
#     games = db_ops.select_query(game_menu_query)
#     helper.pretty_print(games)


# Make reservation
@app.route('/reserve', methods=['POST'])
def make_reservation():
    print(request.form)  # Debugging
    customer_id = request.form.get('customer_id')  # Safely get customer_id
    reserve_date = request.form.get('date')
    reserve_time = request.form.get('time')
    guest_count = request.form.get('guestCount')

    if not all([customer_id, reserve_date, reserve_time, guest_count]):
        return jsonify({"error": "Missing required fields"}), 400

    db_ops.create_new_reservation(customer_id, reserve_date, reserve_time, guest_count)
    return jsonify({"message": "Reservation created successfully!"})





# def make_reservation(id):

#     # asks for reservation date
#     failed = True
#     while failed:
#         failed = False
#         reserve_date = input("What day would you like to make a reservation? (YYYY-MM-DD)\n")
#         if len(reserve_date) != 10:
#             failed = True
#         else:
#             for i in range(len(reserve_date)):
#                 if i == 4 or i == 7:
#                     if reserve_date[i] != '-':
#                         failed = True
#                 else:
#                     try:
#                         int(reserve_date[i])
#                     except:
#                         failed = True
#         if failed == False:
#             if int(reserve_date[:4]) < 2024 or int(reserve_date[5:7]) > 12 or int(reserve_date[8:]) > 30:
#                 failed = True
#         if failed:
#             print("Invalid entry. Please enter a valid date in the correct format (YYYY-MM-DD)")

#     # asks for reservation time
#     failed = True
#     while failed:
#         failed = False
#         reserve_time = input("What time would you like your reservation to be? (##:##)\n")
#         if len(reserve_time) != 5:
#             failed = True
#         else:
#             if reserve_time[2] != ':':
#                 failed = True
#             else:
#                 try:
#                     if int(reserve_time[:2]) > 23 or int(reserve_time[3:]) > 59:
#                         failed = True
#                 except:
#                     failed = True
#         if failed:
#             print("Invalid entry. Please enter a valid time in the correct format")

#     # asks for guest number
#     failed = True
#     while failed:
#         failed = False
#         guest_amount = input("How many people will there be (including yourself)\n")
#         try:
#             int(guest_amount)
#         except:
#             failed = True
#         if failed:
#             print("Invalid. Please enter an integer")

#     # allows them to pre-order drinks
#     # print("Would you like to order drinks ahead of time?\n")
#     # print('''1. Yes
#     #          2. No
#     #          ''')
#     # if helper.get_choice([1,2]) == 1:
        
#     #print("Would you like to reserve a game?")
#     #print("What game would you like to reserve?")

#     # adds new reservation to table
#     db_ops.create_new_reservation(id, reserve_date, reserve_time, guest_amount)

# allows user to view their reservations


# View reservations
@app.route('/reservations/<customer_id>', methods=['GET'])
def view_reservations(customer_id):
    print("reservations route called")
    reservations = db_ops.view_reservations(customer_id)
    reservations_list = [list(reservation) for reservation in reservations]
    print("list length: " + str(len(reservations_list)))
    return {"reservations": reservations_list}

# def view_reservations(id):
#     reservations_query = f'''
#     SELECT *
#     FROM Reservation
#     WHERE customerID LIKE "{id}";
#     '''
#     results = db_ops.select_query(reservations_query)
#     print("Here are all of your reservations:\n")
#     helper.pretty_print(results)

    # data to be written to the csv
    exported_file = [
                ["menuItemName", "menuItemPrice", "itemSpecifications", "gameName"]
    ]
    
    # have user enter/click reservation_id of reservation they want to get info for
    # reservation_id = (the one they entered)
    temp_list = []
    
    for a in db_ops.get_reservation_details(reservation_id):
        temp_list.append(a)
    
    exported_file.append(temp_list)
    
    file_name = 'past_reservations.csv'
    
    # writing data to csv
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(exported_file)
    
    print(f"Report saved as {file_name}")


#main method


# Account info
@app.route('/account-info/<int:user_id>')
def account_info(user_id):
    # Fetch customer info based on the user_id
    customer_info = db_ops.get_customer_info_by_id(user_id+1)
    if customer_info:
        return render_template('account-info.html', user_id=user_id, customer_info=customer_info)
    else:
        # Handle case where customer is not found
        return "Customer not found", 404

if __name__ == "__main__":
    print("Starting application...")
    initialize_database()  # Call the initialization method
    app.run(debug=True)

# db_ops.create_Customers_table()
# db_ops.create_BoardGames_table()
# db_ops.create_MenuItems_table()
# db_ops.create_Reservations_table()
# db_ops.create_BoardGameOrders_table()
# db_ops.create_MenuOrders_table()

# db_ops.populate_table("Customers", "Customers.csv")
# db_ops.populate_table("BoardGames", "BoardGames.csv")
# db_ops.populate_table("MenuItems", "MenuItems.csv")
# db_ops.populate_table("Reservations", "Reservations.csv")
# db_ops.populate_table("BoardGameOrders", "BoardGameOrders.csv")
# db_ops.populate_table("MenuOrders", "MenuOrders.csv")

# #testing
# db_ops.create_new_customer("alex", "lark@chapman.edu")
# print(db_ops.get_customer_id("alex", "lark@chapman.edu"))
# print(db_ops.check_customer_id("1"))

# while True:
#     user_choice = options()
#     if user_choice == 1:
#         user_menu()
#     if user_choice == 2:
#         create_account()
#     if user_choice == 3:
#         print("Bye bye! Come again soon!")
#         break

# db_ops.destructor()
