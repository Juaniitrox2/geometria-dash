import pygame
import Modules.Data.templatecolores as Colors
import Modules.Core.NewColliderManager as NewColliderManager
import Modules.Core.CharacterManager as CharacterManager
import Modules.Core.EventManager as EventManager
import Modules.Core.UIManager as UIManager

pygame.init()

ndea = True
ScreenResolution = [1000, 600]
Screen = pygame.display.set_mode(ScreenResolution) 
pygame.display.set_caption("")

finished = True
clock = pygame.time.Clock()
selected_level = "Level1"

def main():
    global finished
    finished = False

    UIManager.LoadMainMenu()

    PlayerCharacter = CharacterManager.new({"Mode":"Cube"})
    EventManager.Init(ScreenResolution, PlayerCharacter)

    while not finished:
        # EVENT LOGIC LOOP
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: 
                finished = True 
            
            if evento.type == pygame.MOUSEBUTTONDOWN or evento.type == pygame.KEYDOWN:
                EventManager.RenderInputs(pygame.key.get_pressed())

                EventManager.TriggerInputDetected(evento, "down")

        # GAME LOGIC 
        if EventManager.IsRunning():
            PlayerInput = EventManager.IsInputDetected()

            Input = False
            if not(PlayerCharacter.Collider.IsColliding):
                PlayerCharacter.MidAir = True

                if PlayerCharacter.Mode == "Ship" and PlayerInput:
                    Input = True
            else:
                if (PlayerCharacter.Mode == "Ship" or PlayerCharacter.Mode == "Cube") and PlayerInput:
                    Input = True

                PlayerCharacter.MidAir = False
                if PlayerCharacter.Collider.TriggerCollision:
                    PlayerCharacter.MidAir = True

            FrameInputDetected = EventManager.ActivatedTrigger()
            PlayerCharacter.Action(Input, FrameInputDetected)
            EventManager.RenderLevel()

            if PlayerCharacter.Collider.Overlapping:
                EventManager.Restart()
                
        else:
            PlayerCharacter.MidAir = False
        
        # GAME RENDERz
        Screen.fill(Colors.BLANCO)

        if EventManager.InLevel:
            Screen.fill(Colors.AZUL_OSCURO)
            PlayerCharacter.RenderPlayerVisuals(Screen)

        EventManager.RefreshScreen(Screen)
        # UPDATE THE SCREEN
        pygame.display.update()

        # FPS LIMIT
        clock.tick(NewColliderManager.FRAME_RATE)

# GAME LOOP
if __name__ == "__main__":
    main()  
