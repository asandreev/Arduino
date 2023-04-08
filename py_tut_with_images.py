# Import the pygame module
import pygame
import requests
import json
from jsonpath_ng.ext import parse

# Import random for random numbers
import random

import serial
ser = serial.Serial(
    port='COM6',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Define constants for the screen width and height
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

gameDisplay = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
# Define the Player object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Player(pygame.sprite.Sprite):
    vspeed = 0

    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("jet.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        

    # Move the sprite based on keypresses
    def update(self, pressed_keys, noise):
        if noise is None or noise == '' :
            noise = 0
        print(noise)
        if pressed_keys[K_UP]:
            self.vspeed = -18
            move_up_sound.play()
        elif int(noise) > 100:
            self.vspeed = -20
        elif int(noise) > 50:
            self.vspeed = -12
        elif int(noise) > 25:
            self.vspeed = -8
            move_up_sound.play()
        elif self.vspeed < 1:
            self.vspeed = self.vspeed+1

        self.rect.move_ip(0, self.vspeed)
        
        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
    
    seq = []
    points = 0
    #Get Noise value
    def getNoise(self):
        for c in ser.read():
            if chr(c) != '\n' and chr(c) != '\r':
                self.seq.append(chr(c)) #convert from ANSII
            if chr(c) == '\n':
                joined_seq = ''.join(str(v) for v in self.seq) #Make a string from array
                self.seq = []
                return joined_seq
    def addPoint(self):
        self.points = self.points + 1

# Define the package object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Package(pygame.sprite.Sprite):
    def __init__(self):
        super(Package, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # The starting position is randomly generated, as is the speed
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(1, 3)

    # Move the package based on speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
    
class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        super(Bomb, self).__init__()
        self.surf = pygame.image.load("bomb.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # The starting position is randomly generated, as is the speed
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(1, 3)

    # Move the package based on speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
  
class Explosion(pygame.sprite.Sprite):
    def __init__(self):
           super(Explosion, self).__init__()
           self.surf = pygame.image.load("explosion.gif").convert()
           self.surf.set_colorkey((0, 0, 0), RLEACCEL)
           # The starting position is randomly generated
           self.rect = self.surf.get_rect(
               center=(
                   (SCREEN_WIDTH/2),
                   (SCREEN_HEIGHT/2),
               )
           )

       # Move the cloud based on a constant speed
       # Remove it when it passes the left edge of the screen
    def update(self):
           self.rect.move_ip(-2, 0)
           if self.rect.right < 0:
               self.kill()
# Define the cloud object extending pygame.sprite.Sprite
# Use an image for a better looking sprite
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("cloud.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Move the cloud based on a constant speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-1, 0)
        if self.rect.right < 0:
            self.kill()


# Setup for sounds, defaults are good
pygame.mixer.init()

# Initialize pygame
pygame.init()

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create custom events for adding a new package and cloud
ADDpackage = pygame.USEREVENT + 1
ADDBOMB = pygame.USEREVENT + 3
pygame.time.set_timer(ADDpackage, 500)
pygame.time.set_timer(ADDBOMB, 1500)
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 500)
pygame.display.set_caption("DHL PLANE")

# Load and play our background music
pygame.mixer.music.load("music.wav")
pygame.mixer.music.play(loops=-1)

# Load all our sound files
# Sound sources: Jon Fincher
move_up_sound = pygame.mixer.Sound("flying.mp3")
move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
collision_sound = pygame.mixer.Sound("Collision.wav")
package_collect_sound = pygame.mixer.Sound("package-collect.wav")

# Set the base volume for all sounds
move_up_sound.set_volume(0.5)
move_down_sound.set_volume(0.5)
collision_sound.set_volume(0.5)

# Variable to keep our main loop running
running = True
started = False
endGame = False

# defining a font
smallfont = pygame.font.SysFont('Arial',45, True)
# light shade of the button
color_red = (212,5,17)
# dark shade of the button
color_yellow = (255,204,0)
# rendering a text written in
# this font

# Getting top score
api_url = "http://localhost:8080/highScores/search/getMaxScore"
response = requests.get(api_url)

highScore = 0
jsonpath_expression = parse("$._embedded.highScores[0].score")
for match in jsonpath_expression.find(response.json()):
    highScore = match.value
    
text = smallfont.render('START' , True , color_yellow)

all_sprites = pygame.sprite.Group()

def text_objects(text, font):
        textSurface = font.render(text, True, color_yellow)
        return textSurface, textSurface.get_rect()

def message_display(text, high, width):
        largeText = pygame.font.Font('freesansbold.ttf',25)
        TextSurf, TextRect = text_objects("Points: " + text + " High Score: " + str(highScore), largeText)
        TextRect.center = ((high),(width))
        screen.blit(TextSurf, TextRect)
        pygame.display.update()

def pushHighScore(points):
    api_url_post = "http://localhost:8080/highScores"
    highscore = {"score": points}
    response = requests.post(api_url_post, json=highscore)
    print(response.status_code)

def start_game():
    global started 
    started = True
    global endGame
    endGame = False
    # Create our 'player'
    global player 
    player = Player()
    # Create groups to hold package sprites, cloud sprites, and all sprites
    # - enemies is used for collision detection and position updates
    # - clouds is used for position updates
    # - all_sprites isused for rendering
    global enemies 
    enemies = pygame.sprite.Group()
    global bombs 
    bombs = pygame.sprite.Group()
    global clouds 
    clouds = pygame.sprite.Group()
    global explosions
    global all_sprites 
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

# Our main loop
while running:
    screen.fill((135, 206, 250))
    if not started: 
        # if mouse is hovered on a button it
        # changes to lighter shade 
        mouse = pygame.mouse.get_pos()
        if 550 <= mouse[0] <= 670 and 250 <= mouse[1] <= 350:
            pygame.draw.rect(screen,color_yellow,[550,250,140,40])
            text = smallfont.render('START' , True , color_red)
        else:
            pygame.draw.rect(screen,color_red,[550,250,140,40])
            text = smallfont.render('START' , True , color_yellow)

        # superimposing the text onto our button
        screen.blit(text , (560,243))

        # Flip everything to the display
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        if endGame:
            message_display(str(player.points), 610, 232)

        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            #checks if a mouse is clicked
            if ev.type == pygame.MOUSEBUTTONDOWN:
                # stores the (x,y) coordinates into
                # the variable as a tuple
                mouse = pygame.mouse.get_pos()
                #if the mouse is clicked on the
                # button the game is terminated
                if 550 <= mouse[0] <= 670 and 250 <= mouse[1] <= 350:
                    start_game()
    else:
        noise = player.getNoise()
        # Look at every event in the queue
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop
                if event.key == K_ESCAPE:
                    running = False

            # Did the user click the window close button? If so, stop the loop
            elif event.type == QUIT:
                running = False

            # Should we add a new package?
            elif event.type == ADDpackage:
                # Create the new package, and add it to our sprite groups
                new_package = Package()
                enemies.add(new_package)
                all_sprites.add(new_package)

                        # Should we add a new package?
            elif event.type == ADDBOMB:
                # Create the new package, and add it to our sprite groups
                new_bomb = Bomb()
                bombs.add(new_bomb)
                all_sprites.add(new_bomb)

            # Should we add a new cloud?
            elif event.type == ADDCLOUD:
                # Create the new cloud, and add it to our sprite groups
                new_cloud = Cloud()
                clouds.add(new_cloud)
                all_sprites.add(new_cloud)

        # Get the set of keys pressed and check for user input
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys,noise)

        # Update the position of our enemies and clouds
        enemies.update()
        bombs.update()
        clouds.update()

        # Draw all our sprites
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        message_display(str(player.points), 150, 20)

        # Check if any enemies have collided with the player
        package = pygame.sprite.spritecollideany(player, enemies)
        if package :
            player.addPoint()
            package.kill()
            package_collect_sound.play()

        bomb = pygame.sprite.spritecollideany(player, bombs)
        if bomb:
            # If so, remove the player
            # Stop any moving sounds and play the collision sound
            move_up_sound.stop()
            move_down_sound.stop()
            collision_sound.play()
            bomb.kill()
            player.kill()
            explosion = Explosion()
            explosion.update()
            all_sprites.add(explosion)

            # Highscore management
            if player.points > highScore :
                pushHighScore(player.points)
                highScore = player.points

            # Stop the loop
            started = False
            endGame = True

            # Ensure we maintain a 30 frames per second rate
            clock.tick(30)

# At this point, we're done, so we can stop and quit the mixer
pygame.mixer.music.stop()
pygame.mixer.quit()



