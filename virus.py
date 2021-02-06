import random
import time
import copy
import pygame
import numpy as np

pygame.init()

#fonts
def_font = pygame.font.SysFont("verdana", 24)
small_font = pygame.font.SysFont("verdana", 16)

#colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
ORANGE = (255,150,0)

#screen size
screen_height = 800
screen_width = 1400

# sizes
tile_size = 7

screen = pygame.display.set_mode((screen_width, screen_height))

# generate a 2d array of people 5x5
#population = [[0 for n in range(100)] for x in range(100)]
population = np.zeros((100,100))

# generate a 2d array for storing recovery time for infected
population_recovery = np.zeros((100,100))

# status of people
status = [0,1,2,3,4]
status[0] = "healthy"
status[1] = "immune"
status[2] = "ill"
status[3] = "dead"
status[4] = "quarantine"

infected_people = 0
immune_people = 0
healthy_people = 0
dead_people = 0
quarantine_people = 0
max_infected = 0
amount_infected_per_day = 0
people_in_quarantine = 0

days = 0

# probabilities and constants
prob_death = 0.01
prob_death_quarantine = 0.001
prob_recover = 0.1
contagiousness = 0.05
quarantine_chance = 0.3
recovery_time = 10
quarantine_size = 300
contacts_amount = 8
initially_infected = 2
initially_immune = 0.1

# randomly infect several people in population
for k in range(initially_infected):
    y = random.randint(0, len(population)-1)
    x = random.randint(0, len(population)-1)
    population[y][x] = 2
    population_recovery[y][x] = recovery_time

# randomly immunize people in population
k = int(round(len(population)*len(population) * initially_immune))
j = 0
while j < k:
    y = random.randint(0, len(population)-1)
    x = random.randint(0, len(population)-1)
    if population[y][x] != 1 and population[y][x] != 2:
        population[y][x] = 1
        print(j)
        j += 1

# calculate the probability to get sick using only close neighbors
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

# calculate probability to get sick using number of contacts a person has
# take into consideration 70% of close contacts and 30% of random contacts
def get_sick_prob_mod(y, x):
    close_contacts = int(round(contacts_amount * 0.7))
    random_contacts = contacts_amount - close_contacts
    # first count the amount of infected in close contacts range
    close_contacts_list = []

    infected_contacts = 0
    for y1 in range(y-1, y+2):
        for x1 in range(x-1, x+2):
            if x1 == x and y1 == y:
                continue
            if y1 < 0 or x1 < 0:
                continue
            try:
                close_contacts_list.append(population[y1][x1])
            except IndexError:
                continue
    if len(close_contacts_list) <= close_contacts:
        for i in range(len(close_contacts_list)):
            if close_contacts_list[i] == 2:
                infected_contacts += 1
    else:
        todays_contacts = random.sample(close_contacts_list, close_contacts)
        for i in range(close_contacts):
            if todays_contacts[i] == 2:
                infected_contacts += 1

    #count infected contacts in distant range (randomly pick people from population)
    for i in range(random_contacts):
        contact = population[random.randint(0, len(population)-1)][random.randint(0, len(population)-1)]
        if contact == 2:
            infected_contacts += 1
        elif contact == 3:
            i -= 1

    #count the probability for this person to get sick
    prob_to_get_sick_mod = 1 - (1-contagiousness) ** infected_contacts

    return prob_to_get_sick_mod
                
# this function draws GUI which chows current statistics
def draw_ui(name, value, indent):
    text = def_font.render(name, False, WHITE)
    text_rect = text.get_rect()
    text_rect.move_ip(850, 60 + indent)
    screen.blit(text, text_rect)
    text_value = def_font.render(value, False, WHITE)
    text_value_rect = text_value.get_rect()
    text_value_rect.move_ip(text_rect.right + 10, text_rect.top)
    screen.blit(text_value, text_value_rect)

