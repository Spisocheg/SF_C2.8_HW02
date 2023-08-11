from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел попадает за границу доски."


class BoardUsedException(BoardException):
    def __str__(self):
        return "В эту клетку уже был произведен выстрел."


class BoardWrongShipException(BoardException):
    pass


class Game:
    def __init__(self, size=6):
        self.size = size
        user = self.create_board()
        ai = self.create_board()
        ai.hide = True

        self.ai = AI(ai, user)
        self.user = User(user, ai)

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя:")
        self.user.self_board.print()
        print("-" * 20)
        print("Доска компьютера:")
        self.ai.self_board.print()
        print("-" * 40)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Field(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def create_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.self_board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.user.self_board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other_dot):
        return self.x == other_dot.x and self.y == other_dot.y


class Field:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count_dest = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def print(self):
        print('  | 1 | 2 | 3 | 4 | 5 | 6 |')
        i = 1
        for line in self.field:
            print(i, end=' |')
            for item in line:
                if self.hide:
                    if item != '■':
                        print(f' {item} |', end='')
                    else:
                        print(f' 0 |', end='')
                else:
                    print(f' {item} |', end='')
            print()
            i += 1

    def is_out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in near:
                current = Dot(dot.x + dx, dot.y + dy)
                if not (self.is_out(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = "."
                    self.busy.append(current)

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.is_out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        if self.is_out(dot):
            raise BoardOutException()

        if dot in self.busy:
            raise BoardUsedException()

        self.busy.append(dot)

        for ship in self.ships:
            if ship.is_shooted(dot):
                ship.hp -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.hp == 0:
                    self.count_dest += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count_dest == len(self.ships)


class Ship:
    def __init__(self, start, length, is_vertical):
        self.start = start  # start dot of ship
        self.length = length
        self.hp = length  # health point
        self.is_vertical = is_vertical  # orientation: True - vertical, False - horizontal

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            current_x = self.start.x
            current_y = self.start.y

            if self.is_vertical:
                current_y += i

            if not self.is_vertical:
                current_x += i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots

    def is_shooted(self, shot_pos):
        return shot_pos in self.dots


class Player:
    def __init__(self, self_board, enemy_board):
        self.self_board = self_board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
        return dot


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


if __name__ == "__main__":
    game = Game()
    game.start()
