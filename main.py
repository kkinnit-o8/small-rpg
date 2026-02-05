import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Window
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2P Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
tiny_font = pygame.font.Font(None, 18)

class Player:
    def __init__(self, x, y, color, controls, corner_pos):
        self.color = color
        self.controls = controls
        self.corner_pos = corner_pos
        self.width = 30
        self.height = 60
        self.speed = 0.8
        self.air_speed = 0.6
        self.hp = 100
        self.max_hp = 100
        
        # Gun mechanics
        self.ammo = 6
        self.max_ammo = 6
        self.is_reloading = False
        self.reload_start_time = 0
        self.reload_duration = 1.5  # 1.5 seconds to reload
        self.last_shot = 0
        self.fire_cooldown = 0.3  # 0.3 seconds between shots
        
        # Deflect mechanics
        self.deflect_active = False
        self.deflect_duration = 0.3  # 0.3 seconds of deflect window
        self.deflect_start_time = 0
        self.deflect_cooldown = 1.5  # 1.5 seconds cooldown after deflect
        self.last_deflect = 0
        
        self.vel = [0, 0]
        self.acc = [0, 0]
        self.pos = [x, y]
        
        # Movement enhancements
        self.dash_speed = 15
        self.can_dash = True
        self.dash_cooldown = 1.0
        self.last_dash = 0
    
    def draw_ui(self, surface):
        """Draw player UI in corner"""
        margin = 20
        if self.corner_pos == "top-left":
            x, y = margin, margin
        elif self.corner_pos == "top-right":
            x, y = WIDTH - 200, margin
        elif self.corner_pos == "bottom-left":
            x, y = margin, HEIGHT - 180
        else:  # bottom-right
            x, y = WIDTH - 200, HEIGHT - 180
        
        # Draw background box
        box_width = 180
        box_height = 140
        pygame.draw.rect(surface, self.color, (x, y, box_width, box_height), 3)
        pygame.draw.rect(surface, WHITE, (x + 3, y + 3, box_width - 6, box_height - 6))
        
        # Draw HP bar
        hp_bar_width = box_width - 20
        hp_bar_height = 15
        hp_percentage = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, GRAY, (x + 10, y + 10, hp_bar_width, hp_bar_height))
        pygame.draw.rect(surface, RED, (x + 10, y + 10, hp_bar_width * hp_percentage, hp_bar_height))
        hp_text = small_font.render(f"HP: {self.hp}", True, BLACK)
        surface.blit(hp_text, (x + 15, y + 11))
        
        # Draw ammo count
        ammo_y = y + 35
        ammo_text = small_font.render(f"Ammo: {self.ammo}/{self.max_ammo}", True, BLACK)
        surface.blit(ammo_text, (x + 10, ammo_y))
        
        # Draw reload progress bar if reloading
        if self.is_reloading:
            reload_progress = (time.time() - self.reload_start_time) / self.reload_duration
            reload_progress = min(1.0, reload_progress)
            pygame.draw.rect(surface, GRAY, (x + 10, ammo_y + 25, hp_bar_width, 10))
            pygame.draw.rect(surface, GREEN, (x + 10, ammo_y + 25, hp_bar_width * reload_progress, 10))
            reload_text = tiny_font.render("Reloading...", True, BLACK)
            surface.blit(reload_text, (x + 15, ammo_y + 27))
        
        # Draw deflect status
        deflect_y = y + 70
        current_time = time.time()
        if self.deflect_active:
            deflect_text = small_font.render("DEFLECT ACTIVE!", True, ORANGE)
            surface.blit(deflect_text, (x + 10, deflect_y))
        elif current_time - self.last_deflect < self.deflect_cooldown:
            cooldown_left = self.deflect_cooldown - (current_time - self.last_deflect)
            cooldown_progress = cooldown_left / self.deflect_cooldown
            pygame.draw.rect(surface, GRAY, (x + 10, deflect_y, hp_bar_width, 10))
            pygame.draw.rect(surface, ORANGE, (x + 10, deflect_y, hp_bar_width * cooldown_progress, 10))
            deflect_text = tiny_font.render(f"Deflect: {cooldown_left:.1f}s", True, BLACK)
            surface.blit(deflect_text, (x + 15, deflect_y + 1))
        else:
            deflect_text = tiny_font.render("Deflect Ready!", True, GREEN)
            surface.blit(deflect_text, (x + 10, deflect_y))
        
        # Draw key instructions
        instructions_y = y + 90
        shoot_key = pygame.key.name(self.controls['shoot']).upper()
        reload_key = pygame.key.name(self.controls['reload']).upper()
        deflect_key = pygame.key.name(self.controls['deflect']).upper()
        
        inst1 = tiny_font.render(f"{shoot_key}: Shoot", True, BLACK)
        inst2 = tiny_font.render(f"{reload_key}: Reload", True, BLACK)
        inst3 = tiny_font.render(f"{deflect_key}: Deflect", True, BLACK)
        surface.blit(inst1, (x + 10, instructions_y))
        surface.blit(inst2, (x + 10, instructions_y + 16))
        surface.blit(inst3, (x + 10, instructions_y + 32))
    
    def drawself(self, surface):
        # Draw deflect shield if active
        if self.deflect_active:
            pygame.draw.circle(surface, ORANGE, 
                             (int(self.pos[0] + self.width / 2), int(self.pos[1] + self.height / 2)), 
                             45, 3)
        
        # Draw player
        pygame.draw.rect(surface, self.color, ((self.pos[0] - 2, self.pos[1] - 2), (self.width + 4, self.height + 4)))
        
        # Draw UI in corner
        self.draw_ui(surface)
    
    def shoot(self, energyballs, target_player):
        """Shoot a bullet"""
        current_time = time.time()
        
        if self.is_reloading:
            return
        
        if self.ammo <= 0:
            return
        
        if current_time - self.last_shot < self.fire_cooldown:
            return
        
        # Calculate direction to target
        direction = [target_player.pos[0] + target_player.width / 2 - (self.pos[0] + self.width / 2),
                     target_player.pos[1] + target_player.height / 2 - (self.pos[1] + self.height / 2)]
        length = (direction[0]**2 + direction[1]**2) ** 0.5
        if length != 0:
            direction[0] /= length
            direction[1] /= length
        
        energyballs.append(EnergyBall(self.pos[0] + self.width / 2,
                                      self.pos[1] + self.height / 2,
                                      direction, self))
        
        self.ammo -= 1
        self.last_shot = current_time
    
    def reload(self):
        """Start reloading"""
        if self.is_reloading or self.ammo == self.max_ammo:
            return
        
        self.is_reloading = True
        self.reload_start_time = time.time()
    
    def activate_deflect(self):
        """Activate deflect shield"""
        current_time = time.time()
        
        if current_time - self.last_deflect < self.deflect_cooldown:
            return
        
        self.deflect_active = True
        self.deflect_start_time = current_time
        self.last_deflect = current_time
    
    def update_deflect(self):
        """Update deflect status"""
        if self.deflect_active:
            if time.time() - self.deflect_start_time > self.deflect_duration:
                self.deflect_active = False
    
    def update_reload(self):
        """Update reload status"""
        if self.is_reloading:
            if time.time() - self.reload_start_time >= self.reload_duration:
                self.ammo = self.max_ammo
                self.is_reloading = False
    
    def handle_input(self, keys, grounded, otherplayer, keys_pressed_this_frame):
        # Horizontal movement with improved acceleration
        if keys[self.controls['left']] and self.pos[0] > 0:
            current_speed = self.speed if "grounded" in grounded else self.air_speed
            self.acc[0] -= current_speed
        if keys[self.controls['right']] and self.pos[0] + self.width < WIDTH:
            current_speed = self.speed if "grounded" in grounded else self.air_speed
            self.acc[0] += current_speed
        
        # Jump with variable height
        if keys[self.controls['up']] and "grounded" in grounded:
            self.vel[1] = -12
        
        # Fast fall
        if keys[self.controls['down']] and "grounded" not in grounded:
            self.acc[1] += 1.5
        
        # Shoot
        if self.controls['shoot'] in keys_pressed_this_frame:
            self.shoot(energyballs, otherplayer)
        
        # Reload
        if self.controls['reload'] in keys_pressed_this_frame:
            self.reload()
        
        # Deflect
        if self.controls['deflect'] in keys_pressed_this_frame:
            self.activate_deflect()
    
    def check(self, obstacles):
        states = []
        g = False
        s = False
        for obs in obstacles:
            if not g:
                if (self.pos[0] + self.width > obs.pos[0] and
                    self.pos[0] < obs.pos[0] + obs.width and
                    self.pos[1] + self.height >= obs.pos[1] and
                    self.pos[1] + self.height <= obs.pos[1] + obs.height):
                    self.pos[1] = obs.pos[1] - self.height
                    self.vel[1] = 0
                    states.append("grounded")
                    g = True
            
            if not s:
                if (self.pos[0] + self.width > obs.pos[0] and
                    self.pos[0] < obs.pos[0] + obs.width and
                    self.pos[1] + self.height > obs.pos[1] and
                    self.pos[1] < obs.pos[1] + obs.height):
                    
                    if self.vel[0] > 0:
                        self.pos[0] = obs.pos[0] - self.width
                    else:
                        self.pos[0] = obs.pos[0] + obs.width
                    
                    self.vel[0] = 0
                    states.append("side")
                    s = True
            if g and s:
                break
        return states
    
    def hit(self, energyballs):
        for ball in energyballs[:]:
            if (self.pos[0] < ball.pos[0] < self.pos[0] + self.width and
                self.pos[1] < ball.pos[1] < self.pos[1] + self.height):
                
                if ball.owner != self:
                    # Check if deflect is active
                    if self.deflect_active:
                        # Deflect the bullet back
                        ball.owner = self
                        ball.direction[0] *= -1
                        ball.direction[1] *= -1
                        ball.color = self.color
                    else:
                        # Take damage
                        self.hp -= 10
                        energyballs.remove(ball)
    
    def update(self, keys, obstacles, otherplayer, keys_pressed_this_frame):
        grounded = self.check(obstacles)
        self.handle_input(keys, grounded, otherplayer, keys_pressed_this_frame)
        self.hit(energyballs)
        self.update_reload()
        self.update_deflect()
        
        # Gravity
        if "grounded" not in grounded:
            self.acc[1] += 0.6
        
        # Update velocity and position
        self.vel[0] += self.acc[0]
        self.vel[1] += self.acc[1]
        
        # Velocity cap
        max_vel = 15
        self.vel[0] = max(-max_vel, min(max_vel, self.vel[0]))
        self.vel[1] = max(-max_vel, min(max_vel, self.vel[1]))
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        # Friction
        if "grounded" in grounded:
            self.vel[0] *= 0.85
        else:
            self.vel[0] *= 0.96
        
        self.acc = [0, 0]


