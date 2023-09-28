class Grid:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.grid = [[0 for _ in range(columns)] for _ in range(rows)]

    def set_value(self, x, y, new_value):
        if 0 <= x < self.rows and 0 <= y < self.columns:
            self.grid[x][y] = new_value
        else:
            print("Position out of grid bounds.")

    def change_shape(self, new_rows, new_columns):
        if new_rows <= 0 or new_columns <= 0:
            print("Invalid shape. Rows and columns must be positive integers.")
            return

        new_grid = [[0 for _ in range(new_columns)] for _ in range(new_rows)]

        for i in range(min(self.rows, new_rows)):
            for j in range(min(self.columns, new_columns)):
                new_grid[i][j] = self.grid[i][j]

        self.rows = new_rows
        self.columns = new_columns
        self.grid = new_grid

    def display(self):
        for i in range(self.rows):
            for j in range(self.columns):
                print(self.grid[i][j], end=' ')
            print()
