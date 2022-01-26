import json
from osmosis_plugin.get_token_value import GetTokenValue


class TestGetTokenValue():
  def test_get_token_name_01(self):
    test_data = TestGetTokenValue.__get_test_data("swap")
    test_value = test_data['data']['logs'][0]['events'][4]['attributes'][2]['value']
    token_name = GetTokenValue.get_token_name(test_value)
    assert token_name == "osmo"

  def test_get_token_name_02(self):
    test_data = TestGetTokenValue.__get_test_data("swap")
    test_value = test_data['data']['logs'][0]['events'][4]['attributes'][5]['value']
    token_name = GetTokenValue.get_token_name(test_value)
    assert token_name == "ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED"

  def test_get_token_amount_01(self):
    test_data = TestGetTokenValue.__get_test_data("swap")
    test_value = test_data['data']['logs'][0]['events'][4]['attributes'][2]['value']
    token_amount = GetTokenValue.get_token_amount(test_value)
    assert token_amount == "0.01"

  @classmethod
  def __get_test_data(cls, filename):
    with open(f"tests/data/{filename}.json", encoding="utf-8") as jsonfile_local:
      test_data = json.load(jsonfile_local)
    return test_data
