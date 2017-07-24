#!/usr/bin/env pyton

import pygame, os, random

COLORKEY = (255, 0, 255)
FRAMERATE = 60
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
WORLD_SPEED = 4
FONT = None

#open configuration and get font name
f = open('config', 'r')

for line in f.readlines():

    if line[0:line.index('=')] == 'font':

        FONT = line[line.index('=') + 1: line.index(';')]

f.close()

#sheets is in the form:
#   SHEETS = {
#       'image_filename':[(spritewidth, spriteheight), num_sprites],
#       ...
#   }
SHEETS = {
    'tn.png':[(16, 24), 8],
    'test_world_scroll1.png':[(640, 480), 1],
    'test_world_scroll2.png':[(640, 480), 1],
    'sasuke.png':[(16, 24), 4],
    'bullet1.png':[(10, 10), 3],
    'title.png':[(640, 480), 1],
    'start.png':[(250, 100), 8],
    'ready.png':[(250, 100), 8],
    'bar_r.png':[(800, 200), 1],
    'bar_l.png':[(1200, 200), 1]
    }

#Animations is in the form:
#   ANIMATIONS = {
#       'image_filename':{
#           anim_name:([(sprite1x, sprite1y), (sprite2x, sprite2y), ...], delay)
#           ...
#       }
#       ...
#   }
#NOTE: the animation name 'PLACEHOLDER' is featured in any image that doesn't
#need to be animated. It makes an image simply hold still.
ANIMATIONS = {
        'tn.png':{
            'PLACEHOLDER':([(0, 0)], 1),
            'run':([(0, 0), (1, 0), (2, 0), (3, 0)], 8),
            'die':([(0, 1), (1, 1), (2, 1), (3, 1)], 2),
            'materialize':([(3, 1), (2, 1), (1, 1), (0, 1)], 3)
            },
        'test_world_scroll1.png':{
            'PLACEHOLDER':([(0, 0)], 1)
            },
        'test_world_scroll2.png':{
            'PLACEHOLDER':([(0, 0)], 1)
            },
        'sasuke.png':{
            'PLACEHOLDER':([(0, 0)], 1),
            'run':([(0, 0), (1, 0), (2, 0), (3, 0)], 8)
            },
        'bullet1.png':{
            'PLACEHOLDER':([(0, 0)], 1),
            'spin':([(0, 0), (1, 0), (2, 0)], 2)
            },
        'title.png':{
            'PLACEHOLDER':([(0, 0)], 1)
            },
        'start.png':{
            'PLACEHOLDER':([(0, 0)], 1),
            'glow':([(1, 0)], 1),
            'appear':([(2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1)], 2)
            },
        'ready.png':{
            'PLACEHOLDER':([(0, 0)], 1),
            'fade':([(3, 1), (2, 1), (1, 1), (0, 1), (3, 0), (2, 0)], 2),
            'appear':([(2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1)], 2),
            'invisible':([(1, 0)], 10)
            },
        'bar_r.png':{
            'PLACEHOLDER':([(0, 0)], 1)
            },
        'bar_l.png':{
            'PLACEHOLDER':([(0, 0)], 1)
            }
    }

SOUNDS = ('select.wav', 'die.wav', 'shoot.wav', 'music.wav', 'taiko.wav')

