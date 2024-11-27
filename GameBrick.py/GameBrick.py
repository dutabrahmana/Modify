import tkinter as tk
import itertools


class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 5  # Kecepatan bola
        self.colors = itertools.cycle(['#FF0000', '#FFFFFF'])  # Warna Merah dan Putih
        self.color_change_speed = 5  # Kecepatan perubahan warna
        self.color_step = 0
        item = canvas.create_oval(
            x - self.radius, y - self.radius, x + self.radius, y + self.radius, fill=next(self.colors)
        )
        super().__init__(canvas, item)

    def update(self):
        # Ubah warna bola secara dinamis
        self.color_step += 1
        if self.color_step >= self.color_change_speed:
            self.canvas.itemconfig(self.item, fill=next(self.colors))
            self.color_step = 0

        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill='#FF0000',  # Merah untuk paddle
        )
        super().__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#FF0000', 2: '#FFFFFF', 3: '#FF0000'}  # Merah untuk semua brick

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=color,
            tags='brick',
        )
        super().__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()
        self.pack()

        # Membuat latar belakang merah-putih
        self.create_background()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 350)
        self.items[self.paddle.item] = self.paddle
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def create_background(self):
        # Membuat background merah-putih dengan bagian atas merah dan bawah putih
        self.canvas.create_rectangle(0, 0, self.width, self.height // 2, fill='red', outline='red')  # Bagian atas merah
        self.canvas.create_rectangle(0, self.height // 2, self.width, self.height, fill='white', outline='white')  # Bagian bawah putih

        # Tambahkan teks "Duta_191" di tengah-tengah layar dengan warna hitam
        self.canvas.create_text(
            self.width / 2,
            self.height / 2,
            text='Duta_191',
            font=('Arial', 60, 'bold'),
            fill='black',  # Warna teks hitam
            tags='background',
        )

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        # Mengubah warna teks menjadi hitam
        self.text = self.draw_text(300, 350, 'Tekan Spasi untuk Mulai!', size='40', color='black')  # Pindahkan teks ke bawah
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 330)  # Bola di atas paddle
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40', color='white'):
        font = ('Arial', size)
        return self.canvas.create_text(x, y, text=text, font=font, fill=color)

    def update_lives_text(self):
        text = f'Nyawa: {self.lives}'
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.draw_text(300, 200, 'Selamat! Kamu Menang 🎉')
        elif self.ball.get_position()[3] >= self.height:
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'Game Over! Coba Lagi.')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Game Brick Breaker - Modifikasi')
    game = Game(root)
    game.mainloop()
