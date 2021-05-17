import random


class SnakeEyes:
    def __init__(self, players):
        self.players = players
        self.scores = {}

        self.turn_left = {}

        for player in players:
            self.scores[player.id] = 0
            self.turn_left[player.id] = True

    def process_input(self, message):

        player = None
        for p in self.players:
            if p.id == message.author.id:
                player = p
                break

        if player is not None:

            if message.content[1:] == "roll":

                allowed_turn = self.turn_left.get(player.id)
                if allowed_turn is None:
                    return player.name + " has lost, wait for game to finish..."
                if allowed_turn is True:

                    self.turn_left[player.id] = False

                    roll1 = random.randint(1, 6)
                    roll2 = random.randint(1, 6)

                    player_score = self.scores.get(player.id)
                    player_score = player_score + roll1 + roll2
                    self.scores[player.id] = player_score

                    output = str(player.name) + " has rolled - " + str(roll1) + "," + str(
                        roll2) + ". Final score: " + str(player_score)

                    if roll1 == 1 and roll2 == 1:
                        output = "!" + str(player.name) + " has rolled snake eyes, player wins"
                    if player_score == 21:
                        output = "!" + output + ", player has won"
                    elif player_score > 21:
                        output = output + ", player has lost"

                        self.turn_left.pop(player.id)

                    if len(self.turn_left) == 1:

                        for key in self.turn_left:

                            for p in self.players:
                                if p.id == key:
                                    return "!" + output + ". " + str(p.name) + " is last one standing, default win"

                    self.new_round()

                    return output
                else:
                    return player.name + " is over, wait for others to finish their turn..."
            else:
                return "Command not recognized by snake eyes"
        else:
            print("Player was not found")
            return None

    def new_round(self):

        round_over = True
        for key in self.turn_left:
            if self.turn_left.get(key):
                round_over = False
                break

        if round_over:
            for key in self.turn_left:
                self.turn_left[key] = True
