from random import choice


def get_computer_choice() -> str:
    '''Randomly select and return "Rock", "Paper", or "Scissors"'''

    print("The computer is making a move...")
    options = ["Rock", "Paper", "Scissors"]
    return choice(options)


def get_user_choice() -> str:
    '''Ask user to input "Rock", "Paper", or "Scissors"'''

    options = ["Rock", "Paper", "Scissors"]
    print("Your move!")
    while True:
        prompt = "Please enter 'Rock', 'Paper', or 'Scissors': "
        user_choice = input(prompt).strip().capitalize()
        if user_choice in options:
            return user_choice


def get_winner(computer_choice: str, user_choice: str) -> None:
    '''Compare computer choice against user choice to determine
    who wins the game of rock, paper, scissors.'''

    if computer_choice == user_choice:
        print("It is a tie!")
    else:
        if computer_choice == "Rock":
            user_wins = user_choice == "Paper"
        elif computer_choice == "Paper":
            user_wins = user_choice == "Scissors"
        else:
            user_wins = user_choice == "Rock"

        print("You won!" if user_wins else "You lost")


def play(rounds: int = 3) -> None:
    '''Play a game of rock, paper, scissors'''

    for _ in range(rounds):
        print("\n")
        computer_choice = get_computer_choice()
        user_choice = get_user_choice()

        print(f"Computer choice: {computer_choice}")
        print(f"User choice: {user_choice}")

        get_winner(computer_choice, user_choice)


if __name__ == '__main__':

    play()
