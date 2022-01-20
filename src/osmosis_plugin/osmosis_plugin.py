from decimal import Decimal
from senkalib.caaj_plugin import CaajPlugin
from senkalib.caaj_journal import CaajJournal


class OsmosisPlugin:
    @classmethod
    def can_handle(cls):
        return True
