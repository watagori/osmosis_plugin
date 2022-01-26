import re
from decimal import Decimal
from senkalib.caaj_plugin import CaajPlugin
from senkalib.caaj_journal import CaajJournal
from src.osmosis_plugin.get_token_value import GetTokenValue

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

    user_address = OsmosisPlugin.__get_attribute_list(
        event_list, "sender")[0]['value']
    token_in = OsmosisPlugin.__get_attribute_list(
        event_list, "tokens_in")[0]['value']
    token_out = OsmosisPlugin.__get_attribute_list(
        event_list, "tokens_out")[0]['value']

    tokenin_amount = GetTokenValue.get_token_amount(token_in)

    tokenout_amount = GetTokenValue.get_token_amount(token_out)

    tokenin_name = GetTokenValue.get_token_name(token_in)
    tokenout_name = GetTokenValue.get_token_name(token_out)

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

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, user_address)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_fee(cls, transaction, user_address) -> dict:
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
  def __get_caaj_join_pool(cls, transaction) -> CaajJournal:
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    senders = OsmosisPlugin.__get_attribute_list(event_list, "sender")
    recipients = OsmosisPlugin.__get_attribute_list(event_list, "recipient")
    token_values = OsmosisPlugin.__get_attribute_list(event_list, "amount")

    user_address = senders[0]['value']

    credit_amounts = token_values[0]['value'].split(",")

    credit_amount_0 = GetTokenValue.get_token_amount(credit_amounts[0])
    credit_amount_1 = GetTokenValue.get_token_amount(credit_amounts[1])

    debit_amount = GetTokenValue.get_token_amount(token_values[1]['value'])

    credit_name_0 = GetTokenValue.get_token_name(credit_amounts[0])
    credit_name_1 = GetTokenValue.get_token_name(credit_amounts[1])
    debit_name = GetTokenValue.get_token_name(token_values[1]['value'])

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

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, user_address)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_start_farming(cls, transaction) -> CaajJournal:
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    user_address = OsmosisPlugin.__get_attribute_list(
        event_list, "sender")[0]['value']
    recipient = OsmosisPlugin.__get_attribute_list(
        event_list, "recipient")[0]['value']
    token_value = OsmosisPlugin.__get_attribute_list(
        event_list, "amount")[0]['value']

    credit_amount = GetTokenValue.get_token_amount(token_value)

    debit_amount = GetTokenValue.get_token_amount(token_value)

    credit_name = GetTokenValue.get_token_name(token_value)
    debit_name = GetTokenValue.get_token_name(token_value)

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

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, user_address)

    return [caaj_main, caaj_fee]

  @ classmethod
  def __get_caaj_exit_pool(cls, transaction) -> CaajJournal:
    event_list = OsmosisPlugin.__get_event_list(transaction, "transfer")

    senders = OsmosisPlugin.__get_attribute_list(event_list, "sender")
    recipients = OsmosisPlugin.__get_attribute_list(event_list, "recipient")
    token_values = OsmosisPlugin.__get_attribute_list(event_list, "amount")

    user_address = senders[1]['value']

    debit_amounts = token_values[0]['value'].split(",")

    debit_amount_0 = GetTokenValue.get_token_amount(debit_amounts[0])
    debit_amount_1 = GetTokenValue.get_token_amount(debit_amounts[1])

    credit_amount = GetTokenValue.get_token_amount(token_values[1]['value'])

    debit_name_0 = GetTokenValue.get_token_name(debit_amounts[0])
    debit_name_1 = GetTokenValue.get_token_name(debit_amounts[1])
    credit_name = GetTokenValue.get_token_name(token_values[1]['value'])

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

    caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, user_address)

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

    tokenin_amount = GetTokenValue.get_token_amount(amount)

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
