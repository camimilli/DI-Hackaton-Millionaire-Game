
# List of questions and money ladder 


# welcome message 
# ask for input - enter (in main loop)
# check input (in main loop)
# fetch question 
# user response 
# log to database using variables from fetch_question 
# check answer 



# FOR GAME LOOP
# Fetch the next question
# q_text, correct_answer, options, money = self.fetch_question()
# self.display_question(q_text, options, money)

# # Ask user what they want to do
# action, value = self.get_user_input()

# if action == 'ANSWER':
#     if self.check_answer(value, options, correct_answer):
#         print(f"Correct! You won ${money}")
#         self.current_question += 1  # move to next question
#     else:
#         print(f"Wrong! The correct answer was {correct_answer}")
#         self.end_game()  # or handle losing logic
# elif action == 'LIFELINE':
#     self.use_lifeline(value)  # handle lifeline usage