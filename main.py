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


def display_menu():
    print("")
    print("")
    print("--------------------------------")
    print("1 - Create new item")
    print("2 - Modify existing item")
    print("3 - Sell item, decrase amount")
    print("4 - Buy item, increase amount")
    print("5 - Search by name")
    print("6 - Search by id")
    print("7 - Custom query")
    print("8 - List all items")
    print("9 - Delete item")
    print("0 - Exit")
    print("--------------------------------")


def main():
    inventory = Inventory()
    print("Welcome to the inventory managment system!")

    still_running = True
    while still_running:
        display_menu()
        command_dirty: str = input("> ").strip()
        try:
            command: int = int(command_dirty)
        except ValueError:
            print("Invalid command -- Try inputing an integer")
        else:
            assert isinstance(command, int)
            if command == 1:  # create new item
                name = ""
                while name == "":
                    name = input("Enter the name of the new item: ").strip()

                price_valid = False
                price = None
                while not price_valid:
                    price = input(
                        "Enter the price of the new item (you can leave this blank): "
                    ).strip()
                    if price == "":
                        price = None
                        price_valid = True
                    else:
                        try:
                            price = float(price)
                        except ValueError:
                            print(
                                "Invalid price -- Try inputing a floating point number"
                            )
                        else:
                            price_valid = True

                id = inventory.new_item(name, price)
                inventory.display_header()
                inventory.display_item(id)
            elif command == 2:  # modify existing item
                id_correct = False
                id = None
                while not id_correct:
                    id = input("Enter the id of item to modify: ").strip()
                    if id == "":
                        continue
                    else:
                        try:
                            id = int(id)
                        except ValueError:
                            print("Invalid id -- Try inputing an integer")
                        else:
                            id_correct = True
                inventory.display_header()
                inventory.display_item(id)
                name = ""
                while name == "":
                    name = input("Enter the new name for this item: ").strip()
                price_correct = False
                while not price_correct:
                    price = input(
                        "Enter the new price for this item (you can leave this blank): "
                    ).strip()
                    try:
                        price = float(price)
                    except ValueError:
                        print("Invalid price -- Try inputing a floating point number")
                    else:
                        price_correct = True
                inventory.modify_item(id, name, price)
                inventory.display_header()
                inventory.display_item(id)
            elif command == 3:  # sell decrease amount
                id_correct = False
                while not id_correct:
                    id = input("Enter the id of item you are selling: ").strip()
                    if id == "":
                        continue
                    else:
                        try:
                            id = int(id)
                        except ValueError:
                            print("Invalid id -- Try inputing an integer")
                        else:
                            id_correct = True
                inventory.display_header()
                inventory.display_item(id)
                print("This will decrease the amount of this item in the inventory")
                amount_correct = False
                while not amount_correct:
                    amount = input(
                        "Enter the amount of items you are selling: "
                    ).strip()
                    if amount == "":
                        continue
                    else:
                        try:
                            amount = int(amount)
                        except ValueError:
                            print("Invalid amount -- Try inputing an integer")
                        else:
                            amount_correct = True
                inventory.sell_item(id, amount)
                inventory.display_header()
                inventory.display_item(id)
            elif command == 4:  # buy increase amount
                id_correct = False
                while not id_correct:
                    id = input("Enter the id of item you are buying: ").strip()
                    if id == "":
                        continue
                    else:
                        try:
                            id = int(id)
                        except ValueError:
                            print("Invalid id -- Try inputing an integer")
                        else:
                            id_correct = True
                inventory.display_header()
                inventory.display_item(id)
                print("This will increase the amount of this item in the inventory")
                amount_correct = False
                while not amount_correct:
                    amount = input("Enter the amount of items you are buying: ").strip()
                    if amount == "":
                        continue
                    else:
                        try:
                            amount = int(amount)
                        except ValueError:
                            print("Invalid amount -- Try inputing an integer")
                        else:
                            amount_correct = True
                inventory.buy_item(id, amount)
                inventory.display_header()
                inventory.display_item(id)
            elif command == 5:  # search name
                name = ""
                while name == "":
                    name = input("Enter the name of the item: ").strip()

                inventory.display_header()
                inventory.display_item(inventory.get_id_from_name(name))
            elif command == 6:  # search id
                id_correct = False
                while not id_correct:
                    id = input("Enter the id of the item: ").strip()
                    if id == "":
                        continue
                    else:
                        try:
                            id = int(id)
                        except ValueError:
                            print("Invalid id -- Try inputing an integer")
                        else:
                            id_correct = True
                inventory.display_header()
                inventory.display_item(id)
            elif command == 7:  # custom query
                query = input("Enter a valid SQL query: ").strip()
                inventory.query(query)
            elif command == 8:  # list all
                inventory.list_all()
            elif command == 9:  # delete
                id_correct = False
                while not id_correct:
                    id = input("Enter the id of item you want to delete: ").strip()
                    if id == "":
                        continue
                    else:
                        try:
                            id = int(id)
                        except ValueError:
                            print("Invalid id -- Try inputing an integer")
                        else:
                            id_correct = True
                print("This will delete the following item:")
                inventory.display_header()
                inventory.display_item(id)
                answer = ""
                while answer not in ["y", "n"]:
                    answer = input("Are you sure you want to continue? ").strip()
                    if answer == "":
                        continue
                    else:
                        answer = answer[0].lower()
                if answer == "y":
                    inventory.delete(id)
                    print("Item was deleted.")
                else:
                    print("Not deleting.")
            elif command == 0:  # quit
                still_running = False
                print("Bye!")
            elif command == 15:
                inventory.execute_commit("DELETE FROM inventory WHERE (amount = 0)")
            elif command == 14:
                inventory.cursor.executescript(
                    """
    INSERT INTO inventory (name, price) VALUES ('Born On The Streets', 25.9);
    INSERT INTO inventory (name, price) VALUES ('Cat Tee Black T-Shirt', 10.9);
    INSERT INTO inventory (name, price) VALUES ('Crazy Monkey Black T-Shirt', 22.5);
    INSERT INTO inventory (name, price) VALUES ('Crazy Monkey Grey', 134.9);
    INSERT INTO inventory (name, price) VALUES ('Danger Knife Grey', 14.9);
    INSERT INTO inventory (name, price) VALUES ('Dark Thug Blue-Navy T-Shirt', 29.45);
    INSERT INTO inventory (name, price) VALUES ('Man Tie Dye Cinza Grey T-Shirt', 49.9);
    INSERT INTO inventory (name, price) VALUES ('On The Streets Black T-Shirt', 49);
    INSERT INTO inventory (name, price) VALUES ('Release 3D Black T-Shirt', 18.7);
    INSERT INTO inventory (name, price) VALUES ('Short Sleeve T-Shirt', 75);
    INSERT INTO inventory (name, price) VALUES ('Skuul', 14);
    INSERT INTO inventory (name, price) VALUES ('Sphynx Tie Dye Grey T-Shirt', 10.9);
    INSERT INTO inventory (name, price) VALUES ('Sphynx Tie Dye Wine T-Shirt', 9);
    INSERT INTO inventory (name, price) VALUES ('Tso 3D Short Sleeve T-Shirt A', 10.9);
    INSERT INTO inventory (name, price) VALUES ('White DGK Script Tee', 14.9);
    INSERT INTO inventory (name, price) VALUES ('Wine Skul T-Shirt', 13.25);
    """
                )
            else:
                print("Invalid command -- Valid commands show below")

    inventory.close()


if __name__ == "__main__":
    main()
