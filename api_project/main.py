import pygame as pg
import requests
import os

apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
map_api_server = "https://static-maps.yandex.ru/1.x/"
geocoder_api_server = "https://geocode-maps.yandex.ru/1.x/"
filename = "map.png"
spn = 1
l = 'map'
size = (450, 450)
clock = pg.time.Clock()


def main():
    global spn, l, point
    deleting = False
    running = True
    focused = False
    point = None
    search_text = ''
    screen = start()
    font = pg.font.Font(None, 60)
    font_2 = pg.font.Font(None, 35)

    pg.display.flip()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    deleting = True
                    timer = 0
                elif event.key == pg.K_PAGEUP:
                    if map_image:
                        if spn > 0.001953125:
                            spn /= 2
                            make_map(point, spn, size, filename)
                            map_image = pg.image.load(filename)
                            screen.blit(map_image, (100, 250))
                elif event.key == pg.K_PAGEDOWN:
                    if map_image:
                        if spn < 64:
                            spn *= 2
                            make_map(point, spn, size, filename)
                            map_image = pg.image.load(filename)
                            screen.blit(map_image, (100, 250))
                elif event.key == 13:
                    point = make_point(search_text)
                    make_map(point, spn, size, filename)
                    map_image = pg.image.load(filename)
                    screen.blit(map_image, (100, 250))
                elif event.key == pg.K_DOWN:
                    point[1] = str(max(float(point[1]) - spn, -85))
                    make_map(point, spn, size, filename)
                    map_image = pg.image.load(filename)
                    screen.blit(map_image, (100, 250))
                elif event.key == pg.K_UP:
                    point[1] = str(min(float(point[1]) + spn, 85))
                    make_map(point, spn, size, filename)
                    map_image = pg.image.load(filename)
                    screen.blit(map_image, (100, 250))
                elif event.key == pg.K_LEFT:
                    point[0] = str(max(float(point[0]) - spn * 2, -180 + spn / 2))
                    make_map(point, spn, size, filename)
                    map_image = pg.image.load(filename)
                    screen.blit(map_image, (100, 250))
                elif event.key == pg.K_RIGHT:
                    point[0] = str(min(float(point[0]) + spn * 2, 180 - spn / 2))
                    make_map(point, spn, size, filename)
                    map_image = pg.image.load(filename)
                    screen.blit(map_image, (100, 250))
                else:
                    search_text += event.unicode

            if event.type == pg.KEYUP:
                deleting = False

            if event.type == pg.MOUSEBUTTONDOWN:
                if focused:
                    point = make_point(search_text)
                    make_map(point, spn, size, filename)
                    map_image = pg.image.load(filename)
                    screen.blit(map_image, (100, 250))
                else:
                    l_checker(*event.pos, screen)

            if event.type == pg.MOUSEMOTION:
                x, y = event.pos
                if 850 <= x <= 990 and 80 <= y <= 130:
                    focused = True
                    button_text = font.render("Enter", 1, (255, 255, 255))
                    screen.blit(button_text, (860, 85))
                    pg.draw.rect(screen, (255, 255, 255), (850, 80, 140, 50), 1)
                else:
                    focused = False
                    button_text = font.render("Enter", 1, (100, 255, 100))
                    screen.blit(button_text, (860, 85))
                    pg.draw.rect(screen, (100, 255, 100), (850, 80, 140, 50), 1)

        pg.draw.rect(screen, (0, 0, 0), (31, 81, 798, 48))
        text_image = font_2.render(search_text, 1, (100, 255, 100))
        length = text_image.get_rect()[2]
        if deleting:
            timer += clock.tick()
            if timer > 100:
                search_text = search_text[:-1]
                timer = 0
        if length > 780:
            new_text_image = pg.Surface([780, 35])
            new_text_image.blit(text_image, (780 - length, 0))
            text_image = new_text_image
        screen.blit(text_image, (35, 90))
        pg.display.flip()
    if os.access('map.png', 1):
        os.remove('map.png')


