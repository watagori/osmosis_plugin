import unittest
import json
from senkalib.caaj_journal import CaajJournal
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

    caaj_main = TestOsmosisPlugin.__get_caaj_data(caajs[0])
    caaj_main_model = {
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

    assert caaj_main == caaj_main_model

  def test_get_caajs_transfer(self):
    test_data = TestOsmosisPlugin.__get_test_data("ibc_transfer")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(
        "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
    )

    caaj_main = TestOsmosisPlugin.__get_caaj_data(caajs[0])
    caaj_main_model = {
        "debit_title": "TRANSFER",
        "debit_amount": {
            "ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.000049"
        },
        "debit_from": "juno14ls9rcxxd5gqwshj85dae74tcp3umyppqw2uq4",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_title": "SPOT",
        "credit_amount": {
            "ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.000049"
        },
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "juno14ls9rcxxd5gqwshj85dae74tcp3umyppqw2uq4",
        "comment": "osmosis ibc transfer",
    }

    assert caaj_main == caaj_main_model

  def test_get_caajs_join_pool(self):
    test_data = TestOsmosisPlugin.__get_test_data("join_pool")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(
        "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
    )

    caaj_main = TestOsmosisPlugin.__get_caaj_data(caajs[0])
    caaj_main_model = {
        "debit_title": "LIQUIDITY",
        "credit_title": "SPOT",
        "debit_amount": {"gamm/pool/497": "0.004323192512586978"},
        "credit_amount": {
            "ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.005146",
            "osmo": "0.009969",
        },
        "debit_from": "osmo1c9y7crgg6y9pfkq0y8mqzknqz84c3etr0kpcvj",
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "comment": "osmosis join pool",
    }

    assert caaj_main == caaj_main_model

  def test_get_caajs_exit_pool(self):
    test_data = TestOsmosisPlugin.__get_test_data("exit_pool")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(
        "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
    )

    caaj_main = TestOsmosisPlugin.__get_caaj_data(caajs[0])
    caaj_main_model = {
        "debit_title": "SPOT",
        "credit_title": "LIQUIDITY",
        "credit_amount": {"gamm/pool/497": "0.001161596256293489"},
        "debit_amount": {
            "ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED": "0.001382",
            "osmo": "0.002678",
        },
        "debit_from": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr",
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "osmo1c9y7crgg6y9pfkq0y8mqzknqz84c3etr0kpcvj",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "comment": "osmosis exit pool",
    }

    assert caaj_main == caaj_main_model

  def test_get_caajs_lock_tokens(self):
    test_data = TestOsmosisPlugin.__get_test_data("lock_tokens")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(
        "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
    )

    caaj_main = TestOsmosisPlugin.__get_caaj_data(caajs[0])
    caaj_main_model = {
        "debit_title": "STAKING",
        "credit_title": "SPOT",
        "debit_amount": {"gamm/pool/497": "0.002"},
        "credit_amount": {"gamm/pool/497": "0.002"},
        "debit_from": "osmo1njty28rqtpw6n59sjj4esw76enp4mg6g7cwrhc",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "osmo1njty28rqtpw6n59sjj4esw76enp4mg6g7cwrhc",
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "comment": "osmosis lock tokens",
    }

    assert caaj_main == caaj_main_model

  def test_get_caajs_delegate(self):
    test_data = TestOsmosisPlugin.__get_test_data("delegate")
    transaction = OsmosisTransaction(test_data)
    caajs = OsmosisPlugin.get_caajs(
        "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m", transaction
    )

    caaj_main = TestOsmosisPlugin.__get_caaj_data(caajs[0])
    caaj_main_model = {
        "debit_title": "STAKING",
        "credit_title": "SPOT",
        "credit_amount": {
            "osmo": "0.1",
        },
        "debit_amount": {"osmo": "0.1"},
        "debit_from": "osmovaloper1clpqr4nrk4khgkxj78fcwwh6dl3uw4ep88n0y4",
        "credit_from": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "credit_to": "osmovaloper1clpqr4nrk4khgkxj78fcwwh6dl3uw4ep88n0y4",
        "debit_to": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m",
        "comment": "osmosis delegate",
    }

    assert caaj_main == caaj_main_model

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

    caaj_main = TestOsmosisPlugin.__get_caaj_data(caajs[0])
    caaj_main_model = {
        "debit_title": "SPOT",
        "credit_title": "RECEIVE",
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
        "comment": "osmosis ibc receive",
    }

    assert caaj_main == caaj_main_model

  @classmethod
  def __get_caaj_data(cls, caaj: CaajJournal):
    caaj_data = {
        "debit_title": caaj.debit_title,
        "credit_title": caaj.credit_title,
        "debit_amount": caaj.debit_amount,
        "credit_amount": caaj.credit_amount,
        "debit_from": caaj.debit_from,
        "credit_from": caaj.credit_from,
        "credit_to": caaj.credit_to,
        "debit_to": caaj.debit_to,
        "comment": caaj.comment,
    }
    return caaj_data

  @classmethod
  def __get_test_data(cls, filename):
    with open(f"tests/data/{filename}.json", encoding="utf-8") as jsonfile_local:
      test_data = json.load(jsonfile_local)
    return test_data


if __name__ == "__main__":
  unittest.main()
