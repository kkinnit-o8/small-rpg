"""
Enhetstester for Pong Mode Madness.

Tester viktige klasser og metoder i prosjektet.
"""

import sys

from paddle import Paddle
from ball import Ball
from game_mode import GameMode, ModeManager


def test_paddle_creation():
    """Tester at Paddle opprettes riktig."""
    print("Test 1: Paddle-oppretting...")
    paddle = Paddle(100, 200, is_left=True)
    
    assert paddle.x == 100, f"Forventet x=100, fikk {paddle.x}"
    assert paddle.y == 200, f"Forventet y=200, fikk {paddle.y}"
    assert paddle.width == 15, f"Forventet width=15, fikk {paddle.width}"
    assert paddle.height == 100, f"Forventet height=100, fikk {paddle.height}"
    
    print("✓ Paddle opprettes med riktige verdier")


def test_paddle_movement():
    """Tester at Paddle beveger seg korrekt."""
    print("\nTest 2: Paddle-bevegelse...")
    paddle = Paddle(100, 300, is_left=True)
    initial_y = paddle.y
    
    # Simuler bevegelse nedover
    paddle.velocity_y = 6
    paddle.y += paddle.velocity_y
    paddle._keep_on_screen()
    
    assert paddle.y == initial_y + 6, f"Forventet y={initial_y + 6}, fikk {paddle.y}"
    
    print("✓ Paddle beveger seg riktig")


def test_paddle_boundary():
    """Tester at Paddle holder seg innenfor skjermen."""
    print("\nTest 3: Paddle grensekontroll...")
    paddle = Paddle(100, 0, is_left=True)
    
    # Prøv å bevege over toppen
    paddle.y = -10
    paddle._keep_on_screen()
    
    assert paddle.y == 0, f"Paddle burde være ved y=0, fikk {paddle.y}"
    
    # Prøv å bevege under bunnen
    paddle.y = 700
    paddle._keep_on_screen()
    
    assert paddle.y <= 600 - paddle.height, "Paddle burde være innenfor skjermen"
    
    print("✓ Paddle holder seg innenfor skjermen")


def test_ball_creation():
    """Tester at Ball opprettes riktig."""
    print("\nTest 4: Ball-oppretting...")
    ball = Ball(400, 300)
    
    assert ball.x == 400, f"Forventet x=400, fikk {ball.x}"
    assert ball.y == 300, f"Forventet y=300, fikk {ball.y}"
    assert ball.size == 15, f"Forventet size=15, fikk {ball.size}"
    assert ball.velocity_x != 0, "Ball burde ha horisontal hastighet"
    assert ball.velocity_y != 0, "Ball burde ha vertikal hastighet"
    
    print("✓ Ball opprettes med riktige verdier")


def test_ball_movement():
    """Tester at Ball beveger seg."""
    print("\nTest 5: Ball-bevegelse...")
    ball = Ball(400, 300)
    initial_x = ball.x
    initial_y = ball.y
    
    ball.move()
    
    # Ball burde ha beveget seg
    assert ball.x != initial_x or ball.y != initial_y, "Ball burde ha beveget seg"
    
    print("✓ Ball beveger seg")


def test_ball_wall_collision():
    """Tester at Ball studser mot vegger."""
    print("\nTest 6: Ball vegg-kollisjon...")
    ball = Ball(400, 5)
    ball.velocity_y = -5  # Beveger seg oppover
    
    ball.move(screen_height=600)
    
    # Hastighet burde ha snudd
    assert ball.velocity_y > 0, "Ball burde ha studset og snudd retning"
    
    print("✓ Ball studser mot vegger")


def test_game_mode_creation():
    """Tester at GameMode opprettes riktig."""
    print("\nTest 7: GameMode-oppretting...")
    mode = GameMode("TEST MODE", (255, 0, 0))
    
    assert mode.name == "TEST MODE", f"Forventet navn 'TEST MODE', fikk {mode.name}"
    assert mode.color == (255, 0, 0), f"Forventet farge (255,0,0), fikk {mode.color}"
    
    print("✓ GameMode opprettes riktig")


def test_mode_manager():
    """Tester at ModeManager håndterer moduser."""
    print("\nTest 8: ModeManager...")
    manager = ModeManager(fps=60)
    
    assert len(manager.modes) == 11, f"Forventet 11 moduser, fikk {len(manager.modes)}"
    assert manager.mode_timer == 0, "Timer burde starte på 0"
    
    initial_mode = manager.get_current_mode()
    
    # Simuler at tiden går (10 sekunder = 600 frames)
    for _ in range(600):
        changed = manager.update()
    
    # Modusen burde ha endret seg
    assert changed, "Modus burde ha endret seg etter 10 sekunder"
    
    print("✓ ModeManager bytter modus riktig")


def test_mode_manager_progress():
    """Tester at ModeManager beregner fremdrift riktig."""
    print("\nTest 9: ModeManager fremdrift...")
    manager = ModeManager(fps=60)
    
    progress_start = manager.get_progress()
    assert progress_start == 0.0, "Fremdrift burde starte på 0.0"
    
    # Oppdater halvveis
    for _ in range(300):
        manager.update()
    
    progress_mid = manager.get_progress()
    assert 0.4 < progress_mid < 0.6, f"Fremdrift burde være rundt 0.5, fikk {progress_mid}"
    
    print("✓ ModeManager beregner fremdrift riktig")


def run_all_tests():
    """Kjører alle tester."""
    print("=" * 50)
    print("KJØRER ENHETSTESTER FOR PONG MODE MADNESS")
    print("=" * 50)
    
    try:
        test_paddle_creation()
        test_paddle_movement()
        test_paddle_boundary()
        test_ball_creation()
        test_ball_movement()
        test_ball_wall_collision()
        test_game_mode_creation()
        test_mode_manager()
        test_mode_manager_progress()
        
        print("\n" + "=" * 50)
        print("ALLE TESTER BESTÅTT! ✓")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n✗ TEST FEILET: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()