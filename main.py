import random
import os
import readchar

FIELD_WIDTH = 32
FIELD_HEIGHT = 32

AREA_MAX = 64
AREA_SIZE_MIN = 16

SCREEN_RANGE = 8

CELL_TYPE = {"NONE": "．",
             "WALL": "■",
             "STAIRS": "％",
             "AMULET": "宝",
             "PLAYER": "＠",
             "ENEMY": "○"}

area_count = -1
floor = 1


class Room():
    # 部屋を定義したクラス
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def intro(self):
        print(self.x, self.y, self.w, self.h)

class Area():
    # エリアを定義したクラス
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.room = Room(0, 0, 0, 0)

    def intro(self):
        # デバッグ用の関数
        print(self.x, self.y, self.w, self.h)


class Character():
    def __init__(self, hp, max_hp, attack):
        self.x = -1
        self.y = -1
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack

    def set_random_position(self):
        # その階層のどこかのエリアのランダムな場所にキャラクターの座標を移動させる
        area_index = random.randint(0, area_count-1)
        self.x = areas[area_index].room.x + random.randint(0, areas[area_index].room.w-1)
        self.y = areas[area_index].room.y + random.randint(0, areas[area_index].room.h-1)

    def intro(self):
        print(self.x, self.y)


def split_area(area_index):
    # エリアを縦か横にある程度の大きさを保ちながら分割する
    global area_count
    global areas
    new_area_index = area_count

    # デバッグ用
    """print('area_count = ' + str(area_count))
    print(area_index)
    print(new_area_index)"""

    w = areas[area_index].w
    h = areas[area_index].h

    # 縦に分割する処理
    if random.random() >= 0.5:
        areas[area_index].w = int(areas[area_index].w / 2)

        areas[new_area_index].x = areas[area_index].x + areas[area_index].w
        areas[new_area_index].y = areas[area_index].y
        areas[new_area_index].w = w - areas[area_index].w
        areas[new_area_index].h = areas[area_index].h

        # デバッグ用
        """for i in range(0, area_count+1):
            print(str(i) + ' : ', end='')
            areas[i].intro()
        print('縦割り')"""
    # 横に分割する処理
    else:
        areas[area_index].h = int(areas[area_index].h / 2)

        areas[new_area_index].x = areas[area_index].x
        areas[new_area_index].y = areas[area_index].y + areas[area_index].h
        areas[new_area_index].w = areas[area_index].w
        areas[new_area_index].h = h - areas[area_index].h

        # デバッグ用
        """for i in range(0, area_count+1):
            print(str(i) + ' : ', end='')
            areas[i].intro()
        print('横割り')"""

    # これ以上分割するとエリアが小さくなりすぎると判断して処理を巻き戻してなかったことにする処理
    if areas[area_index].w < AREA_SIZE_MIN or areas[area_index].h < AREA_SIZE_MIN or \
            areas[new_area_index].w < AREA_SIZE_MIN or areas[new_area_index].h < AREA_SIZE_MIN:
        # print(areas[area_index].w)
        # print(areas[area_index].h)

        areas[area_index].w = w
        areas[area_index].h = h

        # print(areas[new_area_index].w)
        # print(areas[new_area_index].h)

        return

    # この関数を再帰的に実行することで１回で最大限に分割することができる
    area_count += 1
    split_area(area_index)
    split_area(new_area_index)


def display_list(li):
    # 二次元配列の中身をprintする関数
    for y in li:
        for x in y:
            print(x, end='')
        print()


def display_area():
    # エリアがちゃんと分けられているかを確認するために表示する関数　ゲーム中には使用しない
    buffer = [[-1] * FIELD_WIDTH for i in range(FIELD_HEIGHT)]
    for i in range(0, area_count):
        for y in range(int(areas[i].y), int(areas[i].y + areas[i].h)):
            for x in range(int(areas[i].x), int(areas[i].x + areas[i].w)):
                buffer[y][x] = i

    for y in range(0, FIELD_HEIGHT):
        for x in range(0, FIELD_WIDTH):
            print(buffer[y][x], end='')
        print('')


def set_random_position():
    area_index = random.randint(0, area_count-1)
    x = areas[area_index].room.x + random.randint(0, areas[area_index].room.w-1)
    y = areas[area_index].room.y + random.randint(0, areas[area_index].room.h-1)
    position = (x, y)
    return position


