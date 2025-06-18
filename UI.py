import pygame
import pygame_gui
import json
import cv2

class UI:
    def __init__(self, manager, screen):
        self.elements = []
        self.background_name = "sprites/main_menu.png"
        self.loading_name = "sprites/loading.png"
        self.death_screen_name = "sprites/death_screen.jpg"
        self.manager = manager
        self.screen = screen
        self.background = pygame.image.load(self.background_name).convert()
        self.background= pygame.transform.scale(self.background, (1200, 700))
        self.background.set_colorkey((1,0,0))
        self.option = None
        self.loading_interval = 100
        self.last_update = 0
        self.loading_bar = "/"
        self.loading_complete = 0
        self.gamemode = "Normal"
    def clear_elements(self):
        for element in self.elements:
            element.kill()
        self.elements.clear()
        
    def loading_screen(self):
        self.clear_elements()
        current_time = pygame.time.get_ticks()
        self.background = pygame.image.load(self.loading_name).convert()
        if self.loading_interval <= current_time - self.last_update and self.loading_complete < 10:
            self.loading_bar += "/"
            self.last_update = current_time
            self.loading_complete += 1
        loading_text = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((475,100),(230,50)), manager=self.manager)
        pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10,10),(210,30)),
            html_text="<font size=7>"+self.loading_bar+"</font>",
            manager=self.manager,
            container=loading_text, object_id="#loading"
            )
        
        self.elements.extend([loading_text])
        self.built()
        return self.loading_complete

    def death_screen(self):
        self.clear_elements()
        self.background = pygame.image.load(self.death_screen_name).convert()

        self.built()
        return self.loading_complete
    def main_menu(self):

        self.clear_elements()
        
        New_game = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((550, 300), (100, 50)), text='New game', manager=self.manager)
        about = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((550, 350), (100, 50)), text='About', manager=self.manager)
        score = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((550, 400), (100, 50)), text='Best scores', manager=self.manager)
        option = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((550, 450), (100, 50)), text='Options', manager=self.manager)
        exit = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((550, 500), (100, 50)), text='Exit', manager=self.manager)
        
        
        self.elements.extend([New_game,about, option, score,exit])
        self.built()

    def options(self):
        self.clear_elements()
        back = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((525, 450), (150, 50)), text='Back', manager=self.manager)
        gamemode =  pygame_gui.elements.UIDropDownMenu(options_list=['Baby mode', 'Normal', 'Dark souls'],starting_option=self.gamemode, relative_rect=pygame.Rect((525, 250), (150, 50)),manager=self.manager)
        self.elements.extend([back, gamemode])
        self.option = gamemode
        self.built()
    def get_selected_option(self):
        return self.option.selected_option if self.option else None
    
    def about(self):
        self.clear_elements()
        
        back = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((550, 450), (100, 50)), text='Back', manager=self.manager)
        about_text = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((300,50),(600,300)), manager=self.manager)
        pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10,10),(580,280)),
            html_text="""<b>Sterowanie</b>
            </hr>
            w,s,a,d - poruszanie się
            Strzałki - strzał w wybranym kierunku
            Wszystkie strzałki na raz - strzał we wszystkich kierunkach
            1,2,3 - wybór ulepszeń
            tab - wyświetlanie statystyk
            Cel:
            Przetrwaj jak najdłużej
            </hr>""",
            manager=self.manager,
            container=about_text
            )       
        self.elements.extend([back, about_text])
        self.built()
        
    def best_score(self):
        try:
            with open("top_score.json", "r") as file:
                table = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            table = [{"Difficulty":":/", "Score": "Not Found"}]
        self.clear_elements()

        table_window = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((425, 50), (350, 400)), manager=self.manager, object_id='#table_window')
        columns = list(table[0].keys())
        for i, col_name in enumerate(columns):
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((20 + i * 150, 20), (140, 30)),
                text=col_name.upper(),
                manager=self.manager,
                container=table_window
            )
        for row_index, row in enumerate(table):
            for col_index, col_name in enumerate(columns):
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((20 + col_index * 150, 60 + row_index * 30), (140, 30)),
                    text=str(row[col_name]),
                    manager=self.manager,
                    container=table_window, 
                    object_id="#cols"
        )
        back = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((550, 450), (100, 50)), text='Back', manager=self.manager)
                
        self.elements.extend([table_window, back])
        self.built()
    def built(self):
        
        self.manager.update(0.1)
        self.screen.blit(self.background, (0, 0))
        self.manager.draw_ui(self.screen)