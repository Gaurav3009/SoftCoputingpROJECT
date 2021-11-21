import pygame
import random
import math
import numpy as np
from pygame import mixer

x = np.array(([723, 123.4000000000003], [121, 133.40000000000038], [586, 125.40000000000032]), dtype=float )
y = np.array(([99], [86], [89]), dtype=float )

# Scaled Units
x = x / np.amax ( x, axis=0 )
y = y / 100


# maximum value

class NeuralNetwork:
    def __init__(self):
        self.input_size = 2
        self.output_size = 1
        self.hidden_size = 3

        # Heights

        self.w1 = np.random.randn(self.input_size, self.hidden_size)
        self.w2 = np.random.randn(self.hidden_size, self.output_size)

    def feed_forward(self, x):
        # forward propagation to the network
        self.z = np.dot(x, self.w1)
        self.z2 = self.sigmoid(self.z)
        self.z3 = np.dot(self.z2, self.w2)
        output = self.sigmoid(self.z3)
        return output


    def sigmoid(self, s, deriv = False):
        if deriv:
            return s*(1-s)
        return 1/(1+np.exp(-s))

    def backward(self, x, y, output):
        # Backward propagation through the network
        self.output_error = y - output
        self.output_delta = self.output_error * self.sigmoid(output, deriv = True)

        self.z2_error = self.output_delta.dot(self.w2.T)
        self.z2_delta = self.z2_error * self.sigmoid(self.z2, deriv = True)

        # Weight updation
        self.w1 += x.T.dot(self.z2_delta)
        self.w2 += self.z2.T.dot(self.output_delta)

    def train(self, x, y):
        output = self.feed_forward(x)
        self.backward(x, y, output)


NN = NeuralNetwork()
for i in range(500000):
    NN.train(x, y)

print("Predicted Output : " + str(NN.feed_forward(x)))


# Initialize the pygame
pygame.init()

# create the screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load("bg.png")

# Background Sound
mixer.music.load("DeathMatch.ogg")
mixer.music.play(-1)

# Title and the Icon of the game
pygame.display.set_caption("Space Shooter")
icon = pygame.image.load("ufoBlue.png")
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load("player.png")
X = 370
Y = 480
player_speed = 2
clock = pygame.time.Clock()

# Enemy
enemyImg = []
enemyX = []
enemyY = []
num_of_enemies = 3
enemy_speed = 1

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load("alien.png"))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(0, 20))

# Bullets
bullets = pygame.image.load("bullet_pl.png")
bulletX = 0
bulletY = 480
bullet_state = "ready"
bullet_x_change = 0
bullet_y_change = 8

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
textY = 10


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 0, 0))
    screen.blit(score, (x, y))


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bullets, (x+18.8, y-5))


def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt(math.pow((enemy_x - bullet_x), 2) + math.pow((enemy_y - bullet_y), 2))
    if distance < 27:
        return True
    else:
        return False


# Game Loop
def run_game():
    global playerImg
    global player_speed
    global bulletX
    global bulletY
    global score_value
    global bullet_state
    global X, Y
    global enemyX, enemyY
    left_move = False
    right_move = False
    blast = False
    action = True

    running = True
    while running:
        # RGB value
        screen.fill((0, 0, 0))
        # Background Image
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Left and Right movement of the player

            if event.type == pygame.KEYUP:
                player_speed = 0

        # For updating the changes made
        X = X + player_speed
        # Setting Boundaries in our game window
        if X <= 0:
            X = 0
        elif X >= 736:
            X = 736
        player(X, Y)
        # Enemy Movement
        for i in range(num_of_enemies):
            enemyY[i] = enemyY[i] + enemy_speed
            if enemyY[i] >= 600:
                enemyX[i] = random.randint(0, 736)
                enemyY[i] = random.randint(0, 50)
                score_value -= 1
            enemy(enemyX[i], enemyY[i], i)

            # Collision
            collision = is_collision(enemyX[i], enemyY[i], bulletX, bulletY )
            if collision:
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                print(score_value)
                enemyX[i] = random.randint(0, 736)
                enemyY[i] = random.randint(0, 50)

        x1 = ([enemyX[0], enemyY[0]], [enemyX[1], enemyY[1]], [enemyX[2], enemyY[2]])
        y1 = NN.feed_forward ( x1 )
        max_value_index = 0
        max_value = -1
        a = 0
        for i in y1 :
            if i > max_value :
                max_value = i
                max_value_index = a
            a += 1
        if X < enemyX[max_value_index]:
            while X < enemyX[max_value_index]:
                X = X + player_speed
        elif X > enemyX[max_value_index]:
            while X > enemyX[max_value_index]:
                X = X - player_speed
        blast = True
        if action :
            if left_move :
                player_speed = -4
            if right_move :
                player_speed = 4
            if blast :
                bulletX = X
                bullet_sound = mixer.Sound ( "laser5.wav" )
                bullet_sound.play ( )
                bullet ( X, bulletY )
                blast = False

        # BulletMovement
        if bulletY <= 0:
            bullet_state = "ready"
            bulletX = 0
            bulletY = 480
        if bullet_state is "fire":
            bullet(bulletX, bulletY)
            bulletY -= bullet_y_change
        show_score(textX, textY)
        pygame.display.update()
        clock.tick(90)

run_game()
