import games

# Gameroom class
class GameRoom:
    def __init__(self, players, room_id):

        self.players = players
        self.room_id = room_id
        self.game_instance = None

    def process_input(self, message):
        output = ""
        # check if there is a command !start
        if message.content[1:6] == "start":
            # if after start there is snakeeyes then call back snakeyes class and return message in the room
            if message.content[7:] == "snakeeyes":
                self.game_instance = games.snakeeyes(players=self.players)
                print(f'{self.room_id}: Snake Eyes game has started!')
                return """***Snake Eyes game has started!***\n
                Rules: players roll on their turn and whoever gets 21 first wins. If someone gets above 21 they lose instant and wait for others to win. If you are the only one standing you will win by default. Whoever starts has the first turn.
                Commands:
                ```!roll - to roll on your turn.
                !stop - to stop the game.
                .endroom - to delete """ + self.room_id + "```\n"
            # if after start there is tic tac toe then call back tictactoe class and return message and game board in the room
            elif message.content[7:] == "tictactoe":
                self.game_instance = games.Tictactoe(players=self.players)
                print(f'{self.room_id}: Tic Tac Toe game has started!')

                return """***Tic Tac Toe game has started!***\n
                               Rules: Only two player are able to play Tic Tac Toe. Whoever starts gets mark x and the other player gets mark o. The goal is to get 3 of yor marks in a row.
                               Commands:
                               ```!place (cordinates of a square 1-9) - to place your mark on a board.
                               !stop - to stop the game.
                               .endroom - to delete """ + self.room_id + "```\n" + self.game_instance.get_output()
        # check if there is command !stop then stop the game
        elif message.content[1:5] == "stop":
            self.game_instance = None
            print(f'{self.room_id}: Game has been ended')
            return "Game has been ended!"

        else:
            # If '!' returned at start of output, means game has finished
            if self.game_instance is not None:
                output = self.game_instance.process_input(message)
                if output[0:1] == "!":
                    self.game_instance = None
                    output = output[1:] + "Game has ended"
                return output