class EnergyBall:
    def __init__(self, x, y, direction, owner):
        self.pos = [x, y]
        self.color = owner.color
        self.direction = direction
        self.radius = 8
        self.speed = 12
        self.owner = owner
    
    def update(self):
        self.pos[0] += self.direction[0] * self.speed
        self.pos[1] += self.direction[1] * self.speed
    
    def drawself(self, surface):
        # Draw glow effect
        pygame.draw.circle(surface, YELLOW, (int(self.pos[0]), int(self.pos[1])), self.radius + 2, 2)
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)


class Obstacle:
    def __init__(self, x, y, width, height, color):
        self.pos = [x, y]
        self.width = width
        self.height = height
        self.color = color
    
    def drawself(self, surface):
        pygame.draw.rect(surface, self.color, (self.pos, (self.width, self.height)))


# Create players
p1 = Player(100, 100, RED, 
            {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s, 
             'shoot': pygame.K_f, 'reload': pygame.K_r, 'deflect': pygame.K_e},
            corner_pos="top-left")

p2 = Player(1000, 100, BLUE, 
            {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN, 
             'shoot': pygame.K_KP1, 'reload': pygame.K_KP2, 'deflect': pygame.K_KP3},
            corner_pos="top-right")

level_obstacles = [
    Obstacle(0, HEIGHT - 30, WIDTH, 50, BLACK),
    Obstacle(300, 600, 200, 20, BLACK),
    Obstacle(700, 450, 200, 20, BLACK),
    Obstacle(500, 300, 150, 20, BLACK),
    Obstacle(100, 500, 150, 20, BLACK),
    Obstacle(950, 600, 150, 20, BLACK)
]

