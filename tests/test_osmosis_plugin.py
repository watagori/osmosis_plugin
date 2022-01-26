import json
from senkalib.chain.osmosis.osmosis_transaction import OsmosisTransaction
from osmosis_plugin.osmosis_plugin import OsmosisPlugin


class TestOsmosisPlugin():
  def test_can_handle_00(self):
    test_data = TestOsmosisPlugin.__get_test_data("ibc_received")
    transaction = OsmosisTransaction(test_data)
    chain_type = OsmosisPlugin.can_handle(transaction)
    assert chain_type

  def test_can_handle_01(self):
    test_data = TestOsmosisPlugin.__get_test_data("cosmos_transfer")
    transaction = OsmosisTransaction(test_data)
    chain_type = OsmosisPlugin.can_handle(transaction)
    assert chain_type is False

  def test_get_caajs_00(self):
    test_data = TestOsmosisPlugin.__get_test_data("swap")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(transaction)
    caaj_fee_model = {
        "time": "2022-01-21 02:47:05",
        "transaction_id": "97A5C4A33FA36397A342D34D576AC07BA3F5CB5B7274E2BAF7092470A681FDEB",
        "debit_title": "FEE",
        "debit_amount": {"OSMO": "0"},
        "debit_from": "0x0000000000000000000000000000000000000000",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_title": "SPOT",
        "credit_amount": {"OSMO": "0"},
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "0x0000000000000000000000000000000000000000",
        "comment": "osmosis transactino fee"
    }

    assert caajs[1] == caaj_fee_model

  def test_get_caajs_01(self):
    test_data = TestOsmosisPlugin.__get_test_data("swap")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(transaction)
    caaj_main_model = {
        "debit_title": "SPOT",
        "debit_amount": {"ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.005147"},
        "debit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_title": "SPOT",
        "credit_amount": {"osmo": "0.01"},
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "comment": "osmosis transactino fee"
    }

    assert caajs[0]['debit_amount'] == caaj_main_model['debit_amount']
    assert caajs[0]['debit_from'] == caaj_main_model['debit_from']
    assert caajs[0]['debit_to'] == caaj_main_model['debit_to']
    assert caajs[0]['credit_amount'] == caaj_main_model['credit_amount']
    assert caajs[0]['credit_from'] == caaj_main_model['credit_from']
    assert caajs[0]['credit_to'] == caaj_main_model['credit_to']

  def test_get_caajs_02(self):
    test_data = TestOsmosisPlugin.__get_test_data("join_pool")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(transaction)
    caaj_main_model = {
        "debit_title": "LIQUIDITY",
        "debit_amount": {"gamm/pool/497": "0.004323192512586978"},
        "debit_from": "osmo1c9y7crgg6y9pfkq0y8mqzknqz84c3etr0kpcvj",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_title": "SPOT",
        "credit_amount": {"ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.005146",
                          "osmo": "0.009969"},
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr",
        "comment": "osmosis transactino fee"
    }

    assert caajs[0]['debit_amount'] == caaj_main_model['debit_amount']
    assert caajs[0]['debit_from'] == caaj_main_model['debit_from']
    assert caajs[0]['debit_to'] == caaj_main_model['debit_to']
    assert caajs[0]['credit_amount'] == caaj_main_model['credit_amount']
    assert caajs[0]['credit_from'] == caaj_main_model['credit_from']
    assert caajs[0]['credit_to'] == caaj_main_model['credit_to']

  def test_get_caajs_03(self):
    test_data = TestOsmosisPlugin.__get_test_data("start_farming")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(transaction)
    caaj_main_model = {
        "debit_title": "STAKING",
        "debit_amount": {"gamm/pool/497": "0.002"},
        "debit_from": "osmo1njty28rqtpw6n59sjj4esw76enp4mg6g7cwrhc",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_title": "LIQUIDITY",
        "credit_amount":  {"gamm/pool/497": "0.002"},
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "osmo1njty28rqtpw6n59sjj4esw76enp4mg6g7cwrhc",
    }

    assert caajs[0]['debit_amount'] == caaj_main_model['debit_amount']
    assert caajs[0]['debit_from'] == caaj_main_model['debit_from']
    assert caajs[0]['debit_to'] == caaj_main_model['debit_to']
    assert caajs[0]['credit_amount'] == caaj_main_model['credit_amount']
    assert caajs[0]['credit_from'] == caaj_main_model['credit_from']
    assert caajs[0]['credit_to'] == caaj_main_model['credit_to']

  def test_get_caajs_04(self):
    test_data = TestOsmosisPlugin.__get_test_data("exit_pool")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(transaction)
    caaj_main_model = {
        "debit_title": "SPOT",
        "debit_amount": {"ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.001382",
                         "osmo": "0.002678"},
        "debit_from": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_title": "LIQUIDITY",
        "credit_amount":  {"gamm/pool/497": "0.001161596256293489"},
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "osmo1c9y7crgg6y9pfkq0y8mqzknqz84c3etr0kpcvj",
    }

    assert caajs[0]['debit_amount'] == caaj_main_model['debit_amount']
    assert caajs[0]['debit_from'] == caaj_main_model['debit_from']
    assert caajs[0]['debit_to'] == caaj_main_model['debit_to']
    assert caajs[0]['credit_amount'] == caaj_main_model['credit_amount']
    assert caajs[0]['credit_from'] == caaj_main_model['credit_from']
    assert caajs[0]['credit_to'] == caaj_main_model['credit_to']

  @classmethod
  def __get_test_data(cls, filename):
    with open(f"tests/data/{filename}.json", encoding="utf-8") as jsonfile_local:
      test_data = json.load(jsonfile_local)
    return test_data
