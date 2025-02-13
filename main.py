from src.service.Trading import monitor_volume
import logging

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.info("Testing send_telegram_message function")
    monitor_volume()

