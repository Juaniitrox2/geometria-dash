import json
import pygame
import Modules.Data.templatecolores as Colors
import Modules.Core.NewColliderManager as NewColliderManager
import Modules.Core.ButtonManager as ButtonManager
import Modules.Core.EventManager as EventManager

def LoadMainMenu():
    NewColliderManager.FROZEN = True
    EventManager.InLevel = False
    EventManager.Restart()
    ButtonManager.Clear()

    LevelSelectButton = ButtonManager.new({
        "Location": [0.5, 0.5], 
        "Transparency":0.25, 
        "Width":0.12, 
        "Height":0.15, 
        "Tag":"MainMenu"
    })

    LevelSelectButton.OnClickFunction = LoadLevelSelectMenu
    
def LoadLevelSelectMenu():
    ButtonManager.Clear()

    Level1SelectButton = ButtonManager.new({
        "Location": [0.5, 0.5], 
        "Transparency":0.5, 
        "Width":0.16, 
        "Height":0.08, 
        "Tag":"SelectMenu",
        "Color":Colors.ROJO
    })

    def StartLevel1():
        NewColliderManager.FROZEN = False
        EventManager.InLevel = True

        LoadInLevelMenu()

    Level1SelectButton.OnClickFunction = StartLevel1

def LoadInLevelMenu():
    ButtonManager.Clear()

    PauseButton = ButtonManager.new({
        "Location": [0.025, 0.025], 
        "Transparency":0.5, 
    })

    Leave = ButtonManager.new({
        "Location": [0.3, 0.865],
        "Width":0.078,
        "Height":0.125,
        "Enabled": False,
        "Color": Colors.ROJO
    })

    Retry = ButtonManager.new({
        "Location": [0.7, 0.865], 
        "Width":0.078,
        "Height":0.125,
        "Enabled": False,
        "Color": Colors.AMARILLO
    })

    # Button functions
    def RetryFunction():
        EventManager.Restart()
        Pause()

    def Pause():
        NewColliderManager.FROZEN = not(NewColliderManager.FROZEN)

        Leave.Enabled = not(Leave.Enabled)
        Retry.Enabled = not(Retry.Enabled)

    Leave.OnClickFunction = LoadMainMenu
    Retry.OnClickFunction = RetryFunction
    PauseButton.OnClickFunction = Pause
