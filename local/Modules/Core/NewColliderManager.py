import math
import pygame
import numpy
import Main
import Modules.Data.templatecolores as Colors
import Modules.Core.EventManager as EventManager

WorldColliders = []

WORLD_GRAVITY = 9.807
FROZEN = True
GLOBAL_SPEED_MULTIPLIER = 1
CURRENT_FRAME = 0
FRAME_RATE = 60
CAMERA_RENDER_Y = 0

class Collider:
    def __init__(self, Properties):
        self.Tags = Properties["Tags"] if Properties.get("Tags") else []
        self.CollisionList = []
        self.Velocity = [0, 0]
        self.Acceleration = [0, 0]
        self.Location = Properties["Location"] if Properties.get("Location") else [0, 0]
        self.Debug = Properties["Debug"] if Properties.get("Debug") else False
        self.IsTrigger = Properties["Trigger"] if Properties.get("Trigger") else False
        self.Static = Properties["Static"] if Properties.get("Static") else False
        self.Overlapping = False
        self.IsColliding = False
        self.Grounded = False
        self.Disabled = False
        self.TriggerCollision = False
        self.__rendered__ = True
        self.MassMultiplier = 1
        self.Width = Properties["Width"] if Properties.get("Width") else 50
        self.Height = Properties["Height"] if Properties.get("Height") else 50
        self.Mass = math.sqrt((self.Height*self.Width)/2)
        self.Rect = pygame.Rect(self.Location[0], self.Location[1], self.Width, self.Height)

        WorldColliders.append(self)

    def Update(self):
        global CAMERA_RENDER_Y

        if not(self.__rendered__):
            return

        self.UpdatePhysics()
        self.Rect = pygame.Rect(self.Location[0], self.Location[1], self.Width, self.Height)
        self.CollisionList = self.GetCollidingObjects()

        if self.Location[1] <= -100:
            self.Overlapping = True

        if len(self.CollisionList) > 0 or self.Grounded:
            self.IsColliding = True
        else:
            self.IsColliding = False

        return

    def GetCollidingObjects(self):
        SCREEN_RES = EventManager.ScreenSize
        UNDER_LIMIT = SCREEN_RES[1] - 30

        CollidingList = []
        GravY = numpy.sign(WORLD_GRAVITY)
        
        self.Overlapping = False
        TriggerCounter = 0

        for Collider in WorldColliders:
            if Collider == self:
                continue

            IsColliding = self.Rect.colliderect(Collider.Rect) 
            self.Rect = pygame.Rect(self.Location[0], self.Location[1] + self.Velocity[1], self.Width, self.Height)
            IsColliding = self.Rect.colliderect(Collider.Rect) and IsColliding
            OverlapY = self.Location[1] > Collider.Location[1] and self.Location[1] < Collider.Location[1] + Collider.Height
            OverlapX = self.Location[0]< Collider.Location[0]
            OverlapY = (OverlapY and GravY == 1)
            isShip = self.Tags.count("Shipmode") > 0
            if isShip:
                OverlapY = False

            Overlapping = OverlapX or OverlapY
            if IsColliding and not(Collider.IsTrigger):
                if Overlapping:
                    self.Overlapping = True

            if IsColliding and (Collider.Tags.count("KillObject") >= 1):
                self.Overlapping = True
                 
            if IsColliding and not(Collider.Disabled):
                CollidingList.append(Collider)

            if Collider.IsTrigger and IsColliding:
                TriggerCounter += 1

        if self.Location[1] + self.Height >= UNDER_LIMIT and numpy.sign(WORLD_GRAVITY) == -1 and self.Tags.count("Cubemode") > 0:
            self.Overlapping = True


        self.TriggerCollision = len(CollidingList) == TriggerCounter if TriggerCounter > 0 else False

        return CollidingList
    
    def UpdatePhysics(self):
        SCREEN_RES = EventManager.ScreenSize
        UNDER_LIMIT = SCREEN_RES[1] - 30

        Mass = (self.Mass/6.5) * self.MassMultiplier
        AppliedGravity = WORLD_GRAVITY/Mass
        ApplyGravity = True
        GravitySign = numpy.sign(WORLD_GRAVITY)

        if FROZEN:
            return

        self.Location = [self.Location[0] + self.Velocity[0], self.Location[1] + self.Velocity[1]]

        if self.Static:
            self.Velocity[0] = -10
            return

        IsShip = self.Tags.count("Shipmode") > 0

        if self.IsColliding:
            for Collider in self.CollisionList:
                if Collider.IsTrigger:
                    continue

                Reach = Collider.Location[1] + Collider.Height
                Height = self.Location[1] + self.Height
                
                if IsShip:
                    if GravitySign == 1:
                        if self.Velocity[1] < 0: 
                            if self.Location[1] < Reach:
                                self.Velocity[1] = 0
                                self.Location[1] = Reach 
                        else:
                            if Height > Collider.Location[1]:
                                self.Velocity[1] = 0
                                self.Location[1] = Collider.Location[1] - self.Height + 1
                    else:
                        if self.Velocity[1] > 0: 
                            if Height > Collider.Location[1]:
                                self.Velocity[1] = 0
                                self.Location[1] = Collider.Location[1] - self.Height + 1
                        else:
                            if self.Location[1] < Reach:
                                self.Velocity[1] = 0
                                self.Location[1] = Reach 
                    
                elif GravitySign == -1:
                    if self.Location[1] < Reach:
                        ApplyGravity = False
                        self.Location[1] = (Collider.Location[1] + Collider.Height - 1)
                elif GravitySign == 1:
                    if Height > Collider.Location[1]:
                        ApplyGravity = False
                        self.Location[1] = (Collider.Location[1] - self.Height + 1)

        if self.Location[1] >= UNDER_LIMIT - self.Height:
            ApplyGravity = False if GravitySign == 1 else True
            if self.Velocity[1] > 0:
                self.Velocity[1] = 0

            self.Location[1] = (UNDER_LIMIT - self.Height) 
            self.Grounded = True
        else:
            self.Grounded = False

        
        Do = (self.Acceleration[1] <= 0) if GravitySign == 1 else (self.Acceleration[1] >= 0)
        if ApplyGravity and Do:
            self.Velocity[1] += AppliedGravity
        else:
            self.Velocity[1] -= self.Acceleration[1]/Mass

        if abs(self.Velocity[1] > 18):
            self.Velocity[1] = numpy.sign(self.Velocity[1]) * 16

        """if (self.Velocity[1]) > 10:
            self.Velocity[1] = (self.Velocity[1] + (10 - self.Velocity[1]) * 0.1)
        elif (self.Velocity[1]) < -10:
            self.Velocity[1] = (self.Velocity[1] + (-10 - self.Velocity[1]) * 0.1)"""

    def SetVelocity(self, x, y):
        self.Velocity[0] = x
        self.Velocity[1] = -y

    def SetAcceleration(self, x, y):
        self.Acceleration = [x, y]

    def DebugCollider(self, screen):
        if not(self.Debug):
            return

        USED_COLOR = Colors.ROJO if self.IsColliding else Colors.AMARILLO if not self.__rendered__ else Colors.VERDE

        pygame.draw.rect(screen, USED_COLOR, self.Rect)

    def IsOnlyTrigger(self):
        trigg = True
        for CollidingObject in self.CollisionList:
            if CollidingObject.IsTrigger:
                continue

            trigg = False
            break
        
        return trigg

def new(Properties):
    return Collider(Properties)

def Clear():
    global WorldColliders, WORLD_GRAVITY

    WORLD_GRAVITY = 9.807/2
    WorldColliders = []

def FrameStepped(Screen):
    global WorldColliders
    for Collider in WorldColliders:
            Collider.Update()
            Collider.DebugCollider(Screen) 

    
            


