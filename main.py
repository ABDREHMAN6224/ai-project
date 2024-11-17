import random
import os
import time
from copy import deepcopy
import keyboard


SHAPES = {
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)],
          [(1, 0), (1, 1), (1, 2), (1, 3)]],
    'O': [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    'T': [[(0, 1), (1, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (1, 0)],
          [(1, 0), (1, 1), (1, 2), (2, 1)],
          [(0, 1), (1, 1), (2, 1), (1, 2)]],
    'S': [[(0, 1), (0, 2), (1, 0), (1, 1)],
          [(0, 0), (1, 0), (1, 1), (2, 1)]],
    'Z': [[(0, 0), (0, 1), (1, 1), (1, 2)],
          [(0, 1), (1, 0), (1, 1), (2, 0)]],
    'J': [[(0, 0), (1, 0), (2, 0), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 0), (0, 1), (1, 1), (2, 1)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]],
    'L': [[(0, 1), (1, 1), (2, 1), (2, 0)],
          [(0, 0), (0, 1), (0, 2), (1, 2)],
          [(0, 0), (1, 0), (2, 0), (0, 1)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]]
}

class Tetrimino:
    def __init__(self, shape):
        self.shape = shape
        self.rotation = 0
        self.blocks = SHAPES[shape]
        self.position = [0, 4] 

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.blocks)

    def get_blocks(self):
        return self.blocks[self.rotation]
    
class TetrisBoard:
    def __init__(self, rows=20, cols=10):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.current_piece = self.spawn_piece()
        self.score = 0

    def spawn_piece(self):
        return Tetrimino(random.choice(list(SHAPES.keys())))

    def is_valid_position(self, piece, pos):
        for block in piece.get_blocks():
            x, y = block[0] + pos[0], block[1] + pos[1]
            if x < 0 or x >= self.rows or y < 0 or y >= self.cols or self.board[x][y]:
                return False
        return True

    def lock_piece(self):
        for block in self.current_piece.get_blocks():
            x, y = block[0] + self.current_piece.position[0], block[1] + self.current_piece.position[1]
            self.board[x][y] = 1
        self.clear_lines()
        self.current_piece = self.spawn_piece()

    def clear_lines(self):
        new_board = [row for row in self.board if any(x == 0 for x in row)]
        cleared = self.rows - len(new_board)
        self.score += cleared
        self.board = [[0] * self.cols for _ in range(cleared)] + new_board

    def move_piece(self, direction):
        new_position = deepcopy(self.current_piece.position)
        if direction == 'down':
            new_position[0] += 1
        elif direction == 'left':
            new_position[1] -= 1
        elif direction == 'right':
            new_position[1] += 1
        if self.is_valid_position(self.current_piece, new_position):
            self.current_piece.position = new_position
            return True
        return False

    def rotate_piece(self):
        self.current_piece.rotate()
        if not self.is_valid_position(self.current_piece, self.current_piece.position):
            self.current_piece.rotate()
            self.current_piece.rotate()
            self.current_piece.rotate()

    def is_game_over(self):
        return not self.is_valid_position(self.current_piece, self.current_piece.position)

    def render(self):
        display = deepcopy(self.board)
        for block in self.current_piece.get_blocks():
            x, y = block[0] + self.current_piece.position[0], block[1] + self.current_piece.position[1]
            display[x][y] = 1
        os.system('cls' if os.name == 'nt' else 'clear')


        for row in display:
            print(''.join(['█' if x else ' ' for x in row]))



        print(f"Score: {self.score}")

class TetrisBot:
    def __init__(self, board):
        self.board = board

    def evaluate(self, piece, position):
        """Basic evaluation function for a potential position."""
        score = 0
        for block in piece.get_blocks():
            x, y = block[0] + position[0], block[1] + position[1]
            score += x  # Prefer lower rows
        return score

    def best_move(self):
        """Finds the best move for the current piece."""
        best_score = -float('inf')
        best_position = None
        best_rotation = 0

        for rotation in range(len(self.board.current_piece.blocks)):
            for col in range(self.board.cols):
                piece = deepcopy(self.board.current_piece)
                piece.rotation = rotation
                position = [0, col]

                while self.board.is_valid_position(piece, position):
                    position[0] += 1
                position[0] -= 1  # Move back to the last valid row

                if self.board.is_valid_position(piece, position):
                    score = self.evaluate(piece, position)
                    if score > best_score:
                        best_score = score
                        best_position = deepcopy(position)
                        best_rotation = rotation

        return best_position, best_rotation

    def play(self):
        """Plays the current piece."""
        best_position, best_rotation = self.best_move()
        if not best_position:
            return False

        # Rotate the piece to the best rotation
        for _ in range(best_rotation):
            self.board.rotate_piece()

        # Move the piece to the target column
        while self.board.current_piece.position[1] < best_position[1]:
            self.board.move_piece('right')
        while self.board.current_piece.position[1] > best_position[1]:
            self.board.move_piece('left')

        # Drop the piece
        while self.board.move_piece('down'):
            pass
        self.board.lock_piece()
        return True

class TetrisGame:
    def __init__(self):
        self.board = TetrisBoard()
        self.bot = TetrisBot(self.board)
        self.running = True

    def run(self):
        while self.running:
            self.board.render()
            time.sleep(0.1)  
            if not self.bot.play():
                self.running = False
                print("Game Over!")
        print("Thanks for playing!")


if __name__ == "__main__":
    TetrisGame().run()