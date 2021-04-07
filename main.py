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
             "KUSA": "Ｗ",
             "FOOD": "▲",
             "SWORD": "剣",
             "SHIELD": "盾"}

ITEM_TYPE = {"GRASS": 0,
             "FOOD": 1,
             "EQUIPMENT": 2,
             "CANE": 3,
             "SCROLL": 4}

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
    def __init__(self, cell_type):
        self.x = -1
        self.y = -1
        self.cell_type = cell_type

    def set_random_position(self):
        area_index = random.randint(0, area_count - 1)
        self.x = areas[area_index].room.x + random.randint(0, areas[area_index].room.w - 1)
        self.y = areas[area_index].room.y + random.randint(0, areas[area_index].room.h - 1)

    def get_room(self):
        # (x, y)が含まれる部屋の番号を返り値として返す、部屋ではなかった場合には-1を返す
        for area_num in range(area_count):
            if areas[area_num].room.x <= self.x < areas[area_num].room.x + areas[area_num].room.w \
                    and areas[area_num].room.y <= self.y < areas[area_num].room.y + areas[area_num].room.h:
                return area_num
        return -1

    def intro(self):
        # デバッグ用
        print(self.x, self.y)

    def set_tile(self, map):
        map[self.y][self.x] = self.cell_type


class Character(DungeonObject):
    # ダンジョンオブジェクトクラスを親クラスに持つプレイヤーや敵などが該当するクラス
    def __init__(self, cell_type, hp=-1, max_hp=-1, attack=-1):
        super().__init__(cell_type)
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack

    """def set_random_position(self):
        # その階層のどこかのエリアのランダムな場所にキャラクターの座標を移動させる
        area_index = random.randint(0, area_count-1)
        self.x = areas[area_index].room.x + random.randint(0, areas[area_index].room.w-1)
        self.y = areas[area_index].room.y + random.randint(0, areas[area_index].room.h-1)"""


class Player(Character):
    def __init__(self, cell_type=CELL_TYPE["PLAYER"], hp=-1, max_hp=-1, attack=-1, defence=0):
        super().__init__(cell_type, hp, max_hp, attack)
        # 満腹度 satiety
        self.satiety = 100
        self.max_satiety = 100
        self.defence = defence

    def open_menu(self):
        while True:
            os.system("cls")
            print("アイテム一覧:アイテムを選んでください。戻る場合はqを押してください")
            for item_num in range(len(player_items)):
                print(item_num, player_items[item_num].name)
            c = readchar.readkey()
            if c == 'q':
                return
            elif is_int(c):
                if int(c) < len(player_items):
                    print(player_items[int(c)].name + "を 1.使用する, 2.置く, 3.説明を見る, q.戻る")
                    chose_num = readchar.readkey()
                    if chose_num == 'q':
                        continue
                    elif is_int(chose_num):
                        if int(chose_num) == 1:
                            self.use_item(player_items[int(c)])
                            return
                        elif int(chose_num) == 2:
                            self.put_item_on_the_floor(player_items[int(c)])
                            dungeon_objects.append(player_items[int(c)])
                            del player_items[int(c)]
                            return
                        elif int(chose_num) == 3:
                            player_items[int(c)].explain()
                            continue

    def use_item(self, item):
        if item.item_type == ITEM_TYPE["EQUIPMENT"]:
            if not item.equipped:
                print(item.name + "を装備しますか？　y/n")
                answer = readchar.readkey()
                if answer == 'y':
                    item.equip()
                    return
                else:
                    pass
            else:
                print(item.name + "を外しますか？　y/n")
                answer = readchar.readkey()
                if answer == 'y':
                    item.equip()
                    return
                else:
                    pass
        else:
            print(item.name + "を使用しますか？ y/n")
            answer = readchar.readkey()
            if answer == 'y':
                item.use()
                player_items.remove(item)
                return
            else:
                pass

    def battle(self):
        pass

    def stepping_on(self):
        pass

    def overlooking(self):
        pass

    def put_item_on_the_floor(self):
        pass


