import pygame
from config import *
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import math
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.heigth = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'

        self.image = pygame.Surface([self.width, self.heigth])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update(self):
        self.movement()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'
        if keys[pygame.K_RIGHT]:
            self.x_change += PLAYER_SPEED
            self.facing = 'right'
        if keys[pygame.K_UP]:
            self.y_change -= PLAYER_SPEED
            self.facing = 'lup'
        if keys[pygame.K_DOWN]:
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

    def collide_blocks(self, direction):
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
        
        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.width
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.hergth = TILESIZE

        self.image = pygame.Surface([self.width, self.hergth])
        self.image.fill(BLUE)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class Pathfinder:
    def __init__(self, npc, matrix):
        self.matrix = matrix
        self.grid = Grid(matrix = matrix)
        self.path = []

        self.npc = npc

    def mouse_active_cell(self):
        mouse_pos = pygame.mouse.get_pos()
        row = mouse_pos[1] // TILESIZE
        col = mouse_pos[0] // TILESIZE
        current_cell_value = self.matrix[row][col]
        rect = pygame.Rect((col*TILESIZE, row*TILESIZE),(TILESIZE, TILESIZE))

    def creat_path(self):
        #start
        start_x, start_y = self.npc
        start = self.grid.node(start_x, start_y)

        #end
        mouse_pos = pygame.mouse.get_pos()
        end_x, end_y = mouse_pos[0] // TILESIZE, mouse_pos[1] // TILESIZE
        end = self.grid.node(end_x, end_y)

        #path
        finder = AStarFinder(diagonal_movement = DiagonalMovement.always)
        self.path,_ = finder.find_path(start, end, self.grid)
        self.grid.cleanup()
        print(self.path)

    def update(self):
        self.mouse_active_cell()


class Npc(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        super().__init__()
        self.game = game
        self._layer = NPC_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.hergth = TILESIZE

        self.image = pygame.Surface([self.width, self.hergth])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.speed = 0.6
        self.direction = pygame.math.Vector2(0,0)
        self.path = []

    def get_coord(self):
        return (self.x, self.y)