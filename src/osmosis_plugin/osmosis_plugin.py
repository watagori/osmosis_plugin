import re
from decimal import Decimal
from unittest import result
from senkalib.chain.transaction import Transaction
from senkalib.caaj_plugin import CaajPlugin
from senkalib.caaj_journal import CaajJournal
from senkalib.caaj_journal_amount import CaajJournalAmount
from senkalib.caaj_journal_meta import CaajJournalMeta
from senkalib.caaj_journal_side import CaajJournalSide
from typing import List
from pandas import DataFrame

MEGA = 10**6
EXA = 10**18

class OsmosisPlugin(CaajPlugin):
  chain = "osmosis"
  PLATFORM = "cosmos_osmosis"

  @classmethod
  def can_handle(cls, transaction: Transaction) -> bool:
    chain_type = transaction.get_transaction()["header"]["chain_id"]
    return OsmosisPlugin.chain in chain_type

  @classmethod
  def get_caajs(cls, address: str, transaction: Transaction, token_original_ids:List) -> List[CaajJournal]:
    caaj = []
    if transaction.get_transaction()["data"]["code"] != 0:
      return caaj
    transaction_type = transaction.get_transaction()["data"]["tx"]["body"]["messages"][0]["@type"]\
        .split(".")[-1]
    if transaction_type in [
        "MsgSwapExactAmountIn",
        "MsgJoinSwapExternAmountIn",
    ]:
      caaj.extend(OsmosisPlugin.__get_caaj_swap(transaction, token_original_ids))
    elif transaction_type in "MsgTransfer":
      caaj.extend(OsmosisPlugin.__get_caaj_transfer(transaction, token_original_ids))
    elif transaction_type == "MsgJoinPool":
      caaj.extend(OsmosisPlugin.__get_caaj_join_pool(transaction, token_original_ids))
    elif transaction_type in "MsgLockTokens":
      caaj.extend(OsmosisPlugin.__get_caaj_send(
          transaction, "STAKING", "SPOT", "osmosis lock tokens", token_original_ids
      ))
    elif transaction_type == "MsgSend":
      caaj.extend(OsmosisPlugin.__get_caaj_send(
          transaction, "TRANSFER", "SPOT", "osmosis send", token_original_ids
      ))
    elif transaction_type == "MsgExitPool":
      caaj.extend(OsmosisPlugin.__get_caaj_exit_pool(transaction, token_original_ids))
    elif transaction_type == "MsgDelegate":
      caaj.extend(OsmosisPlugin.__get_caaj_delegate(transaction, address, token_original_ids))
    elif transaction_type == "MsgUpdateClient":
      caaj.extend(OsmosisPlugin.__get_caaj_update_client(
          transaction, address, token_original_ids))
      return caaj # it ignores fee because this address does not pay fee in case of MsgUpdateClient.

    transaction_fee = transaction.get_transaction_fee()
    if transaction_fee != 0:
      caaj_fee = OsmosisPlugin.__get_caaj_fee(transaction, address, token_original_ids)
      caaj.extend(caaj_fee)

    return caaj

  @classmethod
  def __get_caaj_swap(cls, transaction: Transaction, token_original_ids:List) -> CaajJournal:
    caaj = []
    attributes_list = OsmosisPlugin.__get_attributes_list(
        transaction, "transfer")
    for attribute in attributes_list:
      senders = OsmosisPlugin.__get_attribute_data(attribute, "sender")
      recipients = OsmosisPlugin.__get_attribute_data(attribute, "recipient")
      amounts = OsmosisPlugin.__get_attribute_data(attribute, "amount")
      credit_to = recipients[0]["value"]
      credit_from = senders[0]["value"]

      credit_amount = cls.__get_token_amount(amounts[0]["value"])
      credit_token = cls.__get_token_name(amounts[0]["value"])
      credit_amount_list = [cls.__get_caaj_journal_amount(credit_amount, credit_token,
        cls.chain, token_original_ids)]

      debit_to = recipients[1]["value"]
      debit_from = senders[1]["value"]

      debit_amount = cls.__get_token_amount(amounts[1]["value"])
      debit_token = cls.__get_token_name(amounts[1]["value"])
      debit_amount_list = [cls.__get_caaj_journal_amount(debit_amount, debit_token,
        cls.chain, token_original_ids)]

      debit_title = "SPOT"
      credit_title = "SPOT"

      meta = CaajJournalMeta(
          transaction.get_timestamp(),
          cls.PLATFORM,
          transaction.transaction_id,
          "osmosis swap",
      )

      debit = CaajJournalSide(debit_from, debit_to, debit_title, debit_amount_list)
      credit = CaajJournalSide(credit_from, credit_to, credit_title, credit_amount_list)

