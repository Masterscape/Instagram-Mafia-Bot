from dotenv import load_dotenv
from instagrapi import Client
from random import randint
from os import getenv
from unofficial_patch import patch_instagrapi

load_dotenv()

def attempt_login() -> Client:
    # Get all the needed info
    username: str = getenv("INSTAGRAM_USERNAME")
    password: str = getenv("INSTAGRAM_PASSWORD")
    session_id: str = getenv("SESSION_ID")

    use_session_id_for_login: bool = bool(getenv("USE_SESSION_ID_FOR_LOGIN"))

    client = Client()

    try:
        if use_session_id_for_login:
            print(f"Attempting login to Instagram... \n"
                  f"Session ID: {session_id}")

            client.login_by_sessionid(session_id)

        else:
            # If you use 2FA, this will fail, unfortunately.
            print(f"Attempting login to Instagram..."
                  f"\nUsername: {username}"
                  f"\nPassword: {password}")

            client.login(username, password)

    except BaseException as err:
        print("Login failed. Error:", err)
        quit(1)

    print("Login successful")
    return client
def shuffle(given_list: list[str]) -> None:
    for i in range( len(given_list) ):
        k: int = randint(0, len(given_list) - 1)
        given_list[i], given_list[k] = given_list[k], given_list[i]
def send_message_to_user(client: Client, username: str, message: str) -> None:
    user_id = client.user_id_from_username(username)

    if user_id:
        client.direct_send(message, user_ids=[client.user_id, user_id])
    else:
        print(f"Failed to find user with the username {username}.")
def send_message_to_self(client: Client, message: str) -> None:
    client.direct_send(message, user_ids=[client.user_id])
def parse_and_send_out_the_roles(client: Client) -> None:
    players: list[str] = [p for p in getenv("PLAYER_LIST", "").split(",") if p]
    minimum_players_required: int = 8
    debug: bool = bool(getenv("DEBUG"))

    send_message_to_self(client, "Trying to start a new game..."
                                 f"Players: {players}")

    if debug:
        send_message_to_self(client, "DEBUG enabled.")
        while len(players) < minimum_players_required:
            players.append(client.username)
        send_message_to_self(client, f"New player list: {players}")

    print(f"Player list: {players}")

    if len(players) < minimum_players_required:
        print("Too few players.\n"
              "Mafia requires at least 4 players.")
        send_message_to_self(client, "Failed to start the game. See console log for more info.")
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

    shuffle(roles)

    for i in range(len(players)):
        message: str = f"Rolul tau este de {roles[i]}"

        send_message_to_user(client, players[i], "A inceput o noua runda.")
        send_message_to_user(client, players[i], message)

    print("Successfully sent all the players their roles.\n"
          "Have fun!")
    send_message_to_self(client, "Successfully sent all the players their roles. Have fun!")

def main():
    patch_instagrapi()

    client = attempt_login()

    parse_and_send_out_the_roles(client)

if __name__ == '__main__':
    main()