class Game(object):

    def __init__(self):

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.frameclock = pygame.time.Clock()

        pygame.display.set_caption('TORSO NINJA')

        self.font = pygame.font.Font(os.path.join('data', 'fonts',
                                                  FONT), 15)

        self.mode = 'INTRO'

        self.sheets = {}
        self.sounds = {}
        self.load_sheets()
        self.load_sounds()

        self.intro_timer = 120
        self.start_appear_timer = 12
        self.start_delay = 30
        self.bar1 = Entity(self, self.sheets['bar_l.png'], (0, 0),
                                   ANIMATIONS['bar_l.png'], (-300, 212))
        self.bar2 = Entity(self, self.sheets['bar_r.png'], (0, 0),
                                   ANIMATIONS['bar_r.png'], (0, 72))
            
        self.score = 0
        self.get_highscore()
        
        self.paths = {
            'A':((20, (2, 2)), (20, (2, 0)), (20, (0, 2)), (20, (2, 0))),
            'B':((20, (-2, 2)), (20, (-2, 0)), (20, (0, 2)), (20, (-2, 0))),
            'C':((5, (-2, 2)), (5, (-2, 2))),
            'D':((5, (2, 2)), (5, (2, 2))),
            'E':((120, (0, 2)), (140, (0, -6))),
            'F':((120, (2, 2)), (140, (-6, -6))),
            'G':((120, (-2, 2)), (140, (6, -6))),
            'H':((120, (0, 2)), (120, (0, 2))),
            'I':((120, (2, 0)), (120, (2, 0))),
            'J':((120, (-2, 0)), (120, (-2, 0)))
            }
        self.patterns = {
            'A':((40, (None)), (10, (0, 4)), (10, (1, 3)), (10, (-1, 3))),
            'A2':((40, (None)), (10, (0, 6)), (10, (2, 5)), (10, (-2, 5))),
            'B':((20, (None)), (20, (0, 3))),
            'B2':((30, (None)), (30, (0, 3))),#delay version to stagger
            'C':((20, (None)), (20, (4, 4))),
            'C2':((20, (None)), (20, (2, 4))),
            'D':((20, (None)), (20, (-4, 4))),
            'D2':((20, (None)), (20, (-2, 4))),
            'E':((20, (None)), (20, (4, 2))),
            'E2':((20, (None)), (20, (6, 2))),
            'F':((20, (None)), (20, (-4, 2))),
            'F2':((20, (None)), (20, (-6, 2)))
            }

        self.on = True
        self.game_over = False
        self.game_over_timer = 60

        self.title_screen = Entity(self, self.sheets['title.png'], (0, 0),
                                   ANIMATIONS['title.png'], (0, 0))

        self.start_button = Button(self, self.sheets['start.png'], (0, 0),
                                   ANIMATIONS['start.png'],(195, 340), 'START')

        self.ready = Entity(self, self.sheets['ready.png'], (0, 0),
                            ANIMATIONS['ready.png'], (195, 160))
        self.ready_counter = 170

        self.enemy_counter = 200
        self.spawns = [
            (#0
                ((-20, -20), 'F', 'A'), ((-20, 10), 'F', 'A'),
                ((-20, 40), 'F', 'A'), ((660, -20), 'G', 'A'),
                ((660, 10), 'G', 'A'), ((660, 40), 'G', 'A')),
            (#1
                ((-20, 20), 'F', 'E'), ((-20, 50), 'F', 'A'),
                ((-20, 80), 'F', 'E'), ((660, 20), 'G', 'F'),
                ((660, 50), 'G', 'A'), ((660, 80), 'G', 'F')),
            (#2
                ((-20, -20), 'D', 'B'), ((-20, 10), 'D', 'B'),
                ((-20, 40), 'D', 'B'), ((660, -20), 'C', 'B'),
                ((660, 10), 'C', 'B'), ((660, 40), 'C', 'B')),
            (#3
                ((210, -20), 'E', 'E'), ((430, -20), 'E', 'F')),
            (#4
                ((210, -20), 'H', 'B'), ((430, -20), 'H', 'B')),
            (#5
                ((210, -20), 'E', 'C'), ((430, -20), 'E', 'D')),
            (#6
                ((210, -20), 'H', 'C'), ((430, -20), 'H', 'D')),
            (#7
                ((110, -20), 'H', 'C'), ((220, -20), 'H', 'B'),
                ((330, -20), 'H', 'B'), ((420, -20), 'H', 'B'),
                ((530, -20), 'H', 'D')),
            (#8
                ((110, -20), 'E', 'C'), ((220, -20), 'H', 'C'),
                ((330, -20), 'E', 'B'), ((420, -20), 'H', 'D'),
                ((530, -20), 'E', 'D')),
            (#9
                ((110, -20), 'E', 'C'), ((220, -20), 'E', 'B'),
                ((330, -20), 'E', 'B'), ((420, -20), 'E', 'B'),
                ((530, -20), 'E', 'D')),
            (#10
                ((110, -20), 'E', 'B'), ((220, -20), 'E', 'B'),
                ((330, -20), 'E', 'B'), ((420, -20), 'E', 'B'),
                ((530, -20), 'E', 'B')),
            (#11
                ((-20, 80), 'I', 'B'), ((-20, 110), 'I', 'C'),
                ((-20, 140), 'I', 'C'), ((660, 80), 'J', 'D'),
                ((660, 110), 'J', 'D'), ((660, 140), 'J', 'B')),
            (#12
                ((-20, -20), 'A', 'C'), ((660, -20), 'B', 'D'),
                ((-20, 10), 'D', 'C'), ((660, 10), 'C', 'D')),
            (#13
                ((-20, -20), 'A', 'C'), ((660, -20), 'B', 'D')),
            (#14
                ((-20, 40), 'I', 'B'), ((-20, 100), 'I', 'B'),
                ((-20, 160), 'I', 'B'), ((660, 70), 'J', 'B'),
                ((660, 130), 'J', 'B'), ((660, 190), 'J', 'B'))
            ]

        self.player = Player_Sprite(self, self.sheets['tn.png'], (0, 0),
                                    ANIMATIONS['tn.png'], (0, 0))
        self.player.visible = False

        self.scroller_grp = pygame.sprite.Group()

        self.bullet_grp = pygame.sprite.Group()
        self.enemy_grp = pygame.sprite.Group()

    def load_sheets(self):

        for sh in SHEETS:

            self.sheets[sh] = Sheet(self, sh, SHEETS[sh][0], SHEETS[sh][1])

    def load_sounds(self):

        for s in SOUNDS:

            self.sounds[s] = pygame.mixer.Sound(os.path.join('data', 'snd', s))

    def play_sound(self, sound, loops = 0):

        self.sounds[sound].play(loops)

    def play_intro(self):

        if self.intro_timer > 0:

            self.intro_timer -= 1

            self.bar1.move((8, 0))
            self.bar2.move((-8, 0))

        else:

            self.mode = 'MENU'
            self.play_sound('music.wav', -1)

    def start_game(self):

        self.enemy_counter = 100

        for b in self.bullet_grp:

            b.kill()

        for e in self.enemy_grp:

            e.kill()

        for s in self.scroller_grp:

            s.kill()

        s1 = Scroller(self, self.sheets['test_world_scroll1.png'], (0, 0),
                      ANIMATIONS['test_world_scroll1.png'], (0, 0))
        s2 = Scroller(self, self.sheets['test_world_scroll2.png'], (0, 0),
                      ANIMATIONS['test_world_scroll2.png'],
                      (0, -SCREEN_HEIGHT))

        self.scroller_grp.add(s1, s2)

        self.player.dead = False
        self.player.death_timer = 8
        self.player.set_animation('run')

        self.mode = 'GAME'
        self.ready_counter = 120
        self.enemy_counter = 160
        pygame.mouse.set_visible(False)

    def print_scores(self):

        hh = self.font.render('BEST:', False, (255, 255, 0))
        hhr = hh.get_rect()
        hhr.topleft = (6, 6)
        bhh = self.font.render('BEST:', False, (0, 0, 0))
        bhhr = hh.get_rect()
        bhhr.topleft = (4, 6)
        sh = self.font.render('SCORE:', False, (255, 255, 0))
        shr = sh.get_rect()
        shr.topleft = (6, 43)
        bsh = self.font.render('SCORE:', False, (0, 0 , 0))
        bshr = sh.get_rect()
        bshr.topleft = (4, 43)

        h = self.font.render(str(self.highscore), False, (255, 255, 0))
        hr = h.get_rect()
        hr.topleft = (6, 24)
        bh = self.font.render(str(self.highscore), False, (0, 0, 0))
        bhr = h.get_rect()
        bhr.topleft = (4, 24)
        s = self.font.render(str(self.score), False, (255, 255, 0))
        sr = s.get_rect()
        sr.topleft = (6, 61)
        bs = self.font.render(str(self.score), False, (0, 0, 0))
        bsr = s.get_rect()
        bsr.topleft = (4, 61)

        self.screen.blit(bhh, bhhr)
        self.screen.blit(bsh, bshr)
        self.screen.blit(bh, bhr)
        self.screen.blit(bs, bsr)
        
        self.screen.blit(hh, hhr)
        self.screen.blit(sh, shr)
        self.screen.blit(s, sr)
        self.screen.blit(h, hr)

    def make_enemies(self):

        if self.enemy_counter > 0:

            self.enemy_counter -= 1

        else:

            self.enemy_counter = 100

            i = random.randint(0, len(self.spawns) - 1)

            stats = self.spawns[i]

            for d in stats:

                r = random.randint(0, 1)#50% chance to use alt shot
                p = d[2]

                if r == 1:

                    p = str(p) + '2'

                e = Enemy(self, self.sheets['sasuke.png'], (0, 0),
                          ANIMATIONS['sasuke.png'], d[0],
                          self.paths[d[1]], self.patterns[p])
                e.set_animation('run')
                self.enemy_grp.add(e)

    def set_game_over(self):

        self.game_over = True
        self.game_over_timer = 60

    def end_game(self):

        if self.game_over_timer > 0:

            self.game_over_timer -= 1

        else:

            self.mode = 'MENU'
            self.game_over = False

            if self.score > self.highscore:
                self.highscore = self.score

            self.score = 0
            pygame.mouse.set_visible(True)

    def get_highscore(self):

        f = open(os.path.join('data', 'score', 'highscore.dat'), 'r')

        self.highscore = int(f.readline())

        f.close()

    def record_highscore(self):

        f = open(os.path.join('data', 'score', 'highscore.dat'), 'w')

        f.write(str(self.highscore))

        f.close()

    def shift_frames(self):

        self.frameclock.tick(FRAMERATE)

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.on = False

            elif self.mode == 'MENU':

                if event.type == pygame.MOUSEBUTTONDOWN:

                    self.start_button.check_pressed(pygame.mouse.get_pos())

    def update(self):

        self.screen.fill((0, 0, 0))

        if self.mode == 'GAME':

            if self.ready_counter == 120:
                self.ready.set_animation('invisible')
            elif self.ready_counter == 110:
                self.ready.set_animation('appear')
                self.player.visible = True
                self.player.set_animation('materialize')
            elif self.ready_counter == 98:
                self.ready.set_animation('PLACEHOLDER')
                self.player.set_animation('run')
            elif self.ready_counter == 14:
                self.ready.set_animation('fade')
            elif self.ready_counter == 2:
                self.ready.set_animation('invisible')

            self.make_enemies()

            self.scroller_grp.update(self.screen)

            self.bullet_grp.update(self.screen)

            self.enemy_grp.update(self.screen)

            self.player.update(self.screen)

            if self.ready_counter > 0:
                self.ready.update(self.screen)
                self.ready_counter -= 1

            self.print_scores()

            if self.game_over:

                self.end_game()

            else:

                self.score += 1

        elif self.mode == 'MENU':

            self.title_screen.update(self.screen)

            if self.start_appear_timer == 12:
                self.start_button.set_animation('appear')

            if self.start_button.rect.collidepoint(pygame.mouse.get_pos()) and (
                self.start_appear_timer == 0):
                self.start_button.set_animation('glow')
            elif self.start_appear_timer == 0:
                self.start_button.set_animation('PLACEHOLDER')

            if self.start_appear_timer > 0:
                self.start_appear_timer -= 1
                
            self.start_button.update(self.screen)

            if self.start_button.pressed:

                self.start_delay -= 1

            if self.start_delay == 0:

                self.start_delay = 30
                self.start_button.reset()
                self.start_game()

        elif self.mode == 'INTRO':
            
            self.title_screen.update(self.screen)
            self.bar1.update(self.screen)
            self.bar2.update(self.screen)

            self.play_intro()

        pygame.display.update()

    def mainloop(self):

        self.play_sound('taiko.wav')

        while self.on:

            self.shift_frames()
            self.handle_events()
            self.update()

        pygame.quit()
        self.record_highscore()

