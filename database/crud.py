from database.db_engine import sync_engine, Base, session_factory
from database.models import Users, Positions
import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="../parse_saucedemo.log",
    filemode="a",
    encoding="utf-8"
)


def create_or_replace_tables():
    # sync_engine.echo = True
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)


def create_new_user(username: str, password: str):
    with session_factory() as session:
        existing_user = session.query(Users).filter_by(username=username).first()
        if existing_user:
            logging.warning(f"Повторная попытка добавить в "
                            f"БД существующий username {username}")

            raise ValueError(f"Пользователь {username} уже существует.")
        new_user = Users(username=username, password=password)
        session.add(new_user)
        session.flush()
        session.commit()


def update_user_info(username: str, first_name: str, last_name: str, postal_code: str):
    with session_factory() as session:
        user = session.query(Users).filter(Users.username == username).first()
        user.first_name = first_name
        user.last_name = last_name
        user.postal_code = postal_code
        session.commit()


def update_order_time(username: str):
    with session_factory() as session:
        user = session.query(Users).filter(Users.username == username).first()
        user.order_timestamp = datetime.datetime.now()
        session.commit()


def add_products(positions: list[dict], username: str):
    with session_factory() as session:
        user = session.query(Users).filter_by(username=username).first()
        for position in positions:
            position = Positions(user_id=user.id,
                                 name=position['title'],
                                 description=position['description']
                                 )
            session.add(position)
        session.commit()


