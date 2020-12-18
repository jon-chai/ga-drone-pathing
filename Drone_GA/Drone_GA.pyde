import random as rand

class Vehicle:
        
    mr = 0.1
    # Food weight, Poison weight, Food percep, Poison percep, FOV, Drone weight, Drone percep, Max acceleration
    feature_creation = [lambda x: random(0, 5), lambda x:random(-5, 0), lambda x:random(20, 100), 
                        lambda x:random(20, 100), lambda x:random(PI/6, PI/2), lambda x:random(-5, 0),
                        lambda x:random(20, 100), lambda x:random(0.1, 2)]
    
    feature_limits = [(0, 5), (-5, 0), (20, 100), (20, 100), (PI/6, PI/2), (-5, 0), (20, 100), (0.1, 2)]
    
    def __init__(self, x=None, y=None, dna=None):
        
        if x is None:
            x = random(width)
        if y is None:
            y = random(height)
        
        self.position = PVector(x, y)
        self.velocity = PVector(0, -2)
        self.acceleration = PVector(0, 0)
        
        self.r = 4
        self.maxspeed = 5
        self.maxforce = 0.5
        
        self.points = 0
        self.alive = True
                
        if dna is None:
            self.dna = [feature(0) for feature in self.feature_creation]
        else:
            self.dna = dna[:]
    
    def update(self):
        # self.points += 0.01
        self.acceleration.limit(self.dna[7])
        self.velocity.add(self.acceleration)
        self.velocity.limit(self.maxspeed)
        self.position.add(self.velocity)
        self.acceleration.mult(0)
    
    def applyForce(self, force):
        self.acceleration.add(force)
    
    def seek(self, target):
        desired = PVector.sub(target, self.position)
        
        desired.setMag(self.maxspeed)
        
        steer = PVector.sub(desired, self.velocity)
        steer.limit(self.maxforce)
        return steer
    
    def behaviors(self, good, bad, drones, idx):
                
        steerG = self.eat(good, 1, self.dna[2])
        steerB = self.eat(bad, -1, self.dna[3])
        steerD = self.crash(drones, idx, self.dna[6])
        
        steerG.mult(self.dna[0])
        steerB.mult(self.dna[1])
        steerD.mult(self.dna[5])

        self.applyForce(steerG)
        self.applyForce(steerB)
        self.applyForce(steerD)
    
    def mutate(self):
        for idx, gene in enumerate(self.dna):
            if random(1) < self.mr:
                self.dna[idx] = self.feature_creation[idx](0)
    
    def bounded_mutation(self):
        for idx, gene in enumerate(self.dna):
            if random(1) < self.mr:
                self.dna[idx] *= random(0.8, 1.2)
                if self.dna[idx] < self.feature_limits[idx][0]:
                    self.dna[idx] = self.feature_limits[idx][0]
                elif self.dna[idx] > self.feature_limits[idx][1]:
                    self.dna[idx] = self.feature_limits[idx][1]
        
    def eat(self, things, nutrition, perception):
        
        record = width+height
        closest = None
        
        theta = self.velocity.heading();
        
        for _, item in enumerate(things):
            d = self.position.dist(item)
            
            if nutrition < 0:
                if d < 3:
                    self.alive = False
                else:
                    dir = PVector.sub(item, self.position).heading()
                    theta_diff = min(abs(dir - theta), 2*PI-abs(dir - theta))
                    if theta_diff < self.dna[4]/2 and d < record and d < perception:
                        record = d
                        closest = item
               
            else:        
                if d < 3:
                    things.remove(item)
                    self.points += nutrition
                
                elif d < record and d < perception:
                    record = d
                    closest = item                
                
        if closest is not None:
            return self.seek(closest)
        return PVector(0, 0)
    
    def crash(self, things, idx, perception):
        record = width + height
        closest = None
        
        for thing in things[idx+1:]:
                d = self.position.dist(thing.position)
                if d < 5:
                    self.alive = False
                    thing.alive = False
                elif d < record and d < perception:
                    record = d
                    closest = thing
        if closest is not None:
            return self.seek(closest.position)
        return PVector(0, 0)
    
    def boundaries(self, d):
        
        desired = None
        
        if self.position.x < d:
            desired = PVector(self.maxspeed, self.velocity.y)
        elif self.position.x > width - d:
            desired = PVector(-self.maxspeed, self.velocity.y)
        
        if self.position.y < d:
            desired = PVector(self.velocity.x, self.maxspeed)
        elif self.position.y > height - d:
            desired = PVector(self.velocity.x, -self.maxspeed)
        
        if desired is not None:
            desired.normalize()
            desired.mult(self.maxspeed)
            steer = PVector.sub(desired, self.velocity)
            steer.limit(self.maxforce)
            self.applyForce(steer)
    
    def display(self):
        theta = self.velocity.heading2D() + PI/2;

        pushMatrix();
        translate(self.position.x, self.position.y);
        rotate(theta);
        
        if debug:
            noFill()
            strokeWeight(3)
            stroke(0, 255, 0, 75)
            # Green ring
            line(0, 0, 0, -self.dna[0] * 20)
            strokeWeight(2)
            circle(0, 0, self.dna[2] * 2)
            stroke(255, 0, 0, 75)
            # Red cone
            line(0, 0, 0, -self.dna[1] * 20)
            fill(255,0,0,75)
            noStroke()
            arc(0, 0, self.dna[3] * 2, self.dna[3] * 2, -self.dna[4]/2 - PI/2, self.dna[4]/2 - PI/2)
            noFill()
            stroke(0, 100, 200, 75)
            strokeWeight(3)
            circle(0, 0, self.dna[6] * 2)
            line(0, 0, 0, -self.dna[5] * 20)
        
        col = color(255, 255, 255)
        
        fill(col);
        stroke(col);
        strokeWeight(1);
        beginShape();
        vertex(0, -self.r*2);
        vertex(-self.r, self.r*2);
        vertex(self.r, self.r*2);
        endShape(CLOSE);

        
        popMatrix();


