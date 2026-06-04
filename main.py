import pygame#game function
import sys#exit

pygame.init()#start pygame

# screen
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Still World")

# font
font = pygame.font.Font(None, 48)#(font,size)

# game state
game_state = "START"
score = 0

clock = pygame.time.Clock()#control game speed

while True:
    screen.fill((0, 0, 0))#black screen

    for event in pygame.event.get():#check
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:#check keyboard press
            if game_state == "START" and event.key == pygame.K_SPACE:
                game_state = "PLAYING"

    # START SCREEN
    if game_state == "START":
        text = font.render("Press SPACE to Start", True, (255, 255, 255))
        screen.blit(text, (200, 250))

    # GAME SCREEN
    elif game_state == "PLAYING":
        score += 1
        text = font.render(f"Score: {score}", True, (255, 255, 255))#show score
        screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)