def start():
    pg.init()
    screen = pg.display.set_mode((1000, 800))
    pg.draw.rect(screen, (100, 255, 100), (30, 80, 800, 50), 1)
    font = pg.font.Font(None, 60)
    text = font.render("Введите начальные координаты/адрес", 1, (100, 255, 100))
    screen.blit(text, (70, 30))
    button_text = font.render("Enter", 1, (100, 255, 100))
    screen.blit(button_text, (860, 85))
    pg.draw.rect(screen, (100, 255, 100), (850, 80, 140, 50), 1)
    pg.display.set_caption('yandex_mini_map')

    font = pg.font.Font(None, 25)
    texts = [font.render("Схема", 1, (255, 255, 255)),
             font.render("Спутник", 1, (100, 255, 100)),
             font.render("Гибрид", 1, (100, 255, 100))]

    pg.draw.rect(screen, (255, 255, 255), (160, 200, 90, 30), 1)
    pg.draw.rect(screen, (100, 255, 100), (260, 200, 90, 30), 1)
    pg.draw.rect(screen, (100, 255, 100), (360, 200, 90, 30), 1)

    screen.blit(texts[0], (175, 205))
    screen.blit(texts[1], (275, 205))
    screen.blit(texts[2], (375, 205))

    return screen


def make_point(request_text):
    geocoder_params = {
        "apikey": apikey,
        "geocode": request_text,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        print('Поиск координат,', response)
        exit(-1)
    return response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
        "pos"].split()


def make_map(point, spn, size, filename):
    map_params = {
        "ll": ','.join(point),
        "l": l,
        "size": '450,450',
        "spn": str(spn) + ',' + str(spn)}
    response = requests.get(map_api_server, params=map_params)

    if not response:
        print('Создание карты,', response)
        exit(-1)

    with open(filename, 'wb') as pic:
        pic.write(response.content)


def l_checker(x, y, screen):
    global l
    if 160 <= x <= 250 and 200 <= y <= 230:
        l = 'map'
        font = pg.font.Font(None, 25)
        texts = [font.render("Схема", 1, (255, 255, 255)),
                 font.render("Спутник", 1, (100, 255, 100)),
                 font.render("Гибрид", 1, (100, 255, 100))]

        pg.draw.rect(screen, (255, 255, 255), (160, 200, 90, 30), 1)
        pg.draw.rect(screen, (100, 255, 100), (260, 200, 90, 30), 1)
        pg.draw.rect(screen, (100, 255, 100), (360, 200, 90, 30), 1)

        screen.blit(texts[0], (175, 205))
        screen.blit(texts[1], (275, 205))
        screen.blit(texts[2], (375, 205))
        make_map(point, spn, size, filename)
        map_image = pg.image.load(filename)
        screen.blit(map_image, (100, 250))
    if 260 <= x <= 350 and 200 <= y <= 230:
        l = 'sat'
        font = pg.font.Font(None, 25)
        texts = [font.render("Схема", 1, (100, 255, 100)),
                 font.render("Спутник", 1, (255, 255, 255)),
                 font.render("Гибрид", 1, (100, 255, 100))]

        pg.draw.rect(screen, (100, 255, 100), (160, 200, 90, 30), 1)
        pg.draw.rect(screen, (255, 255, 255), (260, 200, 90, 30), 1)
        pg.draw.rect(screen, (100, 255, 100), (360, 200, 90, 30), 1)

        screen.blit(texts[0], (175, 205))
        screen.blit(texts[1], (275, 205))
        screen.blit(texts[2], (375, 205))

        make_map(point, spn, size, filename)
        map_image = pg.image.load(filename)
        screen.blit(map_image, (100, 250))
    if 360 <= x <= 450 and 200 <= y <= 230:
        l = 'sat,skl'
        font = pg.font.Font(None, 25)
        texts = [font.render("Схема", 1, (100, 255, 100)),
                 font.render("Спутник", 1, (100, 255, 100)),
                 font.render("Гибрид", 1, (255, 255, 255))]

        pg.draw.rect(screen, (100, 255, 100), (160, 200, 90, 30), 1)
        pg.draw.rect(screen, (100, 255, 100), (260, 200, 90, 30), 1)
        pg.draw.rect(screen, (255, 255, 255), (360, 200, 90, 30), 1)

        screen.blit(texts[0], (175, 205))
        screen.blit(texts[1], (275, 205))
        screen.blit(texts[2], (375, 205))

        make_map(point, spn, size, filename)
        map_image = pg.image.load(filename)
        screen.blit(map_image, (100, 250))


if __name__ == '__main__':
    main()
