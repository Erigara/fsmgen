from hypothesis import strategies as st, given
from hypothesis.stateful import (
    RuleBasedStateMachine,
    rule,
    initialize,
    invariant,
    Bundle,
    precondition,
)
from hypothesis.strategies import composite

from fsm import generate


@composite
def states_inputs_outputs(draw):
    length = draw(st.integers(min_value=1, max_value=100))
    allowed = st.sets(
        st.one_of(st.integers(), st.characters()), min_size=length, max_size=length
    )
    states = list(draw(allowed))
    inputs = list(draw(allowed))
    outputs = list(draw(allowed))
    return states, inputs, outputs


@given(
    data=states_inputs_outputs(),
    seed=st.one_of(
        st.integers().filter(lambda val: val != 0),
        st.binary(min_size=1),
        st.floats().filter(lambda val: val != 0.0),
        st.text(min_size=1),
    ),
)
def test_generate_equal(data, seed):
    states, inputs, outputs = data
    fsm1 = generate(states, inputs, outputs, seed)
    fsm2 = generate(states, inputs, outputs, seed)
    assert fsm1.transition == fsm2.transition
    assert fsm1.emit == fsm2.emit


class GeneratedStateMachine(RuleBasedStateMachine):
    """
    Testing correctness of FSM.
    """

    outs = Bundle("outs")

    @initialize(data=states_inputs_outputs())
    def init(self, data):
        self.states, self.inputs, self.outputs = data
        self.fsm = generate(self.states, self.inputs, self.outputs)

    @rule(target=outs, data=st.data())
    def tick(self, data):
        input = data.draw(st.sampled_from(self.inputs), label="Input")
        return self.fsm.tick(input)

    @rule(output=outs)
    def output_in_outputs_or_none(self, output):
        assert output is None or output in self.outputs

    @precondition(lambda self: hasattr(self, "fsm"))
    @invariant()
    def state_in_states(self):
        assert self.fsm.state in self.states


class StateMachine(RuleBasedStateMachine):
    states = "ABCD"
    inputs = [0, 1, 2, 3]
    outputs = [0, 1, 2, 3]

    outs = Bundle("outs")

    @initialize()
    def setup(self, seed):
        self.concrete_fsm = generate(self.states, self.inputs, self.outputs, seed=seed)
        self.reference_fsm = generate(self.states, self.inputs, self.outputs, seed=seed)
        self.reference_fsm.transition["B"] = {}
        self.reference_fsm.emit["B"] = {}

    @rule(target=outs, input=st.sampled_from(inputs))
    def tick(self, input):
        concrete_output = self.concrete_fsm.tick(input)
        reference_output = self.reference_fsm.tick(input)
        return reference_output, concrete_output

    @rule(outs=outs)
    def check_output(self, outs):
        reference_output, concrete_output = outs
        assert reference_output == concrete_output


TestStateMachine = GeneratedStateMachine.TestCase
