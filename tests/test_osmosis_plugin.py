import unittest
import json
from senkalib.chain.osmosis.osmosis_transaction import OsmosisTransaction
from osmosis_plugin.osmosis_plugin import OsmosisPlugin


class TestOsmosisPlugin(unittest.TestCase):
    def test_can_handle_ibc_received(self):
        test_data = TestOsmosisPlugin.__get_test_data("ibc_received_effect1")
        transaction = OsmosisTransaction(test_data)
        chain_type = OsmosisPlugin.can_handle(transaction)
        assert chain_type

    def test_can_handle_cosmos_transfer(self):
        test_data = TestOsmosisPlugin.__get_test_data("cosmos_transfer")
        transaction = OsmosisTransaction(test_data)
        chain_type = OsmosisPlugin.can_handle(transaction)
        assert chain_type is False

    def test_get_caajs_swap(self):
        test_data = TestOsmosisPlugin.__get_test_data("swap")
        transaction = OsmosisTransaction(test_data)
        caajs = OsmosisPlugin.get_caajs(
            "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
        )
        caaj_main_model = {
            "transaction_id": "97A5C4A33FA36397A342D34D576AC07BA3F5CB5B7274E2BAF7092470A681FDEB",
            "debit_title": "SPOT",
            "debit_amount": {
                "ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.005147"
            },
            "debit_from": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr",
            "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
            "credit_title": "SPOT",
            "credit_amount": {"osmo": "0.01"},
            "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
            "credit_to": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr",
            "comment": "osmosis swap",
        }

        assert caajs[0].debit_amount == caaj_main_model["debit_amount"]
        assert caajs[0].debit_from == caaj_main_model["debit_from"]
        assert caajs[0].debit_to == caaj_main_model["debit_to"]
        assert caajs[0].credit_amount == caaj_main_model["credit_amount"]
        assert caajs[0].credit_to == caaj_main_model["credit_to"]
        assert caajs[0].transaction_id == caaj_main_model["transaction_id"]
        assert caajs[0].credit_from == caaj_main_model["credit_from"]
        assert caajs[1].transaction_id == caaj_main_model["transaction_id"]

        assert len(caajs) == 2

    def test_get_caajs_send(self):
        test_data = TestOsmosisPlugin.__get_test_data("start_farming")
        transaction = OsmosisTransaction(test_data)
        caajs = OsmosisPlugin.get_caajs(
            "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
        )
        caaj_main_model = {
            "debit_amount": {"gamm/pool/497": "0.002"},
            "credit_amount": {"gamm/pool/497": "0.002"},
            "debit_from": "osmo1njty28rqtpw6n59sjj4esw76enp4mg6g7cwrhc",
            "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        }
        assert caajs[0].debit_amount == caaj_main_model["debit_amount"]
        assert caajs[0].credit_amount == caaj_main_model["credit_amount"]

    def test_get_caajs_join_pool(self):
        test_data = TestOsmosisPlugin.__get_test_data("join_pool")
        transaction = OsmosisTransaction(test_data)
        caajs = OsmosisPlugin.get_caajs(
            "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
        )
        caaj_main_model = {
            "debit_amount": {"gamm/pool/497": "0.004323192512586978"},
            "credit_amount": {
                "ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.005146",
                "osmo": "0.009969",
            },
            "debit_from": "osmo1c9y7crgg6y9pfkq0y8mqzknqz84c3etr0kpcvj",
            "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
            "credit_to": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr",
            "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        }
        assert caajs[0].debit_amount == caaj_main_model["debit_amount"]
        assert caajs[0].credit_amount == caaj_main_model["credit_amount"]
    def test_get_caajs_exit_pool(self):
        test_data = TestOsmosisPlugin.__get_test_data("exit_pool")
        transaction = OsmosisTransaction(test_data)
        caajs = OsmosisPlugin.get_caajs(
            "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
        )
        caaj_main_model = {
            "credit_amount": {"gamm/pool/497": "0.001161596256293489"},
            "debit_amount": {
                "ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.001382",
                "osmo": "0.002678",
            },
            "debit_from": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr",
            "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
            "credit_to": "osmo1c9y7crgg6y9pfkq0y8mqzknqz84c3etr0kpcvj",
            "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        }


        assert caajs[0].debit_amount == caaj_main_model["debit_amount"]
        assert caajs[0].credit_amount == caaj_main_model["credit_amount"]

    def test_get_caajs_delegate(self):
        test_data = TestOsmosisPlugin.__get_test_data("delegate")
        transaction = OsmosisTransaction(test_data)
        caajs = OsmosisPlugin.get_caajs(
            "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
        )
        caaj_main_model = {
            "credit_amount": {
                "osmo": "0.1",
            },
            "debit_amount": {"osmo": "0.1"},
            "debit_from": "osmovaloper1clpqr4nrk4khgkxj78fcwwh6dl3uw4ep88n0y4",
            "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
            "credit_to": "osmovaloper1clpqr4nrk4khgkxj78fcwwh6dl3uw4ep88n0y4",
            "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        }

        assert caajs[0].debit_amount == caaj_main_model["debit_amount"]
        assert caajs[0].credit_amount == caaj_main_model["credit_amount"]


    def test_get_caajs_ibc_received_effect0(self):
        test_data = TestOsmosisPlugin.__get_test_data("ibc_received_effect0")
        transaction = OsmosisTransaction(test_data)
        caajs = OsmosisPlugin.get_caajs(
            "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
        )

        assert caajs == []

    def test_get_caajs_ibc_received_effect1(self):
        test_data = TestOsmosisPlugin.__get_test_data("ibc_received_effect1")
        transaction = OsmosisTransaction(test_data)
        caajs = OsmosisPlugin.get_caajs(
            "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
        )

        caaj_main_model = {
            "credit_amount": {
                "ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2": "0.25"
            },
            "debit_amount": {
                "ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2": "0.25"
            },
            "debit_from": "osmo1yl6hdjhmkf37639730gffanpzndzdpmhxy9ep3",
            "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
            "credit_to": "osmo1yl6hdjhmkf37639730gffanpzndzdpmhxy9ep3",
            "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        }


        assert caajs[0].debit_amount == caaj_main_model["debit_amount"]
        assert caajs[0].credit_amount == caaj_main_model["credit_amount"]

    @classmethod
    def __get_test_data(cls, filename):
        with open(f"tests/data/{filename}.json", encoding="utf-8") as jsonfile_local:
            test_data = json.load(jsonfile_local)
        return test_data






if __name__ == "__main__":
    unittest.main()

