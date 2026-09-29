def make_basic_reservation(client, **overrides):
    data = {
        'date': '2026-10-01', 'time': '18:00', 'guestCount': '3',
    }
    data.update(overrides)
    return client.post('/reserve', data=data)


def test_reserve_requires_login(client):
    response = make_basic_reservation(client)
    assert response.status_code == 302


def test_reserve_requires_date_time_and_guest_count(logged_in_client):
    response = logged_in_client.post('/reserve', data={'date': '2026-10-01'})
    assert response.status_code == 400


def test_bare_reservation_with_no_game_or_drink_succeeds(logged_in_client):
    response = make_basic_reservation(logged_in_client)
    assert response.status_code == 200
    assert 'reservationID' in response.get_json()


def test_reserving_a_game_makes_it_unavailable(logged_in_client):
    before = {g[1]: g[5] for g in logged_in_client.get('/board-games').get_json()['games']}
    assert before['Catan'] == 1

    make_basic_reservation(logged_in_client, boardGame='Catan')

    after = {g[1]: g[5] for g in logged_in_client.get('/board-games').get_json()['games']}
    assert after['Catan'] == 0


def test_cold_drink_with_topping_and_customization(logged_in_client):
    response = make_basic_reservation(
        logged_in_client,
        drink='Taro Milk Tea', sweetness='50', temperature='Cold', iceLevel='Light',
        toppings=['Boba'], specifications='less sugar please',
    )
    assert response.status_code == 200
    reservation_id = response.get_json()['reservationID']

    reservations = logged_in_client.get('/reservations/3').get_json()['reservations']
    res = next(r for r in reservations if r['reservationID'] == reservation_id)

    assert res['drink'] == 'Taro Milk Tea'
    assert res['sweetness'] == 50
    assert res['temperature'] == 'Cold'
    assert res['iceLevel'] == 'Light'
    assert res['toppings'] == 'Boba'
    assert res['specifications'] == 'less sugar please'
    assert abs(res['total'] - (4.75 + 0.50)) < 0.001


def test_hot_drink_never_stores_an_ice_level(logged_in_client):
    response = make_basic_reservation(
        logged_in_client,
        drink='Matcha Latte', sweetness='75', temperature='Hot', iceLevel='Normal',
    )
    reservation_id = response.get_json()['reservationID']

    reservations = logged_in_client.get('/reservations/3').get_json()['reservations']
    res = next(r for r in reservations if r['reservationID'] == reservation_id)

    assert res['temperature'] == 'Hot'
    assert res['iceLevel'] is None


def test_customer_cannot_view_another_customers_reservations(logged_in_client):
    response = logged_in_client.get('/reservations/1')
    assert response.status_code == 403


def test_deleting_a_reservation_removes_it_and_frees_the_game(logged_in_client):
    response = make_basic_reservation(logged_in_client, boardGame='Chess')
    reservation_id = response.get_json()['reservationID']

    games = {g[1]: g[5] for g in logged_in_client.get('/board-games').get_json()['games']}
    assert games['Chess'] == 0

    delete_response = logged_in_client.delete(f'/reservations/{reservation_id}')
    assert delete_response.status_code == 200

    reservations = logged_in_client.get('/reservations/3').get_json()['reservations']
    assert all(r['reservationID'] != reservation_id for r in reservations)

    games = {g[1]: g[5] for g in logged_in_client.get('/board-games').get_json()['games']}
    assert games['Chess'] == 1


def test_deleting_someone_elses_reservation_is_rejected(logged_in_client):
    # reservationID 1 belongs to seeded customer #1, not the logged-in #3
    response = logged_in_client.delete('/reservations/1')
    assert response.status_code == 404

    # and it should still be there
    import boardGameCafe as module
    remaining = module.db_ops.view_reservations(1)
    assert any(r[0] == 1 for r in remaining)


def test_deleting_a_nonexistent_reservation_returns_404(logged_in_client):
    response = logged_in_client.delete('/reservations/99999')
    assert response.status_code == 404
