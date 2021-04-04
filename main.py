import random
import os
import readchar
import copy

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
             "ENEMY": "○",
             "KUSA": "Ｗ"}

area_count = -1
floor = 1


class Room:
    # 部屋を定義したクラス
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def intro(self):
        # デバッグ用
        print(self.x, self.y, self.w, self.h)


class Area:
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


class DungeonObject:
    # ダンジョンに配置されるものや人はこのクラスを親に持つことを想定している
    def __init__(self):
        self.x = -1
        self.y = -1

    def set_random_position(self):
        area_index = random.randint(0, area_count - 1)
        self.x = areas[area_index].room.x + random.randint(0, areas[area_index].room.w - 1)
        self.y = areas[area_index].room.y + random.randint(0, areas[area_index].room.h - 1)


class Character(DungeonObject):
    # ダンジョンオブジェクトクラスを親クラスに持つプレイヤーや敵などが該当するクラス
    def __init__(self, hp=-1, max_hp=-1, attack=-1):
        super().__init__()
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack

    """def set_random_position(self):
        # その階層のどこかのエリアのランダムな場所にキャラクターの座標を移動させる
        area_index = random.randint(0, area_count-1)
        self.x = areas[area_index].room.x + random.randint(0, areas[area_index].room.w-1)
        self.y = areas[area_index].room.y + random.randint(0, areas[area_index].room.h-1)"""

    def intro(self):
        # デバッグ用
        print(self.x, self.y)


class Item(DungeonObject):
    # ダンジョンオブジェクトクラスを親に持つアイテムのクラス、とりあえず座標の初期化と名前を変数に持つ
    def __init__(self, name):
        super().__init__()
        self.name = name


class Yakusou(Item):
    # Itemを親クラスに持つ薬草のクラス、アイテムをすべてクラスとして実装するかは未定
    def __init__(self):
        super().__init__('薬草')

    def use(self):
        heal = 5
        if player.hp + heal <= player.max_hp:
            player.hp += heal
            draw_field()
            print("薬草を使用した！")
            print("シレンは" + str(heal) + "回復した！")
            readchar.readkey()
        else:
            heal = player.max_hp - player.hp
            player.hp = player.max_hp
            draw_field()
            print("薬草を使用した！")
            if heal == 0:
                print("シレンのHPは満タンだった")
            else:
                print("シレンは" + str(heal) + "回復した！")
            readchar.readkey()


def is_int(input_string):
    # 引数に渡した文字列が数字であるかどうかを判断しboolean型で返す関数
    # メニュー画面でプレイヤーの入力が数字であるかどうかを判定したかったため作成
    try:
        int(input_string)
        return True
    except ValueError:
        return False


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


"""def set_random_position():
    # この関数はダンジョンオブジェクトクラスに実装したためもう使わない
    area_index = random.randint(0, area_count-1)
    x = areas[area_index].room.x + random.randint(0, areas[area_index].room.w-1)
    y = areas[area_index].room.y + random.randint(0, areas[area_index].room.h-1)
    position = (x, y)
    return position"""


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

    # この上までが通路を作る処理 この下は周囲３ますが壁に囲まれているマスは行き止まりであると判定し行き止まりを消去する処理を行う
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

    # ここからはダンジョンを生成し終わった後にプレイヤーや敵、アイテムや階段の初期座標を決めていく
    player.set_random_position()
    stair.set_random_position()
    if floor <= 4:
        field[stair.y][stair.x] = CELL_TYPE["STAIRS"]
    elif floor == 5:
        field[stair.y][stair.x] = CELL_TYPE["AMULET"]

    enemy.hp = 2 + floor
    enemy.max_hp = 2 + floor
    enemy.attack = 2 + floor
    enemy.set_random_position()
    yakusou.set_random_position()
    field[yakusou.y][yakusou.x] = CELL_TYPE["KUSA"]


def draw_field():
    # とりあえずマップ全体を表示する関数　ゲーム中には使用しない予定　カメラを実装するまではこれで行く
    buffer = copy.deepcopy(field)

    if player.hp > 0:
        buffer[player.y][player.x] = CELL_TYPE["PLAYER"]
    if enemy.hp > 0:
        buffer[enemy.y][enemy.x] = CELL_TYPE["ENEMY"]

    os.system("cls")
    print(str(floor) + 'F  turn:' + str(turn) + '  HP ' + str(player.hp) + '/' + str(player.max_hp))
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            print(buffer[y][x], end='')
        print('')

    # デバッグ用にプレイヤーの座標とエリアと部屋の変数を表示させた
    """player.intro()
    for ac in range(area_count):
        print(ac, end=': ')
        areas[ac].intro()
        areas[ac].room.intro()"""


