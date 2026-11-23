# RGB Logistic Growth Simulator
This project simulates the population growth of hypothetical system of three populations
which grow somewhat according to the logistic population model, but with the addition of a
rock-paper-scissors predation relationship, wherein Red predates on Green, Green predates
on Blue, and Blue predates on Red - somewhat inspired by the Fire-Grass-Water pokemon type triangle.

The general case considers a grid of cells (pixels) in which populations will diffuse and affect
surrounding cells in a local area.
The "Single Pixel" case considers a single cell with no outside interaction.

## How to run
This project is designed to run inside a Docker container within a MacOS or Linux environment.
Two scripts, `build` and `run` are responsible for compiling and executing the docker runtime env.
`build` is necessary typically only once, to construct the Docker image. `run` is then responsible
for spinning up the application for use.

You can run the scripts from this directory in a terminal window with the following commands.
```
# execute build script
bash build

# execute run script
bash run
```

While running, the application will occupy the terminal window and can be accessible in-browser
locally on port 5000 by typing [`localhost:5000`](http://localhost:5000) into the address bar.

The application can then be terminated with the key combo `CTRL+C` in the active terminal window.
Most code changes will require a restart to take effect. It isn't necessary to rebuild unless the
`requirements.txt` is altered.

## Math
The relationship between the three "species" is modeled after the
[**Logistics function**](https://en.wikipedia.org/wiki/Logistic_function#Logistic_differential_equation)
and the
[**Lotka-Volterrra predetor-prey model**](https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations)
and may be considered a special case of the
[**Competitive Lotka–Volterra equations**](https://en.wikipedia.org/wiki/Competitive_Lotka%E2%80%93Volterra_equations)
or more generally the
[**Replicator equation**](https://en.wikipedia.org/wiki/Replicator_equation).
The math is generalized so that each species behaves as both predetor and prey in a "Rock Paper Scissors" type
relationship - for example, "Red" predates on "Green", and is prey to "Blue".
This is similar to the starter Pokemon type triangle of Fire, Grass, and Water.
```
Rock > Scissors > Paper > Rock ...
Fire > Grass > Water > Fire ...
R > G > B > R ...
```

### Standard Logistic Growth
```
# x: population, r: growth rate, K: capacity
dx/dt = rx(1 - x/K)
```

### Predator/Prey Model
```
# x: prey, y: predators
# a: prey growth rate
# b: predation rate
# g: predator death rate (overpopulation, related to capacity)
# d: effect of predation on predator growth
dx/dt = ax - bxy
dy/dt = -gy + dxy
```

### RGB Model
```
# v: 3-vector representing the population of the three species
# a: scalar, individual growth rate for each species (same for all three)
# A: Matrix encapsulating effects of predation and population capacity
dv/dt = av + (v * A(v))
```

In the above expression, `A(v)` represents a vector-matrix multiplication of v onto A
(identical to `np.matvec(A, v)`) resulting in a 3-vector,
and `v * (...)` represents a piecewise multiplication of two similar 3-vectors resulting
in another 3-vector.

The matrix `A` can be understood by combining the behavior of the standard logistic growth
equations and the predator/prey model.

Let `v = (x, y, z)`, where the predation cycle follows the pattern `x > y > z > x ...`.

Standard Logistic growth
```
dx/dt = ax(1 - x/K) ...
```

Let `g = a/K` to encapsulate death rate as it relates to population capacity
into one variable.
```
dx/dt = x(a - ax/K) ...
dx/dt = x(a - gx) ...
```

Let `d` represent the population growth due to predation from `x` onto `y`.
```
dx/dt = x(a - gx) + dxy ...
dx/dt = x(a - gx + dy) ...
```

Let `b` represent the death rate due to predation from `z` onto `x`.
```
dx/dt = x(a - gx + dy) - bxz
dx/dt = x(a - gx + dy - bz)
```

The full system of equations:
```
dx/dt = x(a - gx + dy - bz)
dy/dt = y(a - bx - gy + dz)
dz/dt = z(a + dx - by - gz)

dx/dt = ax + x(gx + dy - bz)
dy/dt = ay + y(bx - gy + dz)
dz/dt = az + z(dx - by - gz)
```

We can now finally condense this system using vector-matrix operations.
Define a matrix, `A`, to encapsulate the effects of overpopulation and
the predator/prey relationships into one variable.
```
v = (x, y, z)
A = [
    [-g,  d, -b],
    [-b, -g,  d],
    [ d, -b, -g]
]
dv/dt = av + v * A(v)
```

The below snippet shows how these parameters are defined in the
project code.
```
a = growth_rate
g = -growth_rate / 255
b = -predation_rate
d = predation_rate * predation_efficiency
A = [
    [g, d, b],
    [b, g, d],
    [d, b, g]
]
# let dt = 1
dv = av + v * A(v)
dv = v * (a + A(v))
```
Note: the negative signs are moved into
the variable definitions to simplify the
declaration of the matrix iteslf.
`predation_efficiency` is meant to encapsulate the benefit the predator
extracts from each "kill", which then is reinvested into population growth.

It is worth noting the Determinant of A:
```
|A| = g^3 + d^3 + b^3 - 3gdb
```