energyballs = []

running = True
clock = pygame.time.Clock()

while running:
    keys_pressed_this_frame = []
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            keys_pressed_this_frame.append(event.key)
    
    # Update
    keys = pygame.key.get_pressed()
    p1.update(keys, level_obstacles, p2, keys_pressed_this_frame)
    p2.update(keys, level_obstacles, p1, keys_pressed_this_frame)
    
    for ball in energyballs[:]:
        ball.update()
        # Remove bullets that go off screen
        if (ball.pos[0] < 0 or ball.pos[0] > WIDTH or 
            ball.pos[1] < 0 or ball.pos[1] > HEIGHT):
            energyballs.remove(ball)
    
    # Draw
    screen.fill(WHITE)
    
    for obs in level_obstacles:
        obs.drawself(screen)
    
    for ball in energyballs:
        ball.drawself(screen)
    
    p1.drawself(screen)
    p2.drawself(screen)
    
    # Check for winner
    if p1.hp <= 0:
        winner_text = font.render("BLUE WINS!", True, BLUE)
        screen.blit(winner_text, (WIDTH // 2 - 100, HEIGHT // 2))
    elif p2.hp <= 0:
        winner_text = font.render("RED WINS!", True, RED)
        screen.blit(winner_text, (WIDTH // 2 - 100, HEIGHT // 2))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()