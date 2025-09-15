from typing import List
import os
import pygame as pg
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame.math import Vector2 as Vec
from random import randint, choice
from math import sin
import json
import cProfile, pstats
from tkinter import Tk
from tkinter.filedialog import askopenfilename


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
    def __init__(self, position, size, text : str, onClick=None, fontSize = 20):
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
        self.center = Vec(self.rect.centerx, self.rect.centery + 4)

        self.fontSize = fontSize
        self.text = Text(text, self.x, self.y, font_size=self.fontSize, font_color=white)
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

# This class below is very AI, be careful :)
# Its atcually funny, because its very not well made? like omg AI is ass for this.
# Generally, I just use it for speeding up mundane tasks like making the colors, or some difficult line of code I dont know how to make
# It's atcually crazy to me, how far I've come, coding is a hobby now lets goo :D

# 12.9.2025 - Bate

"""
class Slider(Button):
    def __init__(self, position, size, text="Slider", onClick=None, min_val=0, max_val=100, start_val=50):
        super().__init__(position, size, text, onClick)

        # Add Slider-specific attributes
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.handle_rect = pg.Rect(self.x, self.y, self.width, self.height)  # slider knob/handle

    def update(self, mousePos, clicking):
        # Use Button hover logic
        super().update(mousePos, clicking)

        # Add slider-specific behavior (dragging the handle)
        if self.isHover and clicking:
            relative_x = mousePos[0] - self.x
            self.value = int((relative_x / self.width) * (self.max_val - self.min_val) + self.min_val)
            self.value = max(self.min_val, min(self.value, self.max_val))  # clamp

            # Update handle position
            self.handle_rect.centerx = self.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.width)

    def render(self, win):
        # Draw base button background
        super().render(win)

        # Draw slider line
        pg.draw.line(win, (200, 200, 200), (self.x, self.y + self.height // 2), (self.x + self.width, self.y + self.height // 2), 4)

        # Draw slider handle
        pg.draw.rect(win, (255, 0, 0), self.handle_rect)
"""
            


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
        self.timeIncrement = 5

        self.state = state
        self.color = color if color else lightGrey
        self.baseColor = self.color

        self.rect = pg.Rect(self.x, self.y, self.gridSize, self.gridSize)
        self.center = Vec(self.rect.center)
        self.renderOffset = 2
        self.renderOffsetHalf= self.renderOffset / 2
        self.size = self.gridSize - self.renderOffset

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
        

    def render(self, win):
        pg.draw.rect(win, self.color, self.rect)

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

        self.gridSize = 12
        self.gridSizeSurface = self.gridSize * self.gridSize
        self.rows = self.width // self.gridSize
        self.cols = self.height // self.gridSize
        self.tiles = []
        
        self.data = {}
        self.cashe = self.initCashe()

        # Image handling
        self.imagesPath = "img_MC/"
        self.imagesColorData = self.getImagesData()
        self.imageIndex = 0
        self.imageColors = self.imagesColorData[0]

        self.cashe = self.updateCashe(self.cashe)
        
        # Create grid 
        counter = 0
        for r in range(0, self.rows):
            for c in range(0, self.cols):
                self.tiles.append(Tile(counter, r, c, self.gridSize, color=self.imageColors[counter]))
                counter+=1

        # UI elements:
        self.ui = []
        self.buttonBack = Button((10, self.height//2), (50, 40), "<", self.cycleImageBack, fontSize=40)
        self.buttonUp = Button((self.width - 60, self.height//2), (50, 40), ">", self.cycleImage, fontSize=40)
        self.buttonIncSize = Button((80, 50), (50, 40), "+", self.increaseGridSize, fontSize=40)
        self.buttonDecSize = Button((10, 50), (50, 40), "-", self.decreaseGridSize, fontSize=40)
        self.txtGridSize = Text(f"Grid Size - {self.gridSize}", 10, 10, 20, white)
        self.buttonSelectImg = Button((10, 100), (150, 40), "Select Image", self.selectImageFile, fontSize=20)

        self.slider = Slider(self.screen, 10, 220, 150, 10, min=0, max=99, step=1)

        #self.slider = Slider((200, 10), (2,64), "Speed")
        #self.slider.onClick = self.slider.
        self.ui.append(self.buttonUp)
        self.ui.append(self.buttonBack)
        self.ui.append(self.buttonIncSize)
        self.ui.append(self.buttonDecSize)
        self.ui.append(self.txtGridSize)
        self.ui.append(self.buttonSelectImg)

        #self.ui.append(self.slider)

        # Event handling
        self.mouseLeftClick = False
        self.testCount = 0

    def selectImageFile(self):
        Tk().withdraw()  # hide the root window

        filename = askopenfilename(
            title="Select an image file",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )

        image = pg.image.load(filename).convert()
        imageColors = self.convertImg(image)
        self.imagesColorData.append(imageColors)
        self.imageColors = self.imagesColorData[-1]

        counter = 0
        for tile in self.tiles:
            tile.baseColor = self.imageColors[counter]
            counter+=1

    def decreaseGridSize(self):
        self.gridSize -= 2
        self.handleSizeChange()

    def increaseGridSize(self):
        self.gridSize += 2
        self.handleSizeChange()
        
    def handleSizeChange(self):
        self.txtGridSize.update(f"Grid Size - {self.gridSize}")

        self.gridSizeSurface = self.gridSize * self.gridSize
        self.rows = self.width // self.gridSize
        self.cols = self.height // self.gridSize
        self.tiles = []

        # Image handling
        self.imagesPath = "img_MC/"
        self.imagesColorData = self.getImagesData()
        self.imageIndex = 0
        self.imageColors = self.imagesColorData[0]

        self.cashe = self.updateCashe(self.cashe)
        
        # Create grid 
        counter = 0
        for r in range(0, self.rows):
            for c in range(0, self.cols):
                self.tiles.append(Tile(counter, r, c, self.gridSize, color=self.imageColors[counter]))
                counter+=1

    def isColorSame(self, color1, color2):
        if color1[0] == color2[0] and color1[1] == color2[1] and color1[2] == color2[2]:
            return True
        return False

    def initCashe(self):
        if os.path.exists("cashe/colorData.json"):
            with open("cashe/colorData.json", "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        return data

    def updateCashe(self, data):
        # Determine the starting index
        if data:
            i = max(map(int, data.keys())) + 1
        else:
            i = 0

        # Add new entries
        for chunkColor in self.imagesColorData:
            if chunkColor in data.values():
                continue
            data[i] = chunkColor
            i += 1

        # Save updated data
        with open("cashe/colorData.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return data


    def getImagesData(self):
        images = [f for f in os.listdir(self.imagesPath) if os.path.isfile(os.path.join(self.imagesPath, f))]
        imgColors = []
        for image in images:
            image = pg.image.load(self.imagesPath + image).convert()
            imageColors = self.convertImg(image)
            imgColors.append(imageColors)
        return imgColors
    
    def cycleImageBack(self):
        self.imageIndex -= 1
        self.imageIndex %= len(self.imagesColorData)
        self.imageColors = self.imagesColorData[self.imageIndex]

        counter = 0
        for tile in self.tiles:
            tile.baseColor = self.imageColors[counter]
            counter += 1

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

    def convertImg(self, image: pg.Surface):
        image = pg.transform.scale(image, (self.width, self.height))
        colors = []
        total_chunks = self.rows * self.cols

        for row in range(0, self.rows):
            for col in range(0, self.cols):
                color_sum = [0, 0, 0]
                x0 = row * self.gridSize
                y0 = col * self.gridSize

                for x in range(x0, x0 + self.gridSize):
                    for y in range(y0, y0 + self.gridSize):
                        r, g, b, *_ = image.get_at((x, y))
                        color_sum[0] += r
                        color_sum[1] += g
                        color_sum[2] += b

                colorAvg = [
                    color_sum[0] // self.gridSizeSurface,
                    color_sum[1] // self.gridSizeSurface,
                    color_sum[2] // self.gridSizeSurface
                ]

                # For the first chunk only: check cache for a full cached palette match
                if len(colors) == 0 and self.cashe:
                    for _id, cached_colors in self.cashe.items():
                        # ensure cached_colors length matches expected and first color matches
                        if isinstance(cached_colors, list) and len(cached_colors) == total_chunks and cached_colors[0] == colorAvg:
                            return cached_colors

                colors.append(colorAvg)

        # Sanity check
        if len(colors) != total_chunks:
            raise ValueError(f"convertImg returned {len(colors)} colors but expected {total_chunks}")

        return colors


    def drawGrid(self):    
        for tile in self.tiles:
            tile.update(self.mousePos)
            tile.render(self.screen)
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
            if type(element) == Button:
                element.update(self.mousePos, self.mouseLeftClick)

    def render(self):
        self.screen.fill(black)
        #self.drawOutline(1)
        self.drawGrid()
        
        for element in self.ui:
            element.render(self.screen)
        pg.display.update()

    def updateTitle(self, string):
        pg.display.set_caption(f"Grid simulation {self.id} - {string} FPS")

    def run(self):
        clock = pg.time.Clock()
        running = True
        while running:
            self.mouseLeftClick = False
            self.events = pg.event.get()
            for event in self.events:
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

"""
 Profiler start
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    
    game = Game("v0.1")
    game.run()
    
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(30)  # top 30 slowest calls
"""