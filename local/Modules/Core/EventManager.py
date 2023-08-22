import json
import pygame
import Modules.Data.templatecolores as Colors
import Modules.Core.NewColliderManager as NewColliderManager
import Modules.Core.ObjectManager as ObjectManager
import Modules.Core.ButtonManager as ButtonManager
import Modules.Core.ParticleManager as ParticleManager

InLevel = False
PlayerCharacter = None
PlrParticles = None
SelectedLevel = "Level1"
LevelData = None
LevelProgress = 0
ScreenSize = []

CachedModules = [
    NewColliderManager, ParticleManager, ObjectManager, ButtonManager
]

def RefreshScreen(Screen):
    NewColliderManager.CURRENT_FRAME += 1
    Collider = PlayerCharacter.Collider
    YPosition = Collider.Location[1] + Collider.Height if NewColliderManager.WORLD_GRAVITY > 0 else Collider.Location[1]
    if PlayerCharacter.MidAir == False:
        PlrParticles.Enabled = True
        PlrParticles.Location = [500, YPosition]
    else:
        PlrParticles.Enabled = False

    for Module in CachedModules:
        if hasattr(Module, "CheckRendering"):
            Module.CheckRendering()

        if hasattr(Module, "FrameStepped"):
            Module.FrameStepped(Screen)

def RenderLevel():
    global LevelData, LevelProgress

    LevelProgress += 1

    for List in LevelData["Sequence"]:
        for Object in List:
            if type(Object) == type(2.0) or type(Object) == type(2):
                if Object*10 != LevelProgress:
                    break
            else:
                NewProperties = {}
                for Property in Object:
                    NewProperties[Property] = Object[Property]

                NewProperties["Type"] = Object["Object"]
                NewProperties["Static"] = True
                NewProperties["Location"] = [ScreenSize[0], 0]
                Y = NewProperties["TilesY"]

                if Y < 0:
                    NewProperties["Location"][1] = -(Y + 1)*50
                else:
                    NewProperties["Location"][1] = (ScreenSize[1] - 30) - Y*50

                NewObject = ObjectManager.new(NewProperties)

                if str.find(NewProperties["Type"], "Orb") > 0:
                    OrbParticles = ParticleManager.new(ParticleManager.Templates.Square)
                    OrbParticles.SpreadAngle = 360
                    OrbParticles.Speed = 2.25
                    OrbParticles.ObjectLocked = NewObject.Collider

                    if NewProperties["OrbType"] == "Yellow":
                        OrbParticles.Color = Colors.ORBE_AMARILLO
                    elif NewProperties["OrbType"] == "Blue":
                        OrbParticles.Color = Colors.ORBE_AZUL
                    elif NewProperties["OrbType"] == "Green":
                        OrbParticles.Color = Colors.ORBE_VERDE
                    elif NewProperties["OrbType"] == "Pink":
                        OrbParticles.Color = Colors.ORBE_ROSA


def RenderInputs():
    for Module in CachedModules:
        if hasattr(Module, "InputStepped"):
            Module.InputStepped()

def IsRunning():
    return not NewColliderManager.FROZEN

def Restart():
    global LevelProgress, PlrParticles
    LevelProgress = 0
    NewColliderManager.CURRENT_FRAME = 0

    ParticleManager.Clear()
    NewColliderManager.Clear()
    if PlayerCharacter != None:
        PlayerCharacter.RestartPlayer()

        PlrParticles = ParticleManager.new(ParticleManager.Templates.Square)
    ObjectManager.Clear()

def IsInputDetected():
    return pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_SPACE]

def Init(ScreenResolution, Player):
    global LevelData, LevelProgress, PlayerCharacter, PlrParticles, ScreenSize

    PlayerCharacter = Player

    LevelObject = open("local/Assets/Levels/" + SelectedLevel + ".json")
    LevelData = json.load(LevelObject)
    LevelProgress = 0

    ScreenSize = ScreenResolution

    PlrParticles = ParticleManager.new(ParticleManager.Templates.Square)