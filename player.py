import pygame
import random
import time

def random_upgrade(player):
    """rolls random upgrades

    Args:
        player (player): player class

    Returns:
        list: 3 randomized upgrades
    """
    upgrades = player.normal_upgrades
    special_upgrades = player.special_upgrades
    rand = random.randint(0,100)
    if rand >= 30:
        rand_choice1 = random.choice(upgrades)
    else:
        rand_choice1 = random.choice(special_upgrades)
    rand_choice2 = random.choice(upgrades)
    while rand_choice2 == rand_choice1:
        rand_choice2 = random.choice(upgrades)
    rand_choice3 = random.choice(upgrades)
    while rand_choice3 == rand_choice1 or rand_choice3 == rand_choice2:
        rand_choice3 = random.choice(upgrades)
    rand_list = [rand_choice1, rand_choice2, rand_choice3]
    for i in rand_list:
        if i == "double_shot":
            player.special_upgrades.remove(i)
        if i == "triple_shot":
            player.special_upgrades.remove(i)
        if i == "quad_shot":
            player.special_upgrades.remove(i)
        if i == "soy_milk":
            player.special_upgrades.remove(i)
    return [rand_choice1, rand_choice2, rand_choice3]
               
class camera:
    """Creates camera
    """
    def __init__(self, width, height):
        """initialized camera

        Args:
            width (int): X border camera
            height (int): Y border camera
        """
        self.camera = pygame.Rect(0,0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        """applys movement to given entity

        Args:
            entity (object): entity to apply camera effect

        Returns:
            object.rect.move: move rect with camera pos
        """
        return entity.rect.move(self.camera.topleft)
    
    def update(self, target, X:int, Y:int):
        """updates camera

        Args:
            target (object): object with camera effect
            X (int): X border camera
            Y (int): Y border camera
        """
        x = -target.rect.x + int(X/2)
        y = -target.rect.y + int(Y/2)
        self.camera = pygame.Rect(x, y, self.width, self.height)
        

class player(pygame.sprite.Sprite):
    """Creates player

    Args:
        pygame (sprite): Gives player sprite properties 
    """
    def __init__(self, posx, posy, sprite):
        """Initialize player class

        Args:
            posx (int): starting pos on X
            posy (int): starting pos on y
            sprite (sprite): Player sprite 
        """
        super(player, self).__init__()

        self.posx = posx
        self.posy = posy
        self.hitted = False
        self.sprite = pygame.image.load(sprite).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (100, 100))
        self.sprite.set_colorkey((255,255,255))
        self.offset = 30
        self.rect = pygame.Rect(self.posx + self.offset, self.posy, 70, 90)
        self.dmg_miltiplayer = 1
        self.dmg = 50*self.dmg_miltiplayer
        self.level = 1
        self.exp = 0
        self.max_exp = 100
        self.hp = 100
        self.max_hp = 100
        self.speed = 20
        self.shoot_rate_miltiplayer = 1
        self.shoot_rate = 0.5*self.shoot_rate_miltiplayer
        self.heavy_shoot_rate = 1.5*self.shoot_rate_miltiplayer 
        self.round = 0
        self.last_shot_time = 0
        self.last_heavy_shot_time = 0
        self.normal_upgrades = ["dmg", "fire_rate", "heavy_fire_rate"]
        self.special_upgrades = ["double_shot", "triple_shot", "quad_shot", "soy_milk"]
        self.pending_upgrades = []
        self.tripple_shot = False
        self.quad_shot = False
        self.double_shot = False
        self.soy_milk = False
        self.bullets_count = 1
        self.facing_left = False
        self.original_sprite = self.sprite.copy() 
        self.gun_sound = pygame.mixer.Sound("music/gun'.wav")
        self.gun_sound.set_volume(0.05)
        self.gun_sound_interval = 1000
        self.gun_sound_last = 0
        
    def shoot(self, mode, keys, bullets, bullet_sprite):
        """Gives player attribute to shoot

        Args:
            mode (int): Game difficulty
            keys (event.keys): event keys
            bullets (sprite.group): adds bullet to bullets sprite group
            bullet_sprite (sprite): bullet sprite
        """
        for i in range(mode):
            if keys[pygame.K_UP]:
                bullets.add(bullet(self, "y-1", bullet_sprite, 40, 50 + (i*10)))
            elif keys[pygame.K_DOWN]:
                bullets.add(bullet(self, "y+1", bullet_sprite, 40, 50 + (i*10)))
            elif keys[pygame.K_LEFT]:
                bullets.add(bullet(self, "x-1", bullet_sprite, 40 + (i*10), 50))
            elif keys[pygame.K_RIGHT]:
                bullets.add(bullet(self, "x+1", bullet_sprite, 40 + (i*10), 50))
    def heavy_shoot(self, mode, keys, bullets, bullet_sprite):
        """Gives player attribute to shoot in all directions at once

        Args:
            mode (int): Game difficulty
            keys (event.keys): event keys
            bullets (sprite.group): adds bullet to bullets sprite group
            bullet_sprite (sprite): bullet sprite
        """
        for i in range(mode):
            if keys[pygame.K_UP] and keys[pygame.K_DOWN] and keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]:
                bullets.add(bullet(self, "x+1", bullet_sprite, 40 + (i*10), 50))
                bullets.add(bullet(self, "y-1", bullet_sprite, 40, 50 + (i*10)))
                bullets.add(bullet(self, "y+1", bullet_sprite, 40, 50 + (i*10)))
                bullets.add(bullet(self, "x-1", bullet_sprite,  40 + (i*10), 50))   
    def level_up(self):
        """Player level up

        Returns:
            list: list of upgrades to choose from
        """
        if self.exp >= self.max_exp:
            if self.shoot_rate < 0:
                self.shoot_rate = 0
            self.max_exp += 10*((self.level)**2)
            self.level += 1
            self.pending_upgrades = random_upgrade(self)
            self.exp = 0
            self.max_hp += 20
            self.hp = self.max_hp
            return self.pending_upgrades
    
    def update(self, dt:int, Sprites, bullets, en, bullet_sprite, events):
        """update player

        Args:
            dt (int): speed of the game
            Sprites (sprite): add sprites to all sprites group 
            bullets (sprite.group): kills bullets from sprite group
            en (sprite.group): kills enemy from sprite group
            bullet_sprite (sprite): bullet sprite
            events (pygame.events): events for key input
        """
        self.rect.topleft = (self.posx + self.offset, self.posy)
        if self.hp <= 0:
            self.kill()
            Sprites.empty()
            bullets.empty()
            for e in en:
                e.kill()
            en.empty()

        keys = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and not self.facing_left:
                    self.sprite = pygame.transform.flip(self.original_sprite, True, False)
                    self.facing_left = True
                elif event.key == pygame.K_d and self.facing_left:
                    self.sprite = self.original_sprite.copy()
                    self.facing_left = False
        if keys[pygame.K_w]:
            self.posy -= self.speed * dt
        if keys[pygame.K_s]:
            self.posy += self.speed * dt
        if keys[pygame.K_a]:
            self.posx -= self.speed * dt
            
        if keys[pygame.K_d]:
            self.posx += self.speed * dt

        current_time = time.time()
        if dt != 0:
            if self.double_shot:
                if current_time - self.last_shot_time >= self.shoot_rate:
    
                    self.shoot(self.bullets_count , keys, bullets, bullet_sprite)
                    self.last_shot_time = current_time
                if current_time - self.last_heavy_shot_time >= self.heavy_shoot_rate:
  
                    self.heavy_shoot(self.bullets_count , keys, bullets, bullet_sprite)
                    self.last_heavy_shot_time = current_time
            elif self.tripple_shot: 
                if current_time - self.last_shot_time >= self.shoot_rate:
   
                    self.shoot(self.bullets_count , keys, bullets, bullet_sprite)
                    self.last_shot_time = current_time
                if current_time - self.last_heavy_shot_time >= self.heavy_shoot_rate:
   
                    self.heavy_shoot(self.bullets_count , keys, bullets, bullet_sprite)
                    self.last_heavy_shot_time = current_time       
            elif self.quad_shot: 
                if current_time - self.last_shot_time >= self.shoot_rate:
    
                    self.shoot(self.bullets_count , keys, bullets, bullet_sprite)
                    self.last_shot_time = current_time
                if current_time - self.last_heavy_shot_time >= self.heavy_shoot_rate:
   
                    self.heavy_shoot(self.bullets_count , keys, bullets, bullet_sprite)
                    self.last_heavy_shot_time = current_time
            else: 
                if current_time - self.last_shot_time >= self.shoot_rate:
     
                    self.shoot(self.bullets_count , keys, bullets, bullet_sprite)
                    self.last_shot_time = current_time
                if current_time - self.last_heavy_shot_time >= self.heavy_shoot_rate:
   
                    self.heavy_shoot(self.bullets_count , keys, bullets, bullet_sprite)
                    self.last_heavy_shot_time = current_time     
                        
