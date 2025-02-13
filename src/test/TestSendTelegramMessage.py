import unittest
from unittest.mock import patch
from src.service.messageTelegram import send_telegram_message, CHAT_ID, TOKEN


class TestSendTelegramMessage(unittest.TestCase):

    @patch('src.main.service.messageTelegram.requests.post')
    def test_send_telegram_message_sends_request(self, mock_post):
        message = "Hello, world!"
        send_telegram_message(message)
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message}
        )


if __name__ == '__main__':
    unittest.main()
