existingSprites = []
LoadedSprites = {}

import Modules.Core.NewColliderManager as NewColliderManager
import pygame
import math
import os



def Init():
    path = "local/Assets/Sprites/"
    filenames = [f for f in os.listdir(path) if f.endswith(".png")]
    for name in filenames:
        imagename = str.split(name, ".png")[0]
        LoadedSprites[imagename] = pygame.image.load(os.path.join(path, name)).convert_alpha()

class Sprite:
    def __init__(self,Properties):
        self.JumpBoost = Properties["JumpBoost"] if Properties.get("JumpBoost") else 0
        self.Type = Properties["Type"]
        self.RythmAngle = 0
        self.Static = Properties["Static"] if Properties.get("Static") else False
        self.Scale = Properties["Scale"] if Properties.get("Scale") else 1
        self.Texture = LoadedSprites[self.Type]
        self.Rotation = Properties["Rotation"] if Properties.get("Rotation") else 0
        self.FittedTexture  = self.GetFittedTexture()     
        self.Collider =  NewColliderManager.new(Properties)
        existingSprites.append(self)      
        
    def GetFittedTexture(self):
        x = self.Scale
        TextureToUse = self.Texture

        ScaledTexture = pygame.transform.scale(TextureToUse, (50 * x,50 * x))
        ScaledTexture = pygame.transform.rotate(ScaledTexture,90*self.Rotation)
        return ScaledTexture    
        
def CheckRendering():
    global existingSprites
    for Sprite in existingSprites:    
        ObjectWidth = Sprite.Collider.Width
        if Sprite.Collider.Location[0] < -ObjectWidth:
            existingSprites.remove(Sprite)

class JumpOrb(Sprite):
    def __init__(self, Properties):     
        Properties["Height"] = 35
        Properties["Width"] = 35 
        Properties["Scale"] = 0.8
        Properties["Tags"] = [Properties["OrbType"]]
        Properties["Type"] = Properties["Tags"][0] + "Orb"
        Properties["Tags"].append("JumpOrb") 
        Properties["Trigger"] = True
        super().__init__(Properties)
        
class Spike(Sprite):
    def __init__(self,Properties):
        Properties["Type"] = "Spike"
        Properties["Tags"] = ["KillObject"]
        Rotation = Properties["Rotation"] if Properties.get("Rotation") else 0
        Cos = math.cos(math.radians(Rotation * 90))
        Sin = math.sin(math.radians(Rotation * 90))
        Properties["Width"] = abs(20 * Cos) + abs(40 * Sin)
        Properties["Height"] = abs(20 * Sin) + abs(40 * Cos)
        xDeviation,yDeviation = CalculateDeviation(Rotation)
        Properties["Location"][0] += xDeviation
        Properties["Location"][1] += yDeviation
        super().__init__(Properties)

class Saw(Sprite):
    def __init__(self,Properties):
        Properties["Type"] = "Saw"
        Properties["Tags"] = ["KillObject"]
        Properties["Width"] = 75
        Properties["Height"] = 75
        Properties["Scale"] = 2
        super().__init__(Properties)

class Block(Sprite):
    def __init__(self, Properties):
        Properties["Width"] *= 50
        Properties["Height"] *= 50
        super().__init__(Properties)

class JumpPad(Sprite):
    def __init__(self, Properties):
        Rotation = Properties["Rotation"] if Properties.get("Rotation") else 0
        Cos = math.cos(math.radians(Rotation * 90))
        Sin = math.sin(math.radians(Rotation * 90))
        X = abs(50 * Cos) + abs(20 * Sin)
        Y = abs(50 * Sin) + abs(20 * Cos)
        Properties["Width"] = X
        Properties["Height"] = Y

        Properties["Tags"] = [Properties["PadType"]]
        Properties["Type"] = Properties["Tags"][0] + "Pad"
        Properties["Tags"].append("JumpPad") 
        Properties["Location"][1] += 30 if Rotation == 0 else 0
        Properties["Location"][0] += 30 if Rotation == 1 else 0
        Properties["Trigger"] = True
        Properties["Debug"] = False
        super().__init__(Properties)

class Coin(Sprite):
    def __init__(self,Properties):
        Properties["Width"] =  75
        Properties["Height"] = 75
        Properties["Scale"] = 1.3
        Properties["Trigger"] = True
        Properties["Tags"] = ["Collectable"]
        Properties["Tags"].append(Properties["CoinType"]) if Properties.get("CoinType") else "Gold"
        Properties["Type"] =   Properties["Tags"][-1] + "Coin"
        super().__init__(Properties)

class Coin(Sprite):
    def __init__(self,Properties):
        Properties["Width"] =  75
        Properties["Height"] = 75
        Properties["Scale"] = 1.3
        Properties["Trigger"] = True
        Properties["Tags"] = ["Collectable"]
        Properties["Tags"].append(Properties["CoinType"]) if Properties.get("CoinType") else "Gold"
        Properties["Type"] =   Properties["Tags"][-1] + "Coin"
        super().__init__(Properties)



