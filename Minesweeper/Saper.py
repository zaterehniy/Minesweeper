import tkinter as tk
import random
import time

class Cell(tk.Button):
    def __init__(self, master, x, y, callback):
        super().__init__(master, font=('Arial', 12), relief='raised', anchor='center')
        self.master = master
        self.x = x
        self.y = y
        self.callback = callback
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.config(text='', width=2, height=1)
        self.bind('<Button-1>', self.left_click)
        self.bind('<Button-3>', self.right_click)
        self.bind('<Double-Button-1>', self.double_click)

    def left_click(self, event):
        if not self.master.game_over and not self.is_flagged:
            self.callback(self.x, self.y)

    def right_click(self, event):
        if not self.master.game_over and not self.is_revealed:
            self.is_flagged = not self.is_flagged
            self.config(text='🚩' if self.is_flagged else '')
            self.master.update_flag_counter()

    def double_click(self, event):
        if self.is_revealed and not self.master.game_over:
            self.master.auto_reveal_neighbors(self.x, self.y)

class Minesweeper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Сапёр")
        self.difficulty_var = tk.StringVar(value="Средний")
        self.set_difficulty("Средний")
        self.create_widgets()
        self.reset_game()

    def set_difficulty(self, level):
        if level == "Лёгкий":
            self.size = 8
            self.mines = 10
        elif level == "Средний":
            self.size = 12
            self.mines = 25
        elif level == "Сложный":
            self.size = 16
            self.mines = 40

    def create_widgets(self):
        self.status = tk.Label(self, text="", font=('Arial', 12))
        self.status.grid(row=self.size, column=0, columnspan=self.size, sticky="ew")

        self.new_game_btn = tk.Button(self, text="Новая игра", command=self.reset_game)
        self.new_game_btn.grid(row=self.size+1, column=0, columnspan=self.size, sticky="ew")

        self.difficulty_menu = tk.OptionMenu(self, self.difficulty_var, "Лёгкий", "Средний", "Сложный", command=self.change_difficulty)
        self.difficulty_menu.grid(row=self.size+2, column=0, columnspan=self.size, sticky="ew")

    def change_difficulty(self, choice):
        self.set_difficulty(choice)
        self.reset_game()

    def reset_game(self):
        self.flags = 0
        self.game_over = False
        self.start_time = time.time()

        if hasattr(self, 'cells'):
            for row in self.cells:
                for cell in row:
                    cell.destroy()

        self.status.grid_forget()
        self.new_game_btn.grid_forget()
        self.difficulty_menu.grid_forget()

        self.status = tk.Label(self, text="", font=('Arial', 12))
        self.status.grid(row=self.size, column=0, columnspan=self.size, sticky="ew")

        self.new_game_btn = tk.Button(self, text="Новая игра", command=self.reset_game)
        self.new_game_btn.grid(row=self.size+1, column=0, columnspan=self.size, sticky="ew")

        self.difficulty_menu = tk.OptionMenu(self, self.difficulty_var, "Лёгкий", "Средний", "Сложный", command=self.change_difficulty)
        self.difficulty_menu.grid(row=self.size+2, column=0, columnspan=self.size, sticky="ew")

        for i in range(self.size):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(self.size, weight=0)
        self.grid_rowconfigure(self.size+1, weight=0)
        self.grid_rowconfigure(self.size+2, weight=0)

        self.create_field()
        self.place_mines()
        self.update_flag_counter()

    def create_field(self):
        self.cells = []
        for x in range(self.size):
            row = []
            for y in range(self.size):
                cell = Cell(self, x, y, self.reveal_cell)
                cell.grid(row=x, column=y, sticky="nsew")
                row.append(cell)
            self.cells.append(row)

    def place_mines(self):
        positions = [(x, y) for x in range(self.size) for y in range(self.size)]
        mines = random.sample(positions, self.mines)
        for x, y in mines:
            self.cells[x][y].is_mine = True

    def count_adjacent_mines(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.cells[nx][ny].is_mine:
                        count += 1
        return count

    def reveal_cell(self, x, y):
        cell = self.cells[x][y]
        if cell.is_revealed or cell.is_flagged:
            return

        cell.is_revealed = True
        cell.config(relief='sunken', bg='lightgrey')

        if cell.is_mine:
            cell.config(text='💣', bg='red')
            self.end_game(False)
            return

        count = self.count_adjacent_mines(x, y)
        if count > 0:
            cell.config(text=str(count), fg='blue')
        else:
            cell.config(text='')
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        neighbor = self.cells[nx][ny]
                        if not neighbor.is_revealed and not neighbor.is_mine:
                            self.reveal_cell(nx, ny)

        self.check_win()

    def auto_reveal_neighbors(self, x, y):
        cell = self.cells[x][y]
        count = self.count_adjacent_mines(x, y)
        flagged = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.cells[nx][ny].is_flagged:
                        flagged += 1
        if flagged == count:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        neighbor = self.cells[nx][ny]
                        if not neighbor.is_flagged and not neighbor.is_revealed:
                            self.reveal_cell(nx, ny)

    def update_flag_counter(self):
        self.flags = sum(cell.is_flagged for row in self.cells for cell in row)
        self.status.config(text=f"Флаги: {self.flags}/{self.mines}")

    def check_win(self):
        for row in self.cells:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return
        self.end_game(True)

    def end_game(self, won):
        self.game_over = True
        for row in self.cells:
            for cell in row:
                if cell.is_mine and not cell.is_flagged:
                    cell.config(text='💣')
        elapsed = int(time.time() - self.start_time)
        msg = "Победа!" if won else "Проигрыш!"
        self.status.config(text=f"{msg} Время: {elapsed} сек.")

if __name__ == "__main__":
    game = Minesweeper()
    game.mainloop()