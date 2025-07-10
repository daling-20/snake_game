import random
import pygame

# 网格参数
W, H = 800, 600
GRID_SIZE = 20
GRID_WIDTH = W // GRID_SIZE
GRID_HEIGHT = H // GRID_SIZE

class Direction:
    right = 0
    left = 1
    up = 2
    down = 3

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        if isinstance(other, tuple) and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        return False

class Snake:
    def __init__(self, block_size, skin="original"):
        self.blocks=[]
        self.blocks.append(Position(20,15))
        self.blocks.append(Position(19,15))
        self.block_size = block_size
        self.current_direction = Direction.right
        self.direction = self.current_direction
        self.speed = 5
        self.current_speed = self.speed
        self.grow = False
        self.score = 0
        if skin == "original":
            self.image = pygame.Surface((self.block_size * 9, self.block_size))
            self.image.fill((255, 255, 128))  # 柔和黄色
        else:
            # 外部会设置image
            self.image = pygame.Surface((self.block_size * 9, self.block_size))
            self.image.fill((255, 255, 128))
        self.body = self.blocks

    def reset(self):
        self.blocks = [Position(20, 15), Position(19, 15)]
        self.body = self.blocks
        self.current_direction = Direction.right
        self.speed = 5
        self.current_speed = self.speed
        self.grow = False
        
    def move(self):
        if not hasattr(self, 'grow'):
            self.grow = False
        head = self.body[0]
        head_x, head_y = head.x, head.y
        if self.current_direction == Direction.right:
            head_x += 1
        elif self.current_direction == Direction.left:
            head_x -= 1
        elif self.current_direction == Direction.up:
            head_y -= 1
        elif self.current_direction == Direction.down:
            head_y += 1
        # 穿墙处理
        head_x = head_x % GRID_WIDTH
        head_y = head_y % GRID_HEIGHT
        new_head = Position(head_x, head_y)
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
    
    def change_direction(self, new_direction):
        print(f"change_direction called: old={self.current_direction}, new={new_direction}")
        opposites = {Direction.right: Direction.left, 
                     Direction.left: Direction.right,
                     Direction.up: Direction.down,
                     Direction.down: Direction.up}
        if new_direction != opposites.get(self.current_direction, None):
            self.current_direction = new_direction
            self.direction = new_direction
    
    def check_collision(self):
        head = self.body[0]
        # 撞到自己（不包含最后一节，因为增长时可能有重叠）
        if head in self.body[1:-1]:
            return True
        return False
    
    def grow_snake(self):
        # 在尾部增长一节
        tail = self.body[-1]
        self.body.append(Position(tail.x, tail.y)) 

    def draw(self, surface, frame):
        print('draw snake', frame, self.blocks)
        for index, block in enumerate(self.blocks):
            positon = (block.x * self.block_size, block.y * self.block_size)
            if index == 0:
                src = (((self.current_direction * 2) + frame) * self.block_size,
                       0, self.block_size, self.block_size)
            else:
                src = (8 * self.block_size, 0, self.block_size, self.block_size)
            surface.blit(self.image, positon, src) 