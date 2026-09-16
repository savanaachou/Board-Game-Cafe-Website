import sqlite3
from helper import helper

class database():
    # constructor with connection path to DB
    def __init__(self, conn_path):
        self.connection = sqlite3.connect(conn_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        print("connection made..")

    # function to return the value of the first row's 
    # first attribute of some select query.
    # best used for querying a single aggregate select 
    # query with no parameters
    def single_record(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]
    
    # function to return the value of the first row's 
    # first attribute of some select query.
    # best used for querying a single aggregate select 
    # query with named placeholders
    def single_record_params(self, query, dictionary):
        self.cursor.execute(query, dictionary)
        return self.cursor.fetchone()[0]

    # function that creates BoardGames table in our database
    def create_BoardGames_table(self):
        query = '''
        CREATE TABLE BoardGames(
            gameID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            gameName VARCHAR(20),
            gameGenre VARCHAR(20),
            MinPlayers INTEGER,
            MAXPLAYERS INTEGER,
            isAvailable BOOL
        );
        '''
        self.cursor.execute(query)
        print('BoardGames table Created')

    # function that creates Menu table in our database
    def create_MenuItems_table(self):
        query = '''
        CREATE TABLE MenuItems(
            menuItemID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            menuItemName VARCHAR(20),
            menuItemPrice DOUBLE,
            isVegan BOOL
        );
        '''
        self.cursor.execute(query)
        print('MenuItems table Created')

    # function that creates customers table in our database
    def create_Customers_table(self):
        query = '''
        CREATE TABLE Customers(
            customerID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            customerName VARCHAR(20),
            customerEmail VARCHAR(20)
        );
        '''
        self.cursor.execute(query)
        print('Customers table Created')

    # function that creates reservations table in our database
    def create_Reservations_table(self):
        query = '''
        CREATE TABLE Reservations(
            reservationID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            customerID INTEGER,
            reservationDate VARCHAR(20),
            reservationTime VARCHAR(20),
            guestCount INT,
            FOREIGN KEY (customerID) REFERENCES Customers(customerID)
        );
        '''
        self.cursor.execute(query)
        print('Reservations table Created')

    # function that creates BoardGameOrders table in our database
    def create_BoardGameOrders_table(self):
        query = '''
        CREATE TABLE BoardGameOrders(
            boardGameOrderID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            reservationID INTEGER,
            gameID INTEGER,
            isReturned BOOL,
            FOREIGN KEY (reservationID) REFERENCES Reservations(reservationID),
            FOREIGN KEY (gameID) REFERENCES BoardGames(gameID)
        );
        '''
        self.cursor.execute(query)
        print('BoardGameOrders table Created')    

    # function that creates MenuOrders table in our database
    def create_MenuOrders_table(self):
        query = '''
        CREATE TABLE MenuOrders(
            menuOrderID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            reservationID INTEGER,
            menuItemID INTEGER,
            itemSpecifications VARCHAR(20),
            FOREIGN KEY (reservationID) REFERENCES Reservations(reservationID),
            FOREIGN KEY (menuItemID) REFERENCES MenuItems(menuItemID)
        );
        '''
        self.cursor.execute(query)
        print('MenuOrders table Created')

    def drop_table(self, table_name):
        try:
            query = f"DROP TABLE IF EXISTS {table_name};"
            self.cursor.execute(query)
            self.connection.commit()
            print(f"Table {table_name} dropped successfully!")
        except sqlite3.Error as e:
            print(f"Error dropping table {table_name}: {e}")

    #function to populate a given table with a given filepath
    def populate_table(self, table, filepath):
        if self.is_table_empty(table):
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns_info = self.cursor.fetchall()
            columns = [col[1] for col in columns_info if col[5] != 1]  # col[5] is 'pk' (primary key flag)
            data = helper.data_cleaner(filepath)
            attribute_count = len(columns)
            placeholders = ("?," * attribute_count)[:-1]
            column_names = ",".join(columns)
            query = f"INSERT INTO {table} ({column_names}) VALUES({placeholders})"
            self.bulk_insert(query, data)

    # function for bulk inserting records
    # best used for inserting many records with parameters
    def bulk_insert(self, query, data):
        self.cursor.executemany(query, data)
        self.connection.commit()

    # function that returns if given table has records
    def is_table_empty(self, table):
        query = f'''
        SELECT COUNT(*)
        FROM "{table}";
        '''
        result = self.single_record(query)
        return result == 0
    
    #Function to create a new customer given the name and email
    def create_new_customer(self, name, email):
        query = f"INSERT INTO Customers (customerName, customerEmail) Values(?, ?)"
        self.cursor.execute(query, (name, email))

    #Function to return a customerID based on name and email
    def get_customer_id(self, name, email):
        query = '''
        SELECT customerID
        FROM Customers
        WHERE customerName LIKE ? AND customerEmail LIKE ?;
        '''
        return self.single_record_params(query, (name, email))
    
    #Function to check if an ID exists in the customers table
    def check_customer_id(self, id):
        if not id:  # Check for empty or None input
            print("Invalid input: ID is None or empty.")
            return False

        if not isinstance(id, (str, int)):  # Ensure ID is a string or integer
            print(f"Invalid input type: ID must be a string or integer, got {type(id)}.")
            return False

        try:
            query = '''
            SELECT COUNT(*)
            FROM Customers
            WHERE customerID = ?
            '''
            result = self.cursor.execute(query, (id,)).fetchone()  # Fetch the result

            # Extract the count from the result tuple (assuming single row)
            count = result[0] if result else 0
            print(f"Checking if customer ID is valid. ID: {id}, Count of ID: {count}")
            return count != 0  # Return True if the count is not 0
        except Exception as e:
            print(f"An error occurred while checking customer ID: {e}")
            return False
        
        # Function to return customer's name and email based on customerID
    def get_customer_info_by_id(self, customer_id):
        query = '''
        SELECT customerName, customerEmail
        FROM Customers
        WHERE customerID = ?;
        '''
        self.cursor.execute(query, (customer_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                'customerName': result[0],
                'customerEmail': result[1]
            }
        else:
            return None
    
    def view_board_games(self):
        query = "SELECT gameName, gameGenre, MinPlayers, MaxPlayers, isAvailable FROM BoardGames;"
        result = self.cursor.execute(query)
        print("view board games called")
        return result
    
    def view_menu_items(self):
        query = "SELECT MenuItemName, MenuItemPrice FROM MenuItems;"
        print("view MenuItems called")
        return self.cursor.execute(query)

    def create_new_reservation(self, customerID, reservationDate, reservationTime, guestCount):
        query = f"INSERT INTO Reservations (customerID, reservationDate, reservationTime, guestCount) Values(?, ?, ?, ?)"
        self.cursor.execute(query, (customerID, reservationDate, reservationTime, guestCount))
    
    def cancel_reservation(self, reservationID):
        query = f"DELETE FROM Reservations WHERE reservationID = ?"
        self.cursor.execute(query, (reservationID,))

    def view_reservations(self, customerID):
        query = f'''
        SELECT Reservations.reservationDate, Reservations.reservationTime, Reservations.guestCount, (
        SELECT SUM(MenuItems.MenuItemPrice)
        FROM MenuOrders
        INNER JOIN MenuItems on MenuOrders.menuItemID = MenuItems.menuItemID
        WHERE MenuOrders.reservationID = Reservations.reservationID)
        FROM Reservations
        WHERE customerID LIKE ?;
        '''
        print ("view reservations called with customerID: " + customerID)


        self.cursor.execute(query, (customerID))
        results = self.cursor.fetchall()
       
        helper.pretty_print(results)
        return results

    def reserve_board_game(self, reservationID, boardGameName):
        try:
            self.cursor.execute("BEGIN TRANSACTION;")
            insert_query = '''
            INSERT INTO BoardGameOrders (reservationID, boardGameID, isReturned)
            VALUES (?, (SELECT boardGameID FROM BoardGames WHERE gameName = ?), 0);
            '''
            self.cursor.execute(insert_query, (reservationID, boardGameName))
        
            update_query = '''
            UPDATE BoardGames
            SET isAvailable = 0
            WHERE gameName = ?;
            '''
            self.cursor.execute(update_query, (boardGameName,))
        
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Transaction failed: {e}")

    def return_board_game(self, BoardGameOrderID, boardGameName):
        try:
            self.cursor.execute("BEGIN TRANSACTION;")
            update_query_1 = '''
            UPDATE BoardGameOrders
            SET isReturned = true
            WHERE BoardGameOrderID = ?;
            '''
            self.cursor.execute(update_query_1, (BoardGameOrderID))
        
            update_query_2 = '''
            UPDATE BoardGames
            SET isAvailable = 2
            WHERE gameName = ?;
            '''
            self.cursor.execute(update_query_2, (boardGameName,))
        
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Transaction failed: {e}")

    def get_reservation_details(self, reservationID):
        create_view_query = '''
        CREATE VIEW reservationDetails AS
        SELECT Reservations.reservationID, MenuItems.menuItemName, MenuItems.menuItemPrice, MenuOrders.itemSpecifications, BoardGames.gameName
        FROM Reservations
        INNER JOIN MenuOrders ON Reservations.reservationID = MenuOrders.reservationID
        INNER JOIN MenuItems ON MenuOrders.menuItemID = MenuItems.menuItemID
        INNER JOIN BoardGameOrders ON Reservations.reservationID = BoardGameOrders.reservationID
        INNER JOIN BoardGames ON BoardGameOrders.gameID = BoardGames.gameID
        '''

        select_query = '''
        SELECT menuItemName, menuItemPrice, itemSpecifications, gameName
        FROM reservationDetails
        WHERE reservationID = ?
        '''

        self.cursor.execute(create_view_query)
        self.cursor.execute(select_query, (reservationID,))
        return self.cursor.fetchall()
