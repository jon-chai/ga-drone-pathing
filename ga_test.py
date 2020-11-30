import numpy
import random

class Drone:

    genes = {'Velocity':(1, 10), 'Reaction Dist':(1, 5)}

    def __init__(self, vel, reac, score = 0):
        self.velo = vel
        self.reac = reac
        self.x = 0
        self.score = score
        self.done = False
        self.genome = [vel, reac]

    def __str__(self):
        return 'Velo: ' + str(self.velo) + ', Reac: ' + str(self.reac) \
        + ', Score: ' + str(self.score) + ', X: ' + str(self.x) + ', Genome: ' \
        + str(self.genome) + ', Done: ' + str(self.done)

    def setGenome(self, genome):
        self.genome = genome
        self.velo = genome[0]
        self.reac = genome[1]

    def setGene(self, gene, value):
        tempgenome = self.genome
        tempgenome[gene] = value
        self.setGenome(tempgenome)

    def resetDrone(self):
        self.score = 0
        self.done = False
        self.x = 0


class Simul:

    distance = 50

    def __init__(self, size = 8, rand = True, num_gen = 5):
        self.pop_size = size
        if rand:
            self.population = []
            for i in range(8):
                self.population.append(Drone(random.randint(1, 10), random.randint(1, 5)))
        self.num_gen = 0
        self.max_gen = num_gen

    def __str__(self):
        result = 'Generation: ' + str(self.num_gen) + '\n'
        for x in self.population:
            result = result + str(x) + '\n'
        return result

    def runSim(self):
        countdown = 200
        drones_done = 0
        while countdown > 0 and drones_done < self.pop_size:
            for drone in self.population:
                if not drone.done:
                    drone.x += drone.velo
                    drone.score += 1
                    if drone.x >= Simul.distance:
                        drones_done += 1
                        drone.done = True
            countdown -= 1
        if countdown == 0:
            print('Max Time Reached')


    def nextgen(self):
        return 0

    def popFitness(self):
        result = []
        for drone in self.population:
            result.append(drone.score)
        return result

    def selectMatingPool(self, num_parents):
        pool = []
        drone_dict = {}
        for drone in range(len(self.population)):
            drone_dict[self.population[drone]] = drone
        for i in range(num_parents):
            if i == 0:
                pool.append(self.popMostFit(drone_dict))
            else:
                pool.append(self.popMostFit(drone_dict, self.population[pool[i - 1]].score))
        return pool

    def popMostFit(self, drone_dict, min_fitness = float('inf')):
        minsofar = float('inf')
        dontcross = min_fitness
        if min_fitness == float('inf'): #Want absolute min
            dontcross = float('-inf')
        mostfit = None
        for drone in drone_dict:
            if drone.score < minsofar and drone.score >= dontcross:
                minsofar = drone.score
                mostfit = drone
        return drone_dict.pop(mostfit)

    def crossoverP(self, num_offspring, parent_pool):
        crossover_point = len(Drone.genes)//2
        result = []
        for i in range(num_offspring):
            parent1 = i % len(parent_pool)
            parent2 = (i + 1) % len(parent_pool)
            child = Drone(random.randint(1, 10), random.randint(1, 5))
            child.setGenome(self.population[parent_pool[parent1]].genome[:crossover_point] + \
            self.population[parent_pool[parent2]].genome[crossover_point:])
            result.append(child)
        return result

    def mutation(self, offspring):
        for child in offspring:
            random_gene = random.randint(0, len(Drone.genes) - 1)
            # May want to port this to helper function when more genes added
            if random_gene == 0: # Velocity
                child.setGene(random_gene, random.randint(1, 10))
            elif random_gene == 1: # Reaction
                child.setGene(random_gene, random.randint(1, 5))
        return offspring

    def getParents(self, parent_pool):
        result = []
        for i in parent_pool:
            result.append(self.population[i])
        return result

    def nextgen(self, offspring, parents):
        self.population = parents + offspring
        self.resetDrones()
        self.num_gen += 1

    def resetDrones(self):
        for drone in self.population:
            drone.resetDrone()

    def printList(self, drone_list):
        for drone in drone_list:
            print(drone)



print('Running Simulation')
sim1 = Simul()
while sim1.num_gen < sim1.max_gen:
    print(sim1)
    sim1.runSim()
    print(sim1.popFitness())
    parent_pool = sim1.selectMatingPool(4)
    print(parent_pool)
    offspring = sim1.crossoverP(4, parent_pool)
    sim1.printList(offspring)
    print()
    offspringM = sim1.mutation(offspring)
    sim1.printList(offspringM)
    sim1.nextgen(offspringM, sim1.getParents(parent_pool))
print('End Simulation')
print('Best drones: ')
sim1.printList(sim1.getParents(parent_pool))
print('Done!')
