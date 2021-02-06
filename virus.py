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

# probabilities
prob_death = 0.01
prob_death_quarantine = 0.001
prob_recover = 0.1
contagiousness = 0.05
quarantine_chance = 0
recovery_time = 10
quarantine_size = 300
contacts_amount = 8

# randomly infect several people in population
i = random.randint(1,2) # number of infected

for k in range(i):
    y = random.randint(0, len(population)-1)
    x = random.randint(0, len(population)-1)

    population[y][x] = 2
    population_recovery[y][x] = recovery_time

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
    infected_num_text = def_font.render("Infected:", False, WHITE)
    infected_num_text_rect = infected_num_text.get_rect()
    infected_num_text_rect.move_ip(850,60)
    screen.blit(infected_num_text, infected_num_text_rect)
    infected_num = def_font.render(str(int(infected_people)), False, WHITE)
    infected_num_rect = infected_num.get_rect()
    infected_num_rect.move_ip(infected_num_text_rect.right + 10, infected_num_text_rect.top)
    screen.blit(infected_num, infected_num_rect)

    #number of quarantined
    quarantine_num_text = def_font.render("Quarantine:", False, WHITE)
    quarantine_num_text_rect = quarantine_num_text.get_rect()
    quarantine_num_text_rect.move_ip(infected_num_text_rect.left, infected_num_rect.bottom+10)
    screen.blit(quarantine_num_text, quarantine_num_text_rect)
    quarantine_num = def_font.render(str(int(quarantine_people)), False, WHITE)
    quarantine_num_rect = quarantine_num.get_rect()
    quarantine_num_rect.move_ip(quarantine_num_text_rect.right + 10, quarantine_num_text_rect.top)
    screen.blit(quarantine_num, quarantine_num_rect)

    #number of immune
    immune_num_text = def_font.render("Immune:", False, WHITE)
    immune_num_text_rect = immune_num_text.get_rect()
    immune_num_text_rect.move_ip(quarantine_num_text_rect.left, quarantine_num_rect.bottom+10)
    screen.blit(immune_num_text, immune_num_text_rect)
    immune_num = def_font.render(str(int(immune_people)), False, WHITE)
    immune_num_rect = immune_num.get_rect()
    immune_num_rect.move_ip(immune_num_text_rect.right + 10, immune_num_text_rect.top)
    screen.blit(immune_num, immune_num_rect)

    #number of dead
    dead_num_text = def_font.render("Dead:", False, WHITE)
    dead_num_text_rect = dead_num_text.get_rect()
    dead_num_text_rect.move_ip(immune_num_text_rect.left, immune_num_rect.bottom+10)
    screen.blit(dead_num_text, dead_num_text_rect)
    dead_num = def_font.render(str(int(dead_people)), False, WHITE)
    dead_num_rect = dead_num.get_rect()
    dead_num_rect.move_ip(dead_num_text_rect.right + 10, dead_num_text_rect.top)
    screen.blit(dead_num, dead_num_rect)

    #number of healthy
    healthy_num_text = def_font.render("Healthy:", False, WHITE)
    healthy_num_text_rect = healthy_num_text.get_rect()
    healthy_num_text_rect.move_ip(dead_num_text_rect.left, dead_num_rect.bottom+10)
    screen.blit(healthy_num_text, healthy_num_text_rect)
    healthy_num = def_font.render(str(int(healthy_people)), False, WHITE)
    healthy_num_rect = healthy_num.get_rect()
    healthy_num_rect.move_ip(healthy_num_text_rect.right + 10, healthy_num_text_rect.top)
    screen.blit(healthy_num, healthy_num_rect)

    #number of days passed
    days_num_text = def_font.render("Days:", False, WHITE)
    days_num_text_rect = days_num_text.get_rect()
    days_num_text_rect.move_ip(healthy_num_text_rect.left, healthy_num_rect.bottom+10)
    screen.blit(days_num_text, days_num_text_rect)
    days_num = def_font.render(str(days), False, WHITE)
    days_num_rect = days_num.get_rect()
    days_num_rect.move_ip(days_num_text_rect.right + 10, days_num_text_rect.top)
    screen.blit(days_num, days_num_rect)

    #CHART
    # draw an area for future chart
    if days <= 1:
        chart_immune = small_font.render("Share of immune", False, WHITE)
        chart_immune_rect = chart_immune.get_rect()
        chart_immune_rect.move_ip(days_num_text_rect.left, days_num_text_rect.bottom+15)
        screen.blit(chart_immune, chart_immune_rect)
        chart_area = pygame.Rect(chart_immune_rect.left, chart_immune_rect.bottom+5, 300, 100)
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

    #control buttons
    #start
    start_button = pygame.Rect(chart_area.left, chart_area.bottom+30, 150, 30)
    start_button_text = small_font.render("START", False, BLACK)
    start_button_text_rect = start_button_text.get_rect()
    start_button_text_rect.center = start_button.center
    pygame.draw.rect(screen, WHITE, start_button)
    screen.blit(start_button_text, start_button_text_rect)

    #stop
    stop_button = pygame.Rect(start_button.right + 20, chart_area.bottom+30, 150, 30)
    stop_button_text = small_font.render("STOP", False, BLACK)
    stop_button_text_rect = stop_button_text.get_rect()
    stop_button_text_rect.center = stop_button.center
    pygame.draw.rect(screen, WHITE, stop_button)
    screen.blit(stop_button_text, stop_button_text_rect)

    #restart
    restart_button = pygame.Rect(stop_button.right + 20, chart_area.bottom+30, 150, 30)
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
    max_num_of_infected = def_font.render("MAX infected:", False, WHITE)
    max_num_of_infected_rect = max_num_of_infected.get_rect()
    max_num_of_infected_rect.move_ip(start_button.left, start_button.bottom+10)
    screen.blit(max_num_of_infected, max_num_of_infected_rect)
    amount_value = def_font.render(str(int(max_infected)), False, WHITE)
    amount_value_rect = amount_value.get_rect()
    amount_value_rect.move_ip(max_num_of_infected_rect.right + 10, max_num_of_infected_rect.top)
    screen.blit(amount_value, amount_value_rect)

    # average amount of infected
    #calculate the amount
    average_amount = (infected_people+dead_people+immune_people+quarantine_people) / days
    # draw the data
    average_num_of_infected = def_font.render("AVERAGE infected per day:", False, WHITE)
    average_num_of_infected_rect = average_num_of_infected.get_rect()
    average_num_of_infected_rect.move_ip(max_num_of_infected_rect.left, max_num_of_infected_rect.bottom+10)
    screen.blit(average_num_of_infected, average_num_of_infected_rect)
    average_amount_value = def_font.render(str(round(average_amount, 2)), False, WHITE)
    average_amount_value_rect = average_amount_value.get_rect()
    average_amount_value_rect.move_ip(average_num_of_infected_rect.right + 10, average_num_of_infected_rect.top)
    screen.blit(average_amount_value, average_amount_value_rect)

    # Infected per day
    infected_per_day = def_font.render("Infected per day:", False, WHITE)
    infected_per_day_rect = infected_per_day.get_rect()
    infected_per_day_rect.move_ip(average_num_of_infected_rect.left, average_num_of_infected_rect.bottom+10)
    screen.blit(infected_per_day, infected_per_day_rect)
    infected_per_day_value = def_font.render(str(amount_infected_per_day), False, WHITE)
    infected_per_day_value_rect = infected_per_day_value.get_rect()
    infected_per_day_value_rect.move_ip(infected_per_day_rect.right + 10, infected_per_day_rect.top)
    screen.blit(infected_per_day_value, infected_per_day_value_rect)

    # R(0) - average amount of people that one infected infects
    # calculate r(0)
    if infected_people > 0:
        r0_value_data = round(amount_infected_per_day / (infected_people - amount_infected_per_day), 2)
    # draw data
    r0 = def_font.render("R(0):", False, WHITE)
    r0_rect = r0.get_rect()
    r0_rect.move_ip(infected_per_day_rect.left, infected_per_day_rect.bottom+10)
    screen.blit(r0, r0_rect)
    r0_value = def_font.render(str(r0_value_data), False, WHITE)
    r0_value_rect = r0_value.get_rect()
    r0_value_rect.move_ip(r0_rect.right + 10, r0_rect.top)
    screen.blit(r0_value, r0_value_rect)
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
            i = random.randint(1,2) # number of infected
            for k in range(i):
                population[random.randint(0, len(population)-1)][random.randint(0,len(population)-1)] = 2




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

        #if disease spread is over - stop simulation
        

    pygame.display.flip()
    #time.sleep(0.1)


            



