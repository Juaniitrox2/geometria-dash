import pygame
import Modules.Core.NewColliderManager as NewColliderManager
import Modules.Data.templatecolores as Colors
import Modules.Core.ParticleManager as ParticleManager
import Modules.Core.EventManager as EventManager
import Main
import numpy

Modes = [
    "Ship",
    "Cube",
    "Ball",
    "Spider",
    "Ufo",
    "Robot",
]
ModeSizes = {
    "Ship":[75,75],
    "Cube":[50, 50],
    "Ball":[60,60]
}

DEFAULT_JUMP_HEIGHT = 13.5
ActiveCharacter = None

def Lerp(a, b, c):
    return (1 - c) * a + c * b

class Character:
    def __init__(self, StartOptions):
        self.Mode = "Cube"
        self.MidAir = False

        self.BallDebounce = 0
        self.DegreeRotation = 0
        self.RestartPlayer()
        self.SwitchMode(StartOptions["Mode"] if StartOptions.get("Mode") else "Cube")
        self.CharacterIcon = pygame.image.load("local\Assets\Sprites/" + self.Mode + ".png") 

    def RestartPlayer(self):
        self.Collider = NewColliderManager.new({"Height": 50, "Width":50, "Location":(Main.ScreenResolution[0]/2, Main.ScreenResolution[1] - 30), "Tags":["Player"]})
        self.SwitchMode(self.Mode)
        self.DegreeRotation = 0
        self.MidAir = False

    def RenderPlayerVisuals(self, screen):
        GravitySign = numpy.sign(NewColliderManager.WORLD_GRAVITY)

        # LOGIC
        RotSpeed = 8 if self.Mode == "Cube" else 12
        if self.Mode != "Cube":
            self.Collider.TerminalVelocity = True
        else:
            self.Collider.TerminalVelocity = False
            
        # VISUALS FOR ROTATING THE CUBE
        CharacterRotation = self.DegreeRotation
        if self.MidAir == True :
            self.DegreeRotation -= GravitySign * RotSpeed
        elif not NewColliderManager.FROZEN:
            if self.Mode == "Cube":
                Rotations = [0, -90, -180, -270]
                Closest = 0

                for i in Rotations:
                    if abs(CharacterRotation) > abs(i):
                        Closest = i

                CharacterRotation = Closest * -GravitySign
            elif self.Mode == "Ball":
                self.DegreeRotation -= GravitySign * RotSpeed

        if self.Mode == "Ship":
            Velocity = self.Collider.Velocity
            NewRotation = -Velocity[1] * 1.5 + 5

            self.DegreeRotation = Lerp(self.DegreeRotation, NewRotation, 0.6)

            CharacterRotation = self.DegreeRotation
        else:
            if self.DegreeRotation < -360 or (self.DegreeRotation < 0 and GravitySign == -1) or (self.DegreeRotation > 0 and GravitySign == 1) or self.DegreeRotation > 360:
                self.DegreeRotation = 0
        
        NewImage = pygame.transform.rotate(self.CharacterIcon, CharacterRotation)
        Rect = NewImage.get_rect()
        Rect.center = (self.Collider.Location[0] + self.Collider.Width/2, self.Collider.Location[1] + self.Collider.Height/2)

        screen.blit(NewImage, Rect)

    def Action(self, ActiveInput, FrameInput):
        GravitySign = numpy.sign(NewColliderManager.WORLD_GRAVITY)
        TriggerList = self.Collider.CollisionList
        JumpHeight = DEFAULT_JUMP_HEIGHT
        TouchedTrigger = False
        Object = None

        for Trigger in TriggerList:
            if Trigger.IsTrigger:
                if Trigger.Tags.count("ignoreobject") > 0:
                    continue
                
                Type = Trigger.Tags[-1]
                if Type in Modes:
                    self.SwitchMode(Type)           
                    continue

                if Trigger.Tags[0] == "Collectable":
                    #Codigo de coleccionables
                    Trigger.Disabled = True
                    continue

                # logic
                TouchedTrigger = True
                Color = "Blue" if Trigger.Tags.count("Blue") > 0 else "Yellow" if Trigger.Tags.count("Yellow") > 0 else "Pink" if Trigger.Tags.count("Pink") > 0 else "Green"
                JumpHeight = GetJumpBehavior(Color,Type)
                if Type == "JumpOrb" and not(FrameInput):
                    TouchedTrigger = False

                Object = Trigger
                if TouchedTrigger:
                    Trigger.Disabled = True
        self.MassMultiplier = 0.5 if self.Mode == "Ship" else 1
        
        if not(ActiveInput):
            if self.Mode == "Ship":
                self.Collider.SetAcceleration(0, 0)
            if TouchedTrigger and Type == "JumpPad":      
                OrbParticles(Color,Object)             
                self.Collider.SetVelocity(0, GravitySign * JumpHeight)
            return     
                 
        self.BallDebounce -= 1

        if TouchedTrigger:
            OrbParticles(Color, Object)
            if Color == "Green" or Color == "Blue":
                NewColliderManager.WORLD_GRAVITY *= -1

        OrbJump = False
        if self.Collider.TriggerCollision and TouchedTrigger:
            OrbJump = True
            self.Collider.SetVelocity(0, GravitySign * JumpHeight) 

        if not OrbJump and self.Mode == "Cube":
            self.Collider.SetVelocity(0, GravitySign * JumpHeight)
            
        
        if self.Mode == "Ship":
            self.Collider.SetAcceleration(0, NewColliderManager.WORLD_GRAVITY)
            if (self.Collider.Velocity[1] > 0 and GravitySign == 1) or (self.Collider.Velocity[1] < 0 and GravitySign == -1):
                self.Collider.Velocity[1] = 0
        
        if self.Mode == "Ball" and self.BallDebounce <= 0:
            self.BallDebounce = 5
            self.Collider.SetVelocity(0, -GravitySign * 18)
            NewColliderManager.WORLD_GRAVITY *= -1

    def SwitchMode(self, NewMode):
        Tags = self.Collider.Tags
        if Tags.count(self.Mode + "mode") > 0:
            for tag in Tags:
                if tag == self.Mode + "mode":
                    Tags.pop(Tags.index(tag))

        if not(Tags.count(NewMode + "mode") > 0):
            Tags.append(NewMode + "mode")

        self.CharacterIcon = pygame.image.load("local\Assets\Sprites/" + NewMode + ".png") 
        self.CharacterIcon = pygame.transform.scale(self.CharacterIcon, ModeSizes[NewMode])
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
        JumpHeight = 22
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