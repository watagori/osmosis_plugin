import json
from senkalib.chain.osmosis.osmosis_transaction import OsmosisTransaction
from osmosis_plugin.osmosis_plugin import OsmosisPlugin


class TestOsmosisPlugin():
    def test_can_handle_00(self):
        test_data = TestOsmosisPlugin.__get_test_data("swap")
        transaction = OsmosisTransaction(test_data)
        chain_type = OsmosisPlugin.can_handle(transaction)
        assert chain_type

    def test_can_handle_01(self):
        test_data = TestOsmosisPlugin.__get_test_data("cosmos_transfer")
        transaction = OsmosisTransaction(test_data)
        chain_type = OsmosisPlugin.can_handle(transaction)
        assert chain_type is False

    @classmethod
    def __get_test_data(cls, filename):
        with open(f"tests/data/{filename}.json", encoding="utf-8") as jsonfile_local:
            test_data = json.load(jsonfile_local)
        return test_data
