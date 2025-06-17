import pygame
import random
import time
import math


def get_spawn_position_around_player(player_posx, player_posy, min_dist, max_dist):
    angle = random.uniform(0, 2 * math.pi)  
    distance = random.uniform(min_dist, max_dist)
    x = player_posx + distance * math.cos(angle)
    y = player_posy + distance * math.sin(angle)
    return x, y

def choice_upgrade(player, rando):
    if rando == "soy_milk":
        player.dmg_miltiplayer *= 0.5       
        player.shoot_rate *= 0.3 
        player.shoot_rate_miltiplayer *= 1.2
        player.heavy_shoot_rate *= 0.4        
    if rando == "dmg":
        player.dmg += (20*player.dmg_miltiplayer)
    if rando == "fire_rate":
        player.shoot_rate = player.shoot_rate - (0.04*(player.shoot_rate_miltiplayer))
    if rando == "heavy_fire_rate":
        player.heavy_shoot_rate = player.heavy_shoot_rate - (0.06*player.shoot_rate_miltiplayer)
    if rando == "double_shot":
        player.double_shot = True
        player.tripple_shot = False
        player.quad_shot = False
        player.shoot_rate = player.shoot_rate+0.2
        player.heavy_shoot_rate = player.heavy_shoot_rate+0.6
        player.bullets_count += 1
    if rando == "triple_shot":
        player.double_shot = False
        player.tripple_shot = True
        player.quad_shot = False
        player.shoot_rate = player.shoot_rate+0.4
        player.heavy_shoot_rate = player.heavy_shoot_rate+1.2
        player.bullets_count += 2
        
    if rando == "quad_shot":
        player.double_shot = False
        player.tripple_shot = False
        player.quad_shot =  True
        player.shoot_rate = player.shoot_rate+0.7
        player.heavy_shoot_rate = player.heavy_shoot_rate+1.6
        player.bullets_count += 3
    player.shoot_rate = round(player.shoot_rate, 2)
    player.heavy_shoot_rate = round(player.heavy_shoot_rate, 2)

def enemy_wave(Player, en, enemy_sprite_fast, enemy_sprite_strong, enemy_sprite_normal, gamemode):
    if len(en) < Player.round*3 and Player.round > 0:
        Player.round += 1
        for _ in range(Player.round*3):
            champion_chance = random.randint(1,100)
            x, y = get_spawn_position_around_player(Player.posx, Player.posy, 250, 500)
            if champion_chance <= 10 + Player.round:
                what_champion = random.randint(1,2)
                if what_champion == 1:
                    enemy = enemy1(x, y, enemy_sprite_fast, 2*gamemode, 1*gamemode, 2*gamemode)
                else:
                    enemy = enemy1(x, y, enemy_sprite_strong, 1*gamemode, 2*gamemode, 3*gamemode)
            else:
                enemy = enemy1(x, y, enemy_sprite_normal, 1*gamemode, 1*gamemode, 1*gamemode)
            en.add(enemy)                         
    
      

class enemy1(pygame.sprite.Sprite):
    def __init__(self, start_posx, start_posy, sprite, mod_speed, mod_dmg, mod_exp):
        super(enemy1, self).__init__()
        self.exp = 40*mod_exp
        self.posx = start_posx
        self.posy = start_posy
        self.sprite = sprite.copy()
        self.rect = pygame.Rect(self.posx + 25, self.posy, 70, 90)
        self.hp = 100*mod_exp
        self.speed = 10 * mod_speed
        self.hit_time = 0
        self.dmg = 50 * mod_dmg
        self.facing_left = True
        self.player_hit_sound = pygame.mixer.Sound("music/hit_death_sound.wav")
        self.player_hit_sound.set_volume(0.1)
        self.player_dead_sound = pygame.mixer.Sound("music/hit_death_sound.wav")
        self.player_dead_sound.set_volume(0.4)
    def update(self, player):
        self.rect.topleft = (self.posx, self.posy)
        player.level_up()
        if self.hp <= 0:
            player.exp += self.exp
            self.kill()
        if len(player.pending_upgrades) != 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                choice_upgrade(player, player.pending_upgrades[0])
                player.pending_upgrades = []
            if keys[pygame.K_2]:
                choice_upgrade(player, player.pending_upgrades[1])
                player.pending_upgrades = []
            if keys[pygame.K_3]:
                choice_upgrade(player, player.pending_upgrades[2])
                player.pending_upgrades = []

    
    def hit_player(self, player):
        
        invincibility_frames = 2
        current_time = time.time()
        if (current_time-self.hit_time) > invincibility_frames:
            if player.hp <= 0:
                self.player_dead_sound.play()
                player.hp = 0
            else:
                self.player_hit_sound.play()
                player.hp -= self.dmg
                self.hit_time = current_time
            
    def move_to_player(self, player, dt):
        dx = player.posx - self.posx
        
        if dx >= 0:
            if not self.facing_left:
                self.sprite = pygame.transform.flip(self.sprite, True, False)
                self.facing_left = True
        elif dx < 0:
            if self.facing_left:
                self.sprite = pygame.transform.flip(self.sprite, True, False)
                self.facing_left = False
        dy = player.posy - self.posy
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        self.posx += dx * self.speed * dt
        self.posy += dy * self.speed * dt
                
    def coll_in(self, other):
        lenx = self.posx - other.posx
        leny = self.posy - other.posy
        if -5 < lenx < 5 and -5 < leny < 5:
            self.posx += lenx
            self.posy += leny