################################################################################

class Sheet(object):
    """
    Class for the spritesheets that entity images are loaded
    from. Supports regularized spritesheets only (all sprites
    feature the same dimensions).
    """

    def __init__(self, game, name, sprite_size, total_sprites):

        self.game = game

        #try and load all sprites on the sheet
        success = self.load_sheet(name, sprite_size, total_sprites)

        if success == 1:#failure, cleanup vals
            
            self.sprites = {}
            print "Failed to load sheet: " + name#error message

    def load_sheet(self, name, sprite_size, total_sprites):
        """
        Load a sheet and divide it into subsurfaces for
        use as images by sprite entities.
        """

        #remember important variables
        self.name = name
        self.sprite_size = sprite_size
        self.total_sprites = total_sprites

        #Step 1: attempt to load the appropriate image file
        try:

            self.sheet = pygame.image.load(os.path.join("data", "img", name))

        #catch a missing file error and stop, set up graceful failure
        except:

            self.sheet = None

        #Step 2: if sheet exists, divide it into sprites
        if self.sheet != None:

            self.sprites = {}#empty dict to hold our loaded images

            #vals to track our progress thru the sheet
            x = 0
            y = 0

            #while we still have more sprites to load, load them
            while len(self.sprites) < total_sprites:

                #get a rect that can be used to make a subsurface of the sheet
                new_rect = pygame.Rect((x * sprite_size[0], y * sprite_size[1]),
                                            sprite_size)

                #load image, store it in our dict, set its colorkey
                self.sprites[(x, y)] = self.sheet.subsurface(new_rect).convert()
                self.sprites[(x, y)].set_colorkey((255, 0, 255))

                x += 1#scoot over to the right

                #if we're hanging off the right side, scoot down and start over
                #again from the far left
                if x * sprite_size[0] >= self.sheet.get_width():

                    x = 0
                    y += 1

            return 0#SUCCESS!!

        #No sheet exists
        else:

            return 1# failure :C

