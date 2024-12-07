WIN_WIDTH = 640
WIN_HEIGTH = 480
TILESIZE = 32
FPS = 60

PLAYER_LAYER = 4
NPC_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER = 1

PLAYER_SPEED = 5

RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

tilemap = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B.............B....B',
    'B.............B....B',
    'B.............B....B',
    'B....B........B....B',
    'B....B.............B',
    'B....B.............B',
    'B....B.............B',
    'B......P...........B',
    'B..................B',
    'B.........B........B',
    'B.........B........B',
    'B.........B........B',
    'B.........B........B',
    'BBBBBBBBBBBBBBBBBBBB'
    ]

GRID_MATRIX = []
for i , row in enumerate(tilemap):
    GRID_MATRIX.append([])
    for j , col in enumerate(row):
        if col == 'B':
            GRID_MATRIX[i].append(0)
        else:
            GRID_MATRIX[i].append(1)