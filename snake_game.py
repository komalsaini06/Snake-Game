import tkinter as tk
import random
import json
import os


# ============================================================
# SETTINGS
# ============================================================

GAME_WIDTH = 1100
GAME_HEIGHT = 650

SPACE_SIZE = 25
BODY_PARTS = 3

SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BACKGROUND_COLOR = "#000000"
OBSTACLE_COLOR = "gray"

HIGH_SCORE_FILE = "highscore.json"

SPEED = 150


# ============================================================
# WINDOW
# ============================================================

window = tk.Tk()
window.title("Advanced Snake Game")

score = 0
direction = "down"
paused = False

snake = None
food = None

obstacles = []

# Used to control the game loop safely
game_loop = None


# ============================================================
# HIGH SCORE
# ============================================================

def load_high_score():

    if os.path.exists(HIGH_SCORE_FILE):

        try:
            with open(HIGH_SCORE_FILE, "r") as file:
                data = json.load(file)

            return data.get("high_score", 0)

        except (json.JSONDecodeError, OSError):
            return 0

    return 0


def save_high_score(high_score):

    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            json.dump({"high_score": high_score}, file)

    except OSError:
        pass


high_score = load_high_score()


# ============================================================
# SCORE LABEL
# ============================================================

label = tk.Label(
    window,
    text=f"Score: {score}   High Score: {high_score}",
    font=("Arial", 20)
)

label.pack()


# ============================================================
# CANVAS
# ============================================================

canvas = tk.Canvas(
    window,
    bg=BACKGROUND_COLOR,
    height=GAME_HEIGHT,
    width=GAME_WIDTH
)

canvas.pack()


# ============================================================
# SNAKE CLASS
# ============================================================

class Snake:

    def __init__(self):

        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []

        for i in range(BODY_PARTS):
            self.coordinates.append([0, 0])

        for x, y in self.coordinates:

            square = canvas.create_rectangle(
                x,
                y,
                x + SPACE_SIZE,
                y + SPACE_SIZE,
                fill=SNAKE_COLOR,
                tag="snake"
            )

            self.squares.append(square)


# ============================================================
# FOOD CLASS
# ============================================================

class Food:

    def __init__(self):

        while True:

            x = random.randrange(
                0,
                GAME_WIDTH,
                SPACE_SIZE
            )

            y = random.randrange(
                0,
                GAME_HEIGHT,
                SPACE_SIZE
            )

            # Don't place food on snake
            if snake and [x, y] in snake.coordinates:
                continue

            # Don't place food on obstacle
            if (x, y) in obstacles:
                continue

            break

        self.coordinates = [x, y]

        canvas.create_oval(
            x,
            y,
            x + SPACE_SIZE,
            y + SPACE_SIZE,
            fill=FOOD_COLOR,
            tag="food"
        )


# ============================================================
# CREATE OBSTACLES
# ============================================================

def create_obstacles():

    obstacles.clear()

    number_of_obstacles = 5

    attempts = 0

    while len(obstacles) < number_of_obstacles and attempts < 100:

        attempts += 1

        x = random.randrange(
            0,
            GAME_WIDTH,
            SPACE_SIZE
        )

        y = random.randrange(
            0,
            GAME_HEIGHT,
            SPACE_SIZE
        )

        position = (x, y)

        # Don't put obstacle on snake
        if snake and [x, y] in snake.coordinates:
            continue

        # Don't put obstacles on each other
        if position in obstacles:
            continue

        obstacles.append(position)

        canvas.create_rectangle(
            x,
            y,
            x + SPACE_SIZE,
            y + SPACE_SIZE,
            fill=OBSTACLE_COLOR,
            tag="obstacle"
        )


# ============================================================
# NEXT TURN
# ============================================================

