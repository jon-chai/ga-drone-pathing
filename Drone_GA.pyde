import random as rand

class Vehicle:
        
    mr = 0.2
    # Food weight, Poison weight, Food percep, Poison percep, FOV, Drone weight, Drone percep
    feature_creation = [lambda x: random(0, 2), lambda x:random(-2, 0), lambda x:random(20, 100), 
                        lambda x:random(20, 100), lambda x:random(PI/6, PI/2), lambda x:random(-2, 0),
                        lambda x:random(20, 100)]
    
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
    
    # def clone(self):
    #     if random(1) < 0.005:
    #         return Vehicle(self.position.x, self.position.y, self.dna)
    
    def mutate(self):
        for idx, gene in enumerate(self.dna):
            if random(1) < self.mr:
                self.dna[idx] = self.feature_creation[idx](0)
        
    def eat(self, things, nutrition, perception):
        
        record = width+height
        closest = None
        
        theta = self.velocity.heading2D();
        a = theta - self.dna[4]/2
        b = theta + self.dna[4]/2
        
        for _, item in enumerate(things):
            d = self.position.dist(item)
            
            if d < 3:
                if nutrition < 0:
                    self.alive = False
                else:
                    things.remove(item)
                    self.points += nutrition
            elif d < record and d < perception:
                if nutrition < 0:
                    dir = PVector.sub(item, self.position)
                    if a < atan(dir.y/(dir.x + 0.0001)) < b:
                        record = d
                        closest = item
                else:
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
            
    
    # def dead(self):
    #     return self.health <= 0
    
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
            stroke(0, 255, 0)
            # Green ring
            line(0, 0, 0, -self.dna[0] * 20)
            strokeWeight(2)
            circle(0, 0, self.dna[2] * 2)
            stroke(255, 0, 0)
            # Red cone
            line(0, 0, 0, -self.dna[1] * 20)
            fill(255,0,0,75)
            noStroke()
            arc(0, 0, self.dna[3] * 2, self.dna[3] * 2, -self.dna[4]/2 - PI/2, self.dna[4]/2 - PI/2)
            noFill()
            stroke(0, 100, 200)
            strokeWeight(3)
            circle(0, 0, self.dna[6] * 2)
            line(0, 0, 0, -self.dna[5] * 20)
        
        # col = lerpColor(color(0, 255, 0), color(255, 0, 0), self.points)
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
        
def create_board(num_food, num_poison, bound):
    food = [PVector(random(bound, width-bound), random(bound, height-bound)) for i in range(num_food)]
    poison = [PVector(random(bound, width-bound), random(bound, height-bound)) for i in range(num_poison)]
    
    # for y in range(200, 400, 5):
    #     poison.append(PVector(200, y))
    
    return food, poison

def create_wall(x1, y1, x2, y2):
    global poison
    
    xs = []
    for i in range(x1, x2, 5):
        xs.append(i)
    ys = []
    # for i in range(
            
def setup():
    global vehicles, food, poison, debug, gen, counter, num_vehicles, bound, best_drones
    size(1200, 800)
    num_vehicles = 20
    bound = 25
    vehicles = [Vehicle(random(width), random(height)) for i in range(num_vehicles)]
    food, poison = create_board(120, 20, bound)
    debug = True
    gen = 0
    counter = 0
    best_drones = []
    # with open('results.txt', 'w') as f:
    #     f.write('')

def mouseClicked():
    global debug
    debug = not debug

# def mouseDragged():
#     poison.append(PVector(mouseX, mouseY))

def keyPressed():
    if key == 'q':
        saveStrings('results.txt', best_drones)
        exit()

def asort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


def draw():
    global gen, counter, vehicles, food, poison, bound, best_drones
    
    counter += 1
    
    if counter > 400 or len(vehicles) == 0 or len(food) == 0:
        gen += 1
        print('Generation: {}'.format(gen))
        counter = 0
        
        sorted_vehicles = sorted(vehicles, key=lambda x: x.points, reverse=True)    
        while len(sorted_vehicles) < 8:
            sorted_vehicles.append(Vehicle())
        best_vehicles = sorted_vehicles[:8]
        print([v.points for v in best_vehicles])
        best_drones.append('{};{}'.format(best_vehicles[0].dna, best_vehicles[0].points))
        vehicles = crossover_mid(best_vehicles)
        food, poison = create_board(120 + 10 * gen, 20 + 5 * gen, bound)
            
    background(51)
    
    # if random(1) < 0.1:
    #     food.append(PVector(random(bound, width-bound), random(bound, height-bound))
    
    # if random(1) < 0.02:
    #     poison.append(PVector(random(width), random(height)))
    
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
