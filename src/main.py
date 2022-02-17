from senkalib.chain.osmosis.osmosis_transaction_generator import OsmosisTransactionGenerator
from senkalib.chain.osmosis.osmosis_transaction import OsmosisTransaction
from osmosis_plugin.osmosis_plugin import OsmosisPlugin
from senkalib.senka_setting import SenkaSetting
import pandas as pd
import sys

if __name__ == '__main__':
  args = sys.argv
  address = args[1]  
  caaj = []
  settings = SenkaSetting({})
  transactions = OsmosisTransactionGenerator\
    .get_transactions(settings, address, None, {})
  for transaction in transactions:
    if OsmosisPlugin.can_handle(transaction):
      caaj_peace = OsmosisPlugin.get_caajs(
        address, transaction
      )
      caaj.extend(caaj_peace)

  caaj_dict_list = map(lambda x: vars(x), caaj)
  df = pd.DataFrame(caaj_dict_list)
  df = df.sort_values('time')
  caaj_csv = df.to_csv(None, index=False)
  print(caaj_csv)
