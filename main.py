# imports 

import pygame
from random import randint, uniform # 
from os.path import join
# join() helps with importing by creating file path

# ----------------------------------------------------------------------------------------------------------------------------

# Classes

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        # super() - with any inheritance, to initalize the parent class
        # sprite added to group automatically calling the sprite
        super().__init__(groups)
        # surface
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha() 
        # get_frect creates a rect from a surface and its centered in middle of the window 
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2,WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2(0, 0)
        self.speed = 600
        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400 # milliseconds

        # mask
        # shows which pixels are visible
        self.mask = pygame.mask.from_surface(self.image)
        

    def laser_timer(self):
        if not self.can_shoot:
            # will get you the time it has passed since start of game 
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        # actually does the moving
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        # only ran once every time a laser is shot
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            # creates one laser each iteration
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()
    
class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt):
        # only shoots upward - y
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            # destroys sprite (not visible in game)
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        # get surf from the actual parameter
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000 # milliseconds because it needs to go away after reaching bottom
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(300, 500)
        self.rotation_speed = randint(20, 50)
        self.rotation = 0

    def update(self, dt):
        # creates meteors coming down
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        # moves meteor
        self.rect.center += self.direction * self.speed * dt
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        # creating new rectangle
        self.rect = self.image.get_frect(center = self.rect.center)
    
class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0 
        self.image = self.frames[self.frame_index]
        # centers at the position when called 
        self.rect = self.image.get_frect(center = pos)
        # explosion_sound.play() could work here too
    
    def update(self, dt):
        # speed of animation
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            # override self.image
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

# ----------------------------------------------------------------------------------------------------------------------------

# Functions

def collision():
    # connects the running = false in this with the running = True in game set up
    global running
    # if any meteor_sprites collides with player then True destroys sprite
    # adding the collide mask makes the collisions more accurate
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        # ends game  
        running = False

    for laser in laser_sprites:
        # for each laser check a collision with a meteor then kill (using True)
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def display_time():
    current_time = pygame.time.get_ticks() // 1000
    # render() creates a surface, always wants a string
    # render(text, antialias, color) (antialias almost always True)
    text_surf = font.render(str(current_time), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    # # blit() used to put surface on another surface
    display_surface.blit(text_surf, text_rect)
    # inflate() changes the size of the rectangle
    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10)

# ----------------------------------------------------------------------------------------------------------------------------

# General Setup 

pygame.init()
# display surface
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
running = True
clock = pygame.time.Clock()

# ---------------------------------------------------------------------------------------------------------------------------

# Imports

star_surf = pygame.image.load(join("images", "star.png")).convert_alpha()
meteor_surf = pygame.image.load(join("images", "meteor.png")).convert_alpha()
laser_surf = pygame.image.load(join("images", "laser.png")).convert_alpha()
# Font(font style, size)
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
# 20 pictures to show the animated explosions
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
# sounds
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
# 50% of the volume
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
# automatically play in the background
# loops played a certain number of time
# -1 plays indefinitely 
game_music.play(loops= -1)

# ----------------------------------------------------------------------------------------------------------------------------

# Sprites

all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

# ----------------------------------------------------------------------------------------------------------------------------

# Displays

# displays stars 
for i in range(50):
    Star(all_sprites, star_surf)

# displays player
player = Player(all_sprites)

# ----------------------------------------------------------------------------------------------------------------------------

# Custom Events
meteor_event = pygame.event.custom_type()
# set_timer for each meteor appearing 
pygame.time.set_timer(meteor_event, 500)

# ----------------------------------------------------------------------------------------------------------------------------

# Actual Game

while running:
    # frame rate
    dt = clock.tick() / 1000 
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            # spawn meteor at top of window
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            # class Meteor(self, surf, pos, groups):
            # all_sprites for update and main part
            # meteor_sprites for 
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    # update the game
    all_sprites.update(dt)

    # check collisions
    collision()

    # draw the game
    display_surface.fill('black') 
    
    # display the time 
    display_time()
    
    # all_sprites.draw() displays everything created using the classes and groups
    # must create background before anything else (time of creation) 
    all_sprites.draw(display_surface)

    pygame.display.update()

# opposite of pygame.init(), closes pygame
pygame.quit() 