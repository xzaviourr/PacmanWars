from bots.bot import Bot
import constants as c
import pprint as pp
from random import shuffle, choice

class GreedyBot(Bot):
    """
    GreedyBot's only weakness is getting attacked during the early game, but as soon as it finds a trail of food it is over
    for the other bots.
    """

    def __init__(self, id: int, start_x: int, start_y: int, minimap: list, map_length: int, map_breadth: int):
        super().__init__(id, start_x, start_y, minimap, map_length, map_breadth)

        self.directions = {
            "up": c.MOVE_UP,
            "down": c.MOVE_DOWN,
            "left": c.MOVE_LEFT,
            "right": c.MOVE_RIGHT,
        }

        self.best_move = None

    def optimal_move(self, grid, food):
        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }

        player_pos = (2, 2)

        goal_positions = []
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell == 'F':
                    goal_positions.append((i, j))

        if not goal_positions:
            swap = False
            for i, row in enumerate(grid):
                for j, e in enumerate(row):
                    if e == "G":
                        swap = True
                        grid[i][j] = "F"
                        return optimal_move(grid)
            if not swap:
                return "invalid (no place for goal)"

        # Check each possible move
        best_move = None
        min_distance = float('inf')
        for move, (di, dj) in directions.items():
            new_i, new_j = player_pos[0] + di, player_pos[1] + dj
            if 0 <= new_i < len(grid) and 0 <= new_j < len(grid[0]):
                if grid[new_i][new_j] not in ('O', 'R') and grid[new_i][new_j] not in [i for i in food if i != self.id]:
                    for goal_pos in goal_positions:
                        distance = abs(new_i - goal_pos[0]) + abs(new_j - goal_pos[1])
                        if distance < min_distance:
                            min_distance = distance
                            best_move = move

        return best_move if best_move else "invalid (stuck)"

    def is_valid(self, value: str) -> bool:
        # print(value)
        return value in ("F", "G") or value.isnumeric()

    def dumb_move(self, minimap: list[list[str]], food: dict) -> None:
        up = "up", minimap[1][2]
        down = "down", minimap[3][2]
        left = "left", minimap[2][1]
        right = "right", minimap[2][3]
        moves = [up, left, down, right]
        preferred = [i for i in moves if i[1] == "F" or (i[1].isnumeric() and food[i] < food[self.id])]
        secondary = [i for i in moves if i[1] == "G"]
        if len(preferred) < 1:
            preferred = secondary
        shuffle(preferred)
        self.best_move = preferred[0][0] if len(preferred) > 0 else choice(moves)

    def flatten(self, minimap: list[list[str]]) -> list[str]:
        my_list = []
        for row in minimap:
            for cell in row:
                my_list.append(cell)
        return my_list

    def far_sight(self, minimap: list[list[str]], food: dict) -> None:
        if self.flatten(minimap).count("F") >= 22:
            self.dumb_move(minimap, food)
            return
        suggested = self.optimal_move(minimap, food)
        if "invalid" in suggested:
            self.dumb_move(minimap)
        else:
            self.best_move = suggested


    def move(self, current_x, current_y, minimap, bot_food):
        self.update_state(current_x, current_y, minimap, bot_food)
        # O = red, G = green, R = void, F = food
        self.far_sight(minimap, bot_food)
        # print(self.best_move)
        if self.best_move is None:
            print("NOT MOVING")
            return c.MOVE_STAY
        print(self.best_move)
        return self.directions[self.best_move]
