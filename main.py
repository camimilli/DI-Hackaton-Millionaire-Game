from game import Game 
import db 

def main():

    # Initialize DB and game 
    db.init_db()
    game = Game()

    print("\n" + "-" * 50)
    print("Welcome to Who Wants to be a Millionaire!?")
    print("Answer 15 questions correctly to win $1,000,000!")
    print("You have three lifelines: 50/50, Ask the Audience, and Call a Friend.")
    print("-" * 50)

    for i in range(15):

        round_result = game.play_round()

        if round_result:
            print("-" * 50)
            print("Moving on to the next question.")
        else:
            print("\nGame Over.")
            final_winnings = 0 
            if i > 0:
                final_winnings = game.money_ladder[i-1]
            print(f"You leave with ${final_winnings}!!!")

            print("\nGame Summary:")
            db.fetch_progress()
            break

    if game.current_round == 15:
        final_winnings = game.money_ladder[-1]
        print(f"\nCongratulations! You answered all 15 questions correctly and won ${final_winnings}!")
        print("You are a Millionaire!")
        print("\nGame Summary:")
        db.fetch_progress()

main()