import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
ORANGE = (255, 165, 0)

# Game modes
MODES = [
    {"name": "NORMAL", "color": WHITE},
    {"name": "2X SPEED", "color": RED},
    {"name": "FLOATING PADDLES", "color": BLUE},
    {"name": "TINY BALL", "color": GREEN},
    {"name": "HUGE PADDLES", "color": PURPLE},
    {"name": "GRAVITY BALL", "color": YELLOW},
    {"name": "INVISIBLE BALL", "color": ORANGE},
    {"name": "REVERSE CONTROLS", "color": (255, 100, 200)},
    {"name": "DRUNK MODE", "color": (100, 255, 200)},
    {"name": "MULTI-BALL", "color": (255, 200, 100)},
]

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = 6
        self.velocity_y = 0
        
    def move(self, keys, up_key, down_key, reverse=False):
        if reverse:
            up_key, down_key = down_key, up_key
            
        if keys[up_key]:
            self.velocity_y = -self.speed
        elif keys[down_key]:
            self.velocity_y = self.speed
        else:
            self.velocity_y = 0
            
        self.y += self.velocity_y
        
        # Keep paddle on screen
        if self.y < 0:
            self.y = 0
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            
    def float_move(self):
        """Floating mode - paddles drift"""
        self.y += self.velocity_y
        
        # Bounce off edges
        if self.y < 0:
            self.y = 0
            self.velocity_y = abs(self.velocity_y) * 0.8
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.velocity_y = -abs(self.velocity_y) * 0.8
            
        # Apply friction
        self.velocity_y *= 0.98
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self, x, y):
        self.reset(x, y)
        self.original_size = BALL_SIZE
        
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.size = BALL_SIZE
        angle = random.choice([random.uniform(-45, 45), random.uniform(135, 225)])
        speed = 5
        self.velocity_x = speed * math.cos(math.radians(angle))
        self.velocity_y = speed * math.sin(math.radians(angle))
        
    def move(self, speed_multiplier=1, gravity=0, drunk=False):
        if drunk:
            # Add random wobble
            self.velocity_x += random.uniform(-0.3, 0.3)
            self.velocity_y += random.uniform(-0.3, 0.3)
            
        self.x += self.velocity_x * speed_multiplier
        self.y += self.velocity_y * speed_multiplier
        
        # Apply gravity
        self.velocity_y += gravity
        
        # Bounce off top and bottom
        if self.y - self.size <= 0 or self.y + self.size >= HEIGHT:
            self.velocity_y *= -1
            self.y = max(self.size, min(HEIGHT - self.size, self.y))
            
    def check_paddle_collision(self, paddle):
        if (self.x - self.size <= paddle.x + paddle.width and 
            self.x + self.size >= paddle.x and
            self.y + self.size >= paddle.y and 
            self.y - self.size <= paddle.y + paddle.height):
            
            # Reflect ball
            self.velocity_x *= -1.1  # Increase speed slightly
            
            # Add spin based on where ball hits paddle
            relative_intersect = (paddle.y + paddle.height/2) - self.y
            normalized = relative_intersect / (paddle.height/2)
            self.velocity_y -= normalized * 3
            
            # Keep ball outside paddle
            if self.velocity_x > 0:
                self.x = paddle.x + paddle.width + self.size
            else:
                self.x = paddle.x - self.size
                
            return True
        return False
    
    def draw(self, screen, visible=True):
        if visible:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong Mode Madness")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.paddle_left = Paddle(30, HEIGHT//2 - PADDLE_HEIGHT//2)
        self.paddle_right = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2)
        self.balls = [Ball(WIDTH//2, HEIGHT//2)]
        
        self.score_left = 0
        self.score_right = 0
        
        self.current_mode = 0
        self.mode_timer = 0
        self.mode_duration = 10 * FPS  # 10 seconds
        self.mode_announcement_timer = 0
        
    def switch_mode(self):
        """Switch to a new random mode"""
        old_mode = self.current_mode
        while self.current_mode == old_mode:
            self.current_mode = random.randint(0, len(MODES) - 1)
        
        self.mode_timer = 0
        self.mode_announcement_timer = FPS * 2  # Show for 2 seconds
        
        # Reset special effects
        self.paddle_left.width = PADDLE_WIDTH
        self.paddle_left.height = PADDLE_HEIGHT
        self.paddle_right.width = PADDLE_WIDTH
        self.paddle_right.height = PADDLE_HEIGHT
        
        # Reset balls to single ball
        if len(self.balls) > 1:
            self.balls = [self.balls[0]]
        self.balls[0].size = BALL_SIZE
        
        # Apply mode-specific changes
        mode_name = MODES[self.current_mode]["name"]
        
        if mode_name == "HUGE PADDLES":
            self.paddle_left.height = 200
            self.paddle_right.height = 200
        elif mode_name == "TINY BALL":
            for ball in self.balls:
                ball.size = 5
        elif mode_name == "MULTI-BALL":
            # Add 2 more balls
            for _ in range(2):
                self.balls.append(Ball(WIDTH//2, HEIGHT//2))
    
    def update(self):
        keys = pygame.key.get_pressed()
        mode_name = MODES[self.current_mode]["name"]
        
        # Update paddles based on mode
        if mode_name == "FLOATING PADDLES":
            self.paddle_left.float_move()
            self.paddle_right.float_move()
            
            # Still allow some control in floating mode
            if keys[pygame.K_w]:
                self.paddle_left.velocity_y -= 0.5
            if keys[pygame.K_s]:
                self.paddle_left.velocity_y += 0.5
            if keys[pygame.K_UP]:
                self.paddle_right.velocity_y -= 0.5
            if keys[pygame.K_DOWN]:
                self.paddle_right.velocity_y += 0.5
        else:
            reverse = (mode_name == "REVERSE CONTROLS")
            self.paddle_left.move(keys, pygame.K_w, pygame.K_s, reverse)
            self.paddle_right.move(keys, pygame.K_UP, pygame.K_DOWN, reverse)
        
        # Update balls based on mode
        speed_mult = 2 if mode_name == "2X SPEED" else 1
        gravity = 0.3 if mode_name == "GRAVITY BALL" else 0
        drunk = (mode_name == "DRUNK MODE")
        
        balls_to_remove = []
        for ball in self.balls:
            ball.move(speed_mult, gravity, drunk)
            
            # Check paddle collisions
            ball.check_paddle_collision(self.paddle_left)
            ball.check_paddle_collision(self.paddle_right)
            
            # Check scoring
            if ball.x < 0:
                self.score_right += 1
                balls_to_remove.append(ball)
            elif ball.x > WIDTH:
                self.score_left += 1
                balls_to_remove.append(ball)
        
        # Remove scored balls and reset if needed
        for ball in balls_to_remove:
            self.balls.remove(ball)
        
        if not self.balls:
            self.balls = [Ball(WIDTH//2, HEIGHT//2)]
            if mode_name == "MULTI-BALL":
                for _ in range(2):
                    self.balls.append(Ball(WIDTH//2, HEIGHT//2))
        
        # Update mode timer
        self.mode_timer += 1
        if self.mode_timer >= self.mode_duration:
            self.switch_mode()
        
        if self.mode_announcement_timer > 0:
            self.mode_announcement_timer -= 1
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw center line
        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(self.screen, WHITE, (WIDTH//2 - 2, y, 4, 10))
        
        # Draw paddles
        self.paddle_left.draw(self.screen)
        self.paddle_right.draw(self.screen)
        
        # Draw balls
        mode_name = MODES[self.current_mode]["name"]
        visible = (mode_name != "INVISIBLE BALL" or self.mode_timer % 30 < 5)
        for ball in self.balls:
            ball.draw(self.screen, visible)
        
        # Draw scores
        score_text_left = self.font.render(str(self.score_left), True, WHITE)
        score_text_right = self.font.render(str(self.score_right), True, WHITE)
        self.screen.blit(score_text_left, (WIDTH//4, 20))
        self.screen.blit(score_text_right, (3*WIDTH//4 - 20, 20))
        
        # Draw mode indicator
        mode = MODES[self.current_mode]
        mode_text = self.font.render(mode["name"], True, mode["color"])
        self.screen.blit(mode_text, (WIDTH//2 - mode_text.get_width()//2, 20))
        
        # Draw mode timer bar
        bar_width = 200
        bar_height = 10
        bar_x = WIDTH//2 - bar_width//2
        bar_y = 60
        progress = self.mode_timer / self.mode_duration
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, mode["color"], (bar_x, bar_y, bar_width * progress, bar_height))
        
        # Draw mode announcement
        if self.mode_announcement_timer > 0:
            alpha = min(255, self.mode_announcement_timer * 3)
            announcement = self.big_font.render(mode["name"], True, mode["color"])
            self.screen.blit(announcement, (WIDTH//2 - announcement.get_width()//2, HEIGHT//2 - 50))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()