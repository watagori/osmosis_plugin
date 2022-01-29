import re
from decimal import Decimal
from senkalib.chain.transaction import Transaction
from senkalib.caaj_plugin import CaajPlugin
from senkalib.caaj_journal import CaajJournal

MEGA = 10**6

EXA = 10**18


class OsmosisPlugin(CaajPlugin):
  chain = "osmosis"

  @classmethod
  def can_handle(cls, transaction: Transaction) -> bool:
    chain_type = transaction.get_transaction()['header']['chain_id']
    if "osmosis" in chain_type:
      return True
    else:
      return False

  @classmethod
  def get_caajs(cls, address: str, transaction: Transaction) -> CaajJournal:
    if transaction.get_transaction()['data']['code'] == 0:
      transaction_type = \
          transaction.get_transaction(
          )['data']['tx']['body']['messages'][0]['@type'].split('.')[-1]

      if transaction_type == "MsgSwapExactAmountIn":
        caaj_main = OsmosisPlugin.__get_caaj_swap(transaction)

      elif transaction_type == "MsgJoinPool":
        caaj_main = OsmosisPlugin.__get_caaj_join_pool(transaction)

      elif transaction_type == "MsgLockTokens":
        caaj_main = OsmosisPlugin.__get_caaj_start_farming(transaction)

      elif transaction_type == "MsgExitPool":
        caaj_main = OsmosisPlugin.__get_caaj_exit_pool(transaction)

      elif transaction_type == "MsgTransfer":
        # ibc transfer
        caaj_main = OsmosisPlugin.__get_caaj_ibc_transfer(transaction)

      elif transaction_type == "MsgSend":
        # send
        caaj_main = OsmosisPlugin.__get_caaj_send(transaction)

      elif transaction_type == "MsgBeginUnlocking":
        caaj_main = OsmosisPlugin.__get_caaj_begin_unlocking(transaction)

      elif transaction_type == "MsgJoinSwapExternAmountIn":
        caaj_main = OsmosisPlugin.__get_caaj_join_swap_extern_amount_in(
            transaction)

      elif transaction_type == "MsgUpdateClient":
        caaj_main = OsmosisPlugin.__get_caaj_ibc_received(transaction)

    if transaction.get_transaction_fee != 0:
      caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, address)
      return [caaj_main, caaj_fee]

    else:
      return [caaj_main]

  @classmethod
  def __get_caaj_swap(cls, transaction: Transaction) -> CaajJournal:
    # data from "type":""event_data"
    event_data = OsmosisPlugin.__get_event_data(transaction, "token_swapped")

    user_address = OsmosisPlugin.__get_attribute_list(
        event_data, "sender")[0]['value']
    token_in = OsmosisPlugin.__get_attribute_list(
        event_data, "tokens_in")[0]['value']
    token_out = OsmosisPlugin.__get_attribute_list(
        event_data, "tokens_out")[0]['value']

    tokenin_amount = OsmosisPlugin.__get_token_amount(token_in)

    tokenout_amount = OsmosisPlugin.__get_token_amount(token_out)

    tokenin_name = OsmosisPlugin.__get_token_name(token_in)
    tokenout_name = OsmosisPlugin.__get_token_name(token_out)

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_name: tokenout_amount},
        "debit_from": user_address,
        "debit_to": user_address,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_name: tokenin_amount},
        "credit_from": user_address,
        "credit_to": user_address,
        "comment": "osmosis swap"
    }

    return caaj_main

  @ classmethod
  def __get_caaj_join_pool(cls, transaction: Transaction) -> CaajJournal:
    event_data = OsmosisPlugin.__get_event_data(transaction, "transfer")

    senders = OsmosisPlugin.__get_attribute_list(event_data, "sender")
    recipients = OsmosisPlugin.__get_attribute_list(event_data, "recipient")
    token_values = OsmosisPlugin.__get_attribute_list(event_data, "amount")

    user_address = senders[0]['value']

    credit_amounts = token_values[0]['value'].split(",")

    credit_amount_0 = OsmosisPlugin.__get_token_amount(credit_amounts[0])
    credit_amount_1 = OsmosisPlugin.__get_token_amount(credit_amounts[1])

    debit_amount = OsmosisPlugin.__get_token_amount(token_values[1]['value'])

    credit_name_0 = OsmosisPlugin.__get_token_name(credit_amounts[0])
    credit_name_1 = OsmosisPlugin.__get_token_name(credit_amounts[1])
    debit_name = OsmosisPlugin.__get_token_name(token_values[1]['value'])

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "LIQUIDITY",
        "debit_amount": {debit_name: debit_amount},
        "debit_from": senders[1]['value'],
        "debit_to": user_address,
        "credit_title": "SPOT",
        "credit_amount": {credit_name_0: credit_amount_0, credit_name_1: credit_amount_1},
        "credit_from": user_address,
        "credit_to": recipients[0]['value'],
        "comment": "osmosis liquidity add"
    }

    return caaj_main

  @ classmethod
  def __get_caaj_start_farming(cls, transaction: Transaction) -> CaajJournal:
    event_data = OsmosisPlugin.__get_event_data(transaction, "transfer")

    user_address = OsmosisPlugin.__get_attribute_list(
        event_data, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_data, "recipient")[0]['value']
    token_value = OsmosisPlugin.__get_attribute_list(
        event_data, "amount")[0]['value']

    credit_amount = OsmosisPlugin.__get_token_amount(token_value)

    debit_amount = OsmosisPlugin.__get_token_amount(token_value)

    credit_name = OsmosisPlugin.__get_token_name(token_value)
    debit_name = OsmosisPlugin.__get_token_name(token_value)

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "STAKING",
        "debit_amount": {debit_name: debit_amount},
        "debit_from": recipient,
        "debit_to": user_address,
        "credit_title": "LIQUIDITY",
        "credit_amount": {credit_name: credit_amount},
        "credit_from": user_address,
        "credit_to": recipient,
        "comment": "osmosis staking"
    }

    return caaj_main

  @ classmethod
  def __get_caaj_exit_pool(cls, transaction: Transaction) -> CaajJournal:
    event_data = OsmosisPlugin.__get_event_data(transaction, "transfer")

    senders = OsmosisPlugin.__get_attribute_list(event_data, "sender")
    recipients = OsmosisPlugin.__get_attribute_list(event_data, "recipient")
    token_values = OsmosisPlugin.__get_attribute_list(event_data, "amount")

    user_address = senders[1]['value']

    debit_amounts = token_values[0]['value'].split(",")

    debit_amount_0 = OsmosisPlugin.__get_token_amount(debit_amounts[0])
    debit_amount_1 = OsmosisPlugin.__get_token_amount(debit_amounts[1])

    credit_amount = OsmosisPlugin.__get_token_amount(token_values[1]['value'])

    debit_name_0 = OsmosisPlugin.__get_token_name(debit_amounts[0])
    debit_name_1 = OsmosisPlugin.__get_token_name(debit_amounts[1])
    credit_name = OsmosisPlugin.__get_token_name(token_values[1]['value'])

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount":  {debit_name_0: debit_amount_0, debit_name_1: debit_amount_1},
        "debit_from": senders[0]['value'],
        "debit_to": user_address,
        "credit_title": "LIQUIDITY",
        "credit_amount": {credit_name: credit_amount},
        "credit_from": user_address,
        "credit_to": recipients[1]['value'],
        "comment": "osmosis liquidity remove"
    }

    return caaj_main

  @ classmethod
  def __get_caaj_ibc_transfer(cls, transaction: Transaction) -> CaajJournal:
    event_data = OsmosisPlugin.__get_event_data(transaction, "transfer")

    sender = OsmosisPlugin.__get_attribute_list(
        event_data, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_data, "recipient")[0]['value']
    amount = OsmosisPlugin.__get_attribute_list(
        event_data, "amount")[0]['value']

    tokenin_amount = OsmosisPlugin.__get_token_amount(amount)

    tokenout_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenin_name = amount[re.search(r'\d+', amount).end():]
    tokenout_name = amount[re.search(r'\d+', amount).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_name: str(tokenout_amount)},
        "debit_from": recipient,
        "debit_to": sender,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_name: str(tokenin_amount)},
        "credit_from": sender,
        "credit_to": recipient,
        "comment": "osmosis transfer"
    }

    return caaj_main

  @ classmethod
  def __get_caaj_send(cls, transaction: Transaction) -> CaajJournal:
    event_data = OsmosisPlugin.__get_event_data(transaction, "transfer")

    sender = OsmosisPlugin.__get_attribute_list(
        event_data, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_data, "recipient")[0]['value']
    amount = OsmosisPlugin.__get_attribute_list(
        event_data, "amount")[0]['value']

    tokenin_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenout_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenin_name = amount[re.search(r'\d+', amount).end():]
    tokenout_name = amount[re.search(r'\d+', amount).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_name: str(tokenout_amount)},
        "debit_from": recipient,
        "debit_to": sender,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_name: str(tokenin_amount)},
        "credit_from": sender,
        "credit_to": recipient,
        "comment": "osmosis transfer"
    }

    return caaj_main

  @ classmethod
  def __get_caaj_begin_unlocking(cls, transaction: Transaction) -> CaajJournal:
    owner = transaction["tx"]["body"]["messages"][0]["owner"]
    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, owner)

    return[caaj_fee]

  @ classmethod
  def __get_caaj_join_swap_extern_amount_in(cls, transaction: Transaction) -> CaajJournal:
    event_data = OsmosisPlugin.__get_event_data(transaction, "transfer")

    sender = OsmosisPlugin.__get_attribute_list(
        event_data, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_data, "recipient")[0]['value']
    amount = OsmosisPlugin.__get_attribute_list(
        event_data, "amount")[0]['value']

    tokenin_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenout_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenin_name = amount[re.search(r'\d+', amount).end():]
    tokenout_name = amount[re.search(r'\d+', amount).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_name: str(tokenout_amount)},
        "debit_from": recipient,
        "debit_to": sender,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_name: str(tokenin_amount)},
        "credit_from": sender,
        "credit_to": recipient,
        "comment": "osmosis join swap"
    }

    return caaj_main

  @classmethod
  def __get_caaj_ibc_received(cls, transaction: Transaction):
    event_transfer = []
    transaction_logs = transaction.get_transaction()['data']['logs']

    for i in range(len(transaction_logs)-1):
      event_transfer_check = list(filter(
          lambda event: event['type'] == "transfer", transaction.get_transaction(
          )['data']['logs'][i]['events']))

      if event_transfer_check:
        event_transfer.append(event_transfer_check)

    sender = OsmosisPlugin.__get_attribute_list(
        event_transfer[0][0], "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_transfer[0][0], "recipient")[0]['value']
    amount = OsmosisPlugin.__get_attribute_list(
        event_transfer[0][0], "amount")[0]['value']

    tokenin_amount = OsmosisPlugin.__get_token_amount(amount)

    tokenout_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenin_name = amount[re.search(r'\d+', amount).end():]
    tokenout_name = amount[re.search(r'\d+', amount).end():]

    tokenout_amount = Decimal.normalize(
        Decimal(tokenout_amount) * Decimal(10 ** 12))

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_name: str(tokenout_amount)},
        "debit_from": recipient,
        "debit_to": sender,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_name: str(tokenin_amount)},
        "credit_from": sender,
        "credit_to": recipient,
        "comment": "osmosis transfer"
    }

    return caaj_main

  @ classmethod
  def __get_caaj_fee(cls, transaction: Transaction, user_address: str) -> CaajJournal:
    caaj_fee = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "FEE",
        "debit_amount": {"OSMO": str(transaction.get_transaction_fee() / Decimal(MEGA))},
        "debit_from": "0x0000000000000000000000000000000000000000",
        "debit_to": user_address,
        "credit_title": "SPOT",
        "credit_amount": {"OSMO": str(transaction.get_transaction_fee() / Decimal(MEGA))},
        "credit_from": user_address,
        "credit_to": "0x0000000000000000000000000000000000000000",
        "comment": "osmosis transactino fee"
    }

    return caaj_fee

  @ classmethod
  def __get_event_data(cls, transaction: Transaction, event_type: str) -> dict:
    event_data = list(filter(
        lambda event: event['type'] == event_type, transaction.get_transaction(
        )['data']['logs'][0]['events']))[-1]

    return event_data

  @ classmethod
  def __get_attribute_list(cls, event_data: dict, attribute_key: str) -> list:
    attribute_list = list(filter(
        lambda attribute: attribute['key'] == attribute_key, event_data['attributes']))

    return attribute_list

  @classmethod
  def __get_token_name(cls, value) -> str:
    token_name = value[re.search(r'\d+', value).end():]
    if token_name == "uosmo":
      token_name = "osmo"
    elif token_name == "uion":
      token_name = "ion"

    return token_name

  @classmethod
  def __get_token_amount(cls, value) -> int:

    if "pool" in value:
      token_amount = str(Decimal(
          re.search(r'\d+', value).group()) / Decimal(EXA))

    else:
      token_amount = str(Decimal(
          re.search(r'\d+', value).group()) / Decimal(MEGA))
    return token_amount
