import pygame
import Modules.Data.templatecolores as Colors
import Modules.Core.EventManager as EventManager

CachedButtons = []
canBeRendered = True

class Button(object):
    def __init__(self, Properties):
        self.Location = Properties["Location"] if Properties.get("Location") else [0, 0]
        self.Anchor = "Center"
        self.Width = Properties["Width"] if Properties.get("Width") else 0.04
        self.Height = Properties["Height"] if Properties.get("Height") else 0.07
        self.Transparency = Properties["Transparency"] if Properties.get("Transparency") else 0
        self.Tag = Properties["Tag"] if Properties.get("Tag") else ""

        self.Enabled = Properties["Enabled"] if Properties.get("Enabled") != None else True
        self.Color = Properties["Color"] if Properties.get("Color") else Colors.GRIS
        self.Debounce = [0, False]
        self.Clicked = False
        self.Rect = pygame.Rect(self.Location[0], self.Location[1], self.Width, self.Height)

        CachedButtons.append(self)

    def draw(self, Screen):
        if not(canBeRendered) or self.Enabled != True:
            return
        
        if not self.Debounce[1]:
            self.Debounce[0] += 1
            if self.Debounce[0] >= 20:
                self.Debounce = [0, True]

        ScreenRes = EventManager.ScreenSize

        if self.Anchor == "Center":
            self.Rect.center = (self.Location[0] * ScreenRes[0], self.Location[1] * ScreenRes[1])

        self.Rect.width = self.Width * ScreenRes[0]
        self.Rect.height = self.Height * ScreenRes[1]

        secondsurface = pygame.Surface((self.Rect.width, self.Rect.height))
        secondsurface.set_alpha((1 - self.Transparency)* 255)
        secondsurface.fill(self.Color)

        Screen.blit(secondsurface, self.Rect)

    def __clicked__(self):
        if not(canBeRendered) or self.Enabled != True:
            return
        
        pos = pygame.mouse.get_pos()
        
        if self.Rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.Debounce[1]:
                self.Clicked = True
                self.Debounce = [0, False]
                if self.OnClickFunction != None:
                    self.OnClickFunction()
            else:
                self.Clicked = False

    def OnClickFunction(self):
        print(self, "mouse-button-1.click.executed()")
        

def new(Properties):
    return Button(Properties)

def Clear():
    global CachedButtons
    for btn in CachedButtons:
        btn = None

    CachedButtons = []

def FrameStepped(Screen):
    global CachedButtons

    for Button in CachedButtons:
        Button.draw(Screen)

def InputStepped(Keybinds):
    global CachedButtons

    for Button in CachedButtons:
        Button.__clicked__()
