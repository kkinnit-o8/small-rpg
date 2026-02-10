"""
Ball-modul for Pong-spillet.

Inneholder Ball-klassen som representerer ballen i spillet.
"""

import pygame
import random
import math


class Ball:
    """
    Representerer en ball i Pong-spillet.
    
    Ballen beveger seg rundt på skjermen, studser mot vegger og paddles,
    og kan påvirkes av ulike spillmoduser.
    
    Attributes:
        x (float): X-posisjon
        y (float): Y-posisjon
        size (int): Radius på ballen
        velocity_x (float): Horisontal hastighet
        velocity_y (float): Vertikal hastighet
        original_size (int): Original størrelse
    """
    
    # Konstanter
    DEFAULT_SIZE = 15
    DEFAULT_SPEED = 5
    SPEED_INCREASE = 1.1
    MAX_SPEED = 15
    
    def __init__(self, x, y):
        """
        Initialiserer en ball.
        
        Args:
            x (float): Start X-posisjon
            y (float): Start Y-posisjon
        """
        self.x = x
        self.y = y
        self.size = self.DEFAULT_SIZE
        self.original_size = self.DEFAULT_SIZE
        self.velocity_x = 0
        self.velocity_y = 0
        self._set_random_velocity()
    
    def _set_random_velocity(self):
        """
        Setter en tilfeldig starthastighet for ballen.
        
        Private metode som gir ballen en retning mot en av spillerne.
        """
        # Velg en vinkel mot venstre eller høyre
        angle = random.choice([
            random.uniform(-45, 45),      # Mot høyre
            random.uniform(135, 225)      # Mot venstre
        ])
        
        self.velocity_x = self.DEFAULT_SPEED * math.cos(math.radians(angle))
        self.velocity_y = self.DEFAULT_SPEED * math.sin(math.radians(angle))
    
    def move(self, speed_multiplier=1, gravity=0, drunk=False, screen_height=600):
        """
        Beveger ballen og håndterer veggkollisjoner.
        
        Args:
            speed_multiplier (float): Multiplikator for hastighet (standard: 1)
            gravity (float): Gravitasjonskraft (standard: 0)
            drunk (bool): Om "drunk mode" er aktivert (standard: False)
            screen_height (int): Høyde på spillskjermen (standard: 600)
        """
        # Legg til tilfeldig wobble i drunk mode
        if drunk:
            self.velocity_x += random.uniform(-0.3, 0.3)
            self.velocity_y += random.uniform(-0.3, 0.3)
        
        # Oppdater posisjon
        self.x += self.velocity_x * speed_multiplier
        self.y += self.velocity_y * speed_multiplier
        
        # Applikér gravitasjon
        self.velocity_y += gravity
        
        # Stud mot topp og bunn
        if self.y - self.size <= 0:
            self.y = self.size
            self.velocity_y *= -1
        elif self.y + self.size >= screen_height:
            self.y = screen_height - self.size
            self.velocity_y *= -1
    
    def check_paddle_collision(self, paddle):
        """
        Sjekker og håndterer kollisjon med en paddle.
        
        Når ballen treffer en paddle, reverseres den horisontale hastigheten,
        hastigheten økes litt, og vertikal hastighet justeres basert på
        hvor på paddle ballen traff.
        
        Args:
            paddle (Paddle): Paddle-objektet å sjekke kollisjon med
            
        Returns:
            bool: True hvis kollisjon skjedde, False ellers
        """
        # Sjekk om ballen overlapper med paddle
        if (self.x - self.size <= paddle.x + paddle.width and 
            self.x + self.size >= paddle.x and
            self.y + self.size >= paddle.y and 
            self.y - self.size <= paddle.y + paddle.height):
            
            # Reverser horisontal retning og øk hastighet
            self.velocity_x *= -self.SPEED_INCREASE
            
            # Begrens maksimal hastighet
            if abs(self.velocity_x) > self.MAX_SPEED:
                self.velocity_x = self.MAX_SPEED * (1 if self.velocity_x > 0 else -1)
            
            # Legg til "spin" basert på hvor ballen traff
            relative_intersect = (paddle.y + paddle.height / 2) - self.y
            normalized = relative_intersect / (paddle.height / 2)
            self.velocity_y -= normalized * 3
            
            # Flytt ballen utenfor paddle for å unngå gjentatt kollisjon
            if self.velocity_x > 0:
                self.x = paddle.x + paddle.width + self.size
            else:
                self.x = paddle.x - self.size
            
            return True
        
        return False
    
    def reset_size(self):
        """
        Tilbakestiller ballen til original størrelse.
        
        Brukes når spillmodusen endres.
        """
        self.size = self.original_size
    
    def draw(self, screen, visible=True):
        """
        Tegner ballen på skjermen.
        
        Args:
            screen (pygame.Surface): Skjermen å tegne på
            visible (bool): Om ballen skal være synlig (standard: True)
        """
        if visible:
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.x), int(self.y)), self.size)