#      caaj_journal.set_caaj_destination(
#          debit_from, debit_to, credit_from, credit_to
#      )
#      caaj_journal.set_caaj_value(
#          debit_title, debit_amount_list, credit_title, credit_amount_list
#      )

      caaj_journal = CaajJournal(meta, debit, credit)
      caaj.append(caaj_journal)
    return caaj

  @classmethod
  def __get_caaj_transfer(cls, transaction: Transaction, token_original_ids:List) -> CaajJournal:
    message = transaction.get_transaction(
    )["data"]["tx"]["body"]["messages"][0]
    sender = message["sender"]
    receiver = message["receiver"]
    token = message["token"]["denom"]
    amount = str(Decimal(message["token"]["amount"]) / Decimal(MEGA))
    amount_list = [cls.__get_caaj_journal_amount(amount, token,
        cls.chain, token_original_ids)]

    debit_title = "TRANSFER"
    credit_title = "SPOT"

    meta = CaajJournalMeta(
        transaction.get_timestamp(),
        cls.PLATFORM,
        transaction.transaction_id,
        "osmosis ibc transfer",
    )
    #debit = CaajJournalSide(receiver, sender, sender, receiver)
    debit = CaajJournalSide(receiver, sender, debit_title, amount_list)
    credit = CaajJournalSide(sender,receiver, credit_title, amount_list)
    #caaj_journal.set_caaj_value(debit_title, amount_list, credit_title, amount_list)
    caaj_journal = CaajJournal(meta, debit, credit)

    return [caaj_journal]

  @classmethod
  def __get_caaj_send(
      cls, transaction: Transaction, debit_title: str, credit_title: str, 
      comment: str, token_original_ids:List
  ) -> CaajJournal:
    caaj = []

    attributes_list = OsmosisPlugin.__get_attributes_list(
        transaction, "transfer")
    for attribute in attributes_list:
      senders = OsmosisPlugin.__get_attribute_data(attribute, "sender")
      recipients = OsmosisPlugin.__get_attribute_data(attribute, "recipient")
      amounts = OsmosisPlugin.__get_attribute_data(attribute, "amount")

      credit_from = senders[0]["value"]
      credit_to = recipients[0]["value"]
      debit_to = senders[0]["value"]
      debit_from = recipients[0]["value"]

      token = OsmosisPlugin.__get_token_name(amounts[0]["value"])
      amount = str(OsmosisPlugin.__get_token_amount(amounts[0]["value"]))
      amount_list = [cls.__get_caaj_journal_amount(amount, token,
          cls.chain, token_original_ids)]

      meta = CaajJournalMeta(
          transaction.get_timestamp(),
          cls.PLATFORM,
          transaction.transaction_id,
          comment,
      )

      debit = CaajJournalSide(debit_from, debit_to, debit_title, amount_list)
      credit = CaajJournalSide(credit_from, credit_to, credit_title, amount_list)

      caaj_journal = CaajJournal(meta, debit, credit)
      caaj.append(caaj_journal)

    return caaj

  @classmethod
  def __get_caaj_join_pool(cls, transaction: Transaction, token_original_ids:List) -> CaajJournal:
    caaj = []

    attributes_list = OsmosisPlugin.__get_attributes_list(
        transaction, "transfer")
    for attribute in attributes_list:
      senders = OsmosisPlugin.__get_attribute_data(attribute, "sender")
      recipients = OsmosisPlugin.__get_attribute_data(attribute, "recipient")
      amounts = OsmosisPlugin.__get_attribute_data(attribute, "amount")

      credit_from = senders[0]["value"]
      credit_to = recipients[0]["value"]
      debit_from = senders[1]["value"]
      debit_to = recipients[1]["value"]

      credit_amounts = amounts[0]["value"].split(",")
      credit_amount_list = []
      for i in [0, 1]:
        credit_amount = str(
          OsmosisPlugin.__get_token_amount(credit_amounts[i]))
        credit_token = OsmosisPlugin.__get_token_name(credit_amounts[i])
        credit_amount_list.append(cls.__get_caaj_journal_amount(credit_amount, credit_token,
          cls.chain, token_original_ids))

      debit_amount = OsmosisPlugin.__get_token_amount(amounts[1]["value"])
      debit_token = OsmosisPlugin.__get_token_name(amounts[1]["value"])
      debit_amount_list = [cls.__get_caaj_journal_amount(debit_amount, debit_token,
          cls.chain, token_original_ids)]

      debit_title = "LIQUIDITY"
      credit_title = "SPOT"

      meta = CaajJournalMeta(
          transaction.get_timestamp(),
          cls.PLATFORM,
          transaction.transaction_id,
          "osmosis join pool",
      )
      #caaj_journal.set_caaj_destination(
      #    debit_from, debit_to, credit_from, credit_to
      #)
      #caaj_journal.set_caaj_value(
      #    debit_title, debit_amount_list, credit_title, credit_amount_list
      #)
      debit = CaajJournalSide(debit_from, debit_to, debit_title, debit_amount_list)
      credit = CaajJournalSide(credit_from, credit_to, credit_title, credit_amount_list)
      caaj_journal = CaajJournal(meta, debit, credit)

      caaj.append(caaj_journal)

    return caaj

  @classmethod
  def __get_caaj_exit_pool(cls, transaction: Transaction, token_original_ids:List) -> CaajJournal:
    caaj = []

    attributes_list = OsmosisPlugin.__get_attributes_list(
        transaction, "transfer")
    for attribute in attributes_list:
      senders = OsmosisPlugin.__get_attribute_data(attribute, "sender")
      recipients = OsmosisPlugin.__get_attribute_data(attribute, "recipient")
      amounts = OsmosisPlugin.__get_attribute_data(attribute, "amount")

      credit_from = senders[1]["value"]
      debit_to = recipients[0]["value"]
      credit_to = recipients[1]["value"]
      debit_from = senders[0]["value"]

      debit_amounts = amounts[0]["value"].split(",")

      debit_amount_list = []
      for i in [0, 1]:
        debit_amount = str(
          OsmosisPlugin.__get_token_amount(debit_amounts[i]))
        debit_token = OsmosisPlugin.__get_token_name(debit_amounts[i])
        debit_amount_list.append(cls.__get_caaj_journal_amount(debit_amount, debit_token,
          cls.chain, token_original_ids))

      credit_amount = str(
          OsmosisPlugin.__get_token_amount(amounts[1]["value"]))
      credit_token = OsmosisPlugin.__get_token_name(amounts[1]["value"])
      credit_amount_list = [cls.__get_caaj_journal_amount(credit_amount, credit_token,
          cls.chain, token_original_ids)]

      debit_title = "SPOT"
      credit_title = "LIQUIDITY"


      meta = CaajJournalMeta(
          transaction.get_timestamp(),
          cls.PLATFORM,
          transaction.transaction_id,
          "osmosis exit pool",
      )
      debit = CaajJournalSide(debit_from, debit_to, debit_title, debit_amount_list)
      credit = CaajJournalSide(credit_from, credit_to, credit_title, credit_amount_list)

