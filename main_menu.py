import pygame
import sys
from button import Button
import main 
import constants

def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)

class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Menu")
        self.bg = pygame.image.load("assets/menu.jpg")
        self.play_button = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250),
                                  text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        self.options_button = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400),
                                     text_input="SETTINGS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        self.quit_button = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550),
                                  text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

    def run(self):
        while True:
            self.screen.blit(self.bg, (0, 0))
            menu_mouse_pos = pygame.mouse.get_pos()
            menu_text = get_font(100).render("ROCKET WATER", True, "#b68f40")
            menu_rect = menu_text.get_rect(center=(640, 100))
            self.screen.blit(menu_text, menu_rect)

            for button in [self.play_button, self.options_button, self.quit_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button.checkForInput(menu_mouse_pos):
                        self.start_game()
                    if self.options_button.checkForInput(menu_mouse_pos):
                        self.options()
                    if self.quit_button.checkForInput(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

    def start_game(self):
        main.run_game()

    def options(self):
        selected_color = "Red"
        default_color = "Black"
        
        difficulty_buttons = {
            "easy": Button(image=None, pos=(520, 500), text_input="EASY", font=get_font(45), base_color=default_color, hovering_color="Green"),
            "medium": Button(image=None, pos=(840, 500), text_input="MEDIUM", font=get_font(45), base_color=default_color, hovering_color="Green"),
            "hard": Button(image=None, pos=(1160, 500), text_input="HARD", font=get_font(45), base_color=default_color, hovering_color="Green")
        }

        graphics_buttons = {
            "low graphics": Button(image=None, pos=(700, 400), text_input="LOW", font=get_font(45), base_color=default_color, hovering_color="Green"),
            "high graphics": Button(image=None, pos=(1000, 400), text_input="HIGH", font=get_font(45), base_color=default_color, hovering_color="Green"),
        }
        
        def update_button_colors():
            for level, button in difficulty_buttons.items():
                if constants.OPPONENT_DIFFICULTY == constants.DIFFICULTY_LEVELS[level]:
                    button.base_color = selected_color
                else:
                    button.base_color = default_color

        def update_button_colors_Graphics():
            for level, button in graphics_buttons.items():
                if constants.LOW_SPEC == constants.GRAPHICS_SETTINGS[level]:
                    button.base_color = selected_color
                else:
                    button.base_color = default_color
        
        update_button_colors()
        update_button_colors_Graphics()
        
        while True:
            options_mouse_pos = pygame.mouse.get_pos()
            self.screen.fill("white")

            controls_text = [
                "WASD to control",
                "K to boost",
                "L to jump",
                "Space to change camera",
                "ESC to Menu"
            ]

            options_text = get_font(45).render("SETTINGS:", True, "Black")
            options_rect = options_text.get_rect(center=(300, 400))
            self.screen.blit(options_text, options_rect)

            options_text = get_font(45).render("BOT AI:", True, "Black")
            options_rect = options_text.get_rect(center=(250, 500))
            self.screen.blit(options_text, options_rect)


            for i, line in enumerate(controls_text):
                options_text = get_font(45).render(line, True, "Black")
                options_rect = options_text.get_rect(center=(640, 50 + i * 50))
                self.screen.blit(options_text, options_rect)

            options_back = Button(image=None, pos=(640, 600), text_input="BACK", font=get_font(75),
                                base_color="Black", hovering_color="Green")
            options_back.changeColor(options_mouse_pos)
            options_back.update(self.screen)

            for level, button in difficulty_buttons.items():
                button.changeColor(options_mouse_pos)
                button.update(self.screen)

            for level, button in graphics_buttons.items():
                button.changeColor(options_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if options_back.checkForInput(options_mouse_pos):
                        return
                    for level, button in difficulty_buttons.items():
                        if button.checkForInput(options_mouse_pos):
                            constants.OPPONENT_DIFFICULTY = constants.DIFFICULTY_LEVELS[level]
                            update_button_colors()
                    for level, button in graphics_buttons.items():
                        if button.checkForInput(options_mouse_pos):
                            constants.LOW_SPEC = constants.GRAPHICS_SETTINGS[level]
                            update_button_colors_Graphics()

            pygame.display.update()



if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
