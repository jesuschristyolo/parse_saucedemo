import logging
import selenium
from selenium.webdriver.common.by import By
from database import crud
import random
from common.exceptions import LoginError

logging.basicConfig(
    level=logging.INFO,
    filename="parse_saucedemo.log",
    filemode="a",
    encoding="utf-8"
)


def parse_login_and_password(driver: selenium.webdriver.Firefox):
    login_credentials_container = driver.find_element(value="login_credentials")

    logins = [login for login
              in login_credentials_container.text.split('\n')
              if login != 'Accepted usernames are:']

    passwords_container = driver.find_element(
        by=By.CLASS_NAME,
        value="login_password"
    )
    password = passwords_container.text.split('\n')[1]

    login = random.choice(logins)
    return login, password


def is_login_successful(driver: selenium.webdriver.Firefox, login: str, password: str):
    driver.find_element(value="user-name").send_keys(login)
    driver.find_element(value="password").send_keys(password)
    driver.find_element(value='login-button').click()

    try:
        driver.find_element(by=By.CLASS_NAME, value='inventory_item_description')
        return True
    except selenium.common.exceptions.NoSuchElementException:
        return False


def handle_login(driver: selenium.webdriver.Firefox, login: str, password: str):
    if is_login_successful(driver, login, password):
        crud.create_new_user(login, password)
        logging.info(f"Авторизация под логином {login} прошла успешно")
        update_data_and_accept_order(driver, login)
    else:
        logging.warning(f"Не удалось авторизоваться под логином {login}")
        raise LoginError(f"Под логином {login} не получилось авторизоваться!")


def authorise(login: str = None, password: str = None):
    driver = selenium.webdriver.Firefox()
    driver.get("https://www.saucedemo.com/")

    if login and password:
        handle_login(driver, login, password)
    elif login or password:
        raise LoginError("Для авторизации необходимо передать и логин, и пароль.")
    else:
        login, password = parse_login_and_password(driver)
        logging.info(f"Выбран рандомный логин: {login}")
        handle_login(driver, login, password)


def collect_user_data(login):
    first_name = input(f"Введите имя пользователя {login}:\n").strip()
    last_name = input(f"Введите фамилию пользователя {login}:\n").strip()
    postal_code = input(f"Введите почтовый индекс пользователя {login}:\n").strip()

    if not first_name or not last_name or not postal_code:
        raise ValueError("Все поля (имя, фамилия, почтовый индекс) должны быть заполнены.")

    return first_name, last_name, postal_code


def add_to_cart_positions(driver: selenium.webdriver.Firefox, login: str):
    add_to_cart_buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn_inventory")

    for button in add_to_cart_buttons:
        button.click()

    driver.find_element(By.CLASS_NAME, value="shopping_cart_link").click()

    items = driver.find_elements(By.CLASS_NAME, "cart_item")
    positions = []

    for item in items:
        splitted_elem = item.text.split('\n')  # Получаем текст из каждого элемента
        positions.append({'title': splitted_elem[1],
                          'description': splitted_elem[2]})

    crud.add_products(positions, login)

    logging.info(f"Для пользователя {login} было добавлено"
                 f" {len(positions)} позиций в корзину")

    return positions


def update_data_and_accept_order(driver: selenium.webdriver.Firefox, login: str):
    # Попытка оформить заказ и внести время выполнения в БД.
    # Если попытка вызвать «continue» или «finish»
    # неудачна - выбрасываем исключение.

    positions = add_to_cart_positions(driver, login)

    driver.find_element(By.ID, "checkout").click()

    first_name, last_name, postal_code = collect_user_data(login)

    driver.find_element(By.ID, "first-name").send_keys(first_name)
    driver.find_element(By.ID, "last-name").send_keys(last_name)
    driver.find_element(By.ID, "postal-code").send_keys(postal_code)

    try:
        driver.find_element(By.ID, "continue").click()
        driver.find_element(By.ID, "finish").click()
        driver.find_element(By.ID, "checkout_complete_container")
    except selenium.common.exceptions.NoSuchElementException:
        logging.warning(f"Не получилось оформить заказ пользователю {login}")
        raise selenium.common.exceptions.NoSuchElementException(
            f"Не удалось подтвердить заказ - "
            f"{login} проблемный аккаунт, просьба сменить username"
        )
    else:
        crud.update_user_info(login, first_name, last_name, postal_code)
        logging.info(f"Для пользователя {login} были обновлены данные в базе")
        crud.update_order_time(login)
        logging.info(f"{login} заказал {len(positions)} позиций")
    finally:
        driver.quit()


def setup_and_authorise():
    crud.create_or_replace_tables()
    authorise()


setup_and_authorise()
