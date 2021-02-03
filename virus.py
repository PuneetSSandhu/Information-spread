import random
import time
import copy
import pygame

pygame.init()

#colors
WHITE = (255,255,255)
BLACK = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

#screen size
screen_height = 770
screen_width = 770

# sizes
tile_size = 10

screen = pygame.display.set_mode((screen_width, screen_height))

# generate a 2d array of people 5x5
population = [[0 for n in range(70)] for x in range(70)]

# status of people
status = [0,1,2,3]
status[0] = "healthy"
status[1] = "immune"
status[2] = "ill"
status[3] = "dead"

# probabilities
prob_death = 0.1
prob_recover = 0.3
contagiousness = 0.05

# randomly infect several people in population
i = random.randint(1,15) # number of infected

for k in range(i):
    population[random.randint(0, len(population)-1)][random.randint(0,len(population)-1)] = 2

# calculate the probability to get sick
def get_sick_prob(y, x):
    #find contacts of a person: cells in array that are close close to this person
    contacts = 0
    for y1 in range(y-1, y+2):
        for x1 in range(x-1, x+2):
            if x1 == x and y1 == y:
                continue
            if y1 < 0 or x1 < 0:
                continue
            try:
                if population[y1][x1] == 2:
                    contacts += 1
                # if a neighbor is dead count take a random person from population into consideration
                elif population[y1][x1] == 3:
                    if population[random.randint(0, len(population))][random.randint(0, len(population))] == 2:
                        contacts += 1
            except IndexError:
                    continue

    # calculate probability (1-cont) is probability not to get sick         
    prob_to_get_sick = 1 - (1-contagiousness) ** contacts
    
    return prob_to_get_sick

running = True
while running:
    #draw array of people
    for y in range(len(population)):
        for x in range(len(population)):
            rect = pygame.Rect(y*tile_size+y*1, x*tile_size+x*1, tile_size, tile_size)
            if population[y][x] == 0:
                pygame.draw.rect(screen, WHITE, rect, 0)
            elif population[y][x] == 1:
                pygame.draw.rect(screen, GREEN, rect, 0)
            elif population[y][x] == 2:
                pygame.draw.rect(screen, RED, rect, 0)
            else:
                pygame.draw.rect(screen, BLUE, rect, 0)

    # calculate new state
    tmp_population = copy.deepcopy(population)

    for y in range(len(population)):
        for x in range(len(population)):
            # calculate new sicknesses for healthy people
            if population[y][x] == 0:
                is_sick = get_sick_prob(y,x)
                # using this probability randomly choose whether person gets sick or not
                tmp_population[y][x] = random.choices([0, 2], weights=(1-is_sick, is_sick), k=1)[0]
            # calculate new recoveries or deaths
            elif population[y][x] == 2:
                tmp_population[y][x] = random.choices([1,3,2], weights=(prob_recover, prob_death, 1-prob_recover-prob_death), k=1)[0]

    population = copy.deepcopy(tmp_population)
    pygame.display.flip()
    time.sleep(0.1)


            



