from dotenv import load_dotenv
from instagrapi import Client
from random import randint
from os import getenv
from unofficial_patch import patch_instagrapi

load_dotenv()
patch_instagrapi()

def attempt_login() -> Client:
    # Get all the needed info
    username: str = getenv("INSTAGRAM_USERNAME")
    password: str = getenv("INSTAGRAM_PASSWORD")
    secret_auth_key: str = getenv("INSTAGRAM_SECRET_AUTH_KEY").replace(" ", "")
    session_id: str = getenv("SESSION_ID")

    use_session_id_for_login: str = getenv("USE_SESSION_ID_FOR_LOGIN").lower()

    client = Client()

    try:
        if use_session_id_for_login == "true":
            # Maybe it's not a good idea to print out env info to the console...
            print(f"Attempting login to Instagram... \n"
                  f"Session ID: {len(session_id)*"*"}")

            client.login_by_sessionid(session_id)

        else:
            # If you use 2FA, this will fail, unfortunately.
            print(f"Attempting login to Instagram..."
                  f"\nUsername: {username}"
                  f"\nPassword: {12*"*"}")
            if secret_auth_key:
                token = client.totp_generate_code(secret_auth_key)
                client.login(username, password, False, token)
            else:
                client.login(username, password)

    except BaseException as err:
        print("Login failed. Error:", err)
        quit(1)

    print("Login successful")
    return client
def shuffle(given_list: list[str], shuffles: int = 16) -> None:
    while shuffles:
        i = randint(0, len(given_list) - 1)
        k = randint(0, len(given_list) - 1)
        given_list[i], given_list[k] = given_list[k], given_list[i]
        shuffles -= 1
def send_message_to_user(client: Client, username: str, message: str) -> None:
    user_id = client.user_id_from_username(username)

    if user_id:
        client.direct_send(message, user_ids=[client.user_id, user_id])
    else:
        print(f"Failed to find user with the username {username}.")
def send_message_to_self(client: Client, message: str, output_to_console: bool = True) -> None:
    if output_to_console:
        print(message)
    client.direct_send(message, user_ids=[client.user_id])
def parse_and_send_out_the_roles(client: Client) -> None:
    players: list[str] = [player for player in getenv("PLAYER_LIST", "").split(",") if player]
    minimum_players_required: int = 4
    debug: bool = bool(getenv("DEBUG"))

    send_message_to_self(client, "Trying to start a new game..."
                                 f"Players: {players}", False)

    if debug:
        send_message_to_self(client, "DEBUG enabled.")
        while len(players) < minimum_players_required:
            players.append(client.username)
        send_message_to_self(client, f"New player list: {players}")

    send_message_to_self(client, f"Player list: {players}")

    if len(players) < minimum_players_required:
        send_message_to_self(client, "Too few players. Mafia requires at least 4 players.")
        return

    roles = ["Doctor", "Detectiv"]

    mafia: int = len(players) // minimum_players_required

    while mafia:
        roles.append("Mafiot")
        mafia -= 1

    # I looked it up. Apparently it's too overpowered to have more medics and detectives.
    detectives: int = 1
    doctors: int = 1

    civilians: int = (len(players) - (mafia + detectives + doctors)) - 1

    while civilians:
        roles.append("Civil")
        civilians -= 1

    shuffle(players)
    shuffle(roles)

    for i in range(len(players)):
        message: str = f"Rolul tau este de {roles[i]}"

        send_message_to_user(client, players[i], "A inceput o noua runda.")
        send_message_to_user(client, players[i], message)

    send_message_to_self(client, "Successfully sent all the players their roles. Have fun!")

def main():
    client = attempt_login()

    parse_and_send_out_the_roles(client)

if __name__ == '__main__':
    main()