def next_turn(snake_obj):

    global score
    global SPEED
    global food
    global high_score
    global game_loop

    # Don't continue while paused
    if paused:
        return

    x, y = snake_obj.coordinates[0]

    # --------------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------------

    if direction == "up":
        y -= SPACE_SIZE

    elif direction == "down":
        y += SPACE_SIZE

    elif direction == "left":
        x -= SPACE_SIZE

    elif direction == "right":
        x += SPACE_SIZE


    # --------------------------------------------------------
    # SCREEN WRAPPING
    # --------------------------------------------------------

    if x < 0:
        x = GAME_WIDTH - SPACE_SIZE

    elif x >= GAME_WIDTH:
        x = 0

    if y < 0:
        y = GAME_HEIGHT - SPACE_SIZE

    elif y >= GAME_HEIGHT:
        y = 0


    # --------------------------------------------------------
    # ADD NEW HEAD
    # --------------------------------------------------------

    snake_obj.coordinates.insert(0, [x, y])

    square = canvas.create_rectangle(
        x,
        y,
        x + SPACE_SIZE,
        y + SPACE_SIZE,
        fill=SNAKE_COLOR,
        tag="snake"
    )

    snake_obj.squares.insert(0, square)


    # --------------------------------------------------------
    # FOOD COLLISION
    # --------------------------------------------------------

    if (
        food
        and x == food.coordinates[0]
        and y == food.coordinates[1]
    ):

        score += 1

        # Update high score
        if score > high_score:

            high_score = score
            save_high_score(high_score)

        label.config(
            text=f"Score: {score}   High Score: {high_score}"
        )

        # Remove old food
        canvas.delete("food")

        # Create new food
        food = Food()

        # Increase speed
        if SPEED > 50:
            SPEED -= 5


    else:

        # Remove tail
        del snake_obj.coordinates[-1]

        canvas.delete(snake_obj.squares[-1])

        del snake_obj.squares[-1]


    # --------------------------------------------------------
    # COLLISION CHECK
    # --------------------------------------------------------

    if check_collisions(snake_obj):

        game_over()
        return


    # --------------------------------------------------------
    # NEXT GAME LOOP
    # --------------------------------------------------------

    game_loop = window.after(
        SPEED,
        next_turn,
        snake_obj
    )


# ============================================================
# CHANGE DIRECTION
# ============================================================

def change_direction(new_direction):

    global direction

    if new_direction == "left":

        if direction != "right":
            direction = "left"

    elif new_direction == "right":

        if direction != "left":
            direction = "right"

    elif new_direction == "up":

        if direction != "down":
            direction = "up"

    elif new_direction == "down":

        if direction != "up":
            direction = "down"


# ============================================================
# COLLISIONS
# ============================================================

def check_collisions(snake_obj):

    x, y = snake_obj.coordinates[0]

    # --------------------------------------------------------
    # SELF COLLISION
    # --------------------------------------------------------

    for body_part in snake_obj.coordinates[1:]:

        if x == body_part[0] and y == body_part[1]:
            return True


    # --------------------------------------------------------
    # OBSTACLE COLLISION
    # --------------------------------------------------------

    for obstacle in obstacles:

        if x == obstacle[0] and y == obstacle[1]:
            return True


    return False


# ============================================================
# GAME OVER
# ============================================================

def game_over():

    global game_loop

    # Stop the current game loop
    game_loop = None

    canvas.delete(tk.ALL)

    canvas.create_text(
        GAME_WIDTH / 2,
        GAME_HEIGHT / 2 - 60,
        font=("Arial", 50, "bold"),
        text="GAME OVER",
        fill="red"
    )

    canvas.create_text(
        GAME_WIDTH / 2,
        GAME_HEIGHT / 2,
        font=("Arial", 25),
        text=f"Final Score: {score}",
        fill="white"
    )

    canvas.create_text(
        GAME_WIDTH / 2,
        GAME_HEIGHT / 2 + 50,
        font=("Arial", 20),
        text="Press R to Restart",
        fill="yellow"
    )

    canvas.create_text(
        GAME_WIDTH / 2,
        GAME_HEIGHT / 2 + 85,
        font=("Arial", 16),
        text="Press P to Pause / Resume",
        fill="cyan"
    )


# ============================================================
# PAUSE / RESUME
# ============================================================

def toggle_pause(event=None):

    global paused

    # Don't do anything if game hasn't started
    if snake is None or food is None:
        return

    paused = not paused

    if paused:

        canvas.delete("pause")

        canvas.create_text(
            GAME_WIDTH / 2,
            GAME_HEIGHT / 2,
            text="PAUSED\nPress P to Resume",
            fill="yellow",
            font=("Arial", 30, "bold"),
            tag="pause"
        )

    else:

        canvas.delete("pause")

        next_turn(snake)


# ============================================================
# START GAME
# ============================================================

