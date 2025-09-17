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
from tkinter.filedialog import askopenfilename, askdirectory
import hashlib
import shutil
import subprocess
#import pyinstaller


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
        self.timeIncrement = 200

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

    def generateAngle(self, dt):
        self.time += self.timeIncrement * dt
        self.angle = Vec(1, 0).rotate(self.time)
        
    def makeArrow(self, win):
        pg.draw.line(win, self.color, self.center, self.pos2, self.gridSizeHalf)
        #pg.draw.circle(win, self.color, self.pos2, 1)

    def update(self, dt):
        self.generateAngle(dt)
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
        self.iconSurf = pg.image.load("icon.png")
        #self.iconTaskBar = pg.image.load("icon.ico")
        pg.display.set_icon(self.iconSurf)
        #subprocess.run([
        #"pyinstaller",
        #"--onefile",
        #"--icon=icon.ico",
        #"main.py"
        #], cwd=r"C:\Users\tadea\OneDrive\Plocha\Files\pokusy 2\Grid system simulation")

        self.gridSize = 12
        self.gridSizeSurface = self.gridSize * self.gridSize
        self.rows = self.width // self.gridSize
        self.cols = self.height // self.gridSize
        self.tiles = []
        
        self.data = {}
        self.baseCashePath = "cashe"
        self.endFormats = [".png", ".jpg", ".jpeg", ".bmp"]
        self.cashePath = f"{self.baseCashePath}/casheData-{self.gridSize}.json"
        self.cashe = self.initCashe()

        # Image handling
        self.imagesPath = "img_MC/"
        
        self.getFilesFromPath(self.imagesPath)
        self.imagesPaths = [f for f in os.listdir(self.imagesPath) if os.path.isfile(os.path.join(self.imagesPath, f))]
        self.imageIcons = []
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

        self.buttonSelectImg = Button((self.width - 160, self.height - 50), (150, 40), "Select Image", self.selectImageFile, fontSize=20)
        self.buttonSelectFile = Button((self.width - 310, self.height - 50), (150, 40), "Select Folder", self.selectImageFolder, fontSize=20)

        self.buttonDeleteLocalCashe = Button((self.width - 210, 2), (200, 40), "Delete Local cashe", self.deleteCasheLocal, fontSize=20)
        self.buttonDeleteCashe = Button((self.width // 2 - 75, self.height // 2 - 20), (150, 40), "Are you sure?", self.deleteCashe, fontSize=20)
        self.buttonDeleteCasheAsk = Button((self.width - 160, 50), (150, 40), "Delete cashe", self.switchDeleteCashe, fontSize=20)

        self.buttonDrop = Button((0, 0), (self.width, self.height), "<- Drop Files in window ->", self.switchDeleteCashe, fontSize=20)

        #self.slider = Slider((200, 10), (2,64), "Speed")
        #self.slider.onClick = self.slider.
        self.ui.append(self.buttonUp)
        self.ui.append(self.buttonBack)
        self.ui.append(self.buttonIncSize)
        self.ui.append(self.buttonDecSize)
        self.ui.append(self.txtGridSize)
        self.ui.append(self.buttonSelectImg)
        self.ui.append(self.buttonSelectFile)
        self.ui.append(self.buttonDeleteLocalCashe)
        self.ui.append(self.buttonDeleteCasheAsk)

        #self.ui.append(self.slider)

        # Event handling
        self.mouseLeftClick = False
        self.testCount = 0

    def getFilesFromPath(self, filepath):
        print(f"FilePath: {filepath}")
        paths =  [f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f))]
        return paths

    def onDropStart(self):
        print("Drop started")

    def onDropEnd(self):
        choice = self.checkPathType(self.droppedFile)
        print(f"Choice = {choice}")

        if choice == "folder":
            print(f"droppedFile: {self.droppedFile}")
            self.addFromFolder(self.droppedFile)
        elif choice == "image":
            self.addFromImage(self.droppedFile)
        else:
            print(f"Dropping of {self.droppedFile} couldn't happen, path type: {choice}")
        
    def checkPathType(self, path):
        if not path:
            return "not found"
        if os.path.isdir(path):
            return "folder"
        elif os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in self.endFormats:
                return "image"
            else:
                return "file"

    def switchDeleteCashe(self):
        if self.buttonDeleteCashe in self.ui:
            self.ui.remove(self.buttonDeleteCashe)
            return
        self.ui.append(self.buttonDeleteCashe)
        

    def deleteCashe(self):
        shutil.rmtree(self.baseCashePath)
        os.mkdir(self.baseCashePath)
        self.switchDeleteCashe()

    def deleteCasheLocal(self):
        try:
            os.remove(self.cashePath)
        except:
            pass
            #print(f"ERROR-'{self.cashePath}' does not exist")

    def selectImageFolder(self):
        foldername = askdirectory(
            title="Select a folder containing images"
        )
        if not foldername:
            return

        # Collect all image files from the folder
        """
        filepaths = [
            os.path.join(foldername, f)
            for f in os.listdir(foldername)
            if f.lower().endswith(tuple(self.endFormats))
        ]
        """
        

        self.addFromFolder(foldername)

    def addFromFolder(self, basePath):
        if not basePath:
            print(f"Path {basePath} does not exist")
            return
        
        filepaths = self.getFilesFromPath(basePath)
        #print(f"BasePath: {basePath}")
        #print(f"FilePaths: {filepaths}")

        for filename in filepaths:
            for end in self.endFormats:
                if end not in filename:
                    continue
                    
            fullPath = f"{basePath}\\{filename}"
            #print(f"append filename {fullPath}")
            self.imagesPaths.append(fullPath)
            image = pg.image.load(fullPath).convert()
            imageColors = self.convertImg(image)
            self.imagesColorData.insert(self.imageIndex, imageColors)

        # Load first image colors into tiles (like in selectImageFile)
        self.imageColors = self.imagesColorData[self.imageIndex]
        counter = 0
        for tile in self.tiles:
            tile.baseColor = self.imageColors[counter]
            counter += 1

    def onExit(self):
        pass
        #os.remove("cashe/colorData.json") 

    def addFromImage(self, filename):
        self.imagesPaths.insert(self.imageIndex, filename)
        image = pg.image.load(filename).convert()
        imageColors = self.convertImg(image)
        self.imagesColorData.insert(self.imageIndex,imageColors)
        self.imageColors = self.imagesColorData[self.imageIndex]

        counter = 0
        for tile in self.tiles:
            tile.baseColor = self.imageColors[counter]
            counter+=1


    def selectImageFile(self):
        filename = askopenfilename(
            title="Select an image file",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        if not filename:
            return

        self.addFromImage(filename)

    def decreaseGridSize(self):
        self.gridSize -= 2
        if self.gridSize <= 0:
            return
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

        # Cashe update
        self.cashePath = f"{self.baseCashePath}/casheData-{self.gridSize}.json"
        self.cashe = self.updateCashe(self.cashe)

        # Image handling
        self.imagesColorData = self.getImagesData()
        self.imageColors = self.imagesColorData[self.imageIndex]

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
        if os.path.exists(self.cashePath):
            with open(self.cashePath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            open(self.cashePath, "x")
            data = {}

        return data

    def updateCashe(self, data):
        # Determine the starting index
        if data:
            i = len(data)
        else:
            i = 0

        # Add new entries
        for chunkColor in self.imagesColorData:
            if chunkColor in data.values():
                continue
            data[i] = chunkColor
            i += 1

        # Save updated data
        with open(self.cashePath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return data


    def getImagesData(self):
        imgColors = []
        for path in self.imagesPaths:
            if "/" not in path:
                path = self.imagesPath + path
            image = pg.image.load(path).convert()
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
        image = pg.transform.scale(image, (self.rows, self.cols))
        #image = pg.transform.scale(image, (self.width, self.height))
        colors = []
        total_chunks = self.rows * self.cols

        for x in range(0, self.rows):
            for y in range(0, self.cols):
                r, g, b, *_ = image.get_at((x, y))
                clr = [r,g,b]
                colors.append(clr)  # make it hashable

        """
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
                colors.append(tuple(colorAvg))  # make it hashable
        """
        

        # Sanity check
        if len(colors) != total_chunks:
            raise ValueError(f"convertImg returned {len(colors)} colors but expected {total_chunks}")

        # Build a unique cache key from the color list
        key = hashlib.md5(str(colors).encode()).hexdigest()

        if key in self.cashe:
            return self.cashe[key]

        # Save to cache
        self.cashe[key] = colors
        return colors



    def drawGrid(self):    
        for tile in self.tiles:
            tile.update(self.dt)
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

                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.mouseLeftClick = True

                elif event.type == pg.DROPFILE:
                    self.droppedFile = event.file
                    self.onDropEnd()                

            self.dt = clock.tick(60) / 1000
            fps = str(round(clock.get_fps(), 2))
            self.updateTitle(fps)

            self.update()
            self.render()

        self.onExit()
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