class Item(DungeonObject):
    # ダンジョンオブジェクトクラスを親に持つアイテムのクラス、とりあえず座標の初期化と名前を変数に持つ
    def __init__(self, name, cell_type, item_type):
        super().__init__(cell_type)
        self.name = name
        self.item_type = item_type

    def explain(self):
        os.system("cls")
        print("これはアイテムです")
        readchar.readkey()


class Yakusou(Item):
    # Itemを親クラスに持つ薬草のクラス、アイテムをすべてクラスとして実装するかは未定.プレイヤーの体力を回復させる効果を持つ
    def __init__(self):
        super().__init__('薬草', CELL_TYPE["KUSA"], ITEM_TYPE["GRASS"])

    def use(self):
        heal = 5
        player.satiety += heal
        if player.satiety > player.max_satiety:
            player.satiety = player.max_satiety

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


class Takatobisou(Item):
    # 草系アイテムの一つ。使用したキャラクターをランダムな部屋のランダムな位置に移動させる。
    def __init__(self):
        super().__init__('高飛び草', CELL_TYPE["KUSA"], ITEM_TYPE["GRASS"])

    def use(self):
        player.satiety += 5
        if player.satiety > player.max_satiety:
            player.satiety = player.max_satiety
        draw_field()
        print("高飛び草を使用した！")
        readchar.readkey()
        player.set_random_position()
        draw_field()


class Onigiri(Item):
    # プレイヤーの満腹度を回復させる。満腹度が最大の場合は最大値を上昇させる。
    def __init__(self):
        super().__init__('おにぎり', CELL_TYPE["FOOD"], ITEM_TYPE["FOOD"])

    def use(self):
        if player.satiety == player.max_satiety:
            player.max_satiety += 5
            player.satiety = player.max_satiety
        player.satiety += 50
        if player.satiety > player.max_satiety:
            player.satiety = player.max_satiety
        draw_field()
        print("おにぎりを食べた！")
        readchar.readkey()
        print("シレンはお腹が膨れた")
        readchar.readkey()
        draw_field()


class Sword(Item):
    # 剣を定義したクラス、このゲーム初の装備することができるアイテム
    def __init__(self):
        super().__init__('剣', CELL_TYPE["SWORD"], ITEM_TYPE["EQUIPMENT"])
        self.power = 1
        self.equipped = False

    def equip(self):
        if not self.equipped:
            player.attack += self.power
            self.name = 'E:剣'
            self.equipped = True
            draw_field()
            print("シレンは剣を装備した！")
            readchar.readkey()
            print("シレンは攻撃力が" + str(self.power) + "上がった！")
            readchar.readkey()
            draw_field()
        else:
            player.attack -= self.power
            self.name = '剣'
            self.equipped = False
            print("シレンは剣をしまった")
            readchar.readkey()
            draw_field()


class Shield(Item):
    # 盾を定義したクラス。プレイヤーの防御力を上げてくれる
    def __init__(self):
        super().__init__('盾', CELL_TYPE["SHIELD"], ITEM_TYPE["EQUIPMENT"])
        self.defence = 1
        self.equipped = False

    def equip(self):
        if not self.equipped:
            player.defence += self.defence
            self.name = 'E:盾'
            self.equipped = True
            print("シレンは盾を装備した！")
            readchar.readkey()
            print("シレンは防御力が" + str(self.defence) + "上がった！")
            readchar.readkey()
            draw_field()
        else:
            player.defence -= self.defence
            self.name = '盾'
            self.equipped = False
            print("シレンは盾をしまった")
            readchar.readkey()
            draw_field()


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
    """stair.set_random_position()
    if floor <= 4:
        field[stair.y][stair.x] = CELL_TYPE["STAIRS"]
    elif floor == 5:
        field[stair.y][stair.x] = CELL_TYPE["AMULET"]

    yakusou.set_random_position()
    yakusou.set_tile()
    field_items.append(yakusou)

    takatobisou.set_random_position()
    takatobisou.set_tile()
    field_items.append(takatobisou)

    onigiri.set_random_position()
    onigiri.set_tile()
    field_items.append(onigiri)

    enemy.hp = 2 + floor
    enemy.max_hp = 2 + floor
    enemy.attack = 2 + floor
    enemy.set_random_position()"""

    player.set_random_position()
    for character in characters:
        character.set_random_position()

    for dungeon_object in dungeon_objects:
        dungeon_object.set_random_position()
        if dungeon_object.cell_type == CELL_TYPE["STAIRS"] and floor == 5:
            dungeon_object.cell_type = CELL_TYPE["AMULET"]
        dungeon_object.set_tile(field)


