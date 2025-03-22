import random

player = ""
computer = random.randint(1, 3)
computer_lives = 3
player_lives = 3

while True:
    print("=====================================")
    print("Welcome to Rock, Paper, Scissors!")
    print("=====================================")
    print("1) ✊ Rock")
    print("2) ✋ Paper")
    print("3) ✌️ Scissors")
    player = int(input("Enter your choice: "))

    if player == 1:
        print("You chose ✊ Rock")
    elif player == 2:
        print("You chose ✋ Paper")
    elif player == 3:
        print("You chose ✌️ Scissors")
    else:
        print("Invalid choice")
        exit()

    if computer == 1:
        print("Computer chose ✊ Rock")
    elif computer == 2:
        print("Computer chose ✋ Paper")
    elif computer == 3:
        print("Computer chose ✌️ Scissors")

    if player == computer:
        print("It's a tie!")
    elif (player == 1 and computer == 2) or (player == 2 and computer == 3) or (player == 3 and computer == 1):
        print("Computer wins!")
        player_lives -= 1
    else:
        print("You win!")
        computer_lives -= 1
    
    if player_lives == 0:
        print("You lost the game!")
        break
    elif computer_lives == 0:
        print("You won the game!")
        break