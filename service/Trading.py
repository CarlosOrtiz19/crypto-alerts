import ccxt
import time
import pandas as pd
import ta

from service.messageTelegram import send_telegram_message

# Configure Binance API
exchange = ccxt.binance()

# Params
symbol = 'SOL/USDT'  # Only SOL for now
timeframe = '1m'  # interval(1 min)
ma_period = 5  # MA(5)
rsi_period = 14  #  RSI -> 14
rsi_threshold = 40  # Min RSI


def get_volume_data():
    """Obtiene los últimos datos de velas para calcular MA(5) del volumen."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=ma_period + 1)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Calcular MA(5) from volum
    df['MA5'] = df['volume'].rolling(window=ma_period).mean()

    return df


def get_price_change_last_hour():
    """Verify price Solana is up in last hour."""
    ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=2)  # last 2 candles 1 hora
    last_close = ohlcv[-1][4]  # close price last hour
    previous_close = ohlcv[-2][4]  # Precio de cierre de la hora anterior

    return last_close > previous_close  #True if price has up


def get_rsi():
    """ RSI < 40."""
    ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=rsi_period + 1)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Calcul RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=rsi_period).rsi()

    last_rsi = df.iloc[-1]['RSI']  # Último valor del RSI
    return last_rsi < rsi_threshold, last_rsi  # is < 40 and RSI value


def monitor_volume():
    """all conditions are good, send alert."""
    while True:
        df = get_volume_data()

        # Último volumen y MA(5)
        last_volume = df.iloc[-1]['volume']
        last_ma5 = df.iloc[-2]['MA5']  # Usamos -2 porque el último dato no tiene MA completo

        # volumen 2x MA(5)
        if last_volume > 2 * last_ma5:

            # price is up last hour
            price_up = get_price_change_last_hour()

            # Verify RSI
            rsi_below_40, last_rsi = get_rsi()

            # 🔥 send alert only if all criterias are good
            if price_up and rsi_below_40:
                send_telegram_message("¡Hola!🔥ALERTA FUERTE: ¡Todos los criterios se cumplen! 🚀")

        time.sleep(180)  # Check every 3 min