################################################################################

class Entity(pygame.sprite.Sprite):
    """
    Visible game object parent class. Allows for drawing, moving,
    animating, and more. Basically expands on pygame.sprite.Sprite.
    """

    def __init__(self, game, sheet, sprite, animations, position):

        pygame.sprite.Sprite.__init__(self)

        self.game = game
        
        #loads image and makes rect
        self.sheet = sheet
        self.image = self.sheet.sprites[sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = position

        #can be turned off if we don't want to be drawn
        self.visible = True

        ########################
        #ANIMATIONS:           
        #Animations are a tuple of two values:
        #   (sprites, timer)
        #where 'sprites' is an ORDERED list of sheet positions values
        #and 'timer' is the amount of time that any one sprite will
        #be shown on the screen.
        #######################
        
        #Animation values. Remember:entity takes a whole dict of animations!
        self.animations = {}#dict which stores all animations
        self.current_animation = None
        self.current_sprite = sprite
        self.animation_timer = -1#-1 = off. this val is used for a countdown

        #setup all animations available to this entity's spritesheet
        for an in animations:

            self.setup_animation(an, animations[an][0], animations[an][1])

    def move(self, offset):

        self.rect.topleft = (self.rect.topleft[0] + offset[0],
                             self.rect.topleft[1] + offset[1])

    def setup_animation(self, name, sprites, timer = 2):
        """
        Sets up an animation given a unique name, a list
        of sprite origin positions on the entity's sheet,
        and a timer. Sprites must be in an ordered list.
        """

        self.animations[name] = (sprites, timer)

    def set_animation(self, name):
        """
        Set the chosen animation as the current (active)
        animation, provided it is already in the animations
        list.
        """

        #check through the animations for the chosen animation
        if name in self.animations.keys():

            #setup all animation values for the new animation
            self.current_animation = self.animations[name]
            self.animation_timer = self.current_animation[1]
            self.current_sprite = self.current_animation[0][0]
            self.image = self.sheet.sprites[self.current_sprite]

    def animate(self):
        """
        Countdown each frame from the maximum (the animation
        timer number) and shift frames when 0 is reached.
        """

        if self.animation_timer != -1:#animations are not off

            #if we are not at zero, countdown 1
            if self.animation_timer > 0:

                self.animation_timer -= 1

            #if we are, shift frames in the animation and reset the timer.
            else:

                self.shift_animation()
                self.animation_timer = self.current_animation[1]

    def shift_animation(self):
        """
        Shifts to the next sprite (frame) in the animation.
        """

        if self.current_animation != None:#make sure we actually have one

            sprites = self.current_animation[0]#'sprites' name for convenience

            #if the iterated sprite value is not out of range
            #NOTE: the same sprite loaction on the sheet cannot be repeated
            #in an animation because of the .index method. A sheet must
            #have a unique sprite for each location used in an animation
            if sprites.index(self.current_sprite) + 1 <= (len(sprites) - 1):

                newsp = sprites[sprites.index(self.current_sprite) + 1]

                self.current_sprite = newsp
                self.image = self.sheet.sprites[newsp]

            #else if the value is out of range, restart animation
            else:

                #shift to the first sprite in the list
                self.current_sprite = sprites[0]
                self.image = self.sheet.sprites[sprites[0]]

    def act(self, surface = None, *args):
        """
        Method to be overwritten with update data unique to subclasses. Can
        handle any arguments passed via update().
        """

        pass

    def update(self, surface = None, *args):

        self.act(surface, args)#method to be overwritten with unique update data

        #play an animation, if one is set
        if self.current_animation != None:

            self.animate()

        #finally, draw this entity if we can (surface exists and we're onscreen)
        r = surface.get_rect()
        
        if surface != None and self.rect.colliderect(r) and self.visible:

            surface.blit(self.image, self.rect)

################################################################################

class Player_Sprite(Entity):

    def __init__(self, game, sheet, sprite, animations, pos):

        Entity.__init__(self, game, sheet, sprite, animations, pos)
        
        self.hitbox = pygame.Rect((self.rect.topleft[0] + 5,
                                   self.rect.topleft[1] + 5),
                                  (self.rect.width - 5, self.rect.height - 8))
        self.death_timer = 8
        self.dead = False
        self.center()

    def center(self):

        self.rect.center = pygame.mouse.get_pos()
        self.hitbox.center = self.rect.center

    def die(self):

        self.set_animation('die')
        self.game.play_sound('die.wav')
        self.dead = True
        self.game.set_game_over()

    def act(self, *args):

        if self.dead and self.death_timer > 0:

            self.death_timer -= 1

        elif self.dead:

            self.visible = False

        self.center()

################################################################################

class Button(Entity):

    def __init__(self, game, sheet, sprite, animations, pos, signal):

        Entity.__init__(self, game, sheet, sprite, animations, pos)

        self.signal = signal
        self.pressed = False

    def check_pressed(self, mouse):

        if self.rect.collidepoint(mouse) and self.pressed == False:

            self.pressed = True

    def reset(self):

        self.pressed = False
            
################################################################################

class Scroller(Entity):

    def __init__(self, game, sheet, sprite, animations, pos):

        Entity.__init__(self, game, sheet, sprite, animations, pos)

    def act(self, *args):

        if self.rect.topleft[1] < SCREEN_HEIGHT:

            self.move((0, WORLD_SPEED))

        else:

            total = len(self.game.scroller_grp)
            y = (-SCREEN_HEIGHT + WORLD_SPEED) * total

            self.move((0, y))

################################################################################

class Enemy(Entity):

    def __init__(self, game, sheet, sprite, animations, pos, path, pattern):

        Entity.__init__(self, game, sheet, sprite, animations, pos)

        self.path = path#list of tuples in the form (duration, direction)

        self.path_index = 0
        self.set_path()

        self.pattern = pattern
        self.pattern_index = 0
        self.set_pattern()

        self.screened = False

    def set_path(self):
        
        self.direction = self.path[self.path_index][1]
        self.duration = self.path[self.path_index][0]

    def set_pattern(self):

        self.shot_delay = self.pattern[self.pattern_index][0]
        self.shot_direction = self.pattern[self.pattern_index][1]

    def check_screen_collision(self, surface):

        r = surface.get_rect()

        if self.screened:

            if not r.colliderect(self.rect):

                self.kill()

        else:

            if r.colliderect(self.rect):

                self.screened = True
                
    def check_collisions(self):

        if self.rect.colliderect(self.game.player.hitbox) and (
            self.game.player.dead == False):

            self.game.player.die()

    def pathfind(self):

        if self.duration > 0:

            self.duration -= 1

            self.move(self.direction)

        else:

            if self.path_index == len(self.path) - 1:

                self.path_index = 0
                self.set_path()

            else:

                self.path_index += 1
                self.set_path()

    def shoot(self):

        if self.shot_delay > 0:

            self.shot_delay -= 1

        else:

            if self.pattern[self.pattern_index][1] != None:

                if self.pattern_index == len(self.pattern) - 1:

                    b = Bullet(self.game, self.game.sheets['bullet1.png'],
                               (0, 0), ANIMATIONS['bullet1.png'],
                               self.rect.center,
                               self.pattern[self.pattern_index][1])
                    b.set_animation('spin')
                    self.game.bullet_grp.add(b)

                    self.pattern_index = 0
                    self.set_pattern()

                else:

                    b = Bullet(self.game, self.game.sheets['bullet1.png'],
                               (0, 0), ANIMATIONS['bullet1.png'],
                               self.rect.center,
                               self.pattern[self.pattern_index][1])
                    b.set_animation('spin')
                    self.game.bullet_grp.add(b)

                    self.pattern_index += 1
                    self.set_pattern()

            else:

                if self.pattern_index == len(self.pattern) - 1:

                    self.pattern_index = 0
                    self.set_pattern()

                else:

                    self.pattern_index += 1
                    self.set_pattern()

    def act(self, surface, *args):

        self.pathfind()

        self.check_collisions()

        self.shoot()

        self.check_screen_collision(surface)

################################################################################

class Bullet(Entity):

    def __init__(self, game, sheet, sprite, animations, pos, direction):

        Entity.__init__(self, game, sheet, sprite, animations, pos)

        self.direction = direction

    def check_collisions(self, surface):

        if self.rect.colliderect(self.game.player.hitbox) and (
            self.game.player.dead == False):

            self.game.player.die()

        elif not self.rect.colliderect(surface.get_rect()):

            self.kill()

    def act(self, surface, *args):

        self.move(self.direction)

        self.check_collisions(surface)
