

data = {
    "events": [
        {
            "type": "coin_received",
            "attributes": [
                {
                    "key": "receiver",
                    "value": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr"
                },
                {"key": "amount", "value": "10000uosmo"},
                {
                    "key": "receiver",
                    "value": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m"
                },
                {
                    "key": "amount",
                    "value": "5147ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED"
                }
            ]
        },
        {
            "type": "coin_spent",
            "attributes": [
                {
                    "key": "spender",
                    "value": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m"
                },
                {"key": "amount", "value": "10000uosmo"},
                {
                    "key": "spender",
                    "value": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr"
                },
                {
                    "key": "amount",
                    "value": "5147ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED"
                }
            ]
        },
        {
            "type": "message",
            "attributes": [
                {
                    "key": "action",
                    "value": "/osmosis.gamm.v1beta1.MsgSwapExactAmountIn"
                },
                {
                    "key": "sender",
                    "value": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m"
                },
                {
                    "key": "sender",
                    "value": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr"
                },
                {"key": "module", "value": "gamm"},
                {
                    "key": "sender",
                    "value": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m"
                }
            ]
        },
        {
            "type": "token_swapped",
            "attributes": [
                {"key": "module", "value": "gamm"},
                {
                    "key": "sender",
                    "value": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m"
                },
                {"key": "pool_id", "value": "497"},
                {"key": "tokens_in", "value": "10000uosmo"},
                {
                    "key": "tokens_out",
                    "value": "5147ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED"
                }
            ]
        },
        {
            "type": "transfer",
            "attributes": [
                {
                    "key": "recipient",
                    "value": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr"
                },
                {
                    "key": "sender",
                    "value": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m"
                },
                {"key": "amount", "value": "10000uosmo"},
                {
                    "key": "recipient",
                    "value": "osmo14ls9rcxxd5gqwshj85dae74tcp3umypp786h3m"
                },
                {
                    "key": "sender",
                    "value": "osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr"
                },
                {
                    "key": "amount",
                    "value": "5147ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED"
                }
            ]
        }
    ]
}


def json_pra():
  token_swapped = list(filter(
      lambda event: event['type'] == "token_swapped", data['events']))

  sender = list(filter(
      lambda attribute: attribute['key'] == "sender", token_swapped[0]['attributes']))
  print(sender[0]['value'])


json_pra()
