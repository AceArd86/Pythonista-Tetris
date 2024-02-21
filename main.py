import scene
from scene import *
import scene_drawing
from scene_drawing import *
import random

# GLOBALS VARS
s_width = 380
s_height = 680
play_width = 300  # meaning 200 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

I = [['.....',
      '.....',
      '0000.',
      '.....',
      '.....'],
     ['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....']]

L = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '...0.',
      '...0.',
      '..00.',
      '.....']]

T = [['.....',
      '.000.',
      '..0..',
      '.....',
      '.....'],
     ['.....',
      '...0.',
      '..00.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '.0...',
      '.00..',
      '.0...',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

S = [['.....',
      '..00.',
      '.00..',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..00.',
      '.....',
      '.....'],
     ['.....',
      '.0...',
      '.00..',
      '..0..',
      '.....']]

shapes = [I, L, T, O, S]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


class Piece(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # number from 0-3


class TetrisGame(scene.Scene):
    def setup(self):
        self.block_size = block_size
        self.grid_width = 10 + 1
        self.grid_height = 20 +1
        self.grid = [[0] * self.grid_width for _ in range(self.grid_height)]
        self.current_piece = self.get_shape()
        self.game_over = False
        self.drop_time = 0
        self.drop_speed = 0.5  # Adjust as needed

    def get_shape(self):
        return Piece(5, self.grid_height - 2, random.choice(shapes))

    def draw(self):
        self.draw_grid()
        self.draw_shape()

    def draw_grid(self):
        sx = top_left_x
        sy = top_left_y
        for i in range(self.grid_height):
            scene_drawing.image('white', sx, sy + i * block_size, play_width, 1)
        for j in range(self.grid_width):
            scene_drawing.image('white', sx + j * block_size, sy, 1, play_height)
    
    def draw_shape(self):
        piece = self.current_piece
        positions = self.convert_shape_format(piece)

        for pos in positions:
            x, y = pos
            # Calculate pixel coordinates relative to the top-left corner of the grid area
            x_pixel = top_left_x + x * block_size
            y_pixel = top_left_y + y * block_size
            # Draw the shape block
            scene_drawing.fill(piece.color)
            scene_drawing.rect(x_pixel, y_pixel, block_size - 2, block_size - 2)

    def convert_shape_format(self, piece):
        positions = []
        shape_format = piece.shape[piece.rotation % len(piece.shape)]

        for i, line in enumerate(shape_format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    positions.append((piece.x + j, piece.y + i))
        return positions
    
    
    def update(self):
        if not self.game_over:
            # Move the current piece down based on the drop speed
            self.drop_time += self.dt
            if self.drop_time > self.drop_speed:
                self.drop_time = 0
                self.move_down()
                
    
    def rotate_piece(self):
        piece = self.current_piece
        piece.rotation = (piece.rotation + 1) % len(piece.shape)
        if self.check_collision(0, 0):
            # Revert rotation if it causes collision
            piece.rotation = (piece.rotation - 1) % len(piece.shape)

    def move_down(self):
        if not self.check_collision(0, -1):
            self.current_piece.y -= 1
        else:
            self.merge_piece()
            self.clear_lines()
            self.current_piece = self.get_shape()
            if self.check_collision(0, 0):
                self.game_over = True

    def move_left(self):
        if not self.check_collision(-1, 0):
            self.current_piece.x -= 1

    def move_right(self):
        if not self.check_collision(1, 0):
            self.current_piece.x += 1

    def merge_piece(self):
        piece = self.current_piece
        for pos in self.convert_shape_format(piece):
            x, y = pos
            self.grid[y][x] = piece.color
        for i, line in enumerate(piece.shape[piece.rotation % len(piece.shape)]):
            for j, column in enumerate(line):
                if column == '0':
                    self.grid[piece.y + i][piece.x + j] = piece.color

    def touch_began(self, touch):
        self.start_pos = touch.location

    def touch_ended(self, touch):
        end_pos = touch.location
        dx = end_pos.x - self.start_pos.x
        dy = end_pos.y - self.start_pos.y
        
        if abs(dx) > abs(dy):  # Horizontal swipe
            if dx > 0:  # Swipe right
                self.move_right()
            elif dx < 0:  # Swipe left
                self.move_left()
        else:  # Vertical swipe
            if dy > 0:  # Swipe down
                self.move_down()
            elif dy < 0:  # Swipe up (rotate)
                self.rotate_piece()
    
    
    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0] * self.grid_width)

    def check_collision(self, x_offset, y_offset):
        piece = self.current_piece
        for i, line in enumerate(piece.shape[piece.rotation % len(piece.shape)]):
            for j, column in enumerate(line):
                if column == '0':
                    next_x = piece.x + j + x_offset
                    next_y = piece.y + i + y_offset
                    if not (0 <= next_x < self.grid_width and 0 <= next_y < self.grid_height):
                        return True  # Collision with the walls
                    if self.grid[next_y][next_x]:
                        return True  # Collision with existing pieces on the grid
        return False

if __name__ == '__main__':
    scene.run(TetrisGame())