def draw_chart():

    chart_immune = small_font.render("Share of immune", False, WHITE)
    chart_immune_rect = chart_immune.get_rect()
    chart_immune_rect.move_ip(850, 300)
    screen.blit(chart_immune, chart_immune_rect)
    chart_area = pygame.Rect(chart_immune_rect.left, chart_immune_rect.bottom+5, 300, 100)
    if days <= 1:
        pygame.draw.rect(screen, WHITE, chart_area)
    chart_infected = small_font.render("Share of infected", False, WHITE)
    chart_infected_rect = chart_infected.get_rect()
    chart_infected_rect.move_ip(chart_area.left, chart_area.bottom+5)
    screen.blit(chart_infected, chart_infected_rect)

    #draw a line of infected
    share_of_infected = int(round((infected_people / 10000) * 100))
    infected_dot = pygame.Rect(chart_area.left + days, chart_area.bottom - share_of_infected, 1,1)
    pygame.draw.rect(screen, BLACK, infected_dot)

    #draw a line for immune
    share_of_immune = int(round((immune_people / 10000) * 100))
    immune_dot = pygame.Rect(chart_area.left + days, chart_area.top + share_of_immune, 1,1)
    pygame.draw.rect(screen, BLACK, immune_dot)

simulating = False
running = True
while running:
    #quit when user hits x button
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BLACK,(850, 60, 300, 250))

    #draw an array of people
    for y in range(len(population)):
        for x in range(len(population)):
            rect = pygame.Rect(y*tile_size+y*1, x*tile_size+x*1, tile_size, tile_size)
            if population[y][x] == 0:
                pygame.draw.rect(screen, WHITE, rect, 0)
            elif population[y][x] == 1:
                pygame.draw.rect(screen, GREEN, rect, 0)
            elif population[y][x] == 2:
                pygame.draw.rect(screen, RED, rect, 0)
            elif population[y][x] == 3:
                pygame.draw.rect(screen, BLUE, rect, 0)
            elif population[y][x] == 4:
                pygame.draw.rect(screen, ORANGE, rect, 0)

    #count the amount of sick, healthy, immune and dead
    # if amount of infected is 0 stop simulation
    infected_bool = False
    (status, counts) = np.unique(population, return_counts = True)
    people_status = np.asarray((status, counts)).T
    for i in range(len(people_status)):
        if people_status[i][0] == 0:
            healthy_people = people_status[i][1]
        elif people_status[i][0] == 1:
            immune_people = people_status[i][1]
        elif people_status[i][0] == 2:
            infected_people = people_status[i][1]
            infected_bool = True
        elif people_status[i][0] == 3:
            dead_people = people_status[i][1]
        elif people_status[i][0] == 4:
            quarantine_people = people_status[i][1]
    
    if infected_bool == False:
        simulating = False
    
    # if there is no infected you should manualy set this
    if infected_bool == False:
        infected_people = 0
        
    
    #draw UI
    #name of project
    rect = pygame.Rect(850, 20, 50, 100)
    program_name = def_font.render("DISEASE SIMULATION", False, WHITE)
    screen.blit(program_name, rect)
    
    #number of infected
    draw_ui("Infected:", str(int(infected_people)), 0) 
    #number of quarantined
    draw_ui("Quarantine:", str(int(quarantine_people)), 40)
    #number of immune
    draw_ui("Immune:", str(int(immune_people)), 80)
    #number of dead
    draw_ui("Dead:", str(int(dead_people)), 120)
    #number of healthy
    draw_ui("Healthy:", str(int(healthy_people)), 160)
    #number of days passed
    draw_ui("Days:", str(days), 200)

    #CHART
    draw_chart()
    
    #control buttons
    #start
    start_button = pygame.Rect(850, 470, 150, 30)
    start_button_text = small_font.render("START", False, BLACK)
    start_button_text_rect = start_button_text.get_rect()
    start_button_text_rect.center = start_button.center
    pygame.draw.rect(screen, WHITE, start_button)
    screen.blit(start_button_text, start_button_text_rect)

    #stop
    stop_button = pygame.Rect(start_button.right + 20, 470, 150, 30)
    stop_button_text = small_font.render("STOP", False, BLACK)
    stop_button_text_rect = stop_button_text.get_rect()
    stop_button_text_rect.center = stop_button.center
    pygame.draw.rect(screen, WHITE, stop_button)
    screen.blit(stop_button_text, stop_button_text_rect)

    #restart
    restart_button = pygame.Rect(stop_button.right + 20, 470, 150, 30)
    restart_button_text = small_font.render("RESTART", False, BLACK)
    restart_button_text_rect = restart_button_text.get_rect()
    restart_button_text_rect.center = restart_button.center
    pygame.draw.rect(screen, WHITE, restart_button)
    screen.blit(restart_button_text, restart_button_text_rect)

    # statistics
    screen.fill(BLACK, (start_button.left, start_button.bottom + 5, 400, 300))
    # maximum amount of infected
    # calculate the amount
    if max_infected < infected_people:
        max_infected = infected_people
    # draw the data
    draw_ui("MAX infected:", str(int(max_infected)), 450)
   

    # average amount of infected
    #calculate the amount
    average_amount = (infected_people+dead_people+immune_people+quarantine_people) / days
    # draw the data
    draw_ui("AVERAGE infected per day:", str(round(average_amount, 2)), 490)

    # Infected per day
    draw_ui("Infected per day:", str(amount_infected_per_day), 530)

    # R(0) - average amount of people that one infected infects
    # calculate r(0)
    if infected_people > 0:
        r0_value_data = round(amount_infected_per_day / (infected_people - amount_infected_per_day), 2)
    # draw data
    draw_ui("R(0):", str(r0_value_data), 570)
    amount_infected_per_day = 0

    #check whether buttons were clicked
    click, _, _ = pygame.mouse.get_pressed()
    if click == True:
        mouse = pygame.mouse.get_pos()
        if start_button.collidepoint(mouse):
            simulating = True
        elif stop_button.collidepoint(mouse):
            simulating = False
        elif restart_button.collidepoint(mouse):
            population = np.zeros((100,100))
            tmp_population = copy.deepcopy(population)
            days = 0
            # randomly infect several people in the population
            for k in range(initially_infected):
                y = random.randint(0, len(population)-1)
                x = random.randint(0, len(population)-1)
                population[y][x] = 2
                population_recovery[y][x] = recovery_time




    if simulating:
        # calculate new state
        tmp_population = copy.deepcopy(population)

        for y in range(len(population)):
            for x in range(len(population)):
                # calculate new sicknesses for healthy people
                if population[y][x] == 0:
                    is_sick = get_sick_prob_mod(y,x)
                    # using this probability randomly choose whether person gets sick or not
                    tmp_population[y][x] = random.choices([0, 2], weights=(1-is_sick, is_sick), k=1)[0]
                    if tmp_population[y][x] == 2:
                        population_recovery[y][x] = recovery_time
                        amount_infected_per_day += 1
                # calculate new recoveries or deaths or quarantine for infected
                elif population[y][x] == 2:
                    #tmp_population[y][x] = random.choices([1,3,2], weights=(prob_recover, prob_death, 1-prob_recover-prob_death), k=1)[0]
                    tmp_population[y][x] = random.choices([2,3], weights=(1-prob_death, prob_death), k=1)[0]
                    if population_recovery[y][x] <= 0:
                        tmp_population[y][x] = 1
                    if people_in_quarantine < quarantine_size:
                        if tmp_population[y][x] == 2:
                            tmp_population[y][x] = random.choices([2,4], weights=(1-quarantine_chance, quarantine_chance), k=1)[0]
                            if tmp_population[y][x] == 4:
                                people_in_quarantine += 1
                # calculate new recoveries or deaths for quarantined
                elif population[y][x] == 4:
                    if population_recovery[y][x] <= 0:
                        tmp_population[y][x] = 1
                    else:
                        tmp_population[y][x] = random.choices([4,3], weights=(1-prob_death_quarantine, prob_death_quarantine), k=1)[0]
                    if tmp_population[y][x] == 3 or tmp_population[y][x] == 1:
                        people_in_quarantine -= 1
        population = copy.deepcopy(tmp_population)
        #remove 1 day from recovery table
        population_recovery = population_recovery - 1
        
        #add new day at the end of the cycle
        days += 1
        

    pygame.display.flip()
    #time.sleep(0.1)


            



