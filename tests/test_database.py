import sqlite3

import pytest


def test_foreign_keys_are_enforced(app):
    import boardGameCafe as module
    db = module.db_ops

    with pytest.raises(sqlite3.IntegrityError):
        db.cursor.execute(
            "INSERT INTO Reservations (customerID, reservationDate, reservationTime, guestCount) "
            "VALUES (?, ?, ?, ?)",
            (99999, '2026-01-01', '12:00', 2),
        )


def test_seed_customer_count_matches_csv(app):
    import boardGameCafe as module
    db = module.db_ops
    db.cursor.execute("SELECT COUNT(*) FROM Customers")
    count = db.cursor.fetchone()[0]
    assert count == 4  # matches the 4 data rows in Customers.csv, not 5 (no header-row bug)


def test_ensure_database_is_idempotent(app):
    """Calling ensure_database() again shouldn't drop/duplicate/error."""
    import boardGameCafe as module
    module.ensure_database()
    module.ensure_database()

    module.db_ops.cursor.execute("SELECT COUNT(*) FROM Customers")
    count = module.db_ops.cursor.fetchone()[0]
    assert count == 4  # still 4, not re-seeded into duplicates
