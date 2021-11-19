"""
.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de>
"""

import numpy as np
import pytest

from pde import PDE, DiffusionPDE, MemoryStorage, ScalarField, UnitGrid
from pde.solvers import Controller, ExplicitSolver


@pytest.mark.parametrize("scheme", ["euler", "runge-kutta"])
@pytest.mark.parametrize("adaptive", [True, False])
def test_solvers_simple_example(scheme, adaptive):
    """test explicit solvers"""
    grid = UnitGrid([4])
    field = ScalarField(grid, 1)
    eq = PDE({"c": "c"})

    dt = 1e-3 if scheme == "euler" else 1e-2

    solver = ExplicitSolver(eq, scheme=scheme, adaptive=adaptive)
    controller = Controller(solver, t_range=10.0, tracker=None)
    res = controller.run(field, dt=dt)
    np.testing.assert_allclose(res.data, np.exp(10), rtol=0.1)
    if adaptive:
        assert solver.info["steps"] != pytest.approx(10 / dt, abs=1)
    else:
        assert solver.info["steps"] == pytest.approx(10 / dt, abs=1)


@pytest.mark.parametrize("scheme", ["euler", "runge-kutta"])
@pytest.mark.parametrize("adaptive", [True, False])
def test_solvers_simple_ode(scheme, adaptive):
    """test explicit solvers with a simple ODE"""
    grid = UnitGrid([1])
    field = ScalarField(grid, 1)
    eq = PDE({"y": "2*sin(t) - y"})

    dt = 1e-3 if scheme == "euler" else 1e-2

    storage = MemoryStorage()
    solver = ExplicitSolver(eq, scheme=scheme, adaptive=adaptive)
    controller = Controller(solver, t_range=20.0, tracker=storage.tracker(1))
    controller.run(field, dt=dt)

    ts = np.ravel(storage.times)
    expect = 2 * np.exp(-ts) - np.cos(ts) + np.sin(ts)
    np.testing.assert_allclose(np.ravel(storage.data), expect, atol=0.05)

    if adaptive:
        assert solver.info["steps"] < 20 / dt
    else:
        assert solver.info["steps"] == pytest.approx(20 / dt, abs=1)


def test_compare_diffusion():
    """test explicit solvers"""
    grid = UnitGrid([16, 16], periodic=True)
    field = ScalarField.random_colored(grid, -3)
    field /= field.fluctuations  # normalize field
    eq = DiffusionPDE()

    # ground truth of simpler solver with low dt
    c1 = Controller(ExplicitSolver(eq), t_range=0.1, tracker=None)
    s1 = c1.run(field, dt=1e-5)

    c2 = Controller(ExplicitSolver(eq, adaptive=True), t_range=0.1, tracker=None)
    s2 = c2.run(field, dt=1e-4)
    np.testing.assert_allclose(s1.data, s2.data, atol=0.1)

    c3 = Controller(ExplicitSolver(eq, scheme="runge-kutta"), t_range=0.1, tracker=None)
    s3 = c3.run(field, dt=1e-3)
    np.testing.assert_allclose(s1.data, s3.data, atol=0.1)

    solver = ExplicitSolver(eq, scheme="runge-kutta", adaptive=True, tolerance=1e-4)
    c4 = Controller(solver, t_range=0.1, tracker=None)
    s4 = c4.run(field, dt=1e-3)
    np.testing.assert_allclose(s1.data, s4.data, atol=0.5)


@pytest.mark.parametrize("backend", ["numba", "numpy"])
def test_stochastic_solvers(backend):
    """test simple version of the stochastic solver"""
    field = ScalarField.random_uniform(UnitGrid([16]), -1, 1)
    eq = DiffusionPDE()
    seq = DiffusionPDE(noise=1e-6)

    solver1 = ExplicitSolver(eq, backend=backend)
    c1 = Controller(solver1, t_range=1, tracker=None)
    s1 = c1.run(field, dt=1e-3)

    solver2 = ExplicitSolver(seq, backend=backend)
    c2 = Controller(solver2, t_range=1, tracker=None)
    s2 = c2.run(field, dt=1e-3)

    np.testing.assert_allclose(s1.data, s2.data, rtol=1e-4, atol=1e-4)
    assert not solver1.info["stochastic"]
    assert solver2.info["stochastic"]


def test_unsupported_stochastic_solvers():
    """test some solvers that do not support stochasticity"""
    field = ScalarField.random_uniform(UnitGrid([16]), -1, 1)
    eq = DiffusionPDE(noise=1)

    with pytest.raises(RuntimeError):
        eq.solve(field, 1, method="explicit", scheme="runge-kutta", tracker=None)
    with pytest.raises(RuntimeError):
        eq.solve(field, 1, method="scipy", scheme="runge-kutta", tracker=None)
