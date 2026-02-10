"""
Pong Mode Madness - Hovedmodul
Et Pong-spill med modusbytte hver 10. sekund.

Dette programmet implementerer et klassisk Pong-spill med en twist: 
spillemodusen endres automatisk hver 10. sekund, noe som gir nye utfordringer.
"""

import pygame
import random
from paddle import Paddle
from ball import Ball
from game_mode import GameMode, ModeManager


class Game:
    """
    Hovedklassen for Pong-spillet.
    
    Denne klassen håndterer spillets hovedløkke, oppdatering av objekter,
    tegning av grafikk og spillogikk.
    
    Attributes:
        screen (pygame.Surface): Spillvinduet
        clock (pygame.Clock): Klokke for å kontrollere FPS
        paddle_left (Paddle): Venstre spillerpaddle
        paddle_right (Paddle): Høyre spillerpaddle
        balls (list): Liste over Ball-objekter i spillet
        score_left (int): Poeng for venstre spiller
        score_right (int): Poeng for høyre spiller
        mode_manager (ModeManager): Håndterer spillmoduser
        running (bool): Om spillet kjører
    """
    
    # Konstanter
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    
    # Farger
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    def __init__(self):
        """
        Initialiserer spillobjektet.
        
        Setter opp pygame, lager spillvindu, paddles, ball og 
        initialiserer spillvariabler.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pong Mode Madness")
        self.clock = pygame.time.Clock()
        
        # Fonter
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        # Spillobjekter
        self.paddle_left = Paddle(30, self.HEIGHT // 2 - 50, is_left=True)
        self.paddle_right = Paddle(self.WIDTH - 45, self.HEIGHT // 2 - 50, is_left=False)
        self.balls = [Ball(self.WIDTH // 2, self.HEIGHT // 2)]
        
        # Spillvariabler
        self.score_left = 0
        self.score_right = 0
        self.running = True
        self.Trip = False
        
        # Modushåndtering
        self.mode_manager = ModeManager(self.FPS)
    
    def handle_events(self):
        """
        Håndterer brukerinput og hendelser.
        
        Sjekker for tastaturtrykk og lukking av vindu.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """
        Oppdaterer spilltilstanden.
        
        Oppdaterer paddles, baller, sjekker kollisjoner og 
        håndterer poenggivning og modusendringer.
        """
        keys = pygame.key.get_pressed()
        current_mode = self.mode_manager.get_current_mode()
        
        # Oppdater modushåndtering
        mode_changed = self.mode_manager.update()
        if mode_changed:
            self._apply_mode_changes(self.mode_manager.get_current_mode())
        
        # Oppdater paddles basert på modus
        if current_mode.name == "FLOATING PADDLES":
            self._update_floating_paddles(keys)
        else:
            reverse = (current_mode.name == "REVERSE CONTROLS")
            self.paddle_left.move(keys, pygame.K_w, pygame.K_s, reverse)
            self.paddle_right.move(keys, pygame.K_UP, pygame.K_DOWN, reverse)
        
        # Bestem ballparametere basert på modus
        speed_mult = 2 if current_mode.name == "2X SPEED" else 1
        gravity = 0.3 if current_mode.name == "GRAVITY BALL" else 0
        drunk = (current_mode.name == "DRUNK MODE")
        
        # Oppdater baller
        self._update_balls(speed_mult, gravity, drunk)
    
    def _update_floating_paddles(self, keys):
        """
        Oppdaterer paddles i floating-modus.
        
        Args:
            keys: Pygame key state
        """
        self.paddle_left.float_move()
        self.paddle_right.float_move()
        
        # Tillat noe kontroll i floating mode
        if keys[pygame.K_w]:
            self.paddle_left.velocity_y -= 0.5
        if keys[pygame.K_s]:
            self.paddle_left.velocity_y += 0.5
        if keys[pygame.K_UP]:
            self.paddle_right.velocity_y -= 0.5
        if keys[pygame.K_DOWN]:
            self.paddle_right.velocity_y += 0.5
    
    def _update_balls(self, speed_mult, gravity, drunk):
        """
        Oppdaterer alle baller i spillet.
        
        Args:
            speed_mult (float): Hastighetsmultiplikator
            gravity (float): Gravitasjonskraft
            drunk (bool): Om "drunk mode" er aktivert
        """
        balls_to_remove = []
        
        for ball in self.balls:
            ball.move(speed_mult, gravity, drunk, self.HEIGHT)
            
            # Sjekk kollisjon med paddles
            ball.check_paddle_collision(self.paddle_left)
            ball.check_paddle_collision(self.paddle_right)
            
            # Sjekk scoring
            if ball.x < 0:
                self.score_right += 1
                balls_to_remove.append(ball)
            elif ball.x > self.WIDTH:
                self.score_left += 1
                balls_to_remove.append(ball)
        
        # Fjern baller som har scoret
        for ball in balls_to_remove:
            self.balls.remove(ball)
        
        # Reset hvis ingen baller
        if not self.balls:
            self._reset_balls()
    
    def _reset_balls(self):
        """Resetter baller basert på nåværende modus."""
        current_mode = self.mode_manager.get_current_mode()
        self.balls = [Ball(self.WIDTH // 2, self.HEIGHT // 2)]
        
        if current_mode.name == "MULTI-BALL":
            for _ in range(2):
                self.balls.append(Ball(self.WIDTH // 2, self.HEIGHT // 2))
    
    def _apply_mode_changes(self, mode):
        """
        Applicerer endringer når en ny modus aktiveres.
        
        Args:
            mode (GameMode): Den nye modusen
        """
        # Reset paddles
        self.paddle_left.reset_size()
        self.paddle_right.reset_size()
        
        # Reset til én ball
        if len(self.balls) > 1:
            self.balls = [self.balls[0]]
        self.balls[0].reset_size()
        
        # Applikér modus-spesifikke endringer
        if mode.name == "HUGE PADDLES":
            self.paddle_left.height = 200
            self.paddle_right.height = 200
        elif mode.name == "TINY BALL":
            for ball in self.balls:
                ball.size = 5
        elif mode.name == "MULTI-BALL":
            for _ in range(2):
                self.balls.append(Ball(self.WIDTH // 2, self.HEIGHT // 2))
        if mode.name == "Trip":
            self.Trip = True
            for _ in range(50):
                self.balls.append(Ball(self.WIDTH // 2, self.HEIGHT // 2))
        else:
            self.Trip = False
    
    def draw(self):
        """
        Tegner alle spillelementer på skjermen.
        
        Tegner bakgrunn, midtlinje, paddles, baller, poeng og modusinformasjon.
        """
        if self.Trip:
            self.screen.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        else:
            self.screen.fill(self.BLACK)
        
        # Tegn midtlinje
        for y in range(0, self.HEIGHT, 20):
            pygame.draw.rect(self.screen, self.WHITE, 
                           (self.WIDTH // 2 - 2, y, 4, 10))
        
        # Tegn paddles
        if self.Trip:
            self.paddle_left.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            self.paddle_right.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        else:
            self.paddle_left.color = (255,255,255)
            self.paddle_right.color = (255,255,255)

        self.paddle_left.draw(self.screen)
        self.paddle_right.draw(self.screen)
        
        # Tegn baller
        current_mode = self.mode_manager.get_current_mode()
        visible = self._should_ball_be_visible(current_mode)
        for ball in self.balls:
            ball.draw(self.screen, visible)
        
        # Tegn UI
        self._draw_ui(current_mode)
        
        pygame.display.flip()
    
    def _should_ball_be_visible(self, mode):
        """
        Bestemmer om ballen skal være synlig basert på modus.
        
        Args:
            mode (GameMode): Nåværende spillmodus
            
        Returns:
            bool: True hvis ballen skal være synlig
        """
        if mode.name != "INVISIBLE BALL":
            return True
        # Blink i invisible mode
        return self.mode_manager.mode_timer % 30 < 5
    
    def _draw_ui(self, current_mode):
        """
        Tegner brukergrensesnitt (poeng, modus, timer).
        
        Args:
            current_mode (GameMode): Nåværende spillmodus
        """
        # Tegn poeng
        score_left = self.font.render(str(self.score_left), True, self.WHITE)
        score_right = self.font.render(str(self.score_right), True, self.WHITE)
        self.screen.blit(score_left, (self.WIDTH // 4, 20))
        self.screen.blit(score_right, (3 * self.WIDTH // 4 - 20, 20))
        
        # Tegn modusindikator
        mode_text = self.font.render(current_mode.name, True, current_mode.color)
        self.screen.blit(mode_text, 
                        (self.WIDTH // 2 - mode_text.get_width() // 2, 20))
        
        # Tegn timer bar
        self._draw_timer_bar(current_mode)
        
        # Tegn moduskunngjøring
        if self.mode_manager.show_announcement():
            self._draw_mode_announcement(current_mode)
    
    def _draw_timer_bar(self, mode):
        """
        Tegner fremdriftsbar for modusvarigheten.
        
        Args:
            mode (GameMode): Nåværende spillmodus
        """
        bar_width = 200
        bar_height = 10
        bar_x = self.WIDTH // 2 - bar_width // 2
        bar_y = 60
        progress = self.mode_manager.get_progress()
        
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, mode.color, 
                        (bar_x, bar_y, bar_width * progress, bar_height))
    
    def _draw_mode_announcement(self, mode):
        """
        Tegner stor kunngjøring når ny modus aktiveres.
        
        Args:
            mode (GameMode): Den nye modusen
        """
        announcement = self.big_font.render(mode.name, True, mode.color)
        self.screen.blit(announcement, 
                        (self.WIDTH // 2 - announcement.get_width() // 2, 
                         self.HEIGHT // 2 - 50))
    
    def run(self):
        """
        Hovedløkken for spillet.
        
        Kjører spillet til brukeren avslutter. Håndterer hendelser,
        oppdaterer spilltilstand og tegner grafikk.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
        
        pygame.quit()


def main():
    """Hovedfunksjonen som starter spillet."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
