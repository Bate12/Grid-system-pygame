from typing import List
import os
import pygame as pg
from pygame.math import Vector2 as Vec
from random import randint, choice
from math import sin


# 🎨 Colors
white      = [255, 255, 255, 255]
black      = [0, 0, 0, 255]
black2     = [49, 53, 63, 255]
red        = [255, 0, 0, 255]
green      = [0, 255, 0, 255]
limeGreen  = [50, 205, 50, 255]
blue       = [0, 0, 255, 255]
yellow     = [255, 255, 0, 255]
cyan       = [0, 255, 255, 255]
magenta    = [214, 122, 177, 255]
gray       = [128, 128, 128, 255]
lightGrey  = [230, 230, 230, 255]
orange     = [255, 165, 0, 255]
purple     = [128, 0, 128, 255]
pink       = [255, 192, 203, 255]
brown      = [165, 42, 42, 255]

class Text:
    def __init__(self, text, x, y, font_size=30, font_color=(0,0,0)):
        self.Pos = Vec(x, y)
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.isVisable = True
        
        self.fontPath = r"font.ttf"
        self.font = pg.font.Font(self.fontPath, self.font_size)
        self.surface = self.font.render(self.text, True, self.font_color)
        self.rect = self.surface.get_rect(topleft=self.Pos)

    def update(self, new_text):
        self.text = new_text
        self.surface = self.font.render(self.text, True, self.font_color)

    def render(self, win):
        if self.isVisable:
            win.blit(self.surface, self.rect)

class Button():
    def __init__(self, position, size, text : str, onClick):
        self.x, self.y = position
        self.width, self.height = size
        self.onClick = onClick

        self.alpha = 128
        self.color = black
        self.hoverColor = lightGrey
        self.color[3] = self.alpha
        self.hoverColor[3] = self.alpha
        
        self.surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        self.rect = self.surface.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.localRect = self.surface.get_rect()
        self.center = Vec(self.rect.center)

        self.text = Text(text, self.x, self.y, font_size=18, font_color=white)
        self.text.rect.center = self.center

        self.isHover = False

    def update(self, mousePos, clicking):
        self.isHover = self.rect.collidepoint(mousePos)
        if self.isHover and clicking:
            if self.onClick:
                self.onClick()

    def render(self, win):
        pg.draw.rect(self.surface, self.color, self.localRect, border_radius=5)
        if self.isHover:
            pg.draw.rect(self.surface, self.hoverColor, self.localRect, width=5, border_radius=5)
        win.blit(self.surface, (self.x, self.y))
        self.text.render(win)
            