def draw_field():
    # とりあえずマップ全体を表示する関数　ゲーム中には使用しない予定　カメラを実装するまではこれで行く
    buffer = copy.deepcopy(field)

    """for game_object in game_objects:
        if hasattr(game_object, 'hp'):
            if game_object.hp < 0:
                buffer[game_object.y][game_object.x] = CELL_TYPE["NONE"]"""

    if player.hp > 0:
        buffer[player.y][player.x] = CELL_TYPE["PLAYER"]

    for character in characters:
        if character.hp > 0:
            character.set_tile(buffer)
        elif character.hp <= 0:
            buffer[character.y][character.x] = CELL_TYPE["NONE"]
            characters.remove(character)

    os.system("cls")
    print(
        f'{str(floor)}F  turn:{str(turn)}  HP {str(player.hp)}/{str(player.max_hp)}  満腹度：{str(player.satiety)}  攻撃力:{str(player.attack)} 防御力:{str(player.defence)}')
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
    # プレイヤークラスが持つメソッドに変更したためこの関数は今後使用しない可能性が高い
    while True:
        os.system("cls")
        print("アイテム一覧:使用するアイテムを選んでください。戻る場合はqを押してください")
        for item_num in range(len(player_items)):
            print(item_num, player_items[item_num].name)
        c = readchar.readkey()
        if c == 'q':
            return
        elif is_int(c):
            if int(c) < len(player_items):
                print(player_items[int(c)].name + "を使用しますか？ y/n")
                answer = readchar.readkey()
                if answer == 'y':
                    player_items[int(c)].use()
                    del player_items[int(c)]
                    return
                else:
                    continue


def generate_dungeon_object_list():
    # ダンジョン内のオブジェクトのリストを作成してリストを二つ戻り値として与える関数
    dungeon_objects = [DungeonObject(CELL_TYPE["STAIRS"]), Yakusou(), Takatobisou(), Onigiri(), Sword(), Shield()]
    characters = [Character(CELL_TYPE["ENEMY"], 2+floor, 2+floor, 1+floor)]

    return dungeon_objects, characters


