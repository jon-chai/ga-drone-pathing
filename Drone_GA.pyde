import random as rand

class Vehicle:
    
    mr = 0.2
    feature_creation = [lambda x: random(-2, 2), lambda x:random(-2, 2), lambda x:random(0, 100), lambda x:random(0, 100)]
    
    def __init__(self, x, y, dna=None):
        
        self.position = PVector(x, y)
        self.velocity = PVector(0, -2)
        self.acceleration = PVector(0, 0)
        
        self.r = 4
        self.maxspeed = 5
        self.maxforce = 0.5
        
        self.health = 1
        
        
        if dna is None:
            self.dna = [0] * 4
            # Food weight
            self.dna[0] = random(-2, 2)
            # Poison weight
            self.dna[1] = random(-2, 2)
            # Food perception
            self.dna[2] = random(0, 100)
            # Poison perception
            self.dna[3] = random(0, 100)
        else:
            self.dna = dna[:]
    
    def update(self):
        self.health -= 0.01
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
    
    def behaviors(self, good, bad):
        steerG = self.eat(good, 0.5, self.dna[2])
        steerB = self.eat(bad, -10, self.dna[3])
        
        steerG.mult(self.dna[0])
        steerB.mult(self.dna[1])
        
        self.applyForce(steerG)
        self.applyForce(steerB)
    
    def clone(self):
        if random(1) < 0.005:
            return Vehicle(self.position.x, self.position.y, self.dna)
    
    def mutate(self):
        for idx, gene in enumerate(self.dna):
            if random(1) < self.mr:
                self.dna[idx] = self.feature_creation[idx](0)
    
    def eat(self, things, nutrition, perception):
        record = width+height
        closest = None
        for _, item in enumerate(things):
            d = self.position.dist(item)
            
            if d < self.maxspeed:
                things.remove(item)
                self.health += nutrition
            elif d < record and d < perception:
                record = d
                closest = item
    
        if closest is not None:
            return self.seek(closest)
        return PVector(0, 0)
    
    def dead(self):
        return self.health <= 0
    
    def boundaries(self):
        
        desired = None
        d = 25
        
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
            line(0, 0, 0, -self.dna[0] * 20)
            strokeWeight(2)
            circle(0, 0, self.dna[2] * 2)
            stroke(255, 0, 0)
            line(0, 0, 0, -self.dna[1] * 20)
            circle(0, 0, self.dna[3] * 2)
        
        col = lerpColor(color(255, 0, 0), color(0, 255, 0), self.health)
        
        fill(col);
        stroke(col);
        strokeWeight(1);
        beginShape();
        vertex(0, -self.r*2);
        vertex(-self.r, self.r*2);
        vertex(self.r, self.r*2);
        endShape(CLOSE);

        
        popMatrix();
            
def setup():
    global vehicles, food, poison, debug, gen, counter
    size(800, 600)
    vehicles = [Vehicle(random(width), random(height)) for i in range(10)]
    food = [PVector(random(width), random(height)) for i in range(40)]
    poison = [PVector(random(width), random(height)) for i in range(20)]
    debug = True
    gen = 0
    counter = 0
    print(gen)

def mouseClicked():
    global debug
    debug = not debug

def asort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)

def crossover_mid(mating_pool):
    
    children = []
    
    crossover_point = int(len(mating_pool[0].dna) / 2)
    
    for i in range(len(vehicles) - len(mating_pool)):
        parents = rand.sample(mating_pool, 2)
        par0 = parents[0].dna[:crossover_point]
        par1 = parents[1].dna[crossover_point:]
        child_genome = par0 + par1
        children.append(Vehicle(random(width), random(height), child_genome))
        children[-1].mutate()
    
    for parent in mating_pool:
        children.append(Vehicle(random(width), random(height), parent.dna[:]))
        
    return children

def draw():
    global gen, counter, vehicles
    
    counter += 1
    
    if counter > 300 or len(vehicles) == 0:
        gen += 1
        print(gen)
        counter = 0
        
        best_vehicles = sorted(vehicles, key=lambda x: x.health, reverse=True)[:3]
        # print(best_vehicles)
        # print([v.health for v in best_vehicles])
        vehicles = crossover_mid(best_vehicles)
        # print(new_vehicles)
        
        
        
    
    background(51)
    
    if random(1) < 0.1:
        food.append(PVector(random(width), random(height)))
    
    if random(1) < 0.02:
        poison.append(PVector(random(width), random(height)))
    
    for item in food:
        fill(0, 255, 0)
        noStroke()
        ellipse(item.x, item.y, 8, 8)
        
    for item in poison:
        fill(255, 0, 0)
        noStroke()
        ellipse(item.x, item.y, 8, 8)
      
    for _, v in enumerate(vehicles):
        v.boundaries()
        v.behaviors(food, poison)
        v.update()
        v.display()
        # newVehicle = v.clone()
        # if newVehicle is not None:
        #     vehicles.append(newVehicle)
        # if v.dead():
        #     food.append(PVector(v.position.x, v.position.y))
        #     vehicles.remove(v)
