import pygame
import pygame_gui
from UI import UI
from player import *
from enemy import *
import json
from operator import itemgetter


pygame.init()
back = "sprites/floor.png"  
framee = "sprites/frame.png"
run = True
X = 1200
Y = 700
screen = pygame.display.set_mode((X, Y))
clock = pygame.time.Clock()
dt = 0.1
font = pygame.font.Font('freesansbold.ttf', 32)
font_stats = pygame.font.Font('freesansbold.ttf', 20)
manager = pygame_gui.UIManager((1200, 700))
Pause = True
debug_mode = False
show_stats = False
death_screen = False
gamemode = 1
main_menu = True
options = False
game = False
score = False
about = False
starting_game = 0 
Player = None
loading = False
cam = None


pygame.mixer.music.load("music/main_theme.mp3")
pygame.mixer.music.play(-1, fade_ms=1000)
pygame.mixer.music.set_volume(0.1)

pygame.mixer.set_num_channels(16)

sound_button = pygame.mixer.Sound("music/button_pressed.wav")
sound_button.set_volume(0.1)
death_sound = pygame.mixer.Sound("music/death_sound.mp3")
death_sound.set_volume(0.1)

def load_sprite(sprit, width, height):
    upg_loaded_upg = {}
    for i in sprit:
        l = "sprites/"+i+".png"
        sprite = pygame.image.load(l).convert()
        sprite = pygame.transform.scale(sprite, (width, height))
        sprite.set_colorkey((255,255,255), pygame.RLEACCEL)
        upg_loaded_upg[i] = sprite
    return upg_loaded_upg

sprites_upg = ["dmg", "fire_rate", "heavy_fire_rate","double_shot", "triple_shot", "quad_shot", "soy_milk"]
loaded_upg = load_sprite(sprites_upg, 50, 50)
def events():   
    global debug_mode, show_stats,score,loading,death_screen, death_screen_initialized, score_initialized, loading_initialized, Pause, dt, run, game, main_menu,options, menu_initialized, options_initialized, mm, gamemode,about, about_initialized
    eventss = pygame.event.get()
    for event in eventss:
        if game:    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    show_stats = not show_stats
                if event.key == pygame.K_ESCAPE:
                    if Pause:
                        Pause = False
                        dt = 0
                    elif not Pause:
                        Pause = True
                        dt = 0.1
                if event.key == pygame.K_F1:
                    debug_mode = not debug_mode 
        if main_menu:
            pygame.mixer.music.set_volume(0.1)
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                sound_button.play()
                
                if event.ui_element.text == 'New game':
                    main_menu = False
                    loading = True
                if event.ui_element.text == 'Options':
                    main_menu = False
                    options = True
                    menu_initialized = False
                    options_initialized = False
                if event.ui_element.text == 'Best scores':
                    main_menu = False
                    score = True
                    menu_initialized = False
                    score_initialized = False
                if event.ui_element.text == 'Exit':
                    run = False
                if event.ui_element.text == "About":
                    main_menu = False
                    about = True
                    menu_initialized = False
                    about_initialized = False
            manager.process_events(event)
        if loading:
            if mm.loading_screen() >= 10:
                loading = False
                game = True
                menu_initialized = False
                loading_initialized = False
            manager.process_events(event)
            
        if score:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                sound_button.play()
                if event.ui_element.text == 'Back':
                    main_menu = True
                    score = False
                    menu_initialized = False
                    score_initialized = False 
            manager.process_events(event)
        if death_screen:

            if event.type == pygame.MOUSEBUTTONDOWN:
                death_sound.stop()
                menu_initialized =False
                main_menu = True
                death_screen = False
                death_screen_initialized = False
                mm.background = pygame.image.load(mm.background_name)
        if about:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                sound_button.play()
                if event.ui_element.text == 'Back':
                    main_menu = True
                    about = False
                    menu_initialized = False
                    about_initialized = False 
            manager.process_events(event)
        if options:
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                sound_button.play()
                opt = mm.get_selected_option()
                if opt[0] == "Baby mode":
                    gamemode = 0.5
                    
                if opt[0] == "Normal":
                    gamemode = 1
                if opt[0] == "Dark souls":
                    gamemode = 1.5
                mm.gamemode = opt[0]
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                sound_button.play()
                if event.ui_element.text == 'Back':
                    main_menu = True
                    options = False
                    menu_initialized = False
                    options_initialized = False
            manager.process_events(event)    
        if event.type == pygame.QUIT:
            run = False   
    if Player is not None:    
        Sprites.update(dt,Sprites, bullets, en, bullet_sprite, eventss)
        cam.update(Player, X, Y) 
