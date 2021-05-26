import random

# game Snakeeyes
class snakeeyes:
    def __init__(self, players):
        self.players = players
        self.scores ={}

        # used for only one player per round
        self.turn_left ={}

        # score-board
        for player in players:
            self.scores[player.id] = 0
            self.turn_left[player.id] =True

    def process_input(self, message):
        # find a player who wrote the command
        player = None
        for p in self.players:
            if p.id == message.author.id:
                player = p
                break


        if player is not None:
            # check for roll command
            if message.content[1:] == "roll":

                # check if the player is still in the game
                allowed_turn = self.turn_left.get(player.id)
                if allowed_turn is None:
                    return player.name + " has lost, wait for game to finish..."
                # if player is in the game continue to get 2 random numbers and add them too score-board
                if allowed_turn is True:

                    self.turn_left[player.id] = False

                    roll1 = random.randint(1,6)
                    roll2 = random.randint(1,6)

                    player_score = self.scores.get(player.id)
                    player_score = player_score + roll1 + roll2
                    self.scores[player.id] = player_score

                    output = str(player.name) + " has rolled - " + str(roll1) + "," + str(roll2) + ". Final score: " + str(player_score)

                    # check winningconditions
                    # if player has rolled "snakeeyes"(two 1) than he wins
                    if roll1 == 1 and roll2 == 1:
                        output = "!" + str(player.name) + " has rolled snake eyes, player wins\n"
                    if player_score == 21:
                        output = "!" + output + ", player has won\n"
                    elif player_score > 21:
                        output = output + ", player has lost\n"
                        # take out player from the list after they lost
                        self.turn_left.pop(player.id)

                    # check if player is the only one standing
                    if len(self.turn_left) == 1:

                        for key in self.turn_left:

                            for p in self.players:
                                if p.id == key:
                                # if he is delcare him as a default winner
                                    return "!" + output + ". " +str(p.name) + " is last one standing, default win\n"

                    self.new_round()

                    return output
                else:
                    # if its not players turn return:
                    return player.name + "turn is over, wait for others to finish their turn..."
            else:
                # if command doesnt exist return:
                return "Command not recognized by snake eyes"
        else:
            print("Player was not found")
            return None
    # new round
    def new_round(self):

        round_over = True
        for key in self.turn_left:
            if self.turn_left.get(key):
                round_over = False
                break

        if round_over:
            for key in self.turn_left:
                self.turn_left[key] = True
# game tic tac toe
class Tictactoe:
    def __init__(self, players):
        # the game board
        self.board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        # declaring marks
        self.marks = [":regional_indicator_x:",":o2:"]
        # mark index
        self.mark_index = 0

        self.players = players
        self.completed_turn = None
        self.winningConditions = [
                                    [0, 1, 2],
                                    [3, 4, 5],
                                    [6, 7, 8],
                                    [0, 3, 6],
                                    [1, 4, 7],
                                    [2, 5, 8],
                                    [0, 4, 8],
                                    [2, 4, 6]]


    # function for output for the board
    def get_output(self):
        line = ""
        for x in range(len(self.board)):
            line += self.board[x]
            if (x + 1) % 3 == 0:
                line += "\n"
        return line
    def process_input(self, message):
        # check if there is to many players for the game
        if len(self.players) > 2:
            return "too many players"

        player = None
        # find a player who wrote the command
        for p in self.players:
            if p.id == message.author.id:
                player = p
                break


        if player is not None:
            # check for command !place
            if message.content[1:6] == "place":
                # check if its that players turn
                if self.completed_turn != player:
                    # check that tehre is no more than 8 symbols
                    if len(message.content) != 8:
                        return "bad input"
                    # say that cordinates are on 7 symbol and that its start from 1 instead of 0
                    cord = int(message.content[7:])
                    cord = cord - 1
                    # check that the cordinate is not taken
                    if self.board[cord] != ":white_large_square:":
                        return "you cant place here"
                    # place mark
                    self.board[cord] = self.marks[self.mark_index]
                    self.completed_turn = player
                    # check if there is a winner
                    if self.checkWinner(self.marks[self.mark_index]):
                        return "!\n" + self.get_output() + "\n" + str(player.name) + " has won! \n"
                    # check if its a tie
                    if self.checkTie():
                        return "!\n" + self.get_output() + "\nGame has ended in a tie!\n"
                    # after a turn increase mark index
                    self.mark_index = self.mark_index + 1
                    # and make it so at the next round its 0 again
                    if self.mark_index > 1:
                        self.mark_index = 0
                    return self.get_output()
                else:
                    return "Its not your turn"
            else:
                return "command not recognized"
        return "player not found"

    # function to se who's a winner
    def checkWinner(self, mark):
        gameOver = False
        # checking if one of the mark are placed into winning conditions
        for condition in self.winningConditions:
            if self.board[condition[0]] == mark and self.board[condition[1]] == mark and self.board[condition[2]] == mark:
                gameOver = True
                break
        return gameOver
    # function to see if it's a tie
    def checkTie(self):
        tie = True
        # if there is no white squares left its a tie
        for x in range(len(self.board)):
            if self.board[x] == ":white_large_square:":
                tie = False
                break
        return tie







