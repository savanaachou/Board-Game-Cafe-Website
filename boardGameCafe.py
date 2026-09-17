import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from database import database

app = Flask(__name__)
# In production set a real SECRET_KEY env var; this fallback is fine for
# local/demo use only.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

db_ops = database("cafe.db")


def ensure_database():
    """Create tables if they don't exist yet and seed them if empty.
    Safe to call on every app startup (dev server or production WSGI
    server) since both operations are idempotent."""
    db_ops.create_Customers_table()
    db_ops.create_BoardGames_table()
    db_ops.create_MenuItems_table()
    db_ops.create_Toppings_table()
    db_ops.create_Reservations_table()
    db_ops.create_BoardGameOrders_table()
    db_ops.create_MenuOrders_table()
    db_ops.create_MenuOrderToppings_table()

    db_ops.populate_table("Customers", "Customers.csv")
    db_ops.populate_table("BoardGames", "BoardGames.csv")
    db_ops.populate_table("MenuItems", "MenuItems.csv")
    db_ops.populate_table("Toppings", "Toppings.csv")
    db_ops.populate_table("Reservations", "Reservations.csv")
    db_ops.populate_table("BoardGameOrders", "BoardGameOrders.csv")
    db_ops.populate_table("MenuOrders", "MenuOrders.csv")


ensure_database()


def login_required(view):
    """Redirect to sign-in if there's no logged-in customer in the session."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "customer_id" not in session:
            return redirect(url_for("sign_in"))
        return view(*args, **kwargs)
    return wrapped


@app.route('/reset-demo-data', methods=['GET'])
def reset_demo_data():
    # Local-dev-only reset: wipes and reseeds every table. Deliberately NOT
    # wired up as a public route on the deployed app -- a GET request that
    # wipes the whole database would be a real vulnerability on a live site.
    # For local resets, just delete cafe.db and restart the app instead
    # (see README); this function is kept for reference/CLI use only.
    if os.environ.get("ALLOW_DB_RESET") != "1":
        return "Not available in this environment.", 403
    for table in ["MenuOrderToppings", "BoardGameOrders", "MenuOrders", "Reservations",
                  "Customers", "BoardGames", "MenuItems", "Toppings"]:
        db_ops.drop_table(table)
    ensure_database()
    return "Database reset and reseeded."


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        entered_id = request.form.get('customer_id', '').strip()
        entered_password = request.form.get('password', '')

        password_hash = db_ops.get_customer_password_hash(entered_id) if entered_id.isdigit() else None
        if password_hash and check_password_hash(password_hash, entered_password):
            session['customer_id'] = int(entered_id)
            return redirect(url_for('menu'))
        return render_template('sign-in.html', error="Invalid ID or password. Please try again!")
    return render_template('sign-in.html')


@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        name = request.form.get('userName', '').strip()
        email = request.form.get('userEmail', '').strip()
        password = request.form.get('userPassword', '')

        if not name or not email or len(password) < 8:
            return render_template(
                'create-account.html',
                error="Please fill out every field; password must be at least 8 characters."
            )
        if db_ops.email_in_use(email):
            return render_template('create-account.html', error="That email is already registered.")

        customer_id = db_ops.create_new_customer(name, email, generate_password_hash(password))
        session['customer_id'] = customer_id
        return redirect(url_for('menu'))
    return render_template('create-account.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('sign_in'))


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

@app.route('/menu', methods=['GET'])
@login_required
def menu():
    return render_template('menu.html', user_id=session['customer_id'])


@app.route('/view-menu', methods=['GET'])
@login_required
def view_menu():
    menu_items = db_ops.view_menu_items()
    return {"menuItems": [list(item) for item in menu_items]}


@app.route('/toppings', methods=['GET'])
@login_required
def view_toppings():
    toppings = db_ops.view_toppings()
    return {"toppings": [list(t) for t in toppings]}


@app.route('/board-games', methods=['GET'])
@login_required
def view_board_games():
    games = db_ops.view_board_games()
    return {"games": [list(game) for game in games]}


@app.route('/reserve', methods=['POST'])
@login_required
def make_reservation():
    customer_id = session['customer_id']
    reserve_date = request.form.get('date')
    reserve_time = request.form.get('time')
    guest_count = request.form.get('guestCount')
    game_name = request.form.get('boardGame') or None
    drink_name = request.form.get('drink') or None

    if not all([reserve_date, reserve_time, guest_count]):
        return jsonify({"error": "Missing required fields"}), 400

    reservation_id = db_ops.create_new_reservation(customer_id, reserve_date, reserve_time, guest_count)

    if game_name:
        game_id = db_ops.get_board_game_id(game_name)
        if game_id:
            db_ops.add_board_game_order(reservation_id, game_id)

    if drink_name:
        menu_item_id = db_ops.get_menu_item_id(drink_name)
        if menu_item_id:
            sweetness = request.form.get('sweetness', type=int)
            temperature = request.form.get('temperature') or None
            ice_level = request.form.get('iceLevel') or None
            specifications = request.form.get('specifications', '').strip()
            topping_names = request.form.getlist('toppings')
            topping_ids = [tid for tid in (db_ops.get_topping_id(name) for name in topping_names) if tid]

            db_ops.add_menu_order(
                reservation_id, menu_item_id,
                sweetness=sweetness, temperature=temperature, ice_level=ice_level,
                item_specifications=specifications, topping_ids=topping_ids,
            )

    return jsonify({"message": "Reservation created successfully!", "reservationID": reservation_id})


@app.route('/reservations/<int:customer_id>', methods=['GET'])
@login_required
def view_reservations(customer_id):
    # only the signed-in customer can view their own reservations
    if customer_id != session['customer_id']:
        return jsonify({"error": "Forbidden"}), 403

    rows = db_ops.view_reservations(customer_id)
    reservations = [
        {
            "reservationID": r[0],
            "date": r[1],
            "time": r[2],
            "guestCount": r[3],
            "game": r[4],
            "drink": r[5],
            "sweetness": r[6],
            "temperature": r[7],
            "iceLevel": r[8],
            "specifications": r[9],
            "toppings": r[10],
            "total": r[11],
        }
        for r in rows
    ]
    return {"reservations": reservations}


@app.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@login_required
def delete_reservation(reservation_id):
    deleted = db_ops.cancel_reservation(reservation_id, session['customer_id'])
    if not deleted:
        return jsonify({"error": "Reservation not found"}), 404
    return jsonify({"message": "Reservation cancelled"})


@app.route('/account-info')
@login_required
def account_info():
    user_id = session['customer_id']
    customer_info = db_ops.get_customer_info_by_id(user_id)
    if not customer_info:
        return "Customer not found", 404
    return render_template('account-info.html', user_id=user_id, customer_info=customer_info)


if __name__ == "__main__":
    app.run(debug=True)
