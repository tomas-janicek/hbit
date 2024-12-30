from hbit_api.adapters import repository
from hbit_api.domain import models


def test_user_add_get(session: repository.Session) -> None:
    seen_tracker = repository.SeenSetTracker[models.User]()
    user_repository = repository.SqlUserRepository(
        session=session, seen_tracker=seen_tracker
    )

    # act
    user = models.User(
        email="test@email.com",
        name="test",
        hashed_password="hashed-password",
        is_active=True,
        is_superuser=False,
    )
    user_repository.add(user)

    # assert
    assert user == user_repository.get(user.email)


def test_user_get_by_id(session: repository.Session) -> None:
    seen_tracker = repository.SeenSetTracker[models.User]()
    user_repository = repository.SqlUserRepository(
        session=session, seen_tracker=seen_tracker
    )

    #   act
    user = models.User(
        email="test@email.com",
        name="test",
        hashed_password="hashed-password",
        is_active=True,
        is_superuser=False,
    )
    user_repository.add(user)

    # commit is necessary to be able to use user.id
    session.commit()

    # assert
    assert user == user_repository.get_by_id(user.id)  # type: ignore


def test_user_delete(session: repository.Session) -> None:
    seen_tracker = repository.SeenSetTracker[models.User]()
    user_repository = repository.SqlUserRepository(
        session=session, seen_tracker=seen_tracker
    )

    # act
    user = models.User(
        email="test@email.com",
        name="test",
        hashed_password="hashed-password",
        is_active=True,
        is_superuser=False,
    )
    user_repository.add(user)

    # assert
    assert user == user_repository.get(user.email)

    user_repository.delete(user)

    assert not user_repository.get(user.email)
