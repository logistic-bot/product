import logging
import sqlite3
import __init__  # noqa pylint: disable=W0611

from time import sleep

logger = logging.getLogger(__name__)


class Inventory:
    def __init__(self):  # noqa
        logger.info("Connecting to database")
        self.connection = sqlite3.connect("products.db")
        self.connection.set_trace_callback(logger.debug)
        logger.debug("Getting cursor")
        self.cursor = self.connection.cursor()

        self.init_table()

    @property
    def columncount(self):
        return 4  # this needs to be updated when init_table is changed

    @property
    def rowcount(self):
        self.execute("SELECT COUNT(id) FROM inventory")
        return self.cursor.fetchone()[0]

    def get_ids(self):
        self.execute("SELECT id FROM inventory ORDER BY id")
        return [i[0] for i in self.cursor.fetchall()]

    def get_name_from_id(self, id):
        self.execute("SELECT name FROM inventory WHERE id = :id", {"id": id})
        return self.cursor.fetchone()[0]

    def get_price_from_id(self, id):
        self.execute("SELECT price FROM inventory WHERE id = :id", {"id": id})
        return self.cursor.fetchone()[0]

    def get_amount_from_id(self, id):
        self.execute("SELECT amount FROM inventory WHERE id = :id", {"id": id})
        return self.cursor.fetchone()[0]

    def init_table(self):
        # if you are changing this, do not forget to update rowcount
        logger.debug("Ensuring table layout is correct")
        self.execute_commit(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                name VARCHAR(30) NOT NULL,
                amount INTEGER DEFAULT 0,
                price FLOAT DEFAULT NULL,
                CHECK (name != ''),
                CHECK (amount >= 0),
                CHECK (price >= 0)
            )
            """
        )

    def execute_commit(self, command, values=None):
        self.execute(command, values)
        self.commit()

    def get_id_name_pairs(self):
        self.execute("SELECT id, name FROM inventory ORDER BY id")
        return self.cursor.fetchall()

    def execute(self, command, values=None):
        if values is None:
            values = {}
        logger.debug(
            "Executing command '%s' with values '%s'",
            self.clean_command(command),
            values,
        )
        self.cursor.execute(command, values)
        affected_rows = self.cursor.rowcount
        if affected_rows > -1:
            logger.debug("Affected rows: %s", affected_rows)
            print("Affected items:", affected_rows)

    def commit(self):
        logger.debug("Committing transaction")
        self.connection.commit()

    def close(self):
        logger.info("Closing database connection")
        self.connection.close()

    def clean_command(self, command):
        lines = command.splitlines()
        ret = ""
        for line in lines:
            line = line.strip().replace("\n", "")
            line += " " if line.endswith(",") else ""
            ret += line
        return ret

    def new_item(self, name, price, amount = None):
        logger.info("Creating new item '%s' with price '%s'", name, price)
        command = """INSERT INTO inventory (name, price, amount) VALUES (:name, :price, :amount)"""
        values = {"name": name, "price": price, "amount": amount}
        self.execute_commit(command, values)
        return self.cursor.lastrowid

    def get_id_from_name(self, name):
        text = "get_id_from_name is DEPRECATED and will always return 0, hopefully crashing the program. It was removed to allow for duplicate product names"
        logger.critical(text)
        print(text)
        return 0

    def display_item(self, id):
        if id is None:
            print("No corresponding item")
            return
        self.execute(
            "SELECT id, name, price, amount FROM inventory WHERE id = :id ORDER BY id",
            {"id": id},
        )
        id, name, price, amount = self.cursor.fetchone()
        if price is None:
            price = "-"
        print("{:<10}{:<30}{:<13}{}".format(id, name, price, amount))

    def display_header(self):
        print("id        name                          price        amount")

    def modify_item(self, id, name, price):
        logger.info("Item '%s' now has name '%s' and price '%s'", id, name, price)
        self.execute_commit(
            "UPDATE inventory SET name = :name, price = :price WHERE id = :id",
            {"name": name, "price": price, "id": id},
        )

    def set_price(self, id, price):
        self.execute_commit(
            "UPDATE inventory SET price = :price WHERE id = :id",
            {"price": price, "id": id},
        )

    def set_name(self, id, name):
        self.execute_commit(
            "UPDATE inventory SET name = :name WHERE id = :id", {"name": name, "id": id}
        )

    def set_amount(self, id, amount):
        self.execute_commit(
            "UPDATE inventory SET amount = :amount WHERE id = :id",
            {"amount": amount, "id": id},
        )

    def sell_item(self, id, amount):
        self.change_amount(id, -amount)

    def buy_item(self, id, amount):
        self.change_amount(id, amount)

    def change_amount(self, id, amount):
        self.execute("SELECT amount FROM inventory WHERE id = :id", {"id": id})
        old_amount = self.cursor.fetchone()[0]
        new_amount = old_amount + amount
        assert new_amount >= 0
        logger.info(
            "Item '%s' now has amount '%s' from amount '%s'", id, new_amount, old_amount
        )
        self.execute_commit(
            "UPDATE inventory SET amount = :amount WHERE id = :id",
            {"amount": new_amount, "id": id},
        )

    def list_all(self):
        self.display_header()
        self.execute("SELECT id FROM inventory ORDER BY id")
        ids = []
        id = self.cursor.fetchone()
        while id:
            ids.append(id[0])
            id = self.cursor.fetchone()
        for id in ids:
            self.display_item(id)
        if ids == []:
            print("No corresponding items found")

    def delete(self, id):
        logger.info("Deleting item '%s'", id)
        self.execute_commit("DELETE FROM inventory WHERE id = :id", {"id": id})

    def query(self, query):
        logger.warning("Using query is unsafe!")
        logger.warning("Got query '%s'", query)
        logger.warning("This query may not be safe!")
        logger.warning("This allows the user to execute arbitrary SQL operations!")
        self.execute_commit(query)
        ids = []
        id = self.cursor.fetchone()
        while id:
            ids.append(id[0])
            id = self.cursor.fetchone()
        if ids == []:
            print("No items in inventory.")
        else:
            self.display_header()
            for id in ids:
                self.display_item(id)