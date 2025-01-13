import pygame
from configs import *
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
        if keys[pygame.K_a]:
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'
        if keys[pygame.K_d]:
            self.x_change += PLAYER_SPEED
            self.facing = 'right'
        if keys[pygame.K_w]:
            self.y_change -= PLAYER_SPEED
            self.facing = 'lup'
        if keys[pygame.K_s]:
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

        self.pos = self.rect.center
        self.speed = ROOBA_SPEED
        self.direction = pygame.math.Vector2(0,0)

        self.matrix = tilemap
        self.grid = Grid(matrix = tilemap)

        self.path = []
        self.collision_rects = []
        self.empty_path = []

    def go_to(self, end_pos=None):
        # start
        start_x, start_y = self.rect.centerx // TILESIZE, self.rect.centery // TILESIZE
        start = self.grid.node(start_x, start_y)

        # end
        if end_pos==None:
            end_pos = pygame.mouse.get_pos()
            end_x, end_y = end_pos[0] // TILESIZE, end_pos[1] // TILESIZE
        else:
            end_x, end_y = end_pos[0], end_pos[1]
        end = self.grid.node(end_x, end_y)

        # path
        finder = AStarFinder(diagonal_movement = DiagonalMovement.always)
        temp,_ = finder.find_path(start, end, self.grid)
        self.path = [(node.x, node.y) for node in temp]
        self.grid.cleanup()
        #print(self.path)
        self.create_collision_rects()
        self.get_direction()

    def create_collision_rects(self):
        if self.path:
            self.collision_rects = []
        for point in self.path:
                x = (point[0] * TILESIZE) + TILESIZE // 2
                y = (point[1] * TILESIZE) + TILESIZE // 2
                rect = pygame.Rect((x - 2,y - 2),(4,4))
                self.collision_rects.append(rect)
                    
    def get_direction(self):
        if self.collision_rects:
            start = pygame.math.Vector2(self.pos)
            end = pygame.math.Vector2(self.collision_rects[0].center)
            self.direction = (end - start)
        else:
            self.direction = pygame.math.Vector2(0,0)
            self.path = []

    def check_collisions(self):
        if self.collision_rects:
            for rect in self.collision_rects:
                if rect.collidepoint(self.pos):
                    del self.collision_rects[0]
                    self.get_direction()
        else:
            self.path = []
    
    def update(self):
        self.pos += self.direction * self.speed
        self.check_collisions()
        self.rect.center = self.pos

# 檢查點
class Check_point(pygame.sprite.Sprite):
    def __init__(self, game, x, y, name):
        self.game = game
        self._layer = CPOINT_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.name = name
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.hergth = TILESIZE

        self.image = pygame.Surface([self.width, self.hergth])
        self.image.fill(PINK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y