def draw_menu():
    # プレイヤーがメニューを開いたときに描画する関数
    while True:
        os.system("cls")
        print("アイテム一覧:使用するアイテムを選んでください。戻る場合はqを押してください")
        for item_num in range(len(items)):
            print(item_num, items[item_num].name)
        c = readchar.readkey()
        if c == 'q':
            return
        elif is_int(c):
            if int(c) < len(items):
                print(items[int(c)].name + "を使用しますか？ y/n")
                answer = readchar.readkey()
                if answer == 'y':
                    items[int(c)].use()
                    del items[int(c)]
                    return
                else:
                    continue


def get_room(x, y):
    # (x, y)が含まれる部屋の番号を返り値として返す、部屋ではなかった場合には-1を返す
    for area_num in range(area_count):
        if areas[area_num].room.x <= x < areas[area_num].room.x + areas[area_num].room.w \
                and areas[area_num].room.y <= y < areas[area_num].room.y + areas[area_num].room.h:
            return area_num
    return -1


if __name__ == '__main__':
    # ゲーム内で用いる変数等の初期化処理を行う
    turn = 0
    # player の初期化処理
    player = Character(hp=15, max_hp=15, attack=3)
    enemy = Character()
    stair = DungeonObject()
    yakusou = Yakusou()
    items = []

    # areas の初期化処理
    areas = [0] * AREA_MAX
    for i in range(0, AREA_MAX):
        area = Area(0, 0, 0, 0)
        areas[i] = area

    # fieldの初期化処理
    field = [[-1] * FIELD_WIDTH for i in range(FIELD_HEIGHT)]

    generate_field()

    # ゲーム部分のメインループ
    while True:
        draw_field()

        px = player.x
        py = player.y

        # ここでユーザーにキーボード入力させwasdで移動を行いmでメニューを開けるようにした
        c = str(readchar.readkey())

        if c == 'w':
            py -= 1
        elif c == 's':
            py += 1
        elif c == 'a':
            px -= 1
        elif c == 'd':
            px += 1
        elif c == 'm':
            draw_menu()
            continue

        # 戦闘処理
        if enemy.hp > 0 and px == enemy.x and py == enemy.y:
            print("シレンの攻撃！")
            readchar.readkey()
            damage = int(player.attack/2 + random.randint(0, player.attack+1))
            enemy.hp -= damage
            print("マムルLv" + str(floor) + "に" + str(damage) + "のダメージ！")
            readchar.readkey()
            if enemy.hp <= 0:
                draw_field()
                print("マムルLv" + str(floor) + "を倒した！")
                readchar.readkey()

        # 戦闘がおこらなかった時の処理
        else:
            next_cell = field[py][px]
            if next_cell == CELL_TYPE["NONE"]:
                player.x = px
                player.y = py
                if turn % 10 == 0 and player.hp < player.max_hp:
                    player.hp += 1
            elif next_cell == CELL_TYPE["WALL"]:
                continue
            elif next_cell == CELL_TYPE["STAIRS"]:
                floor += 1
                generate_field()
            elif next_cell == CELL_TYPE["AMULET"]:
                print("シレンはイェンダーの魔除けを手に入れた！")
                print("～終～")
                readchar.readkey()
                break
            elif next_cell == CELL_TYPE["KUSA"]:
                player.x = px
                player.y = py
                field[py][px] = CELL_TYPE["NONE"]
                draw_field()
                print("シレンは薬草を拾った！")
                items.append(yakusou)
                readchar.readkey()

        # プレイヤーのターンが終わり敵側の処理に移る　ここでのアルゴリズムではプレイヤーとの距離に応じて戦闘か移動処理を行う
        if enemy.hp > 0:
            room_num = get_room(enemy.x, enemy.y)
            distance = abs(player.x - enemy.x) + abs(player.y - enemy.y)
            # 距離が1マスしか離れていないときには戦闘処理を行う
            if distance == 1:
                draw_field()
                print("マムルLv" + str(floor) + "の攻撃！")
                readchar.readkey()
                damage = int(enemy.attack/2 + random.randint(0, enemy.attack))
                player.hp -= damage
                print("シレンに" + str(damage) + "のダメージ！")
                readchar.readkey()

                if player.hp <= 0:
                    draw_field()
                    print("シレンは倒れた…")
                    print("Game Over")
                    readchar.readkey()
                    break

            # プレイヤーと敵が同じ部屋にいるか２マスだけ離れている場合は敵がプレイヤーに近づくように移動を行う
            elif (room_num >= 0 and room_num == get_room(player.x, player.y)) or distance == 2:
                ex = enemy.x
                ey = enemy.y

                if ex < player.x:
                    ex += 1
                elif ex > player.x:
                    ex -= 1
                elif ey < player.y:
                    ey += 1
                elif ey > player.y:
                    ey -= 1

                if field[ey][ex] is not CELL_TYPE["WALL"]:
                    enemy.x = ex
                    enemy.y = ey

        turn += 1
