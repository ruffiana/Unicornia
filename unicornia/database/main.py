from pathlib import Path

try:
    from .sqlite_interface import DBInterface
    from . import data_classes
except ImportError:
    from sqlite_interface import DBInterface
    import data_classes


TABLES_DATA_CLASSES = {
    "DiscordUser": data_classes.DiscordUser,
    "ShopEntry": data_classes.ShopEntry,
    "ShopEntryItem": data_classes.ShopEntryItem,
    "XPCurrencyReward": data_classes.XPCurrencyReward,
    "XpRoleReward": data_classes.XpRoleReward,
    "XpShopOwnedItem": data_classes.XpShopOwnedItem,
    "BankUsers": data_classes.BankUser,
    "Clubs": data_classes.Club,
}


# Example usage
if __name__ == "__main__":
    from pprint import pprint

    filepath = Path(__file__).parent / "_db" / "NadekoBot.db"
    db_interface = DBInterface(filepath, tables_data_classes=TABLES_DATA_CLASSES)

    # tables = db_interface.list_tables()
    # tables.sort()
    # pprint(tables)

    for table, class_ in TABLES_DATA_CLASSES.items():
        data = getattr(db_interface, table)
        data_obj = class_(**data[0])
        pprint(data_obj)
