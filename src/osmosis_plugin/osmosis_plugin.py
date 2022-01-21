from decimal import Decimal
from senkalib.caaj_plugin import CaajPlugin
from senkalib.caaj_journal import CaajJournal


class OsmosisPlugin(CaajPlugin):
    @classmethod
    def can_handle(cls, transaction) -> bool:
        chain_type = transaction.get_transaction()['header']['chain_id']
        if "osmosis" in chain_type:
            return True
        else:
            return False

    @classmethod
    def get_caajs(cls, transaction) -> CaajJournal:
        pass
