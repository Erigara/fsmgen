import argparse
import hashlib
import random
from collections import defaultdict
from collections.abc import Callable
from typing import TypeVar, Optional, Generic

from graphviz import Digraph

import config
from random_graph import random_graph


S = TypeVar("S")
T = TypeVar("T")
G = TypeVar("G")
P = TypeVar("P")


class FiniteStateMachine(Generic[S, T, P]):
    def __init__(
        self,
        init_state: S,
        states: list[S],
        inputs: list[T],
        outputs: list[G],
        transition: defaultdict[S, dict[T, S]],
        emit: defaultdict[S, dict[T, G]],
    ):
        self.init_state = init_state
        self.states = states
        self._current_state = init_state
        self.inputs = inputs
        self.outputs = outputs
        self.transition = transition
        self.emit = emit

    @property
    def state(self) -> S:
        return self._current_state

    def tick(self, input: T) -> Optional[G]:
        output = None
        if input in self.transition[self.state] and input in self.emit[self.state]:
            output = self.emit[self.state][input]
            state = self.transition[self.state][input]
            self._current_state = state
        return output


def generate(
    states: list[S], inputs: list[T], outputs: list[G], seed=None
) -> FiniteStateMachine:
    """
    Generate random finite state machine.

    :param states: list of unique hashable elements (int, str, ...)
    :param inputs: list of unique hashable elements (int, str, ...)
    :param outputs: list of unique hashable elements (int, str, ...)
    :param seed: random seed
    :return: random finite state machine
    """

    def create_random(seq):
        def rand(k=1):
            return random.sample(seq, k=k)

        return rand

    random_input = create_random(inputs)
    random_output = create_random(outputs)

    if seed:
        random.seed(seed)

    n = len(states)
    m = random.randint(n - 1, min(2 * n, n ** 2))
    root, edges = random_graph(n, m)
    init_state = states[root]

    transition: defaultdict[S, dict[T, S]] = defaultdict(dict)
    emit: defaultdict[S, dict[T, G]] = defaultdict(dict)

    for i, frm in enumerate(states):
        frm_inputs = random_input(n)
        frm_outputs = random_output(n)
        for j, to in enumerate(states):
            if edges[n * i + j]:
                transition[frm][frm_inputs[j]] = to
                emit[frm][frm_inputs[j]] = frm_outputs[j]

    return FiniteStateMachine(init_state, states, inputs, outputs, transition, emit)


def fsm2graph(fsm: FiniteStateMachine) -> Digraph:
    """
    Transform finite state machine to directer graph for next visualization

    :param fsm: finite state machine
    :return: directed graph that represent finite state machine
    """

    def hash_state(state):
        return hashlib.md5(state.encode()).hexdigest()

    dot = Digraph()

    for state in fsm.states:
        dot.node(
            f"{hash_state(state)}",
            label=f"{state}",
            shape="circle" if state != fsm.init_state else "doublecircle",
        )

    for frm in fsm.states:
        for input in fsm.transition[frm]:
            to = fsm.transition[frm][input]
            output = fsm.emit[frm][input]
            dot.edge(
                f"{hash_state(frm)}", f"{hash_state(to)}", label=f"{input}/{output}"
            )

    return dot


def parser():
    parser = argparse.ArgumentParser(description="Generate finite state machine")
    parser.add_argument(
        "--directory",
        type=str,
        metavar="directory",
        nargs="?",
        default=".",
        help="directory where collect results, by default put in current directory",
    )
    parser.add_argument(
        "seeds",
        type=str,
        metavar="seed",
        nargs="+",
        help="random seed used to generate fsm",
    )
    return parser


if __name__ == "__main__":
    args = parser().parse_args()

    for seed in args.seeds:
        machine = generate(config.states, config.inputs, config.outputs, seed)
        dot = fsm2graph(machine)
        dot.render(seed, directory=args.directory, cleanup=True, format="png")