class bullet(pygame.sprite.Sprite):
    """Creates bullet

    Args:
        pygame (sprite): Gives bullet sprite properties 
    """
    def __init__(self, player, direction, sprite, offsety, offsetx):
        """initialized bullet class

        Args:
            player (player): player class
            direction (str): in what direction bullet should go format 'axis+/-1'
            sprite (sprite): bullet sprite
            offsety (int): offset to bullet spawn point on Y
            offsetx (int): offset to bullet spawn point on X
        """
        super(bullet, self).__init__()
        self.damage = player.dmg
        self.speed = 10
        self.offsetx = offsetx
        self.offsety = offsety
        self.posx = player.posx+self.offsetx
        self.posy = player.posy+self.offsety
        self.direction = direction
        self.sprite = sprite.copy()
        current_time = time.time()
        if player.gun_sound_interval <= current_time - player.gun_sound_last:
            player.gun_sound.play()
        self.hit_sound = pygame.mixer.Sound("music/enemy_hit.wav")
        self.hit_sound.set_volume(0.2)
        if self.direction == "x+1":
            self.sprite = pygame.transform.rotate(self.sprite, 0)
            self.rect = pygame.Rect(self.posx, self.posy, 20, 10)
        elif self.direction == "x-1":
            self.sprite = pygame.transform.rotate(self.sprite, 180)
            self.rect = pygame.Rect(self.posx, self.posy, 20, 10)
        elif self.direction == "y+1":
            self.sprite = pygame.transform.rotate(self.sprite, 270)
            self.rect = pygame.Rect(self.posx, self.posy, 10, 20)
        elif self.direction == "y-1":
            self.sprite = pygame.transform.rotate(self.sprite, 90)
            self.rect = pygame.Rect(self.posx, self.posy, 10, 20)

    def update(self, player, dt:int, cam, X:int, Y:int):
        """updates bullet class

        Args:
            player (player]): player class
            dt (int): speed of the game
            cam (camera): camera class
            X (int): X border of screen
            Y (int): Y border of screen
        """
        dir = int(self.direction[1:])
        self.rect.topleft = (self.posx, self.posy)
        if self.direction[0] == "x":
            self.posx += self.speed*dir*dt*10
        if self.direction[0] == "y":
            self.posy += self.speed*dir*dt*10
        if player.hp <= 0:
            self.kill()
        screen_rect = pygame.Rect(-cam.camera.x, -cam.camera.y, X, Y)
        if not screen_rect.collidepoint(self.posx, self.posy):
            self.kill()

    def hit(self, enemy):
        """hit enemy

        Args:
            enemy (enemy): enemy hit
        """
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self.hit_sound)
        enemy.hp -= self.damage
        self.kill()