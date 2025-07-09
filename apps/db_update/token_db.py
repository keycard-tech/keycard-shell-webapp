import struct

from common.consts import CHAIN_MAGIC, ERC20_MAGIC
from common.errors import InvalidChainDBFile, InvalidAddressLength, InvalidTokenDBFile, ProcessTokenError

def serialize_addresses(addresses):
  res = b''
  for id, address in sorted(addresses.items()):
    if len(address) != 42:
        raise InvalidAddressLength
    res = res + struct.pack("<I20s", id, bytes.fromhex(address[2:]))

  return res

def serialize_chain(chain):
  try:
    chain_len = 4 + len(chain["ticker"]) + 1 + len(chain["name"]) + 1 + len(chain["shortName"]) + 1
    return struct.pack("<HHI", CHAIN_MAGIC, chain_len, chain["id"]) + \
      bytes(chain["ticker"], "ascii") + b'\0' + \
      bytes(chain["name"], "ascii") + b'\0' + \
      bytes(chain["shortName"], "ascii") + b'\0'
  except Exception as err:
    raise InvalidChainDBFile(err)  

def serialize_token(token):
  try:
    addresses = serialize_addresses(token["addresses"])
    token_len = 1 + len(addresses) + 1 + len(token["ticker"]) + 1

    return struct.pack("<HHB", ERC20_MAGIC, token_len, len(token["addresses"])) + \
      addresses + \
      struct.pack("B", token["decimals"]) + \
      bytes(token["ticker"], "ascii") + b'\0'
  except Exception as err:
    raise InvalidTokenDBFile(err)  

def lookup_chain(chains_json, chain_id):
  try:
    for chain in chains_json:
      if chain["chainId"] == chain_id:
        return chain
  except Exception as err:
    raise InvalidChainDBFile(err)  

def process_token(tokens, chains, token_json, chains_json):
  try:
    chain_id = token_json["chainId"]

    chain = chains.get(chain_id)
    if chain is None:
      chain_json = lookup_chain(chains_json, chain_id)
      chain = {
          "id": chain_id,
          "name": chain_json["name"],
          "shortName": chain_json["shortName"],
          "ticker": chain_json["nativeCurrency"]["symbol"],
          "decimals": chain_json["nativeCurrency"]["decimals"],
      }
      chains[chain_id] = chain

    symbol = token_json["symbol"]
    token = tokens.get(symbol)

    if token is None:
      token = {
          "addresses": {},
          "ticker": symbol,
          "decimals": token_json["decimals"]
      }
      tokens[symbol] = token

    token["addresses"][chain_id] = token_json["address"]
  except Exception as err:
    raise ProcessTokenError(err)