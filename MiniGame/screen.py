import sys
import pygame
from configs import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGTH))
        self.font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()
        self.running = True
        
    def createTilemap(self):
        # blocks
        for i, row in enumerate(tilemap):
            for j , column in enumerate(row):
                if column == 0:
                    Block(self, j, i)
        # you
        Player(self, 6, 5)
        # npc
        self.rooba = Npc(self, 3, 2)
        # Check points
        for p in CHECK_POINTS.items():
            Check_point(self, p[0][0], p[0][1], p[1])
        
    def new(self):
        self.playing = True
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        
        self.createTilemap()
        
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # path find
                self.rooba.go_to((25,21))
                # Time show
                elapsed_time_ms = pygame.time.get_ticks()
                elapsed_time_sec = elapsed_time_ms // 1000
                minutes = elapsed_time_sec // 24
                seconds = elapsed_time_sec % 60
                print(f"Time: {minutes:02}:{seconds:02}")

            
    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        # Time show
        #elapsed_time_ms = self.clock.get_time()
        elapsed_time_ms = pygame.time.get_ticks()
        elapsed_time_sec = elapsed_time_ms // 1000
        minutes = elapsed_time_sec // 24
        seconds = elapsed_time_sec % 60
        time_text = f"Time: {minutes:02}:{seconds:02}"
        time_surface = self.font.render(time_text, True, WHITE)
        self.screen.blit(time_surface, (16, 0))

        pygame.display.update()
        self.clock.tick(FPS)

    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False

    def game_over(self):
        pass

    def intro_screen(self):
        pass

def main():
    g = Game()
    g.intro_screen()
    g.new()
    while g.running:
        g.main()

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()