def play():
    global starting_game,Player,cam, game,  gamemode, framee, death_screen
    
    if starting_game == 0:
        Player = player(X // 2, Y // 2, 'sprites/player1.png')
        cam = camera(X/2, Y/2)
        Sprites.add(Player) 
        starting_game += 1
    if Player.round == 0:
        Player.round = 1
        for _ in range(10 * Player.round):
            x, y = get_spawn_position_around_player(Player.posx, Player.posy, 250, 500)
            enemy = enemy1(x, y, enemy_sprite_normal, 1*gamemode, 1*gamemode, 1*gamemode)
            en.add(enemy) 
    if Player.hp <= 0:
        try:
            with open("top_score.json", "r") as file:
                table = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            table = []

        table.append({"Difficulty": gamemode, "Survived": Player.round})

        sorted_table = sorted(table, key=itemgetter('Survived'), reverse=True)

        top_scores = sorted_table[:10]
        mm.loading_complete = 0
        mm.loading_bar = "/"
        mm.background = pygame.image.load(mm.background_name).convert()
        with open("top_score.json", "w") as f:
            json.dump(top_scores, f, indent=4)
        
        
        Player = None
        death_screen = True
        starting_game = 0
        game = False
  

    if Player is not None:
        dmg = font_stats.render("DMG: "+str(Player.dmg), True, "white", "brown")
        dmgrect = dmg.get_rect()
        dmgrect.center = (50, 320)
        
        shoot_rate = font_stats.render("SHOOT RATE: "+str(Player.shoot_rate), True, "white", "brown")
        shoot_raterect = shoot_rate.get_rect()
        shoot_raterect.center = (96, 350)
        
        heavy_shoot_rate = font_stats.render("HEAVY ATTACK RATE: "+str(Player.heavy_shoot_rate), True, "white", "brown")
        heavy_shoot_raterect = heavy_shoot_rate.get_rect()
        heavy_shoot_raterect.center = (126, 380)
        
        text = font.render("HP: "+str(round(Player.hp))+"/"+str(Player.max_hp), True, "white", "brown")
        textRect = text.get_rect()
        textRect.center = (150, 20)
        
        exp_txt = font.render("EXP: "+str(int(Player.exp))+"/"+str(Player.max_exp), True, "white", "brown")
        exp_txt_rect = exp_txt.get_rect()
        exp_txt_rect.center = (1050, 20)
        
        rounds = font.render("Runda: "+str(Player.round), True, "white", "brown")
        round_rect = rounds.get_rect()
        round_rect.center = (600, 20)

        

        
        background = pygame.image.load(back).convert()
        background = pygame.transform.scale(background, (300, 300))
        background.set_colorkey((255,255,255)) 
        tile_width, tile_height = background.get_size()
        camera_offset_x, camera_offset_y = cam.camera.topleft
        tiles_x = X // tile_width + 2
        tiles_y = Y // tile_height + 2
        for i in range(tiles_x):
            for j in range(tiles_y):
                x = i * tile_width + camera_offset_x % tile_width - tile_width
                y = j * tile_height + camera_offset_y % tile_height - tile_height
                screen.blit(background, (x, y))
        
        
                
        
        if debug_mode:
            # Hitbox gracza
            pygame.draw.rect(screen, (0, 255, 0), cam.apply(Player), 2)

            # Hitboxy przeciwników
            for e in en:
                pygame.draw.rect(screen, (255, 0, 0), cam.apply(e), 2)

            # Hitboxy pocisków
            for b in bullets:
                pygame.draw.rect(screen, (0, 0, 255), cam.apply(b), 2)

        enemy_wave(Player, en, enemy_sprite_fast, enemy_sprite_strong, enemy_sprite_normal, gamemode )  
        for object in Sprites:
            screen.blit(object.sprite, cam.apply(object))

        for i in en:
            i.move_to_player(Player, dt)
            screen.blit(i.sprite, cam.apply(i))
            if pygame.sprite.collide_rect(i, Player):
                i.hit_player(Player)
            for j in en:
                if j != i:
                    i.coll_in(j)

        en.update(Player)
        bullets.update(Player, dt, cam, X, Y)
        
            
        for b in bullets:
            for e in en:
                if pygame.sprite.collide_rect(b, e):
                    b.hit(e)
            screen.blit(b.sprite, cam.apply(b))
        if Player.pending_upgrades != []:
            l=0
            for i in Player.pending_upgrades:
                upg = loaded_upg[i].copy()

                screen.blit(upg, (470+l, 550)) 
                l+=105  
        screen.blit(frame, (0, 0))        
        screen.blit(text, textRect) 
        screen.blit(exp_txt, exp_txt_rect) 
        screen.blit(rounds, round_rect)
        if show_stats:
            screen.blit(dmg, dmgrect) 
            screen.blit(shoot_rate, shoot_raterect) 
            screen.blit(heavy_shoot_rate, heavy_shoot_raterect)

    
    
frame = pygame.image.load(framee).convert_alpha()
frame.set_colorkey((0,0,1))


enemy_sprite_normal = pygame.image.load('sprites/en_normal.png').convert_alpha()
enemy_sprite_normal = pygame.transform.scale(enemy_sprite_normal, (100, 120))
enemy_sprite_normal.set_colorkey((254,255,255), pygame.RLEACCEL)

enemy_sprite_fast = pygame.image.load('sprites/en_fast.png').convert_alpha()
enemy_sprite_fast = pygame.transform.scale(enemy_sprite_fast, (100, 100))
enemy_sprite_fast.set_colorkey((254,255,255), pygame.RLEACCEL)

enemy_sprite_strong = pygame.image.load('sprites/en_strong.png').convert_alpha()
enemy_sprite_strong = pygame.transform.scale(enemy_sprite_strong, (100, 100))
enemy_sprite_strong.set_colorkey((254,255,255), pygame.RLEACCEL)


bullet_sprite = pygame.image.load("sprites/bullet.png").convert_alpha()
bullet_sprite = pygame.transform.scale(bullet_sprite, (20, 10))
bullet_sprite.set_colorkey((254,255,255))   

mm = UI(manager,screen)


Sprites = pygame.sprite.Group()
en = pygame.sprite.Group()
bullets = pygame.sprite.Group()

menu_initialized = False
options_initialized = False
score_initialized = False
about_initialized = False
loading_initialized = False
death_screen_initialized = False

while run:

    events()
    if game:
        menu_initialized = False
        play()
    elif main_menu:
        if not menu_initialized:
            mm.main_menu()
            menu_initialized = True
        mm.built()
    elif loading:
        if not loading_initialized:
            mm.loading_screen()
            loading_initialized = True
        mm.built()
    elif options:
        if not options_initialized:
            mm.options()
            options_initialized = True
        mm.built()
    elif about:
        if not about_initialized:
            mm.about()
            about_initialized = True
        mm.built()
    elif death_screen:
        if not death_screen_initialized: 
            pygame.mixer.music.set_volume(0)
            death_sound.play()
            mm.death_screen()
            death_screen_initialized = True
        mm.built()
    elif score:
        if not score_initialized:
            mm.best_score()
            score_initialized = True
        mm.built()
    pygame.display.update()
    clock.tick(60)
pygame.quit()