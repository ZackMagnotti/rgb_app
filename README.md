# RGB Rock Paper Scissors Logistic Population Growth Sim
This project simulates the population growth of hypothetical system of three populations
which grow according to the logistic population growth model, with the addition of a
rock-paper-scissors predation relationship, wherein Red predates on Green, Green predates
on Blue, and Blue predates on Red - somewhat inspired by the Fire Grass Water pokemon types.

The general case considers a grid of cells (pixels) in which the surrounding cells in a local area
will affect eachother. The "single pixel" case considers a single cell with no interaction with
surrounding populations.

## How to run
This project is designed to run inside a Docker container within a MacOS or Linux environment.
Two scripts, `build` and `run` are responsible for compiling and executing the docker runtime env.
`build` is necessary typically only once, to construct the Docker image. `run` is then responsible
for spinning up the application for use.

From this directory you can run these scripts like so:
```
# execute build script
bash build

# execute run script
bash run
```

While running, the application will occupy the terminal window and can be accessible in-browser
at the address `localhost:5000`.

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

### Predetor/Prey Model
```
# x: prey, y: predators
# _a: prey growth rate
# _b: predation rate
# _g: predator death rate (overpopulation, related to capacity)
# _d: effect of predation on predator growth
dx/dt = _ax - _bxy
dy/dt = -_gy + _dxy
```

### RGB Model
```
# v: 3-vector representing the population of the three species
# _a: growth rate
# A: Matrix encapsulating effects of predation and population capacity
dv/dt = _av + (v * A(v))
```

In the above expression, `A(v)` represents a vector-matrix multiplication of v onto A
(identical to `np.matvec(_A, v)`) resulting in a 3-vector,
and `v * A(v)` represents a piecewise multiplication of two similar 3-vectors resulting
in another 3-vector.

The matrix `A` can be understood by combining the behavior of the standard logistic growth
equations and the predator/prey model.

Let `v = (x, y, z)`, where the predation cycle follows the pattern `x > y > z > x ...`.

Standard Logistic growth
```
dx/dt = _ax(1 - x/K) ...
```

Let `_g = -_a/K` to encapsulate death rate as it relates to population capacity
```
dx/dt = x(_a - _gx) ...
```

Add a term called `_d` to represent population growth due to `x` predating on `y`.
```
dx/dt = x(_a - _gx) + _dxy ...
dx/dt = x(_a - _gx + _dy) ...
```

Add a term called `_b` to represent death rate due to predation from `z`.
```
dx/dt = x(_a - _gx + _dy) - _bxz
dx/dt = x(_a - _gx + _dy - _bz)
```

The full system of equations:
```
dx/dt = x(_a - _gx + _dy - _bz)
dy/dt = y(_a - _bx - _gy + _dz)
dz/dt = z(_a + _dx - _by - _gz)

dx/dt = _ax + x(_gx + _dy - _bz)
dy/dt = _ay + y(_bx - _gy + _dz)
dz/dt = _az + z(_dx - _by - _gz)
```

We can now finally condense this system using vector-matrix operations.
(Note: _g and _b can be defined as negative values to simplify the negative
out of the definition for A)
```
v = (x, y, z)
A = [
    [_g, _d, _b],
    [_b, _g, _d],
    [_d, _b, _g]
]
dv/dt = _av + v * A(v)
```

In the project code, the above parameters are defined as such:
```
_a = growth_rate
_g = -growth_rate / 255
_b = -predation_rate
_d = predation_rate * predation_efficiency
```
`predation_efficiency` is meant to encapsulate the benefit the predator
extracts from each "kill", which then is reinvested into population growth.

It is worth noting the determinate of A:
```
|A| = _g^3 + _d^3 + _b^3 - (3 _g _d _b)
```