def crossover_mid(mating_pool):
    
    global num_vehicles
    
    children = []
    
    crossover_point = int(len(mating_pool[0].dna) / 2)
    
    for i in range(num_vehicles - len(mating_pool)):
        parents = rand.sample(mating_pool, 2)
        par0 = parents[0].dna[:crossover_point]
        par1 = parents[1].dna[crossover_point:]
        child_genome = par0 + par1
        children.append(Vehicle(dna=child_genome))
        children[-1].mutate()
    
    for parent in mating_pool:
        children.append(Vehicle(random(width), random(height), parent.dna[:]))
        
    return children

def crossover_random(mating_pool):
    
    global num_vehicles
    
    children = []
    
    for i in range(num_vehicles - len(mating_pool)):
        parents = rand.sample(mating_pool, 2)
        child_genome = []
        for i in range(len(self.feature_limits)):
            if random(1) < 0.5:
                child_genome.append(parents[0].dna[i])
            else:
                child_genome.append(parents[1].dna[i])
        children.append(Vehicle(dna=child_genome))
        children[-1].mutate()
    
    for parent in mating_pool:
        children.append(Vehicle(random(width), random(height), parent.dna[:]))
        
    return children
        
def create_board(num_food, num_poison, bound):
    food = [PVector(random(bound, width-bound), random(bound, height-bound)) for i in range(num_food)]
    poison = [PVector(random(bound, width-bound), random(bound, height-bound)) for i in range(num_poison)]
    
    return food, poison

def create_test_board(num_food, num_poison, bound):
    food = ['{},{}'.format(random(bound, width-bound), random(bound, height-bound)) for i in range(num_food)]
    poison = ['{},{}'.format(random(bound, width-bound), random(bound, height-bound)) for i in range(num_poison)]
    
    saveStrings('test_food.txt', food)
    saveStrings('test_poison.txt', poison)
            
def setup():
    global vehicles, food, poison, debug, gen, counter, num_vehicles, bound, best_drones, toggle
    size(1200, 800)
    num_vehicles = 8
    bound = 25
    vehicles = [Vehicle(random(width), random(height)) for i in range(num_vehicles)]
    food, poison = create_board(120, 60, bound)
    debug = True
    gen = 0
    counter = 0
    best_drones = []
    toggle = 0
    
    #tcreate_test_board(120, 60, bound)

def mouseClicked():
    global debug
    debug = not debug

# def mouseDragged():
#     poison.append(PVector(mouseX, mouseY))

