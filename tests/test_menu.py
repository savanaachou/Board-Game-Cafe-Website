def test_board_games_requires_login(client):
    assert client.get('/board-games').status_code == 302


def test_board_games_returns_seeded_games(logged_in_client):
    response = logged_in_client.get('/board-games')
    assert response.status_code == 200
    games = response.get_json()['games']
    assert len(games) == 7
    names = [g[1] for g in games]
    assert "Catan" in names


def test_menu_items_include_description_for_every_drink(logged_in_client):
    response = logged_in_client.get('/view-menu')
    items = response.get_json()['menuItems']
    assert len(items) == 5
    for item in items:
        menu_item_id, name, price, description = item
        assert description, f"{name} is missing a description"


def test_menu_items_were_renamed_away_from_boba_in_the_name(logged_in_client):
    response = logged_in_client.get('/view-menu')
    names = [item[1] for item in response.get_json()['menuItems']]
    assert "Strawberry Milk" in names
    assert "Brown Sugar Milk Tea" in names
    # old names should be fully gone, not just supplemented
    assert "Strawberry Boba" not in names
    assert "Brown Sugar Boba" not in names


def test_toppings_endpoint_returns_boba(logged_in_client):
    response = logged_in_client.get('/toppings')
    assert response.status_code == 200
    toppings = response.get_json()['toppings']
    names_and_prices = [(t[1], t[2]) for t in toppings]
    assert ("Boba", 0.5) in names_and_prices
