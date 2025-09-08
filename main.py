from typing import List
import pygame as pg
from pygame.math import Vector2 as Vec
from random import randint
from noise import pnoise2
from math import sin


# 🎨 Colors
white = (255,255,255)
black = (0, 0, 0)
black2 = (49,53,63)
red = (255, 0, 0)
green = (0, 255, 0)
limeGreen = (50,205,50)
blue = (0, 0, 255)
yellow = (255, 255, 0)
cyan = (0, 255, 255)
magenta = (255, 0, 255)
gray = (128, 128, 128)
lightGrey = (230, 230, 230)
orange = (255, 165, 0)
purple = (128, 0, 128)
pink = (255, 192, 203)
brown = (165, 42, 42)


class Tile:
    def __init__(self, x: int, y: int, gridSize: int, state: int = 0, color=()):
        self.x = x
        self.y = y
        self.gridSize = gridSize
        self.phase = randint(0, 2000)
        self.time = 0
        self.timeIncrement = randint(100,1000) / 100000

        self.generateAngle()

        self.state = state
        self.color = color if color else lightGrey

        # make a rect for mouse collision
        self.rect = pg.Rect(self.x, self.y, gridSize, gridSize)

    def generateAngle(self):
        scale = 0.1
        self.time += self.timeIncrement
        #self.time += 0.01

        #noise_val = pnoise2(self.x * scale + self.time, self.y * scale + self.time + self.phase)
        noise_val = sin(self.time+self.phase)

        angle = noise_val * 360
        self.angleDegree = angle
        self.angle = Vec(1, 0).rotate(angle)

    def makeArrow(self, win):
        pg.draw.line(win, lightGrey, (self.x, self.y), self.pos2)
        pg.draw.circle(win, lightGrey, self.pos2, 1)

    def update(self):
        self.generateAngle()
        self.pos2 = (self.angle * (self.gridSize * 0.5)) + Vec(self.x, self.y)

    def render(self, win, highlight=False):
        size = self.gridSize-10
        rect = pg.Rect(0, 0, size, size)
        rect.topleft = (self.x+5, self.y+5)
        pg.draw.rect(win, self.color, rect)

        # 🟨 Draw border if highlighted
        if highlight:
            pg.draw.rect(win, limeGreen, rect, 3)

    def deleteOtherTile(self, tiles: List):
        for tile in tiles:
            if tile.x == self.x and tile.y == self.y:
                tile.delete(tiles)

    def delete(self, tiles: List):
        if self in tiles:
            tiles.remove(self)


class Game:
    def __init__(self, id):
        pg.init()
        self.id = id
        self.width, self.height = 800, 600
        self.screen = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption(f"Grid simulation {self.id}")

        self.gridSize = 20
        self.tiles = []

        # Create grid of cyan tiles
        for x in range(0, self.width, self.gridSize):
            for y in range(0, self.height, self.gridSize):
                self.tiles.append(Tile(x, y, self.gridSize, color=black2))

        # Add one red tile
        #self.tiles.append(Tile(400, 300, self.gridSize, color=red))

    def drawGrid(self):
        mouse_pos = pg.mouse.get_pos()
        for tile in self.tiles:
            highlight = tile.rect.collidepoint(mouse_pos)  # 🖱️ check mouse hover
            tile.render(self.screen, highlight)
            tile.makeArrow(self.screen)

    def drawOutline(self, thickness):
        for x in range(0, self.width, self.gridSize):
            pg.draw.line(self.screen, black2, (x, 0), (x, self.height), thickness)
        for y in range(0, self.height, self.gridSize):
            pg.draw.line(self.screen, black2, (0, y), (self.width, y), thickness)

    def update(self):
        for tile in self.tiles:
            tile.update()

    def render(self):
        self.screen.fill(black)
        self.drawOutline(1)
        self.drawGrid()
        pg.display.flip()

    def updateTitle(self, string):
        pg.display.set_caption(f"Grid simulation {self.id} - {string} FPS")

    def run(self):
        clock = pg.time.Clock()
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False

            clock.tick(60)
            fps = str(round(clock.get_fps(), 2))
            self.updateTitle(fps)

            self.update()
            self.render()

        pg.quit()


if __name__ == "__main__":
    game = Game("v0.1")
    game.run()
