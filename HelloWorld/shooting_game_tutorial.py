# part 1
import pygame

pygame.init()  # format pygame的all 模块，pygame第一步


screen_width = 800
screen_height = int(screen_width*0.8)


screen = pygame.display.set_mode((screen_width, screen_height))

# create窗口
pygame.display.set_caption('shooter')

x = 200
y = 200
img = pygame.image.load('img/player/Idle/0.png')
img = pygame.transform.scale()
rect = img.get_rect()
rect.center = (x, y)

run = True
while run:

    screen.blit(img.rect)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False
pygame.quit()


x = 100
y = 100
print(x+y)

# part 8:AI
