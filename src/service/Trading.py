import ccxt
import time
import pandas as pd
import ta
import logging
from datetime import datetime
from tabulate import tabulate

from src.service.messageTelegram import send_telegram_message

# Configure Binance API
exchange = ccxt.binance()

# Params
symbol = 'SOL/USDT'
timeframe = '1m'  # Intervalo de 1 minuto
ma_period = 5  # MA(5)
rsi_period = 6  # RSI(6)
rsi_threshold = 40  # Min RSI


def get_volume_data():
    """Obtiene los últimos datos de velas para calcular MA(5) del volumen."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=ma_period + 20)  # Más datos para mejor MA
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Sincroniza con UTC
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)

    # Calcular MA(5) del volumen
    df['MA5'] = df['volume'].rolling(window=ma_period).mean()

    return df


def get_price_change_last_hour():
    """Verify price Solana is up in last hour."""
    ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=2)  # last 2 candles 1 hora
    last_close = ohlcv[-1][4]  # close price last hour
    previous_close = ohlcv[-2][4]  # Precio de cierre de la hora anterior

    return last_close > previous_close  # True if price has up


def get_rsi():
    """Calcula RSI(6) y verifica si está por debajo de 40."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=rsi_period + 20)  # Más datos para RSI estable
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)

    # Calcula RSI(6)
    df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=rsi_period, fillna=True).rsi()

    last_rsi = df.iloc[-1]['RSI']  # Último valor del RSI
    return last_rsi < rsi_threshold, last_rsi


def monitor_volume():
    """Monitorea el volumen y verifica condiciones para alerta."""
    while True:
        # Obtiene datos de volumen y MA(5)
        df = get_volume_data()

        # Último volumen, MA(5), precio actual y fecha
        last_volume = df.iloc[-1]['volume']
        last_ma5 = df.iloc[-2]['MA5']  # Usamos -2 porque el último dato no tiene MA completo
        last_close = df.iloc[-1]['close']  # Precio de cierre más reciente
        last_date = df.iloc[-1]['datetime']

        # Obtiene RSI(6)
        rsi_below_40, last_rsi = get_rsi()

        # Prepara datos para tabla
        table_data = [
            ["Fecha (UTC)", "Precio Actual", "Volumen", "MA(5) Volumen", "RSI(6)"],
            [last_date, f"{last_close:.4f}", f"{last_volume:.2f}", f"{last_ma5:.2f}", f"{last_rsi:.2f}"]
        ]

        # Muestra en consola como tabla
        print("\n" + tabulate(table_data, headers="firstrow", tablefmt="grid"))

        # Registra en logs
        logging.info(f"Fecha: {last_date}, Precio Actual: {last_close}, Volumen: {last_volume}, MA(5) Volumen: {last_ma5}, RSI(6): {last_rsi}")

        # Condición: volumen > 2x MA(5)
        if last_volume > 2 * last_ma5:
            # Verifica si el precio ha subido en la última hora
            price_up = get_price_change_last_hour()

            # 🔥 Envía alerta si se cumplen todos los criterios
            if price_up and rsi_below_40:
                message = (f"🔥ALERTA FUERTE: Todos los criterios se cumplen 🚀\n"
                           f"Fecha: {last_date}\n"
                           f"Precio Actual: {last_close:.4f}\n"
                           f"RSI(6): {last_rsi:.2f}\n"
                           f"Volumen: {last_volume:.2f}\n"
                           f"MA5 Volumen: {last_ma5:.2f}")
                send_telegram_message(message)

        # Espera antes de la próxima verificación
        time.sleep(60)
