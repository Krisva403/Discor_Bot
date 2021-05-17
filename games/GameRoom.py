from games import games


class GameRoom:

    def __init__(self, players, room_id):

        self.players = players
        self.room_id = room_id
        self.game_instance = None

    def process_input(self, message):
        output = ""
        if message.content[1:6] == "start":
            if message.content[7:] == "snakeeyes":
                self.game_instance = games.SnakeEyes(players=self.players)
                print(f'{self.room_id}: Snake Eyes game has started!')
                return "Snake Eyes game has started!"
        elif message.content[1:5] == "stop":
            self.game_instance = None
            print(f'{self.room_id}: Game has been ended')
            return "Game has been ended!"
        else:
            if self.game_instance is not None:
                output = self.game_instance.process_input(message)
                if output[0:1] == "!":
                    self.game_instance = None
                    output = output + "Game has ended"
                return output
            else:
                print(f'{self.room_id}: game instance is null so command is ignored')
                return "Unknown command :("