#      caaj_journal.set_caaj_destination(
#          debit_from, debit_to, credit_from, credit_to
#      )
#      caaj_journal.set_caaj_value(
#          debit_title, debit_amount_list, credit_title, credit_amount_list
#      )

      caaj_journal = CaajJournal(meta, debit, credit)
      caaj.append(caaj_journal)

    return caaj

  @classmethod
  def __get_caaj_fee(cls, transaction: Transaction, user_address: str, token_original_ids:List) -> CaajJournal:
    debit_from = "0x0000000000000000000000000000000000000000"
    debit_to = user_address
    credit_from = user_address
    credit_to = "0x0000000000000000000000000000000000000000"

    debit_title = "FEE"
    credit_title = "SPOT"

    token = "osmo"
    amount = str(transaction.get_transaction_fee() / Decimal(MEGA))
    amount_list = [cls.__get_caaj_journal_amount(amount, token,
        cls.chain, token_original_ids)]

    meta = CaajJournalMeta(
        transaction.get_timestamp(),
        cls.PLATFORM,
        transaction.transaction_id,
        "osmosis swap",
    )
#    caaj_journal.set_caaj_destination(
#        debit_from, debit_to, credit_from, credit_to)
#    caaj_journal.set_caaj_value(debit_title, amount_list, credit_title, amount_list)

    debit = CaajJournalSide(debit_from, debit_to, debit_title, amount_list)
    credit = CaajJournalSide(credit_from, credit_to, credit_title, amount_list)
    caaj_journal = CaajJournal(meta, debit, credit)
    return [caaj_journal]

  @classmethod
  def __get_caaj_delegate(cls, transaction: Transaction, address: str, token_original_ids) -> CaajJournal:
    caaj = []

    attributes_list_delegate = OsmosisPlugin.__get_attributes_list(
        transaction, "delegate"
    )
    for attribute in attributes_list_delegate:
      recipients = OsmosisPlugin.__get_attribute_data(attribute, "validator")
      amounts = OsmosisPlugin.__get_attribute_data(attribute, "amount")

      credit_from = address
      credit_to = recipients[0]["value"]
      debit_to = address
      debit_from = recipients[0]["value"]


      token = "osmo"
      amount = str(OsmosisPlugin.__get_token_amount(amounts[0]["value"]))
      amount_list = [cls.__get_caaj_journal_amount(amount, token,
          cls.chain, token_original_ids)]

      debit_title = "STAKING"
      credit_title = "SPOT"

      meta = CaajJournalMeta(
          transaction.get_timestamp(),
          cls.PLATFORM,
          transaction.transaction_id,
          "osmosis delegate",
      )
      #caaj_journal.set_caaj_destination(
      #    debit_from, debit_to, credit_from, credit_to
      #)
      #caaj_journal.set_caaj_value(
      #    debit_title, amount_list, credit_title, amount_list
      #)
      debit = CaajJournalSide(debit_from, debit_to, debit_title, amount_list)
      credit = CaajJournalSide(credit_from, credit_to, credit_title, amount_list)
      caaj_journal = CaajJournal(meta, debit, credit)

      caaj.append(caaj_journal)

    attributes_list_transfer = OsmosisPlugin.__get_attributes_list(
        transaction, "transfer"
    )
    if len(attributes_list_transfer) > 0:
      caaj_send = OsmosisPlugin.__get_caaj_send(
          transaction, "SPOT", "REWARD", "osmosis reward", token_original_ids
      )

      caaj.extend(caaj_send)
    return caaj

  @classmethod
  def __get_caaj_update_client(
      cls, transaction: Transaction, address: str, token_original_ids
  ) -> CaajJournal:
    caaj = []
    logs = transaction.get_transaction()["data"]["logs"]
    for log in logs:
      fungible_token_packet_list = list(
          filter(
              lambda event: event["type"] == "fungible_token_packet",
              log["events"],
          )
      )
      if not fungible_token_packet_list:
        pass
      else:
        success = OsmosisPlugin.__get_attribute_data(
            fungible_token_packet_list[0]["attributes"], "success"
        )[0]["value"]

        receiver = OsmosisPlugin.__get_attribute_data(
            fungible_token_packet_list[0]["attributes"], "receiver"
        )[0]["value"]

        if success == "true" and receiver == address:
          transfer_list = list(
              filter(
                  lambda event: event["type"] == "transfer",
                  log["events"],
              )
          )

          recipients = OsmosisPlugin.__get_attribute_data(
              transfer_list[0]["attributes"], "recipient"
          )

          senders = OsmosisPlugin.__get_attribute_data(
              transfer_list[0]["attributes"], "sender"
          )

          amounts = OsmosisPlugin.__get_attribute_data(
              transfer_list[0]["attributes"], "amount"
          )

          credit_to = senders[0]["value"]
          credit_from = recipients[0]["value"]
          debit_from = senders[0]["value"]
          debit_to = recipients[0]["value"]

          token = OsmosisPlugin.__get_token_name(amounts[0]["value"])
          amount = str(OsmosisPlugin.__get_token_amount(amounts[0]["value"]))
          amount_list = [cls.__get_caaj_journal_amount(amount, token,
              cls.chain, token_original_ids)]

          debit_title = "SPOT"
          credit_title = "RECEIVE"

          meta = CaajJournalMeta(
              transaction.get_timestamp(),
              cls.PLATFORM,
              transaction.transaction_id,
              "osmosis ibc receive",
          )

          debit = CaajJournalSide(debit_from, debit_to, debit_title, amount_list)
          credit = CaajJournalSide(credit_from, credit_to, credit_title, amount_list)
          #caaj_journal.set_caaj_destination(
          #    debit_from, debit_to, credit_from, credit_to
          #)
          #caaj_journal.set_caaj_value(
          #    debit_title, amount_list, credit_title, amount_list
          #)
          caaj_journal = CaajJournal(meta, debit, credit)

          caaj.append(caaj_journal)

    return caaj

  @classmethod
  def __get_attributes_list(cls, transaction: Transaction, event_type: str) -> dict:
    logs = transaction.get_transaction()["data"]["logs"]
    events_list = []
    for log in logs:
      events = list(
          filter(lambda event: event["type"] == event_type, log["events"])
      )
      if len(events) > 0:
        events_list.append(*events)

    attributes_list = list(map(lambda event: event["attributes"], events_list))

    return attributes_list

  @classmethod
  def __get_attribute_data(cls, attribute: dict, attribute_key: str) -> list:
    attribute_data = list(
        filter(lambda attribute: attribute["key"] == attribute_key, attribute)
    )

    return attribute_data

  @classmethod
  def __get_token_name(cls, value: str) -> str:
    token_name = value[re.search(r"\d+", value).end():]
    if token_name == "uosmo" or token_name == "":
      token_name = "osmo"
    elif token_name == "uion":
      token_name = "ion"

    return token_name

  @classmethod
  def __get_token_amount(cls, value: str) -> int:

    if "pool" in value:
      token_amount = str(
          Decimal(re.search(r"\d+", value).group()) / Decimal(EXA))

    else:
      token_amount = str(
          Decimal(re.search(r"\d+", value).group()) / Decimal(MEGA)
      )
    return token_amount

  @classmethod
  def __get_caaj_journal_amount(cls, amount:Decimal, token:str,
    chain:str, token_original_ids: DataFrame) -> dict:
    symbol = token
    symbol_uuid = 'c0c8e177-53c3-c408-d8bd-067a2ef41ea7'
    original_id = None
    if token != 'osmo':
      original_id = token
      token_info = token_original_ids.query(f"chain == '{chain}' and original_id == '{original_id}'")
      if len(token_info) == 0:
        symbol = None
        symbol_uuid = None
      elif len(token_info) > 1:
        raise ValueError('token_original_ids table has duplicated entries')
      else:
        symbol = str(token_info['symbol'].iloc[-1])
        symbol_uuid = token_info['symbol_uuid'].iloc[-1]

    caaj_journal_amount = CaajJournalAmount(symbol, original_id, symbol_uuid, amount)
    return caaj_journal_amount
