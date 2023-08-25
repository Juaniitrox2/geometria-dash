import Modules.Data.templatecolores as Colors
import Modules.Data.templateparticles as Templates
import Modules.Core.NewColliderManager as NewColliderManager
import Modules.Core.EventManager as EventManager
import random
import pygame
import time
import numpy

WorldEmitters = []

class Emitter(object):
    def __init__(self, Properties) -> None:
        for Property in Properties:
            if not(hasattr(self, Property)):
                setattr(self, Property, Properties[Property])

        self.Color = Colors.NEGRO if not(hasattr(self, "Color")) else self.Color

        self.ObjectLocked = None
        self.Enabled = True
        self.Location = [0, 0]
        self.ParticleObjects = []
        self.LastTime = 0
        self.CanRender = True
        self.Tag = ""

        WorldEmitters.append(self)
        
    def Draw(self, Screen):
        if self.CanRender == False and len(self.ParticleObjects) == 0:
            WorldEmitters.pop(WorldEmitters.index(self))

        if self.EmitType == "Spray":
            self.drawSprayType(Screen)
        elif self.EmitType == "Ring":
            self.drawRingType(Screen)

    def drawRingType(self, Screen):
        if time.time() - self.LastTime >= 1/self.EmitRate and self.Enabled == True and EventManager.IsRunning() and self.CanRender:
            if hasattr(self, "EmitOnce"):
                self.CanRender = False

            self.LastTime = time.time()

            TimeDelta = self.MaxTime - self.MinTime
            RandomSize = self.SizeMultiplier if hasattr(self, "SizeMultiplier") else [1, 1]
            RandomSize = random.random() * (RandomSize[0] - RandomSize[1]) + RandomSize[1]

            NewParticle = {
                "Lifetime":random.random() * TimeDelta + self.MinTime, 
                "Clock":time.time(),
                "Position":self.Location,
                "Radius":self.Radius * RandomSize,
                "Transparency":1,
            }

            self.ParticleObjects.append(NewParticle)

        for Particle in self.ParticleObjects:
            Radius = Particle["Radius"]
            if self.ObjectLocked != None:
                Pos = self.ObjectLocked.Location
                W = self.ObjectLocked.Width
                H = self.ObjectLocked.Height
                Particle["Position"] = [Pos[0] + W/2, Pos[1] + H/2]

            if EventManager.IsRunning():
                if hasattr(self, "TransparencyGoal"):
                    Particle["Transparency"] = self.TransparencyGoal * (1-(time.time() - Particle["Clock"])/Particle["Lifetime"])
                
                if hasattr(self, "SizeGoal"):
                    Overtime = (time.time() - Particle["Clock"])/Particle["Lifetime"]
                    Radius = Particle["Radius"] * (1 + (self.SizeGoal - 1) * Overtime)

                if time.time() - Particle["Clock"] > Particle["Lifetime"]:
                    self.ParticleObjects.pop(self.ParticleObjects.index(Particle))
                    continue
            
            ParticleObjSurface = pygame.Surface((Radius*2, Radius*2), pygame.SRCALPHA)
            ParticleObjSurface.set_alpha(Particle["Transparency"] * 255)

            if hasattr(self, "Texture") != False:
                Image = pygame.image.load("local/Assets/Sprites/" + self.Texture + ".png",)
                LoadedImage = pygame.transform.scale(Image, (Radius, Radius)) 
                LoadedImage.convert_alpha(ParticleObjSurface)

                ParticleObjSurface.blit(LoadedImage, (0, 0, Radius, Radius))
            else: 
                pygame.draw.circle(ParticleObjSurface, self.Color, (Radius, Radius), Radius/2)
                
                #ParticleObjSurface.blit()
            Pos = (Particle["Position"][0] - Radius, Particle["Position"][1] - Radius)
            Rect = pygame.Rect(Pos, (Radius/2, Radius/2))
            #Rect.center = Pos
            Screen.blit(ParticleObjSurface, Rect)
            
        
        
    def drawSprayType(self, Screen):
        if time.time() - self.LastTime >= 1/self.EmitRate and self.Enabled == True and EventManager.IsRunning() and self.CanRender:
            self.LastTime = time.time()
            if hasattr(self, "EmitOnce"):
                self.CanRender = False


            RandomDirection = self.Rotation + random.randint(-self.SpreadAngle//2, self.SpreadAngle//2)
            TimeDelta = self.MaxTime - self.MinTime
            RandomSize = self.SizeMultiplier if self.SizeMultiplier != None else [1, 1]
            RandomSize = random.random() * (RandomSize[0] - RandomSize[1]) + RandomSize[1]

            NewParticle = {
                "Direction":RandomDirection, 
                "Lifetime":random.random() * TimeDelta + self.MinTime, 
                "Clock":time.time(),
                "Position":self.Location,
                "Width":self.Width * RandomSize,
                "Height":self.Height * RandomSize,
                "Transparency":0,
            }
            NewParticle["Position"][1] -= NewParticle["Height"] if NewColliderManager.WORLD_GRAVITY > 0 and self.ObjectLocked == None else 0
            self.ParticleObjects.append(NewParticle)

        for Particle in self.ParticleObjects:
            Location = self.Location
            if self.TransparencyGoal:
                Particle["Transparency"] = self.TransparencyGoal * (1-(time.time() - Particle["Clock"])/Particle["Lifetime"])

            if EventManager.IsRunning():
                if time.time() - Particle["Clock"] > Particle["Lifetime"]:
                    self.ParticleObjects.pop(self.ParticleObjects.index(Particle))
                    continue
                Angle = numpy.deg2rad(Particle["Direction"])
                Xdir = numpy.cos(Angle)
                Ydir = numpy.sin(Angle)

                Xpos, Ypos = Particle["Position"][0], Particle["Position"][1]
                NextX, NextY = Xpos + Xdir * self.Speed, Ypos + Ydir * self.Speed

                Particle["Position"] = [NextX, NextY]
                Location = Particle["Position"]

                if self.ObjectLocked != None:
                    Pos = self.ObjectLocked.Location
                    W = self.ObjectLocked.Width
                    H = self.ObjectLocked.Height

                    Location = [Pos[0] + W/2, Pos[1] + H/2]
                    Location = [Particle["Position"][0] + Location[0], Particle["Position"][1] + Location[1]]

                    #print(Location, Particle["Position"])

            ParticleObjSurface = pygame.Surface((Particle["Width"], Particle["Height"]), pygame.SRCALPHA)
            ParticleObjSurface.set_alpha(Particle["Transparency"] * 255)

            if hasattr(self, "Texture") != False:
                Image = pygame.image.load("local/Assets/Sprites/" + self.Texture + ".png",)
                LoadedImage = pygame.transform.scale(Image, (Particle["Width"], Particle["Height"])) 
                LoadedImage.convert_alpha(ParticleObjSurface)

                ParticleObjSurface.blit(LoadedImage, (0, 0, Particle["Width"], Particle["Height"]))
            else:
                ParticleObjSurface.fill(self.Color)
            Screen.blit(ParticleObjSurface, (Location[0], Location[1]))
            
        
        
def FrameStepped(Screen) -> None:
    for ParticleEmitter in WorldEmitters:
        ParticleEmitter.Draw(Screen)

def Clear():
    global WorldEmitters
    WorldEmitters = []

def new(Template) -> Emitter:
    return Emitter(Template)