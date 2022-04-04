import re
import uuid
from decimal import Decimal

import pandas as pd
from senkalib.caaj_journal import CaajJournal
from senkalib.chain.transaction import Transaction

MEGA = 10**6
EXA = 10**18


class OsmosisPlugin:
    chain = "osmosis"
    PLATFORM = "osmosis"
    TOKEN_ORIGINAL_ID_URL = "https://raw.githubusercontent.com/ca3-caaip/token_original_id/master/token_original_id.csv"

    @classmethod
    def can_handle(cls, transaction: Transaction, token_original_ids: list) -> bool:
        chain_type = transaction.get_transaction()["header"]["chain_id"]
        return OsmosisPlugin.chain in chain_type

    @classmethod
    def get_caajs(cls, address: str, transaction: Transaction) -> list:
        caaj = []
        if transaction.get_transaction()["data"]["code"] != 0:
            return caaj

        transaction_type = transaction.get_transaction()["data"]["tx"]["body"][
            "messages"
        ][0]["@type"].split(".")[-1]

        if transaction_type in [
            "MsgSwapExactAmountIn",
            "MsgJoinSwapExternAmountIn",
        ]:
            caaj.extend(OsmosisPlugin._get_caaj_swap(transaction))

        elif transaction_type in "MsgTransfer":
            caaj.extend(OsmosisPlugin._get_caaj_transfer(transaction))

        elif transaction_type == "MsgJoinPool":
            caaj.extend(OsmosisPlugin._get_caaj_join_pool(transaction))

        elif transaction_type in ["MsgSend", "MsgLockTokens"]:
            caaj.extend(OsmosisPlugin._get_caaj_lock_token(transaction))

        elif transaction_type == "MsgExitPool":
            caaj.extend(OsmosisPlugin._get_caaj_exit_pool(transaction))

        elif transaction_type == "MsgDelegate":
            caaj.extend(OsmosisPlugin._get_caaj_delegate(address, transaction))

        elif transaction_type == "MsgUpdateClient":
            caaj.extend(OsmosisPlugin._get_caaj_update_client(address, transaction))
            return caaj  # it ignores fee because this address does not pay fee in case of MsgUpdateClient.

        transaction_fee = transaction.get_transaction_fee()
        if transaction_fee != 0:
            caaj_fee = OsmosisPlugin._get_caaj_fee(address, transaction)
            caaj.extend(caaj_fee)

        return caaj

    @classmethod
    def _get_caaj_swap(cls, transaction: Transaction) -> list:
        caaj = []
        attributes_list = OsmosisPlugin._get_attributes_list(transaction, "transfer")
        for attribute in attributes_list:
            caaj_to = OsmosisPlugin._get_attribute_data(attribute, "sender")[0]["value"]
            caaj_from = OsmosisPlugin._get_attribute_data(attribute, "recipient")[0][
                "value"
            ]

            amounts = OsmosisPlugin._get_attribute_data(attribute, "amount")
            amount_to = OsmosisPlugin._get_token_amount(amounts[0]["value"])
            token_original_id_to = OsmosisPlugin._get_token_original_id(
                amounts[0]["value"]
            )
            token_original_id_to_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(amounts[0]["value"])
            )

            token_symbol_to = OsmosisPlugin._get_token_symbol(
                token_original_id_to_for_symbol
            )
            symbol_uuid_to = OsmosisPlugin._get_symbol_uuid(
                token_original_id_to, cls.chain, token_symbol_to
            )

            amount_from = OsmosisPlugin._get_token_amount(amounts[1]["value"])
            token_original_id_from = OsmosisPlugin._get_token_original_id(
                amounts[1]["value"]
            )
            token_original_id_from_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(amounts[1]["value"])
            )

            token_symbol_from = OsmosisPlugin._get_token_symbol(
                token_original_id_from_for_symbol
            )
            symbol_uuid_from = OsmosisPlugin._get_symbol_uuid(
                token_original_id_from, cls.chain, token_symbol_from
            )

            trade_uuid = OsmosisPlugin._get_uuid()

            caaj_journal_get = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "swap",
                transaction.get_transaction_id(),
                trade_uuid,
                "lose",
                amount_to,
                token_symbol_to,
                token_original_id_to,
                symbol_uuid_to,
                caaj_to,
                caaj_from,
                "",
            )

            caaj_journal_lose = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "swap",
                transaction.get_transaction_id(),
                OsmosisPlugin._get_uuid(),
                "lose",
                amount_from,
                token_symbol_from,
                token_original_id_from,
                symbol_uuid_from,
                caaj_from,
                caaj_to,
                "",
            )
            caaj.append(caaj_journal_get)
            caaj.append(caaj_journal_lose)
        return caaj

    @classmethod
    def _get_caaj_transfer(cls, transaction: Transaction) -> list:
        caaj = []
        message = transaction.get_transaction()["data"]["tx"]["body"]["messages"][0]

        caaj_journal_lose = CaajJournal(
            transaction.get_timestamp(),
            cls.chain,
            cls.PLATFORM,
            "transfer",
            transaction.get_transaction_id(),
            OsmosisPlugin._get_uuid(),
            "lose",
            str(Decimal(message["token"]["amount"]) / Decimal(MEGA)),
            OsmosisPlugin._get_token_symbol(message["token"]["denom"]),
            message["token"]["denom"],
            OsmosisPlugin._get_uuid(),
            message["sender"],
            message["receiver"],
            "",
        )
        caaj.append(caaj_journal_lose)
        return caaj

    @classmethod
    def _get_caaj_join_pool(cls, transaction: Transaction) -> list:
        caaj = []
        attributes_list = OsmosisPlugin._get_attributes_list(transaction, "transfer")
        for attribute in attributes_list:
            senders = OsmosisPlugin._get_attribute_data(attribute, "sender")
            recipients = OsmosisPlugin._get_attribute_data(attribute, "recipient")
            amounts = OsmosisPlugin._get_attribute_data(attribute, "amount")
            amount_one = OsmosisPlugin._get_token_amount(
                amounts[0]["value"].split(",")[0]
            )
            token_original_id_one_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(
                    amounts[0]["value"].split(",")[0]
                )
            )

            token_symbol_one = OsmosisPlugin._get_token_symbol(
                token_original_id_one_for_symbol
            )
            token_original_id_one = OsmosisPlugin._get_token_original_id(
                amounts[0]["value"].split(",")[0]
            )
            symbol_uuid_one = OsmosisPlugin._get_symbol_uuid(
                token_original_id_one, cls.chain, token_symbol_one
            )

            trade_uuid = OsmosisPlugin._get_uuid()

            caaj_journal_lose_one = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "lend",
                transaction.get_transaction_id(),
                trade_uuid,
                "deposit",
                str(Decimal(amount_one)),
                token_symbol_one,
                OsmosisPlugin._get_token_original_id(amounts[0]["value"].split(",")[0]),
                symbol_uuid_one,
                senders[0]["value"],
                recipients[0]["value"],
                "",
            )
            caaj.append(caaj_journal_lose_one)

            amount_two = OsmosisPlugin._get_token_amount(
                amounts[0]["value"].split(",")[1]
            )
            token_original_id_two_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(
                    amounts[0]["value"].split(",")[1]
                )
            )

            token_symbol_two = OsmosisPlugin._get_token_symbol(
                token_original_id_two_for_symbol
            )

            token_original_id_two = OsmosisPlugin._get_token_original_id(
                amounts[0]["value"].split(",")[1]
            )
            symbol_uuid_two = OsmosisPlugin._get_symbol_uuid(
                token_original_id_two, cls.chain, token_symbol_two
            )

            caaj_journal_lose_two = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "lend",
                transaction.get_transaction_id(),
                trade_uuid,
                "deposit",
                str(Decimal(amount_two)),
                token_symbol_two,
                OsmosisPlugin._get_token_original_id(amounts[0]["value"].split(",")[1]),
                symbol_uuid_two,
                senders[0]["value"],
                recipients[0]["value"],
                "",
            )
            caaj.append(caaj_journal_lose_two)

            token_original_id_liquidity = OsmosisPlugin._get_token_original_id(
                amounts[1]["value"]
            )
            token_original_id_liquidity_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(amounts[1]["value"])
            )

            token_symbol_liquidity = OsmosisPlugin._get_token_symbol(
                token_original_id_liquidity_for_symbol
            )
            symbol_uuid_liquidity = OsmosisPlugin._get_symbol_uuid(
                token_original_id_liquidity, cls.chain, token_symbol_liquidity
            )

            amount_liquidity = OsmosisPlugin._get_token_amount(amounts[1]["value"])

            caaj_journal_get_liquidity = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "lend",
                transaction.get_transaction_id(),
                trade_uuid,
                "get_liquidity",
                amount_liquidity,
                token_symbol_liquidity,
                token_original_id_liquidity,
                symbol_uuid_liquidity,
                senders[1]["value"],
                recipients[1]["value"],
                "",
            )
            caaj.append(caaj_journal_get_liquidity)
        return caaj

    @classmethod
    def _get_caaj_lock_token(cls, transaction: Transaction) -> list:
        caaj = []
        attributes_list = OsmosisPlugin._get_attributes_list(transaction, "transfer")
        for attribute in attributes_list:
            senders = OsmosisPlugin._get_attribute_data(attribute, "sender")
            recipients = OsmosisPlugin._get_attribute_data(attribute, "recipient")
            amounts = OsmosisPlugin._get_attribute_data(attribute, "amount")

            token_original_id_liquidity = OsmosisPlugin._get_token_original_id(
                amounts[0]["value"]
            )
            token_original_id_liquidity_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(amounts[0]["value"])
            )

            token_symbol_liquidity = OsmosisPlugin._get_token_symbol(
                token_original_id_liquidity_for_symbol
            )
            symbol_uuid_liquidity = OsmosisPlugin._get_symbol_uuid(
                token_original_id_liquidity, cls.chain, token_symbol_liquidity
            )

            amount_liquidity = OsmosisPlugin._get_token_amount(amounts[0]["value"])

            caaj_journal_get_liquidity = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "lend",
                transaction.get_transaction_id(),
                OsmosisPlugin._get_uuid(),
                "deposit_liquidity",
                amount_liquidity,
                token_symbol_liquidity,
                token_original_id_liquidity,
                symbol_uuid_liquidity,
                senders[0]["value"],
                recipients[0]["value"],
                "",
            )
            caaj.append(caaj_journal_get_liquidity)
        return caaj

    @classmethod
    def _get_caaj_exit_pool(cls, transaction: Transaction) -> list:
        caaj = []
        attributes_list = OsmosisPlugin._get_attributes_list(transaction, "transfer")
        for attribute in attributes_list:
            senders = OsmosisPlugin._get_attribute_data(attribute, "sender")
            recipients = OsmosisPlugin._get_attribute_data(attribute, "recipient")
            amounts = OsmosisPlugin._get_attribute_data(attribute, "amount")
            amount_one = OsmosisPlugin._get_token_amount(
                amounts[0]["value"].split(",")[0]
            )
            token_original_id_one_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(
                    amounts[0]["value"].split(",")[0]
                )
            )

            token_symbol_one = OsmosisPlugin._get_token_symbol(
                token_original_id_one_for_symbol
            )
            token_original_id_one = OsmosisPlugin._get_token_original_id(
                amounts[0]["value"].split(",")[0]
            )
            symbol_uuid_one = OsmosisPlugin._get_symbol_uuid(
                token_original_id_one, cls.chain, token_symbol_one
            )

            trade_uuid = OsmosisPlugin._get_uuid()

            caaj_journal_lose_one = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "lend",
                transaction.get_transaction_id(),
                trade_uuid,
                "withdraw_liquidity",
                str(Decimal(amount_one)),
                token_symbol_one,
                OsmosisPlugin._get_token_original_id(amounts[0]["value"].split(",")[0]),
                symbol_uuid_one,
                senders[0]["value"],
                recipients[0]["value"],
                "",
            )
            caaj.append(caaj_journal_lose_one)

            amount_two = OsmosisPlugin._get_token_amount(
                amounts[0]["value"].split(",")[1]
            )
            token_original_id_two_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(
                    amounts[0]["value"].split(",")[1]
                )
            )

            token_symbol_two = OsmosisPlugin._get_token_symbol(
                token_original_id_two_for_symbol
            )

            token_original_id_two = OsmosisPlugin._get_token_original_id(
                amounts[0]["value"].split(",")[1]
            )
            symbol_uuid_two = OsmosisPlugin._get_symbol_uuid(
                token_original_id_two, cls.chain, token_symbol_two
            )

            caaj_journal_lose_two = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "lend",
                transaction.get_transaction_id(),
                trade_uuid,
                "withdraw_liquidity",
                str(Decimal(amount_two)),
                token_symbol_two,
                OsmosisPlugin._get_token_original_id(amounts[0]["value"].split(",")[1]),
                symbol_uuid_two,
                senders[0]["value"],
                recipients[0]["value"],
                "",
            )
            caaj.append(caaj_journal_lose_two)

            token_original_id_liquidity = OsmosisPlugin._get_token_original_id(
                amounts[1]["value"]
            )
            token_original_id_liquidity_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(amounts[1]["value"])
            )

            token_symbol_liquidity = OsmosisPlugin._get_token_symbol(
                token_original_id_liquidity_for_symbol
            )
            symbol_uuid_liquidity = OsmosisPlugin._get_symbol_uuid(
                token_original_id_liquidity, cls.chain, token_symbol_liquidity
            )

            amount_liquidity = OsmosisPlugin._get_token_amount(amounts[1]["value"])

            caaj_journal_get_liquidity = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "lend",
                transaction.get_transaction_id(),
                trade_uuid,
                "lose_liquidity",
                amount_liquidity,
                token_symbol_liquidity,
                token_original_id_liquidity,
                symbol_uuid_liquidity,
                senders[1]["value"],
                recipients[1]["value"],
                "",
            )
            caaj.append(caaj_journal_get_liquidity)
        return caaj

    @classmethod
    def _get_caaj_delegate(cls, address: str, transaction: Transaction) -> list:
        caaj = []

        attributes_list_delegate = OsmosisPlugin._get_attributes_list(
            transaction, "delegate"
        )
        for attribute in attributes_list_delegate:
            caaj_to = OsmosisPlugin._get_attribute_data(attribute, "validator")[0][
                "value"
            ]
            amounts = OsmosisPlugin._get_attribute_data(attribute, "amount")
            caaj_from = address

            token_original_id_liquidity = OsmosisPlugin._get_token_original_id(
                amounts[0]["value"]
            )
            token_original_id_liquidity_for_symbol = (
                OsmosisPlugin._get_token_original_id_for_symbol(amounts[0]["value"])
            )

            token_symbol_liquidity = OsmosisPlugin._get_token_symbol(
                token_original_id_liquidity_for_symbol
            )
            symbol_uuid_liquidity = OsmosisPlugin._get_symbol_uuid(
                token_original_id_liquidity, cls.chain, token_symbol_liquidity
            )

            amount_liquidity = OsmosisPlugin._get_token_amount(amounts[0]["value"])

            caaj_journal_get_liquidity = CaajJournal(
                transaction.get_timestamp(),
                cls.chain,
                cls.PLATFORM,
                "lend",
                transaction.get_transaction_id(),
                OsmosisPlugin._get_uuid(),
                "deposit",
                amount_liquidity,
                token_symbol_liquidity,
                token_original_id_liquidity,
                symbol_uuid_liquidity,
                caaj_from,
                caaj_to,
                "",
            )
            caaj.append(caaj_journal_get_liquidity)
        return caaj

    @classmethod
    def _get_caaj_update_client(cls, address: str, transaction: Transaction) -> list:
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
                success = OsmosisPlugin._get_attribute_data(
                    fungible_token_packet_list[0]["attributes"], "success"
                )[0]["value"]

                receiver = OsmosisPlugin._get_attribute_data(
                    fungible_token_packet_list[0]["attributes"], "receiver"
                )[0]["value"]

                if success == "true" and receiver == address:
                    transfer_list = list(
                        filter(
                            lambda event: event["type"] == "transfer",
                            log["events"],
                        )
                    )

                    recipients = OsmosisPlugin._get_attribute_data(
                        transfer_list[0]["attributes"], "recipient"
                    )

                    senders = OsmosisPlugin._get_attribute_data(
                        transfer_list[0]["attributes"], "sender"
                    )

                    amounts = OsmosisPlugin._get_attribute_data(
                        transfer_list[0]["attributes"], "amount"
                    )

                    caaj_from = senders[0]["value"]
                    caaj_to = recipients[0]["value"]

                    token_original_id_liquidity = OsmosisPlugin._get_token_original_id(
                        amounts[0]["value"]
                    )
                    token_original_id_liquidity_for_symbol = (
                        OsmosisPlugin._get_token_original_id_for_symbol(
                            amounts[0]["value"]
                        )
                    )

                    token_symbol_liquidity = OsmosisPlugin._get_token_symbol(
                        token_original_id_liquidity_for_symbol
                    )
                    symbol_uuid_liquidity = OsmosisPlugin._get_symbol_uuid(
                        token_original_id_liquidity, cls.chain, token_symbol_liquidity
                    )

                    amount_liquidity = OsmosisPlugin._get_token_amount(
                        amounts[0]["value"]
                    )

                    caaj_journal_get_liquidity = CaajJournal(
                        transaction.get_timestamp(),
                        cls.chain,
                        cls.PLATFORM,
                        "lend",
                        transaction.get_transaction_id(),
                        OsmosisPlugin._get_uuid(),
                        "deposit",
                        amount_liquidity,
                        token_symbol_liquidity,
                        token_original_id_liquidity,
                        symbol_uuid_liquidity,
                        caaj_from,
                        caaj_to,
                        "",
                    )
                    caaj.append(caaj_journal_get_liquidity)
        return caaj

    @classmethod
    def _get_caaj_fee(cls, address: str, transaction: Transaction) -> list:
        caaj = []
        caaj_journal_get = CaajJournal(
            transaction.get_timestamp(),
            cls.chain,
            cls.PLATFORM,
            "osmosis",
            transaction.get_transaction_id(),
            None,
            "lose",
            str(transaction.get_transaction_fee() / Decimal(MEGA)),
            "osmo",
            None,
            OsmosisPlugin._get_uuid(),
            address,
            "fee",
            "",
        )
        caaj.append(caaj_journal_get)
        return caaj

    @classmethod
    def _get_token_amount(cls, value: str) -> int:

        if "pool" in value:
            token_amount = str(Decimal(re.search(r"\d+", value).group()) / Decimal(EXA))

        else:
            token_amount = str(
                Decimal(re.search(r"\d+", value).group()) / Decimal(MEGA)
            )
        return token_amount

    @classmethod
    def _get_uuid(cls) -> str:
        return str(uuid.uuid4())

    @classmethod
    def _get_token_original_id(cls, value: str) -> str:
        token_original_id = value[re.search(r"\d+", value).end() :]
        if token_original_id == "uosmo" or token_original_id == "":
            token_original_id = None
        elif token_original_id == "uion":
            token_original_id = None
        return token_original_id

    @classmethod
    def _get_attribute_data(cls, attribute: dict, attribute_key: str) -> list:
        attribute_data = list(
            filter(lambda attribute: attribute["key"] == attribute_key, attribute)
        )

        return attribute_data

    @classmethod
    def _get_attributes_list(cls, transaction: Transaction, event_type: str) -> dict:
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
    def _get_token_symbol(cls, token_original_id: str) -> str:
        if token_original_id == "osmo":
            return "osmo"
        elif token_original_id == "ion":
            return "ion"
        df = pd.read_csv(cls.TOKEN_ORIGINAL_ID_URL, index_col=0)
        token_table = df[df["original_id"] == token_original_id]
        if len(token_table) > 0:
            token_symbol = token_table["symbol"].item()
        else:
            token_symbol = None
        return token_symbol

    @classmethod
    def _get_token_original_id_for_symbol(cls, value: str) -> str:
        token_original_id = value[re.search(r"\d+", value).end() :]
        if token_original_id == "uosmo" or token_original_id == "":
            token_original_id = "osmo"
        elif token_original_id == "uion":
            token_original_id = "ion"
        return token_original_id

    @classmethod
    def _get_symbol_uuid(cls, original_id: str, chain: str, symbol: str) -> str:
        if original_id is None:
            df = pd.read_csv(cls.TOKEN_ORIGINAL_ID_URL)
            token_table = df[(df["chain"] == chain) & (df["symbol"] == symbol)]
            if len(token_table) == 0:
                return str(uuid.uuid4())
            symbol_uuid = token_table["symbol_uuid"].item()
            return symbol_uuid

        df = pd.read_csv(cls.TOKEN_ORIGINAL_ID_URL)
        token_table = df[
            (df["original_id"] == original_id)
            & (df["chain"] == chain)
            & (df["symbol"] == symbol)
        ]
        if len(token_table) == 0:
            return str(uuid.uuid4())
        symbol_uuid = token_table["symbol_uuid"].item()
        return symbol_uuid
