import pygame

pygame.init()
win = pygame.display.set_mode((600, 600))
pygame.display.set_caption("First Game")

# deklarowanie kolorów
CZARNY=(0,0,0)
BIALY=(255,255,255)
ZOLTY = (255, 255, 0)



run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.draw.rect(win, BIALY, (0, 0, 600, 600))
    pygame.draw.circle(win, CZARNY, (300, 300), 150, 0)
    pygame.draw.rect(win, ZOLTY, (225, 225, 150, 150))

    pygame.display.update()

    # rysowanie kwadratów
    # pygame.draw.rect(win, CZERWONY , (10, 30, 100, 100))
    # pygame.draw.rect(win, ZIELONY, (310, 30, 100, 100))
    # rysowanie kół
    # pygame.draw.circle(win, JASNY_NIEBIESKI, (210, 200), 50, 25)
    # pygame.draw.circle(win, POMARANCZOWY, (360, 200), 50, 5)
    # # linia pozioma
    # pygame.draw.line(win, NIEBIESKI, (10, 325), (110, 325), 15)
    # # linia pionowa
    # pygame.draw.line(win, SZARY, (210, 275), (210, 375), 5)
    # # rysowanie plusa
    # pygame.draw.line(win, NIEBIESKI, (310, 325), (410, 325), 10)
    # pygame.draw.line(win, SZARY, (360, 275), (360, 375), 10)
    # wypisywanie tekstu
    # font = pygame.font.SysFont('comicsans', 30)
    # label = font.render('Tekst do wyświetlania ', 1, (255, 255, 255))
    #win.blit(label, (100, 425))

