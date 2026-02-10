"""
Paddle-modul for Pong-spillet.

Inneholder Paddle-klassen som representerer spillerens paddle.
"""

import pygame


class Paddle:
    """
    Representerer en paddle i Pong-spillet.
    
    En paddle kan kontrolleres av spilleren og har både normal bevegelse
    og en "floating" modus hvor den glir med fysikk.
    
    Attributes:
        x (float): X-posisjon
        y (float): Y-posisjon
        width (int): Bredde på paddle
        height (int): Høyde på paddle
        velocity_y (float): Vertikal hastighet
        speed (int): Bevegelseshastighet
        is_left (bool): Om dette er venstre paddle
        original_width (int): Original bredde
        original_height (int): Original høyde
    """
    
    # Konstanter
    DEFAULT_WIDTH = 15
    DEFAULT_HEIGHT = 100
    DEFAULT_SPEED = 6
    FRICTION = 0.98
    BOUNCE_DAMPING = 0.8
    
    def __init__(self, x, y, color=(255,255,255), is_left=True):
        """
        Initialiserer en paddle.
        
        Args:
            x (float): X-posisjon
            y (float): Y-posisjon
            is_left (bool): Om dette er venstre paddle (standard: True)
        """
        self.x = x
        self.y = y
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.original_width = self.DEFAULT_WIDTH
        self.original_height = self.DEFAULT_HEIGHT
        self.velocity_y = 0
        self.speed = self.DEFAULT_SPEED
        self.is_left = is_left
        self.color = color
    
    def move(self, keys, up_key, down_key, reverse=False):
        """
        Beveger paddle basert på tastaturinput.
        
        Args:
            keys: Pygame key state (fra pygame.key.get_pressed())
            up_key (int): Tast for å bevege oppover
            down_key (int): Tast for å bevege nedover
            reverse (bool): Om kontrollene skal reverseres (standard: False)
        """
        if reverse:
            up_key, down_key = down_key, up_key
        
        if keys[up_key]:
            self.velocity_y = -self.speed
        elif keys[down_key]:
            self.velocity_y = self.speed
        else:
            self.velocity_y = 0
        
        self.y += self.velocity_y
        self._keep_on_screen()
    
    def float_move(self):
        """
        Beveger paddle i "floating" modus.
        
        I denne modusen glir paddle med fysikk, inkludert friksjon
        og studsing ved kantene.
        """
        self.y += self.velocity_y
        
        # Stud ved øvre kant
        if self.y < 0:
            self.y = 0
            self.velocity_y = abs(self.velocity_y) * self.BOUNCE_DAMPING
        
        # Stud ved nedre kant
        if self.y > 600 - self.height:  # 600 er skjermhøyden
            self.y = 600 - self.height
            self.velocity_y = -abs(self.velocity_y) * self.BOUNCE_DAMPING
        
        # Applikér friksjon
        self.velocity_y *= self.FRICTION
    
    def _keep_on_screen(self):
        """
        Sørger for at paddle forblir innenfor skjermen.
        
        Private metode som kalles etter bevegelse.
        """
        if self.y < 0:
            self.y = 0
        if self.y > 600 - self.height:  # 600 er skjermhøyden
            self.y = 600 - self.height
    
    def reset_size(self):
        """
        Tilbakestiller paddle til original størrelse.
        
        Brukes når spillmodusen endres.
        """
        self.width = self.original_width
        self.height = self.original_height
    
    def get_rect(self):
        """
        Returnerer pygame.Rect for kollisjondeteksjon.
        
        Returns:
            pygame.Rect: Rektangel som representerer paddle
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """
        Tegner paddle på skjermen.
        
        Args:
            screen (pygame.Surface): Skjermen å tegne på
        """
        pygame.draw.rect(screen, self.color, 
                        (self.x, self.y, self.width, self.height))
