import requests

class DiscordNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_discord_notify(self, notification_message: str):
        """
        指定されたメッセージをDiscordに通知する。
        """
        if not notification_message.strip():
            print("Notification message is empty. Skipping.")
            return
            
        try:
            data = {"content": notification_message}
            response = requests.post(self.webhook_url, data=data)
            response.raise_for_status()
            print("Successfully sent notification to Discord.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send notification to Discord: {e}")
