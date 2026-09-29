def test_sign_in_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Sign In" in response.data


def test_sign_in_with_correct_credentials_redirects_to_menu(client):
    response = client.post('/', data={'customer_id': '3', 'password': 'dicebox2026'})
    assert response.status_code == 302
    assert '/menu' in response.headers['Location']


def test_sign_in_with_wrong_password_shows_error(client):
    response = client.post('/', data={'customer_id': '3', 'password': 'wrong-password'})
    assert response.status_code == 200
    assert b"Invalid" in response.data


def test_sign_in_with_nonexistent_id_shows_error(client):
    response = client.post('/', data={'customer_id': '9999', 'password': 'anything'})
    assert response.status_code == 200
    assert b"Invalid" in response.data


def test_menu_requires_login(client):
    response = client.get('/menu')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_menu_accessible_once_logged_in(logged_in_client):
    response = logged_in_client.get('/menu')
    assert response.status_code == 200


def test_logout_clears_session_and_protects_routes_again(logged_in_client):
    assert logged_in_client.get('/menu').status_code == 200
    logged_in_client.get('/logout')
    response = logged_in_client.get('/menu')
    assert response.status_code == 302


def test_create_account_logs_the_new_customer_in(client):
    response = client.post('/create-account', data={
        'userName': 'Test User',
        'userEmail': 'test-user@example.com',
        'userPassword': 'testpass123',
    })
    assert response.status_code == 302
    assert '/menu' in response.headers['Location']


def test_create_account_rejects_short_password(client):
    response = client.post('/create-account', data={
        'userName': 'Test User',
        'userEmail': 'shortpw@example.com',
        'userPassword': 'short',
    })
    assert response.status_code == 200
    assert b"at least 8 characters" in response.data


def test_create_account_rejects_duplicate_email(client):
    data = {'userName': 'First', 'userEmail': 'dup@example.com', 'userPassword': 'testpass123'}
    first = client.post('/create-account', data=data)
    assert first.status_code == 302

    client.get('/logout')
    second = client.post('/create-account', data={**data, 'userName': 'Second'})
    assert second.status_code == 200
    assert b"already registered" in second.data


def test_seed_passwords_are_hashed_not_plaintext(app):
    with app.app_context():
        import boardGameCafe as module
        stored = module.db_ops.get_customer_password_hash(3)
    assert stored is not None
    assert stored != "dicebox2026"
    assert stored.startswith(("pbkdf2:", "scrypt:"))
