import requests


class Oauth:
    client_id = "821014425015943178"
    client_secret = "r-i6hOKtso5ZnPOznYd0hD3JflASvfY8"
    redirect_uri = "http://127.0.0.1:5000/login"
    scope = "identify%20email%20guilds"
    discord_login_url = "https://discord.com/api/oauth2/authorize?client_id=821014425015943178&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Flogin&response_type=code&scope=email%20identify%20guilds"
    discord_token_url = "https://discord.com/api/oauth2/token"
    discord_api_url = "https://discord.com/api"

    @staticmethod
    def get_access_token(code):
        payload = {
            "client_id": Oauth.client_id,
            "client_secret": Oauth.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": Oauth.redirect_uri,
            "scope": Oauth.scope
        }

        access_token = requests.post(url=Oauth.discord_token_url, data=payload).json()
        return access_token.get("access_token")

    @staticmethod
    def get_user_json(access_token):
        url = f"{Oauth.discord_api_url}/users/@me"
        headers = {"Authorization": f"Bearer {access_token}"}

        user_object = requests.get(url=url, headers=headers).json()
        return user_object