if __name__ == '__main__':
    # ゲーム内で用いる変数等の初期化処理を行う
    turn = 0
    # player の初期化処理
    player = Player(hp=15, max_hp=15, attack=3)
    # generate_dungeon_object_list関数のテストのためにコメントアウト
    """enemy = Character(CELL_TYPE["ENEMY"])
    stair = DungeonObject(CELL_TYPE["STAIRS"])
    yakusou = Yakusou()
    takatobisou = Takatobisou()
    onigiri = Onigiri()"""

    # 左からダンジョン内のアイテムや階段などの動かないもの、キャラクター等の動くものをまとめたリスト
    dungeon_objects, characters = generate_dungeon_object_list()
    player_items = []  # プレイヤーが現在所持しているアイテムを集めたリスト

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
            # draw_menu()
            player.open_menu()
            continue

        # 戦闘処理
        battle = False
        if len(characters) > 0:
            for enemy in characters:
                if enemy.hp > 0 and px == enemy.x and py == enemy.y:
                    print("シレンの攻撃！")
                    readchar.readkey()
                    damage = int(player.attack / 2 + random.randint(0, player.attack + 1))
                    enemy.hp -= damage
                    print("マムルLv" + str(floor) + "に" + str(damage) + "のダメージ！")
                    readchar.readkey()
                    if enemy.hp <= 0:
                        draw_field()
                        print("マムルLv" + str(floor) + "を倒した！")
                        readchar.readkey()
                    battle = True

        # 戦闘がおこらなかった時の処理 プレイヤーの移動先の座標のタイルのタイプによって分岐する
        if not battle:
            next_cell = field[py][px]
            # 移動先に何もなければプレイヤーを移動させる　１０ターンに１回回復する
            if next_cell == CELL_TYPE["NONE"]:
                player.x = px
                player.y = py
                if turn % 10 == 0 and player.hp < player.max_hp:
                    player.hp += 1
            # 移動先に壁がある場合はターンを進めずメインループをもう一度回す
            elif next_cell == CELL_TYPE["WALL"]:
                continue
            # 移動先に階段がある場合はfloorを１増やして次の階層を自動生成する
            elif next_cell == CELL_TYPE["STAIRS"]:
                floor += 1
                dungeon_objects, characters = generate_dungeon_object_list()
                generate_field()
            # 移動先に宝がある場合はゲームのクリア処理を行う
            elif next_cell == CELL_TYPE["AMULET"]:
                print("シレンはイェンダーの魔除けを手に入れた！")
                print("～終～")
                readchar.readkey()
                break
            # 移動先にアイテムがある場合は移動してアイテムを拾うという処理を行う
            else:
                player.x = px
                player.y = py
                field[py][px] = CELL_TYPE["NONE"]
                draw_field()

                # フィールド上にあるアイテムのうちプレイヤーの移動先にあるアイテムがどれかを判別しプレイヤーの持ち物に加える処理を行う
                for item in dungeon_objects:
                    if px == item.x and py == item.y:
                        print("シレンは" + item.name + "を拾った！")
                        player_items.append(item)
                        readchar.readkey()
                        dungeon_objects.remove(item)

        # プレイヤーのターンが終わり敵側の処理に移る　ここでのアルゴリズムではプレイヤーとの距離に応じて戦闘か移動処理を行う
        for enemy in characters:
            if enemy.hp > 0:
                room_num = enemy.get_room()
                distance = abs(player.x - enemy.x) + abs(player.y - enemy.y)
                # 距離が1マスしか離れていないときには戦闘処理を行う
                if distance == 1:
                    draw_field()
                    print("マムルLv" + str(floor) + "の攻撃！")
                    readchar.readkey()
                    damage = int(enemy.attack / 2 + random.randint(0, enemy.attack) - random.randint(0, player.defence))
                    player.hp -= damage
                    print("シレンに" + str(damage) + "のダメージ！")
                    readchar.readkey()

                # プレイヤーと敵が同じ部屋にいるか２マスだけ離れている場合は敵がプレイヤーに近づくように移動を行う
                elif (room_num >= 0 and room_num == player.get_room()) or distance == 2:
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

        # 満腹度の処理を追加
        if turn % 5 == 0:
            if player.satiety > 0:
                player.satiety -= 1
            if player.satiety == 20:
                draw_field()
                print("シレンはお腹が空いてきた")
                readchar.readkey()
            elif player.satiety == 10:
                draw_field()
                print("シレンはお腹が空きすぎて倒れそうだ")
                readchar.readkey()
            elif player.satiety == 0:
                draw_field()
                print("何か食べないと死んでしまう！")
                readchar.readkey()

        if player.satiety == 0:
            player.hp -= 1

        # プレイヤーの死亡処理
        if player.hp <= 0:
            draw_field()
            print("シレンは倒れた…")
            print("Game Over")
            readchar.readkey()
            break
