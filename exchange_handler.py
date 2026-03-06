"""
Exchange handler for Binance Testnet using ccxt.
Handles price fetching, balance, and mock market orders.
"""

import os
from decimal import Decimal
from typing import Optional

import ccxt
from dotenv import load_dotenv

load_dotenv()

# Trading pair and default order amount
SYMBOL = "BTC/USDT"
DEFAULT_BUY_AMOUNT_BTC = 0.0001  # Small amount for test orders


def get_exchange() -> ccxt.binance:
    """Create and return a configured Binance Testnet exchange instance."""
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    secret = os.getenv("BINANCE_SECRET_KEY", "").strip()

    if not api_key or not secret:
        raise ValueError("BINANCE_API_KEY and BINANCE_SECRET_KEY must be set in .env")

    exchange = ccxt.binance(
        {
            "apiKey": api_key,
            "secret": secret,
            "enableRateLimit": True,
            "options": {
                "defaultType": "spot",
            },
        }
    )
    # Enable Binance Spot Testnet
    exchange.set_sandbox_mode(True)
    return exchange


def fetch_btc_price() -> Optional[str]:
    """
    Fetch current BTC/USDT price from Binance Testnet.
    Returns formatted price string or None on error.
    """
    try:
        exchange = get_exchange()
        ticker = exchange.fetch_ticker(SYMBOL)
        price = ticker.get("last")
        if price is not None:
            return f"${float(price):,.2f}"
        return None
    except ccxt.RateLimitExceeded:
        raise
    except ccxt.NetworkError as e:
        raise
    except ccxt.ExchangeError as e:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to fetch price: {e}") from e


def get_wallet_balance() -> Optional[dict]:
    """
    Fetch wallet balance from Binance Testnet.
    Returns dict with 'USDT' and 'BTC' balances or None on error.
    """
    try:
        exchange = get_exchange()
        balance = exchange.fetch_balance()
        usdt = balance.get("USDT", {}) or {}
        btc = balance.get("BTC", {}) or {}
        return {
            "USDT": float(usdt.get("free", 0) or 0),
            "BTC": float(btc.get("free", 0) or 0),
        }
    except ccxt.RateLimitExceeded:
        raise
    except ccxt.NetworkError:
        raise
    except ccxt.ExchangeError as e:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to fetch balance: {e}") from e


def place_market_buy(amount_btc: float = DEFAULT_BUY_AMOUNT_BTC) -> Optional[dict]:
    """
    Place a market BUY order for the given amount of BTC on Binance Testnet.
    Returns order info dict or None on error.
    """
    try:
        exchange = get_exchange()
        amount = Decimal(str(amount_btc)).quantize(Decimal("0.00001"))
        order = exchange.create_market_buy_order(SYMBOL, float(amount))
        return order
    except ccxt.RateLimitExceeded:
        raise
    except ccxt.NetworkError:
        raise
    except ccxt.InsufficientFunds as e:
        raise
    except ccxt.ExchangeError as e:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to place buy order: {e}") from e


def place_market_sell(amount_btc: float = DEFAULT_BUY_AMOUNT_BTC) -> Optional[dict]:
    """
    Place a market SELL order for the given amount of BTC on Binance Testnet.
    Returns order info dict or None on error.
    """
    try:
        exchange = get_exchange()
        amount = Decimal(str(amount_btc)).quantize(Decimal("0.00001"))
        order = exchange.create_market_sell_order(SYMBOL, float(amount))
        return order
    except ccxt.RateLimitExceeded:
        raise
    except ccxt.NetworkError:
        raise
    except ccxt.InsufficientFunds as e:
        raise
    except ccxt.ExchangeError as e:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to place sell order: {e}") from e
