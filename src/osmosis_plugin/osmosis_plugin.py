import re
from decimal import Decimal
from senkalib.caaj_plugin import CaajPlugin
from senkalib.caaj_journal import CaajJournal

MEGA = 10**6

EXA = 10**18


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
    if transaction.get_transaction()['data']['code'] == 0:
      transaction_type = \
          transaction.get_transaction(
          )['data']['tx']['body']['messages'][0]['@type'].split('.')[-1]

      if transaction_type == "MsgSwapExactAmountIn":
        caaj = OsmosisPlugin.__get_caaj_swap(transaction)
        return caaj

      elif transaction_type == "MsgJoinPool":
        caaj = OsmosisPlugin.__get_caaj_join_pool(transaction)
        return caaj

      elif transaction_type == "MsgLockTokens":
        caaj = OsmosisPlugin.__get_caaj_start_farming(transaction)
        return caaj

      elif transaction_type == "MsgExitPool":
        caaj = OsmosisPlugin.__get_caaj_exit_pool(transaction)
        return caaj

      elif transaction_type == "MsgTransfer":
        # ibc transfer
        caaj_main = OsmosisPlugin.__get_caaj_ibc_transfer(transaction)
        return caaj_main

      elif transaction_type == "MsgSend":
        # send
        caaj_main = OsmosisPlugin.__get_caaj_send(transaction)
        return caaj_main

      elif transaction_type == "MsgBeginUnlocking":
        caaj_main = OsmosisPlugin.__get_caaj_begin_unlocking(transaction)
        return caaj_main

      elif transaction_type == "MsgJoinSwapExternAmountIn":
        caaj_main = OsmosisPlugin.__get_caaj_join_swap_extern_amount_in(
            transaction)
        return caaj_main

  @classmethod
  def __get_caaj_swap(cls, transaction) -> CaajJournal:
    # data from "type":""event_list"
    event_list = OsmosisPlugin.__get_event_list(transaction, "token_swapped")

    address = OsmosisPlugin.__get_attribute_list(
        event_list, "sender")[0]['value']
    token_in = OsmosisPlugin.__get_attribute_list(
        event_list, "tokens_in")[0]['value']
    token_out = OsmosisPlugin.__get_attribute_list(
        event_list, "tokens_out")[0]['value']

    tokenin_amount = Decimal(
        re.search(r'\d+', token_in).group()) / Decimal(MEGA)

    tokenout_amount = Decimal(
        re.search(r'\d+', token_out).group()) / Decimal(MEGA)

    tokenin_denom = token_in[re.search(r'\d+', token_in).end():]
    tokenout_denom = token_out[re.search(r'\d+', token_out).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_denom: str(tokenout_amount)},
        "debit_from": address,
        "debit_to": address,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_denom: str(tokenin_amount)},
        "credit_from": address,
        "credit_to": address,
        "comment": "osmosis swap"
    }

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, address)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_fee(cls, transaction, address) -> dict:
    caaj_fee = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "FEE",
        "debit_amount": {"OSMO": str(transaction.get_transaction_fee() / Decimal(MEGA))},
        "debit_from": "0x0000000000000000000000000000000000000000",
        "debit_to": address,
        "credit_title": "SPOT",
        "credit_amount": {"OSMO": str(transaction.get_transaction_fee() / Decimal(MEGA))},
        "credit_from": address,
        "credit_to": "0x0000000000000000000000000000000000000000",
        "comment": "osmosis transactino fee"
    }

    return caaj_fee

  @ classmethod
  def __get_caaj_join_pool(cls, transaction) -> CaajJournal:
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    senders = OsmosisPlugin.__get_attribute_list(event_list, "sender")
    recipients = OsmosisPlugin.__get_attribute_list(event_list, "recipient")
    amounts = OsmosisPlugin.__get_attribute_list(event_list, "amount")

    address = senders[0]['value']

    credit_amounts = amounts[0]['value'].split(",")

    tokenin_amount_0 = Decimal(
        re.search(r'\d+', credit_amounts[0]).group()) / Decimal(MEGA)
    tokenin_amount_1 = Decimal(
        re.search(r'\d+', credit_amounts[1]).group()) / Decimal(MEGA)

    tokenout_amount = Decimal(
        re.search(r'\d+', amounts[1]['value']).group()) / Decimal(EXA)

    tokenin_denom_0 = credit_amounts[0][re.search(
        r'\d+', credit_amounts[0]).end():]
    tokenin_denom_1 = credit_amounts[1][re.search(
        r'\d+', credit_amounts[1]).end():]
    tokenout_denom = amounts[1]['value'][re.search(
        r'\d+', amounts[1]['value']).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "LIQUIDITY",
        "debit_amount": {tokenout_denom: str(tokenout_amount)},
        "debit_from": senders[1]['value'],
        "debit_to": address,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_denom_0: str(tokenin_amount_0), tokenin_denom_1: str(tokenin_amount_1)},
        "credit_from": address,
        "credit_to": recipients[0]['value'],
        "comment": "osmosis liquidity add"
    }

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, address)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_start_farming(cls, transaction) -> CaajJournal:
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    address = OsmosisPlugin.__get_attribute_list(
        event_list, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_list, "recipient")[0]['value']
    amount = OsmosisPlugin.__get_attribute_list(
        event_list, "amount")[0]['value']

    tokenin_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenout_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenin_denom = amount[re.search(r'\d+', amount).end():]
    tokenout_denom = amount[re.search(r'\d+', amount).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "STAKING",
        "debit_amount": {tokenout_denom: str(tokenout_amount)},
        "debit_from": recipient,
        "debit_to": address,
        "credit_title": "LIQUIDITY",
        "credit_amount": {tokenin_denom: str(tokenin_amount)},
        "credit_from": address,
        "credit_to": recipient,
        "comment": "osmosis staking"
    }

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, address)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_exit_pool(cls, transaction) -> CaajJournal:
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    senders = OsmosisPlugin.__get_attribute_list(event_list, "sender")
    recipients = OsmosisPlugin.__get_attribute_list(event_list, "recipient")
    amounts = OsmosisPlugin.__get_attribute_list(event_list, "amount")

    address = senders[1]['value']

    debit_amounts = amounts[0]['value'].split(",")

    tokenout_amount_0 = Decimal(
        re.search(r'\d+', debit_amounts[0]).group()) / Decimal(MEGA)
    tokenout_amount_1 = Decimal(
        re.search(r'\d+', debit_amounts[1]).group()) / Decimal(MEGA)

    tokenin_amount = Decimal(
        re.search(r'\d+', amounts[1]['value']).group()) / Decimal(EXA)

    tokenout_denom_0 = debit_amounts[0][re.search(
        r'\d+', debit_amounts[0]).end():]
    tokenout_denom_1 = debit_amounts[1][re.search(
        r'\d+', debit_amounts[1]).end():]
    tokenin_denom = amounts[1]['value'][re.search(
        r'\d+', amounts[1]['value']).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount":  {tokenout_denom_0: str(tokenout_amount_0), tokenout_denom_1: str(tokenout_amount_1)},
        "debit_from": senders[0]['value'],
        "debit_to": address,
        "credit_title": "LIQUIDITY",
        "credit_amount": {tokenin_denom: str(tokenin_amount)},
        "credit_from": address,
        "credit_to": recipients[1]['value'],
        "comment": "osmosis liquidity remove"
    }

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, address)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_ibc_transfer(cls, transaction) -> CaajJournal:
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    sender = OsmosisPlugin.__get_attribute_list(
        event_list, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_list, "recipient")[0]['value']
    amount = OsmosisPlugin.__get_attribute_list(
        event_list, "amount")[0]['value']

    tokenin_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenout_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenin_denom = amount[re.search(r'\d+', amount).end():]
    tokenout_denom = amount[re.search(r'\d+', amount).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_denom: str(tokenout_amount)},
        "debit_from": recipient,
        "debit_to": sender,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_denom: str(tokenin_amount)},
        "credit_from": sender,
        "credit_to": recipient,
        "comment": "osmosis transfer"
    }

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, sender)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_send(cls, transaction) -> CaajJournal:
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    sender = OsmosisPlugin.__get_attribute_list(
        event_list, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_list, "recipient")[0]['value']
    amount = OsmosisPlugin.__get_attribute_list(
        event_list, "amount")[0]['value']

    tokenin_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenout_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenin_denom = amount[re.search(r'\d+', amount).end():]
    tokenout_denom = amount[re.search(r'\d+', amount).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_denom: str(tokenout_amount)},
        "debit_from": recipient,
        "debit_to": sender,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_denom: str(tokenin_amount)},
        "credit_from": sender,
        "credit_to": recipient,
        "comment": "osmosis transfer"
    }

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, sender)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_begin_unlocking(cls, transaction):
    owner = transaction["tx"]["body"]["messages"][0]["owner"]
    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, owner)

    return[caaj_fee]

  @ classmethod
  def __get_caaj_join_swap_extern_amount_in(cls, transaction):
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    sender = OsmosisPlugin.__get_attribute_list(
        event_list, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_list, "recipient")[0]['value']
    amount = OsmosisPlugin.__get_attribute_list(
        event_list, "amount")[0]['value']

    tokenin_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenout_amount = Decimal(
        re.search(r'\d+', amount).group()) / Decimal(EXA)

    tokenin_denom = amount[re.search(r'\d+', amount).end():]
    tokenout_denom = amount[re.search(r'\d+', amount).end():]

    caaj_main = {
        "time": transaction.get_timestamp(),
        "transaction_id": transaction.transaction_id,
        "debit_title": "SPOT",
        "debit_amount": {tokenout_denom: str(tokenout_amount)},
        "debit_from": recipient,
        "debit_to": sender,
        "credit_title": "SPOT",
        "credit_amount": {tokenin_denom: str(tokenin_amount)},
        "credit_from": sender,
        "credit_to": recipient,
        "comment": "osmosis join swap"
    }

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, sender)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_event_list(cls, transaction, event_type):
    event_list = list(filter(
        lambda event: event['type'] == event_type, transaction.get_transaction(
        )['data']['logs'][0]['events']))[-1]

    return event_list

  @ classmethod
  def __get_attribute_list(cls, event_list, attribute_key):
    attribute_list = list(filter(
        lambda attribute: attribute['key'] == attribute_key, event_list['attributes']))

    return attribute_list
