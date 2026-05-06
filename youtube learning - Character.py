import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

class Soldier(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        img = pygame.image.load('img/0.png')
        self.image = pygame.transform.scale(img,(int(img.get_width()* scale),int(img.get_height()*scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        screen.blit(self.image, self.rect)

player = Soldier(200,200,1/2)
player2 = Soldier(400,200,1/2)


run = True
while run:

    screen.fill((0, 0, 0))  # clear screen
    
    player.draw()
    player2.draw()




    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()