def keyPressed():
    global vehicles, counter, toggle, next_vehicles, bound
    
    if key == 's':
        saveStrings('results.txt', best_drones)
    elif key == 't':
        toggle = (toggle + 1) % 3
        
        if toggle == 1:
            load_test_world()
            # reset the drone
            vehicles = []
            counter = 0
            
            # human drone
            # Food weight, Poison weight, Food percep, Poison percep, FOV, Drone weight, Drone percep, Max Accel
            human = Vehicle(x = width/2, y = height/2, dna = [5, -5, 100, 100, PI/3, -5, 100, 2])
            vehicles.append(human)
            
            # add learned drones
            best_dnas = loadStrings('results.txt')
            next_vehicles = []
            for line in best_dnas:
                dna_strings = line.split(',')
                next_vehicles.append(Vehicle(x = width/2, y = height/2, dna = [float(x) for x in dna_strings]))
            
        elif toggle == 2:
            load_test_world()
            # reset the drone
            vehicles = []
            counter = 0
            
            # add drones
            best_dnas = loadStrings('results.txt')
            next_vehicles = []
            # human drones
            vehicles = [Vehicle(x = random(bound, width - bound), y = random(bound, height - bound), dna = [5, -5, 100, 100, PI/3, -5, 100, 2]) for i in range(8)]
            for line in best_dnas:
                dna_strings = line.split(',')
                next_v = [Vehicle(x = random(bound, width - bound), y = random(bound, height - bound), dna = [float(x) for x in dna_strings]) for i in range(8)]
                next_vehicles.append(next_v)
        
    elif key == 'q':
        exit()
        
def load_test_world():
    global food, poison
    
    food_string = loadStrings('test_food.txt')
    food = []
    for line in food_string:
        data = line.split(',')
        food.append(PVector(float(data[0]), float(data[1])))
        
    poison_string = loadStrings('test_poison.txt')
    poison = []
    for line in poison_string:
        data = line.split(',')
        poison.append(PVector(float(data[0]), float(data[1])))
    
    
def asort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


def draw():
    global gen, counter, vehicles, food, poison, bound, best_drones, toggle
    
    if toggle == 0:
        counter += 1
        
        if counter > 800 or len(vehicles) == 0 or len(food) == 0:
            gen += 1
            print('Generation: {}'.format(gen))
            counter = 0
            
            sorted_vehicles = sorted(vehicles, key=lambda x: x.points, reverse=True)    
            while len(sorted_vehicles) < 4:
                sorted_vehicles.append(Vehicle())
            best_vehicles = sorted_vehicles[:4]
            print([v.points for v in best_vehicles])
            best_drones.append(','.join([str(x) for x in best_vehicles[0].dna]))
            vehicles = crossover_mid(best_vehicles)
            food, poison = create_board(120, 60, bound)
       
    elif toggle == 1:
        counter += 1
        
        if len(vehicles) == 0 or len(food) == 0 or counter == 1200:
            if len(vehicles) == 0:
                print('Vehicle died! Generation: {}'.format(len(next_vehicles)))
                
            else:
                print('Complete! Gen: {}, Counter: {}, Points: {}'.format(len(next_vehicles), counter, vehicles[0].points))
            counter = 0
            vehicles = [next_vehicles.pop()]
            load_test_world()
    
    else:
        counter += 1
        
        if len(vehicles) == 0 or len(food) == 0 or counter == 1200:
            if len(vehicles) == 0:
                print('All died! Generation: {}'.format(len(next_vehicles)))
            else:
                print('Complete! Gen: {}, Counter: {}, Points: {}, Total Points: {}/120'.format(len(next_vehicles), counter, [x.points for x in vehicles], sum([x.points for x in vehicles])))
            counter = 0
            vehicles = next_vehicles.pop()
            load_test_world()
        
    background(51)
    
    for item in food:
        fill(0, 255, 0)
        noStroke()
        ellipse(item.x, item.y, 8, 8)
        
    for item in poison:
        fill(255, 0, 0)
        noStroke()
        ellipse(item.x, item.y, 8, 8)
    
    for idx, v in enumerate(vehicles):
        v.boundaries(bound)
        v.behaviors(food, poison, vehicles, idx)
        v.update()
        v.display()
    
    for _, v in enumerate(vehicles):
        if not v.alive:
            vehicles.remove(v)
        
