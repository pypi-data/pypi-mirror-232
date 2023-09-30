# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

"""
This test style covers the classes and functions in the backends/graph_compilation.py
file.
"""

import pytest
import networkx as nx
from matplotlib.axes import Axes

from quantify_scheduler import Schedule
from quantify_scheduler.backends.graph_compilation import (
    QuantifyCompiler,
    SerialCompiler,
    SimpleNode,
)
from quantify_scheduler.operations.gate_library import Reset
from quantify_scheduler.schedules.schedule import CompiledSchedule


# pylint: disable=unused-argument
def dummy_compile_add_reset_q0(schedule: Schedule, config=None) -> Schedule:
    schedule.add(Reset("q0"))
    return schedule


dummy_node_A = SimpleNode(
    name="dummy_node_A",
    compilation_func=dummy_compile_add_reset_q0,
)


dummy_node_B = SimpleNode(
    name="dummy_node_B",
    compilation_func=dummy_compile_add_reset_q0,
)

dummy_node_C = SimpleNode(
    name="dummy_node_C",
    compilation_func=dummy_compile_add_reset_q0,
)


dummy_node_D = SimpleNode(
    name="dummy_node_D",
    compilation_func=dummy_compile_add_reset_q0,
)


def test_draw_backend():
    """
    Tests if we can visualize a graph defined by a generic backend.
    This test will only test if the draw code can be executed and a matplotlib figure
    is created. It will not test the details of how the figure looks.
    """
    quantify_compilation = QuantifyCompiler(name="test")

    with pytest.raises(RuntimeError):
        # because the graph is not initialized yet.
        quantify_compilation.draw()

    # this is a private attribute, normally this is set using the construct graph
    # based on a config file, but here we want to keep the test of the drawing backend
    # uncoupled from the configs.
    quantify_compilation._task_graph = nx.DiGraph()

    quantify_compilation._task_graph.add_node(dummy_node_A)
    quantify_compilation._task_graph.add_node(dummy_node_B)
    quantify_compilation._task_graph.add_edge(dummy_node_A, dummy_node_B)

    quantify_compilation._task_graph.add_edge(dummy_node_C, dummy_node_B)
    quantify_compilation._task_graph.add_edge(dummy_node_C, dummy_node_A)

    ax = quantify_compilation.draw()
    assert isinstance(ax, Axes)


def test_compiled_schedule_invariance(mock_setup_basic_transmon_with_standard_params):
    """If the last compilation step returns an instance of CompiledSchedule (also
    inherited), use this instance instead of creating a new CompiledSchedule.

    This test skips the compilation step and passes the CompiledSchedule directly
    to the compilation.
    """
    mock_setup = mock_setup_basic_transmon_with_standard_params
    schedule = Schedule("test_schedule")
    _ = schedule.add(Reset("q0"))

    class InheritedFromCompiledSchedule(CompiledSchedule):
        pass

    compiled_schedule = SerialCompiler("test", mock_setup["quantum_device"]).compile(
        InheritedFromCompiledSchedule(schedule)
    )
    assert isinstance(compiled_schedule, CompiledSchedule)
    assert isinstance(compiled_schedule, InheritedFromCompiledSchedule)
