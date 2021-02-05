import random
import hashlib
from collections import defaultdict

from graphviz import Digraph

from random_graph import random_graph


class FSM:
    def __init__(self, init_state, states, inputs, outputs, transition, emit):
        self.init_state = init_state
        self.states = states
        self._current_state = init_state
        self.inputs = inputs
        self.outputs = outputs
        self.transition = transition
        self.emit = emit

    @property
    def inner_state(self):
        return self._current_state

    @inner_state.setter
    def inner_state(self, state):
        self._current_state = state

    def reset(self):
        self.inner_state = self.init_state

    def tick(self, inp):
        if inp in self.transition[self.inner_state] and inp in self.emit[self.inner_state]:
            out = self.emit[self.inner_state][inp]
            state = self.transition[self.inner_state][inp]
            self.inner_state = state
        else:
            out = None
        return out

    @classmethod
    def generate(cls, states, inputs, outputs, seed=None):
        def create_random(seq):
            def rand(k=1):
                return random.sample(seq, k=k)

            return rand

        random_input = create_random(inputs)
        random_output = create_random(outputs)

        if seed:
            random.seed(seed)

        n = len(states)
        m = random.randint(n - 1, 2 * n)
        root, edges = random_graph(n, m)
        init_state = states[root]

        transition = defaultdict(dict)
        emit = defaultdict(dict)

        for i, frm in enumerate(states):
            frm_inputs = random_input(n)
            frm_outputs = random_output(n)
            for j, to in enumerate(states):
                if edges[n * i + j]:
                    transition[frm][frm_inputs[j]] = to
                    emit[frm][frm_inputs[j]] = frm_outputs[j]

        return cls(init_state, states, inputs, outputs, transition, emit)


def fsm2graph(fsm: FSM) -> Digraph:
    def hash_state(state):
        return hashlib.md5(state.encode()).hexdigest()

    dot = Digraph()

    for state in fsm.states:
        dot.node(
            f'{hash_state(state)}', label=f'{state}',
            shape="circle" if state != fsm.init_state else "doublecircle"
        )

    for frm in fsm.states:
        for inp in fsm.transition[frm]:
            to = fsm.transition[frm][inp]
            out = fsm.emit[frm][inp]
            dot.edge(
                f'{hash_state(frm)}', f'{hash_state(to)}',
                label=f'{inp}/{out}'
            )
    return dot