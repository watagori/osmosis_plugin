import re
from decimal import Decimal

EXA = 10**18
MEGA = 10**6


class GetTokenValue():
  @classmethod
  def get_token_name(cls, value) -> str:
    token_name = value[re.search(r'\d+', value).end():]
    if token_name == "uosmo":
      token_name = "osmo"
    elif token_name == "uion":
      token_name = "ion"

    return token_name

  @classmethod
  def get_token_amount(cls, value) -> int:

    if "pool" in value:
      token_amount = str(Decimal(
          re.search(r'\d+', value).group()) / Decimal(EXA))

    else:
      token_amount = str(Decimal(
          re.search(r'\d+', value).group()) / Decimal(MEGA))
    return token_amount
