import sqlite3
from helper import helper
from werkzeug.security import generate_password_hash


class database():
    # constructor with connection path to DB
    def __init__(self, conn_path):
        self.connection = sqlite3.connect(conn_path, check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()

    # function to return the value of the first row's
    # first attribute of some select query.
    def single_record(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    # ---------------------------------------------------------------
    # Table setup
    # ---------------------------------------------------------------

    def create_BoardGames_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS BoardGames(
            gameID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            gameName VARCHAR(40),
            gameGenre VARCHAR(20),
            MinPlayers INTEGER,
            MaxPlayers INTEGER,
            isAvailable BOOL
        );
        '''
        self.cursor.execute(query)

    def create_MenuItems_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS MenuItems(
            menuItemID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            menuItemName VARCHAR(40),
            menuItemPrice DOUBLE,
            isVegan BOOL,
            description VARCHAR(255)
        );
        '''
        self.cursor.execute(query)

    def create_Toppings_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS Toppings(
            toppingID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            toppingName VARCHAR(40),
            toppingPrice DOUBLE
        );
        '''
        self.cursor.execute(query)

    def create_Customers_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS Customers(
            customerID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            customerName VARCHAR(40),
            customerEmail VARCHAR(60),
            customerPassword VARCHAR(255) NOT NULL DEFAULT ''
        );
        '''
        self.cursor.execute(query)

    def create_Reservations_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS Reservations(
            reservationID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            customerID INTEGER,
            reservationDate VARCHAR(20),
            reservationTime VARCHAR(20),
            guestCount INT,
            FOREIGN KEY (customerID) REFERENCES Customers(customerID)
        );
        '''
        self.cursor.execute(query)

    def create_BoardGameOrders_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS BoardGameOrders(
            boardGameOrderID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            reservationID INTEGER,
            gameID INTEGER,
            isReturned BOOL,
            FOREIGN KEY (reservationID) REFERENCES Reservations(reservationID),
            FOREIGN KEY (gameID) REFERENCES BoardGames(gameID)
        );
        '''
        self.cursor.execute(query)

    def create_MenuOrders_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS MenuOrders(
            menuOrderID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            reservationID INTEGER,
            menuItemID INTEGER,
            itemSpecifications VARCHAR(80),
            sweetness INTEGER,
            temperature VARCHAR(10),
            iceLevel VARCHAR(10),
            FOREIGN KEY (reservationID) REFERENCES Reservations(reservationID),
            FOREIGN KEY (menuItemID) REFERENCES MenuItems(menuItemID)
        );
        '''
        self.cursor.execute(query)

    def create_MenuOrderToppings_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS MenuOrderToppings(
            menuOrderToppingID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            menuOrderID INTEGER,
            toppingID INTEGER,
            FOREIGN KEY (menuOrderID) REFERENCES MenuOrders(menuOrderID),
            FOREIGN KEY (toppingID) REFERENCES Toppings(toppingID)
        );
        '''
        self.cursor.execute(query)

    def drop_table(self, table_name):
        query = f"DROP TABLE IF EXISTS {table_name};"
        self.cursor.execute(query)
        self.connection.commit()

    # ---------------------------------------------------------------
    # Seeding
    # ---------------------------------------------------------------

    def populate_table(self, table, filepath):
        if not self.is_table_empty(table):
            return
        self.cursor.execute(f"PRAGMA table_info({table})")
        columns_info = self.cursor.fetchall()
        columns = [col[1] for col in columns_info if col[5] != 1]  # skip PK column
        data = helper.data_cleaner(filepath)
        attribute_count = len(columns)
        placeholders = ",".join(["?"] * attribute_count)
        column_names = ",".join(columns)
        query = f"INSERT INTO {table} ({column_names}) VALUES({placeholders})"
        self.bulk_insert(query, data)

        # Seed rows for Customers ship with a plaintext demo password in the
        # CSV (see Customers.csv) — hash it immediately so nothing plaintext
        # ever sits in the database.
        if table == "Customers":
            self.hash_seed_passwords()

    def hash_seed_passwords(self):
        self.cursor.execute("SELECT customerID, customerPassword FROM Customers")
        rows = self.cursor.fetchall()
        for customer_id, password in rows:
            if password and not password.startswith(("pbkdf2:", "scrypt:")):
                self.cursor.execute(
                    "UPDATE Customers SET customerPassword = ? WHERE customerID = ?",
                    (generate_password_hash(password), customer_id),
                )
        self.connection.commit()

    def bulk_insert(self, query, data):
        self.cursor.executemany(query, data)
        self.connection.commit()

    def is_table_empty(self, table):
        query = f'SELECT COUNT(*) FROM "{table}";'
        return self.single_record(query) == 0

    # ---------------------------------------------------------------
    # Customers / auth
    # ---------------------------------------------------------------

    def create_new_customer(self, name, email, password_hash):
        query = "INSERT INTO Customers (customerName, customerEmail, customerPassword) VALUES (?, ?, ?)"
        self.cursor.execute(query, (name, email, password_hash))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_customer_id(self, name, email):
        query = "SELECT customerID FROM Customers WHERE customerName = ? AND customerEmail = ?;"
        self.cursor.execute(query, (name, email))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_customer_password_hash(self, customer_id):
        query = "SELECT customerPassword FROM Customers WHERE customerID = ?;"
        self.cursor.execute(query, (customer_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def email_in_use(self, email):
        query = "SELECT COUNT(*) FROM Customers WHERE customerEmail = ?;"
        self.cursor.execute(query, (email,))
        return self.cursor.fetchone()[0] > 0

    def get_customer_info_by_id(self, customer_id):
        query = "SELECT customerName, customerEmail FROM Customers WHERE customerID = ?;"
        self.cursor.execute(query, (customer_id,))
        result = self.cursor.fetchone()
        if result:
            return {'customerName': result[0], 'customerEmail': result[1]}
        return None

    # ---------------------------------------------------------------
    # Board games / menu
    # ---------------------------------------------------------------

    def view_board_games(self):
        query = "SELECT gameID, gameName, gameGenre, MinPlayers, MaxPlayers, isAvailable FROM BoardGames ORDER BY gameName;"
        return self.cursor.execute(query).fetchall()

    def view_menu_items(self):
        query = "SELECT menuItemID, menuItemName, menuItemPrice, description FROM MenuItems ORDER BY menuItemName;"
        return self.cursor.execute(query).fetchall()

    def view_toppings(self):
        query = "SELECT toppingID, toppingName, toppingPrice FROM Toppings ORDER BY toppingName;"
        return self.cursor.execute(query).fetchall()

    def get_board_game_id(self, game_name):
        query = "SELECT gameID FROM BoardGames WHERE gameName = ?;"
        self.cursor.execute(query, (game_name,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_menu_item_id(self, item_name):
        query = "SELECT menuItemID FROM MenuItems WHERE menuItemName = ?;"
        self.cursor.execute(query, (item_name,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_topping_id(self, topping_name):
        query = "SELECT toppingID FROM Toppings WHERE toppingName = ?;"
        self.cursor.execute(query, (topping_name,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    # ---------------------------------------------------------------
    # Reservations
    # ---------------------------------------------------------------

    def create_new_reservation(self, customerID, reservationDate, reservationTime, guestCount):
        query = "INSERT INTO Reservations (customerID, reservationDate, reservationTime, guestCount) VALUES (?, ?, ?, ?)"
        self.cursor.execute(query, (customerID, reservationDate, reservationTime, guestCount))
        self.connection.commit()
        return self.cursor.lastrowid

    def cancel_reservation(self, reservationID, customerID):
        # scoped to customerID so one signed-in customer can't delete another's reservation
        self.cursor.execute(
            "SELECT reservationID FROM Reservations WHERE reservationID = ? AND customerID = ?",
            (reservationID, customerID),
        )
        if not self.cursor.fetchone():
            return False

        # free up any board games that were reserved for this booking, then
        # clear the child order rows before removing the reservation itself
        self.cursor.execute("SELECT gameID FROM BoardGameOrders WHERE reservationID = ?", (reservationID,))
        for (game_id,) in self.cursor.fetchall():
            self.cursor.execute("UPDATE BoardGames SET isAvailable = 1 WHERE gameID = ?", (game_id,))
        self.cursor.execute("DELETE FROM BoardGameOrders WHERE reservationID = ?", (reservationID,))

        self.cursor.execute("SELECT menuOrderID FROM MenuOrders WHERE reservationID = ?", (reservationID,))
        for (menu_order_id,) in self.cursor.fetchall():
            self.cursor.execute("DELETE FROM MenuOrderToppings WHERE menuOrderID = ?", (menu_order_id,))
        self.cursor.execute("DELETE FROM MenuOrders WHERE reservationID = ?", (reservationID,))

        self.cursor.execute("DELETE FROM Reservations WHERE reservationID = ?", (reservationID,))
        self.connection.commit()
        return True

    def add_board_game_order(self, reservation_id, game_id):
        self.cursor.execute(
            "INSERT INTO BoardGameOrders (reservationID, gameID, isReturned) VALUES (?, ?, 0)",
            (reservation_id, game_id),
        )
        self.cursor.execute("UPDATE BoardGames SET isAvailable = 0 WHERE gameID = ?", (game_id,))
        self.connection.commit()

    def add_menu_order(self, reservation_id, menu_item_id, sweetness=None, temperature=None,
                        ice_level=None, item_specifications="", topping_ids=None):
        # ice level only makes sense for a cold drink
        if temperature != "Cold":
            ice_level = None

        self.cursor.execute(
            '''INSERT INTO MenuOrders
               (reservationID, menuItemID, itemSpecifications, sweetness, temperature, iceLevel)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (reservation_id, menu_item_id, item_specifications, sweetness, temperature, ice_level),
        )
        menu_order_id = self.cursor.lastrowid

        for topping_id in (topping_ids or []):
            self.cursor.execute(
                "INSERT INTO MenuOrderToppings (menuOrderID, toppingID) VALUES (?, ?)",
                (menu_order_id, topping_id),
            )
        self.connection.commit()
        return menu_order_id

    def return_board_game(self, board_game_order_id, game_id):
        self.cursor.execute(
            "UPDATE BoardGameOrders SET isReturned = 1 WHERE boardGameOrderID = ?",
            (board_game_order_id,),
        )
        self.cursor.execute("UPDATE BoardGames SET isAvailable = 1 WHERE gameID = ?", (game_id,))
        self.connection.commit()

    def view_reservations(self, customerID):
        query = '''
        SELECT
            r.reservationID,
            r.reservationDate,
            r.reservationTime,
            r.guestCount,
            bg.gameName,
            mi.menuItemName,
            mo.sweetness,
            mo.temperature,
            mo.iceLevel,
            mo.itemSpecifications,
            (SELECT GROUP_CONCAT(t.toppingName) FROM MenuOrderToppings mot
                JOIN Toppings t ON t.toppingID = mot.toppingID
                WHERE mot.menuOrderID = mo.menuOrderID) AS toppings,
            COALESCE(mi.menuItemPrice, 0) + COALESCE(
                (SELECT SUM(t.toppingPrice) FROM MenuOrderToppings mot
                    JOIN Toppings t ON t.toppingID = mot.toppingID
                    WHERE mot.menuOrderID = mo.menuOrderID), 0
            ) AS total
        FROM Reservations r
        LEFT JOIN BoardGameOrders bgo ON bgo.reservationID = r.reservationID
        LEFT JOIN BoardGames bg ON bg.gameID = bgo.gameID
        LEFT JOIN MenuOrders mo ON mo.reservationID = r.reservationID
        LEFT JOIN MenuItems mi ON mi.menuItemID = mo.menuItemID
        WHERE r.customerID = ?
        ORDER BY r.reservationDate DESC, r.reservationTime DESC;
        '''
        self.cursor.execute(query, (customerID,))
        return self.cursor.fetchall()