class Tile:
    def __init__(self, id: int, row: int, col: int, gridSize: int, state: int = 0, color=()):
        self.id = id
        self.row = row
        self.col = col
        self.gridSize = gridSize
        self.gridSizeHalf = self.gridSize // 2
        self.x = self.row * self.gridSize
        self.y = self.col * self.gridSize

        self.sum = self.row + self.col
        self.arrowLen = self.sum / 10
        self.time = self.sum * 20
        self.timeIncrement = 10     

        self.state = state
        self.color = color if color else lightGrey
        self.baseColor = self.color

        self.rect = pg.Rect(self.x, self.y, self.gridSize, self.gridSize)
        self.center = Vec(self.rect.center)
        self.renderOffset = 2
        self.renderOffsetHalf= self.renderOffset / 2

    def generateColor(self, value):
        # For a different design try: max(self.baseColor)
        highestValueRGB = 255
        period = highestValueRGB * 2

        value = value % period
        if value > highestValueRGB:
            value = period - value  

        # scale goes 0 → 1 → 0
        scale = value / highestValueRGB  

        r = int(self.baseColor[0] * scale)
        g = int(self.baseColor[1] * scale)
        b = int(self.baseColor[2] * scale)

        self.color = (r, g, b)

    def generateAngle(self, mousePos=[]):
        self.time += self.timeIncrement
        self.angle = Vec(1, 0).rotate(self.time)
        
    def makeArrow(self, win):
        pg.draw.line(win, self.color, self.center, self.pos2, self.gridSizeHalf)
        #pg.draw.circle(win, self.color, self.pos2, 1)

    def update(self, mousePos):
        self.generateAngle()
        self.generateColor(self.time)
        self.pos2 = (self.angle * (self.gridSize*2)) + self.center

    def render(self, win, highlight=False):
        size = self.gridSize-self.renderOffset
        rect = pg.Rect(0, 0, size, size)
        rect.topleft = (self.x + self.renderOffsetHalf, self.y + self.renderOffsetHalf)
        pg.draw.rect(win, self.color, rect)

        return
        if highlight:
            pg.draw.rect(win, limeGreen, rect, 1)

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

        self.gridSize = 16
        self.gridSizeSurface = self.gridSize * self.gridSize
        self.rows = self.width // self.gridSize
        self.cols = self.height // self.gridSize
        self.tiles = []

        # Image handling
        self.imagesPath = "images/"
        self.imagesColorData = self.getImagesData()
        self.imageIndex = 0
        self.imageColors = self.imagesColorData[0]
        
        # Create grid 
        counter = 0
        for r in range(0, self.rows):
            for c in range(0, self.cols):
                self.tiles.append(Tile(counter, r, c, self.gridSize, color=self.imageColors[counter]))
                counter+=1

        # UI elements:
        self.ui = []
        self.button = Button((10, 10), (150, 50), "Change Image", self.cycleImage)
        self.ui.append(self.button)

        # Event handling
        self.mouseLeftClick = False
        self.testCount = 0

    def getImagesData(self):
        images = [f for f in os.listdir(self.imagesPath) if os.path.isfile(os.path.join(self.imagesPath, f))]
        imgColors = []
        for image in images:
            image = pg.image.load(self.imagesPath + image).convert()
            image = pg.transform.scale(image, (self.width, self.height))
            imageColors = self.convertImg(image)
            imgColors.append(imageColors)
        return imgColors

    def cycleImage(self):
        self.imageIndex += 1
        self.imageIndex %= len(self.imagesColorData)
        self.imageColors = self.imagesColorData[self.imageIndex]

        counter = 0
        for tile in self.tiles:
            tile.baseColor = self.imageColors[counter]
            counter += 1

    def printTest(self):
        self.testCount+=1
        print(f"{self.testCount} - Hello world")

    def convertImg(self, image : pg.Surface):
        colors = []
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                chunkColors = []
                rowPos = row * self.gridSize
                colPos = col * self.gridSize

                colorAvg = [0, 0, 0]
                for x in range(rowPos, rowPos + self.gridSize):
                    for y in range(colPos, colPos + self.gridSize):
                        pixelColor = image.get_at((x, y))
                        chunkColors.append(pixelColor)

                        r = pixelColor[0]
                        g = pixelColor[1]
                        b = pixelColor[2]

                        colorAvg[0] += r
                        colorAvg[1] += g
                        colorAvg[2] += b

                colorAvg[0] //= self.gridSizeSurface
                colorAvg[1] //= self.gridSizeSurface
                colorAvg[2] //= self.gridSizeSurface

                colors.append(colorAvg)

        return colors

    def drawGrid(self):    
        for tile in self.tiles:
            highlight = tile.rect.collidepoint(self.mousePos) 
            tile.render(self.screen, highlight)
        for tile in self.tiles:
            tile.makeArrow(self.screen)

    def drawOutline(self, thickness):
        for x in range(0, self.width, self.gridSize):
            pg.draw.line(self.screen, black2, (x, 0), (x, self.height), thickness)
        for y in range(0, self.height, self.gridSize):
            pg.draw.line(self.screen, black2, (0, y), (self.width, y), thickness)

    def update(self):
        self.mousePos = pg.mouse.get_pos()
        for element in self.ui:
            if type(element) != Text:
                element.update(self.mousePos, self.mouseLeftClick)
        for tile in self.tiles:
            tile.update(self.mousePos)

    def render(self):
        self.screen.fill(black)
        self.drawOutline(1)
        self.drawGrid()
        for element in self.ui:
            element.render(self.screen)
        pg.display.flip()

    def updateTitle(self, string):
        pg.display.set_caption(f"Grid simulation {self.id} - {string} FPS")

    def run(self):
        clock = pg.time.Clock()
        running = True
        while running:
            self.mouseLeftClick = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False

                if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.mouseLeftClick = True
                    

            clock.tick(60)
            fps = str(round(clock.get_fps(), 2))
            self.updateTitle(fps)

            self.update()
            self.render()

        pg.quit()


if __name__ == "__main__":
    game = Game("v0.1")
    game.run()