def generate_field():
    # 最初にマップ全体を覆うエリアを作ってそこから分割していくために全体を覆うエリアを初期化する
    global area_count
    area_count = 0
    area = Area(0, 0, FIELD_WIDTH, FIELD_HEIGHT)
    areas[0] = area
    area_count += 1
    split_area(0)
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            field[y][x] = CELL_TYPE["WALL"]

    # 各エリアに部屋を割り当てて部屋を作りそのあとに通路を作る
    for i in range(area_count):
        areas[i].room.x = areas[i].x + 2
        areas[i].room.y = areas[i].y + 2
        areas[i].room.w = areas[i].w - 4
        areas[i].room.h = areas[i].h - 4

        for y in range(areas[i].room.y, areas[i].room.y + areas[i].room.h):
            for x in range(areas[i].room.x, areas[i].room.x + areas[i].room.w):
                field[y][x] = CELL_TYPE["NONE"]

        for x in range(areas[i].x, areas[i].x + areas[i].w):
            field[areas[i].y + areas[i].h - 1][x] = CELL_TYPE["NONE"]

        for y in range(areas[i].y, areas[i].y + areas[i].h):
            field[y][areas[i].x + areas[i].w - 1] = CELL_TYPE["NONE"]

        for y2 in range(areas[i].y, areas[i].room.y):
            field[y2][int(areas[i].x + areas[i].room.w / 2)] = CELL_TYPE["NONE"]

        for y2 in range(areas[i].room.y + areas[i].room.h, areas[i].y + areas[i].h):
            field[y2][int(areas[i].x + areas[i].room.w / 2)] = CELL_TYPE["NONE"]

        for x2 in range(areas[i].x, areas[i].room.x):
            field[int(areas[i].y + areas[i].room.h / 2)][x2] = CELL_TYPE["NONE"]

        for x2 in range(areas[i].room.x + areas[i].room.w, areas[i].x + areas[i].w):
            field[int(areas[i].y + areas[i].room.h / 2)][x2] = CELL_TYPE["NONE"]

    for y in range(FIELD_HEIGHT):
        field[y][FIELD_WIDTH - 1] = CELL_TYPE["WALL"]

    for x in range(FIELD_WIDTH):
        field[FIELD_HEIGHT - 1][x] = CELL_TYPE["WALL"]

    while True:
        filled = False
        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                if field[y][x] == CELL_TYPE["WALL"]:
                    continue

                vec2 = [
                    [0, -1],
                    [-1, 0],
                    [0, 1],
                    [1, 0]
                ]

                wall_count = 0
                for i in range(4):
                    x2 = x + vec2[i][0]
                    y2 = y + vec2[i][1]
                    if x2 < 0 or x2 >= FIELD_WIDTH or y2 < 0 or y2 >= FIELD_HEIGHT:
                        wall_count += 1
                    elif field[y2][x2] == CELL_TYPE["WALL"]:
                        wall_count += 1

                if wall_count >= 3:
                    field[y][x] = CELL_TYPE["WALL"]
                    filled = True

        if not filled:
            break

    player.set_random_position()
    stair_position = set_random_position()
    field[stair_position[1]][stair_position[0]] = CELL_TYPE["STAIRS"]


def draw_field():
    # とりあえずマップ全体を表示する関数　ゲーム中には使用しない予定
    os.system("cls")
    print(str(floor) + 'F  turn:' + str(turn))
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            if x == player.x and y == player.y:
                print("＠", end='')
            else:
                print(field[y][x], end='')
        print('')

    # デバッグ用にプレイヤーの座標とエリアと部屋の変数を表示させた
    """player.intro()
    for ac in range(area_count):
        print(ac, end=': ')
        areas[ac].intro()
        areas[ac].room.intro()"""


if __name__ == '__main__':
    turn = 0
    # player の初期化処理
    player = Character(hp=15, max_hp=15, attack=3)

    # areas の初期化処理
    areas = [0] * AREA_MAX
    for i in range(0, AREA_MAX):
        area = Area(0, 0, 0, 0)
        areas[i] = area

    # fieldの初期化処理
    field = [[-1] * FIELD_WIDTH for i in range(FIELD_HEIGHT)]

    generate_field()

    while True:
        draw_field()

        px = player.x
        py = player.y

        c = str(readchar.readkey())

        if c == 'w':
            py -= 1
        elif c == 's':
            py += 1
        elif c == 'a':
            px -= 1
        elif c == 'd':
            px += 1

        next_cell = field[py][px]
        if next_cell == CELL_TYPE["NONE"]:
            player.x = px
            player.y = py
        elif next_cell == CELL_TYPE["WALL"]:
            continue
        elif next_cell == CELL_TYPE["STAIRS"]:
            floor += 1
            generate_field()

        turn += 1