def Clear():
    global existingSprites
    existingSprites = []


def new(Properties):
    if Properties.get("Object") == "Block":
        return Block(Properties)
    elif Properties.get("Object") == "JumpOrb":
        return JumpOrb(Properties)
    elif Properties.get("Object") == "Spike":
        return Spike(Properties)
    elif Properties.get("Object") == "Saw":
        return Saw(Properties)
    elif Properties.get("Object") == "JumpPad":
        return JumpPad(Properties)
    elif Properties.get("Object") == "Coin":
        return Coin(Properties)
    
def FrameStepped(screen):
    for Sprite in existingSprites:
        if Sprite.Type == "Block":
            DrawBlock(screen, Sprite.Collider.Height, Sprite.Collider.Width, Sprite.Collider.Location)
        elif Sprite.Type == "Spike":
            xDeviation,yDeviation = CalculateDeviation(Sprite.Rotation)
            screen.blit(Sprite.FittedTexture, (Sprite.Collider.Location[0] -xDeviation,Sprite.Collider.Location[1] - yDeviation))

        elif Sprite.Type == "Saw" or Sprite.Type.count("Coin") > 0:
            ColliderSize = [Sprite.Collider.Height, Sprite.Collider.Width]
            ScaleDifference = ColliderSize[0]/2

            Texture = pygame.transform.rotate(Sprite.FittedTexture, Sprite.Rotation)
            ColliderRect = Texture.get_rect()
            ColliderRect.center = (Sprite.Collider.Location[0] + ScaleDifference, Sprite.Collider.Location[1] + ScaleDifference)

            screen.blit(Texture, ColliderRect)
            Sprite.Rotation -= 2 if Sprite.Type == "Saw" else 0
        elif Sprite.Type.count("Pad") > 0:
            Y = Sprite.Collider.Location[1] - (30 if Sprite.Rotation == 0 else 0)
            X = Sprite.Collider.Location[0] - (30 if Sprite.Rotation == 1 else 0)
            screen.blit(Sprite.FittedTexture, (X, Y))
        else: 
            Size = Sprite.FittedTexture.get_size()
            Pos = Sprite.Collider.Location
            Rect = pygame.Rect(Pos, Size)
            Rect.center = (Pos[0] + Size[0]/2.2 , Pos[1] + Size[1]/2.2)

            Rect.center = (Pos[0] + Size[0]/2.2, Pos[1]+Size[1]/2.2)
            screen.blit(Sprite.FittedTexture, Rect)


def CalculateDeviation(Rotation):
    xDeviation = 0
    yDeviation = 0
    if Rotation == 1 or Rotation == 3:
        yDeviation = 15
        xDeviation = 10 if Rotation == 1 else 0
    else: 
        xDeviation = 15
        yDeviation = 10 if Rotation == 4 or Rotation == 0 else 0
    return xDeviation,yDeviation

def DrawBlock(Screen, Height, Width,Location):
    XTiles = int(Width)//50
    YTiles = int(Height)//50

    for y in range(YTiles): 
        for x in range(XTiles):    
            if x == 0 and y == 0:
                Texture = LoadedSprites["Block23"] if YTiles > 1 else LoadedSprites["Block2"]
            elif x == XTiles-1 and y == 0:
                Texture = LoadedSprites["Block34"] if not y == YTiles - 1 else LoadedSprites["Block4"]
            else:
                Texture = LoadedSprites["Block24"]

            if x == 0 and y == YTiles - 1 and YTiles > 1:
                Texture = LoadedSprites["Block12"]
            elif x == XTiles - 1 and y == 0 and XTiles > 1:
                Texture = LoadedSprites["Block34"]
            elif x == XTiles - 1 and y == YTiles - 1 and XTiles > 1 and XTiles > 1:
                Texture = LoadedSprites["Block14"]
            elif x > 0 and XTiles > 1 and YTiles > 1 and y == 0:
                Texture = LoadedSprites["Block234"]
            elif x > 0 and XTiles > 1 and YTiles > 1 and y == YTiles - 1:
                Texture = LoadedSprites["Block124"]

            if x == XTiles - 1 and y == 0 and YTiles - 1 == 0:
                Texture = LoadedSprites["Block4"]

            if x + 1 == XTiles and x == 0:
                Texture = LoadedSprites["Block"]
                if YTiles == 2:
                    Texture = LoadedSprites["Block1"] if y == YTiles-1 else LoadedSprites["Block3"]
                elif YTiles > 2:
                    Texture = LoadedSprites["Block1"] if y == YTiles-1 else LoadedSprites["Block3"] if y == 0 else LoadedSprites["Block13"]
                

            Screen.blit(Texture, (x*50 + Location[0], y*50 + Location[1] + 1))