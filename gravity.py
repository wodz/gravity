import pygame
from pygame import gfxdraw
import math

# It is assumed that Body is not moving.
# Body is described by:
# 1) position vector R [x,y]
# 2) mass
# 3) radius (density is implied then)
# 4) color (purely for visual reasons)

# Bullet or Rocket is moving in gravity field of 1...n Bodies
# The mass of bullet/rocket is considerably smaller then bodies.
# Bullet/Rocket is described by:
# 1) current position vector Rb [x,y]
# 2) mass (we can assume unity for example)
# 3) velocity vector Vb [x,y]

# The system is advance in small time steps:
# 1) Calculate gravitational force for the bullet
# F = G*SUMi((mi*m/r^2)*r/|r|)
# where:
#  r/|r| is versore vector
#  G - gravitational constant
#  mi - mass of body i
#  m - mass of bullet
#  r - distance between body and bullet
#
# 2) Having force, calculate acceleration
# a = F/m
#
# 3) Calculate distance moved in dt
# S = V*dt + a*dt^2/2
#
# 4) Update position
# Rb += S
#
# 5) Update velocity
# V += a*dt
#
# Rinse and repeate :-)

class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            # Mulitply vector by scalar
            return Vector(other * self.x, other * self.y)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(other * self.x, other * self.y)

    def __div__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x/other, self.y/other)

    def __str__(self):
        return '(%g, %g)' % (self.x, self.y)

    def __repr__(self):
        return '%s(%g, %g)' % (self.__class__.__name__, self.x, self.y)

    def draw(self, surface, origin):
        pygame.draw.line(surface, (0,255,0), (origin.x, -origin.y), (origin.x + self.x, -origin.y - self.y), 5)

    def rotate(self, angle):
        rad = math.radians(angle)
        return Vector(self.x * math.cos(rad) - self.y * math.sin(rad), self.x * math.sin(rad) + self.y * math.cos(rad))

class Body:
    def __init__(self, R=Vector(0,0), m=1, r=1):
        self.position = R
        self.mass = m
        self.radius = r

    def draw(self, surface):
        MAX_MASS = 40000
        r = 255 * self.mass/MAX_MASS
        b = 255 - r
        pygame.gfxdraw.aacircle(surface, self.position.x, -self.position.y, self.radius, (r,0,b))
        pygame.gfxdraw.filled_circle(surface, self.position.x, -self.position.y, self.radius, (r,0,b))

class Rocket:
    def __init__(self, R=Vector(0,0), m=1, V=Vector(0,0)):
        self.position = R
        self.mass = m
        self.velocity = V
        self.angle = 90
        self.power = 10.0
        self.steps = [R, R]

    def gravity(self, planets):
        F = Vector(0,0)
        for p in planets.bodies:
            r = p.position - self.position
            F = F + (G * p.mass * self.mass / abs(r)**3) * r

        return F

    def collide(self, planets):
        for p in planets.bodies:
            r = p.position - self.position
            if abs(r) < p.radius:
                return True

        return False

    def trace(self, surface):
        pygame.draw.aalines(surface, (200,200,200), False, map(lambda p : (p.x, -p.y), self.steps), True)
#        pygame.draw.lines(surface, (0,200,200), False, map(lambda p : (p.x, -p.y), self.steps), 2)

    def update_position(self):
        F = rocket.gravity(planets)
        a = F/rocket.mass
        S = rocket.velocity * dt + a * dt**2/2

        # Advance
        rocket.position = rocket.position + S
        rocket.velocity = rocket.velocity + a * dt

        last_step = self.steps[-1]
        if (abs(last_step.x - self.position.x) >= 1.0) or \
            (abs(last_step.y - self.position.y) >= 1.0):
            self.steps.append(self.position)

    def reset(self):
        self.steps = self.steps[0:2]

class Planets:
    def __init__(self):
        self.bodies = []

    def add(self, obj):
        self.bodies.append(obj)

    def draw(self, surface):
        for b in self.bodies:
            b.draw(surface)

if __name__ == "__main__":
    done = False
    fired = False

    pygame.init()
    screen_size = (600, 600)
    screen = pygame.display.set_mode(screen_size)

    background_surface = pygame.Surface((600,600))
    trace_surface = pygame.Surface((600,600))
    trace_surface.set_colorkey((0,0,0))

    pygame.key.set_repeat(100, 10)
    planets = Planets()

    planets.add(Body(R=Vector(500,-300), m=10000, r=20))
    planets.add(Body(R=Vector(100,-250), m=28000, r=30))
    planets.add(Body(R=Vector(10, -400), m=1000, r=60))
    planets.draw(background_surface)

    rocket = Rocket(R=Vector(450,-200), m=1, V=Vector(10,0))

    screen.blit(background_surface, (0,0))
    screen.blit(trace_surface, (0,0))

    font = pygame.font.SysFont('Calibri', 25, True, False)
    text = 'angle=%03.1f velocity=%03.1f' % (rocket.angle, rocket.power)
    textrender = font.render(text ,True,(255,255,255))
    textsize = font.size(text)
    screen.blit(textrender, ((600-textsize[0])/2,0))

    pygame.display.flip()

    G = 1.0
    dt = 0.05
    n = 0

    #clock = pygame.time.Clock()
    while not done:
        event =  pygame.event.poll()
        if event.type == pygame.QUIT:
            done = True

        if fired == False:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    angle = rocket.angle - 0.1
                    if angle < -180:
                        angle = 180

                    rocket.angle = angle

                elif event.key == pygame.K_RIGHT:
                    angle = rocket.angle + 0.1
                    if angle > 180:
                        angle = -180

                    rocket.angle = angle

                elif event.key == pygame.K_UP:
                    power = rocket.power + 0.1
                    if power > 100:
                        power = 0

                    rocket.power = power

                elif event.key == pygame.K_DOWN:
                    power = rocket.power - 0.1
                    if power < 0:
                        power = 100

                    rocket.power = power

                elif event.key == pygame.K_RETURN:
                    print('Fired')
                    rocket.velocity = Vector(math.sin(math.radians(rocket.angle)), math.cos(math.radians(rocket.angle))) * rocket.power
                    rocket.position = Vector(450,-200)
                    rocket.reset()
                    rocket.velocity.draw(screen, rocket.position)

                    
                    rocket.velocity.draw(screen, rocket.position)
                    fired = True

                pygame.draw.rect(screen, (0,0,0), ((600-textsize[0])/2, 0, textsize[0], textsize[1]), 0)
                text = 'angle=%03.1f velocity=%03.1f' % (rocket.angle, rocket.power)
                textrender = font.render(text ,True,(255,255,255))
                textsize = font.size(text)
                screen.blit(textrender, ((600-textsize[0])/2,0))
                pygame.display.flip()

        else:
            if rocket.position.x > 0 and rocket.position.x < 2*600 and \
                rocket.position.y < 0 and rocket.position.y > 2*-600 and \
                not rocket.collide(planets):

                rocket.update_position()

                # Update screen
                rocket.trace(trace_surface)
                screen.blit(background_surface, (0,0))
                screen.blit(trace_surface, (0,0))
                screen.blit(textrender, ((600-textsize[0])/2,0))
                pygame.display.flip()

            else:
                fired = False
                print('fired False')
                trace_surface.fill((0,0,0))
                rocket.reset()

    pygame.quit()
