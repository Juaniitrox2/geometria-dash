import pygame
import Modules.Core.NewColliderManager as NewColliderManager
import Modules.Data.templatecolores as Colors
import Modules.Core.ParticleManager as ParticleManager
import Main
import numpy

DEFAULT_JUMP_HEIGHT = 12
ActiveCharacter = None

class Character:
    def __init__(self, StartOptions):
        self.Mode = "Cube"
        self.MidAir = False

        self.CharacterIcon = pygame.image.load("local\Assets\Sprites\CharacterSprite.png") 

        self.DegreeRotation = 0
        self.RestartPlayer()
        self.SwitchMode(StartOptions["Mode"] if StartOptions.get("Mode") else "Cube")

    def RestartPlayer(self):
        self.Collider = NewColliderManager.new({"Height": 50, "Width":50, "Location":(Main.ScreenResolution[0]/2, Main.ScreenResolution[1] - 30), "Tags":["Player"]})
        self.SwitchMode(self.Mode)
        self.DegreeRotation = 0
        self.MidAir = False

    def RenderPlayerVisuals(self, screen):
        GravitySign = numpy.sign(NewColliderManager.WORLD_GRAVITY)

        # LOGIC
        if self.Mode != "Cube":
            self.Collider.TerminalVelocity = True
        else:
            self.Collider.TerminalVelocity = False
            
        # VISUALS FOR ROTATING THE CUBE
        CharacterRotation = self.DegreeRotation
        if self.MidAir == True :
            self.DegreeRotation -= GravitySign * 8
        elif not NewColliderManager.FROZEN:
            Rotations = [0, -90, -180, -270]
            Closest = 0

            for i in Rotations:
                if abs(CharacterRotation) > abs(i):
                    Closest = i

            CharacterRotation = Closest * -GravitySign

        if self.DegreeRotation < -360 or self.Mode != "Cube" or (self.DegreeRotation < 0 and GravitySign == -1) or (self.DegreeRotation > 0 and GravitySign == 1) or self.DegreeRotation > 360:
            self.DegreeRotation = 0
        
        NewImage = pygame.transform.rotate(self.CharacterIcon, CharacterRotation)
        Rect = NewImage.get_rect()
        Rect.center = (self.Collider.Location[0] + self.Collider.Width/2, self.Collider.Location[1] + self.Collider.Height/2)

        screen.blit(NewImage, Rect)

    def Action(self, ActiveInput):
        GravitySign = numpy.sign(NewColliderManager.WORLD_GRAVITY)
        TriggerList = self.Collider.CollisionList
        JumpHeight = DEFAULT_JUMP_HEIGHT
        CanJump = True
        TouchedTrigger = False
        
        for Trigger in TriggerList:
            if Trigger.IsTrigger:
                if Trigger.Tags[0] == "Collectable":
                    Trigger.Location[0] = -300
                    return
                Trigger.Disabled = True 
                # logic
                TouchedTrigger = True
                Color = "Blue" if Trigger.Tags.count("Blue") > 0 else "Yellow" if Trigger.Tags.count("Yellow") > 0 else "Pink" if Trigger.Tags.count("Pink") > 0 else "Green"
                Type = Trigger.Tags[-1]
                JumpHeight = GetJumpBehavior(Color,Type) 
                Object = Trigger
        self.MassMultiplier = 0.5 if self.Mode == "Ship" else 1

        
        
        if not(ActiveInput):
            if self.Mode == "Ship":
                self.Collider.SetAcceleration(0, 0)
            if TouchedTrigger:                  
                if Type == "JumpPad":      
                    OrbParticles(Color,Object)               
                    self.Collider.SetVelocity(0, GravitySign * JumpHeight) 
            return          
        
        if TouchedTrigger:
            OrbParticles(Color,Object)
            if Color == "Green" or Color == "Blue":
                NewColliderManager.WORLD_GRAVITY *= -1

        if self.Mode == "Cube":
            self.Collider.SetVelocity(0, GravitySign * JumpHeight) 
        
        if self.Mode == "Ship":
            self.Collider.SetAcceleration(0, NewColliderManager.WORLD_GRAVITY)
            if (self.Collider.Velocity[1] > 0 and GravitySign == 1) or (self.Collider.Velocity[1] < 0 and GravitySign == -1):
                self.Collider.Velocity[1] = 0
            

    def SwitchMode(self, NewMode):
        Tags = self.Collider.Tags
        if Tags.count(self.Mode + "mode") > 0:
            for tag in Tags:
                if tag == self.Mode + "mode":
                    Tags.pop(Tags.index(tag))

        if not(Tags.count(NewMode + "mode") > 0):
            Tags.append(NewMode + "mode")

        self.Mode = NewMode
        self.Collider.Tags = Tags

def GetJumpBehavior(Color,Type):
    if Color == "Blue":
        JumpHeight = 18
    elif Color == "Pink":
        JumpHeight = 9
    elif Color == "Yellow":
        JumpHeight = 18
    elif Color == "Green":
        JumpHeight = -11
    elif Color == "Red":
        JumpHeight = 18
    return JumpHeight

def OrbParticles(Color,Trigger):
    OrbParticles = ParticleManager.new(ParticleManager.Templates.Ring)
    OrbParticles.ObjectLocked = Trigger
    OrbParticles.EmitOnce = True
    if Color == "Yellow":
        OrbParticles.Color = Colors.ORBE_AMARILLO
    elif Color == "Blue":
        OrbParticles.Color = Colors.ORBE_AZUL
    elif Color == "Green":
        OrbParticles.Color = Colors.ORBE_VERDE
    elif Color == "Pink":
        OrbParticles.Color = Colors.ORBE_ROSA


def new(StartOptions):
    global ActiveCharacter
    ActiveCharacter = Character(StartOptions)
    return ActiveCharacter

def getCharacter():
    return ActiveCharacter