def start_game():

    global SPEED
    global direction

    level = difficulty_var.get()

    # Set difficulty
    if level == "Easy":

        SPEED = 180

    elif level == "Medium":

        SPEED = 120

    else:

        SPEED = 80

    # Reset direction
    direction = "down"

    # Remove menu
    menu_frame.destroy()

    # Start game
    restart_game()


# ============================================================
# RESTART GAME
# ============================================================

def restart_game(event=None):

    global snake
    global food
    global score
    global SPEED
    global paused
    global obstacles
    global game_loop
    global direction

    # --------------------------------------------------------
    # CANCEL OLD GAME LOOP
    # --------------------------------------------------------

    if game_loop is not None:

        try:
            window.after_cancel(game_loop)

        except tk.TclError:
            pass

        game_loop = None


    # --------------------------------------------------------
    # RESET GAME
    # --------------------------------------------------------

    canvas.delete(tk.ALL)

    score = 0
    paused = False

    # Reset direction
    direction = "down"

    # Keep selected difficulty
    level = difficulty_var.get()

    if level == "Easy":

        SPEED = 180

    elif level == "Medium":

        SPEED = 120

    else:

        SPEED = 80


    label.config(
        text=f"Score: {score}   High Score: {high_score}"
    )


    # --------------------------------------------------------
    # CREATE SNAKE FIRST
    # --------------------------------------------------------

    snake = Snake()


    # --------------------------------------------------------
    # CREATE OBSTACLES
    # --------------------------------------------------------

    create_obstacles()


    # --------------------------------------------------------
    # CREATE FOOD LAST
    # --------------------------------------------------------

    food = Food()


    # --------------------------------------------------------
    # START GAME LOOP
    # --------------------------------------------------------

    next_turn(snake)


# ============================================================
# KEYBOARD CONTROLS
# ============================================================

window.bind(
    "<Left>",
    lambda event: change_direction("left")
)

window.bind(
    "<Right>",
    lambda event: change_direction("right")
)

window.bind(
    "<Up>",
    lambda event: change_direction("up")
)

window.bind(
    "<Down>",
    lambda event: change_direction("down")
)

# P = Pause / Resume
window.bind("p", toggle_pause)

# R = Restart
window.bind("r", restart_game)


# ============================================================
# START MENU
# ============================================================

difficulty = "Medium"

menu_frame = tk.Frame(
    window,
    bg="black"
)

menu_frame.place(
    relx=0.5,
    rely=0.5,
    anchor="center"
)


# Title
title = tk.Label(
    menu_frame,
    text="SNAKE GAME",
    font=("Arial", 32, "bold"),
    fg="lime",
    bg="black"
)

title.pack(pady=20)


# Difficulty label
difficulty_label = tk.Label(
    menu_frame,
    text="Select Difficulty",
    font=("Arial", 18),
    fg="white",
    bg="black"
)

difficulty_label.pack(pady=10)


# Difficulty variable
difficulty_var = tk.StringVar(
    value="Medium"
)


# Easy
tk.Radiobutton(
    menu_frame,
    text="Easy",
    variable=difficulty_var,
    value="Easy",
    font=("Arial", 14),
    bg="black",
    fg="white",
    selectcolor="black",
    activebackground="black",
    activeforeground="white"
).pack()


# Medium
tk.Radiobutton(
    menu_frame,
    text="Medium",
    variable=difficulty_var,
    value="Medium",
    font=("Arial", 14),
    bg="black",
    fg="white",
    selectcolor="black",
    activebackground="black",
    activeforeground="white"
).pack()


# Hard
tk.Radiobutton(
    menu_frame,
    text="Hard",
    variable=difficulty_var,
    value="Hard",
    font=("Arial", 14),
    bg="black",
    fg="white",
    selectcolor="black",
    activebackground="black",
    activeforeground="white"
).pack()


# Start button
start_btn = tk.Button(
    menu_frame,
    text="Start Game",
    font=("Arial", 16, "bold"),
    command=start_game
)

start_btn.pack(pady=15)


# Exit button
exit_btn = tk.Button(
    menu_frame,
    text="Exit",
    font=("Arial", 16),
    command=window.destroy
)

exit_btn.pack()


# ============================================================
# START WINDOW
# ============================================================

window.mainloop()