"""
Game Mode-modul for Pong-spillet.

Inneholder GameMode-klassen og ModeManager-klassen som håndterer
de forskjellige spillmodusene.
"""

import random


class GameMode:
    """
    Representerer en spillmodus.
    
    En spillmodus har et navn og en farge, og definerer hvordan
    spillet oppfører seg i en gitt periode.
    
    Attributes:
        name (str): Navn på modusen
        color (tuple): RGB-farge for modusen
    """
    
    def __init__(self, name, color):
        """
        Initialiserer en spillmodus.
        
        Args:
            name (str): Navn på modusen
            color (tuple): RGB-farge (r, g, b)
        """
        self.name = name
        self.color = color
    
    def __str__(self):
        """
        Returnerer en streng-representasjon av modusen.
        
        Returns:
            str: Modusens navn
        """
        return self.name


class ModeManager:
    """
    Håndterer spillmoduser og bytte mellom dem.
    
    ModeManager holder styr på alle tilgjengelige moduser, den nåværende
    modusen, og håndterer automatisk bytte hver 10. sekund.
    
    Attributes:
        modes (list): Liste over alle GameMode-objekter
        current_mode_index (int): Indeks til nåværende modus
        mode_timer (int): Teller for tid i nåværende modus
        mode_duration (int): Varighet av hver modus i frames
        announcement_timer (int): Teller for kunngjøringsvisning
        fps (int): Frames per sekund
    """
    
    # Modusliste med farger
    MODE_LIST = [
        {"name": "NORMAL", "color": (255, 255, 255)},
        {"name": "2X SPEED", "color": (255, 100, 100)},
        {"name": "FLOATING PADDLES", "color": (100, 100, 255)},
        {"name": "TINY BALL", "color": (100, 255, 100)},
        {"name": "HUGE PADDLES", "color": (200, 100, 255)},
        {"name": "GRAVITY BALL", "color": (255, 255, 100)},
        {"name": "INVISIBLE BALL", "color": (255, 165, 0)},
        {"name": "REVERSE CONTROLS", "color": (255, 100, 200)},
        {"name": "DRUNK MODE", "color": (100, 255, 200)},
        {"name": "MULTI-BALL", "color": (255, 200, 100)},
        {"name": "Trip", "color": (100,255,0)}
    ]
    
    def __init__(self, fps):
        """
        Initialiserer ModeManager.
        
        Args:
            fps (int): Frames per sekund for spillet
        """
        self.fps = fps
        self.modes = [GameMode(m["name"], m["color"]) for m in self.MODE_LIST]
        self.current_mode_index = 0
        self.mode_timer = 0
        self.mode_duration = 10 * fps  # 10 sekunder
        self.announcement_timer = 0
    
    def update(self):
        """
        Oppdaterer modushåndteringen.
        
        Øker timeren og bytter modus ved behov.
        
        Returns:
            bool: True hvis modusen ble byttet, False ellers
        """
        self.mode_timer += 1
        
        if self.announcement_timer > 0:
            self.announcement_timer -= 1
        
        if self.mode_timer >= self.mode_duration:
            self._switch_mode()
            return True
        
        return False
    
    def _switch_mode(self):
        """
        Bytter til en ny tilfeldig modus.
        
        Private metode som velger en ny modus forskjellig fra nåværende.
        """
        old_mode = self.current_mode_index
        
        # Velg en ny modus forskjellig fra nåværende
        while self.current_mode_index == old_mode:
            self.current_mode_index = random.randint(0, len(self.modes) - 1)
        
        self.mode_timer = 0
        self.announcement_timer = self.fps * 2  # Vis i 2 sekunder
    
    def get_current_mode(self):
        """
        Henter den nåværende spillmodusen.
        
        Returns:
            GameMode: Nåværende GameMode-objekt
        """
        return self.modes[self.current_mode_index]
    
    def get_progress(self):
        """
        Beregner fremdriften i nåværende modus.
        
        Returns:
            float: Fremdrift fra 0.0 til 1.0
        """
        return self.mode_timer / self.mode_duration
    
    def show_announcement(self):
        """
        Sjekker om moduskunngjøring skal vises.
        
        Returns:
            bool: True hvis kunngjøring skal vises
        """
        return self.announcement_timer > 0
    
    def get_all_modes(self):
        """
        Henter alle tilgjengelige moduser.
        
        Returns:
            list: Liste over alle GameMode-objekter
        """
        return self.modes
