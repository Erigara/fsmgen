import argparse
import importlib.util
from functools import partial

from hypothesis import strategies as st, settings
from hypothesis.reporting import reporter, report
from hypothesis.stateful import (
    RuleBasedStateMachine,
    Bundle,
    rule,
    run_state_machine_as_test,
)

from fsmgenerator import generate


def create_reference_fsm(states, inputs, outputs, seed):
    return generate(states, inputs, outputs, seed)


def create_concrete_fsm(concrete_implementation_file_path):
    module_name = "concrete_fsm"
    spec = importlib.util.spec_from_file_location(
        module_name, concrete_implementation_file_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(
        module, "FiniteStateMachine"
    ), "File don't have FiniteStateMachine class"

    return module.FiniteStateMachine()


def state_machine_factory(path, seed, states, inputs, outputs):
    create_concrete_fsm_partial = partial(create_concrete_fsm, path)
    create_reference_fsm_partial = partial(
        create_reference_fsm, states, inputs, outputs, seed
    )

    class FiniteStateMachine(RuleBasedStateMachine):
        output = Bundle("output")

        def __init__(self):
            super().__init__()
            self.concrete_fsm = create_concrete_fsm_partial()
            self.reference_fsm = create_reference_fsm_partial()

        @rule(target=output, input=st.sampled_from(inputs))
        def tick(self, input):
            concrete_output = self.concrete_fsm.tick(input)
            reference_output = self.reference_fsm.tick(input)
            return reference_output, concrete_output

        @rule(output=output)
        def check_output(self, output):
            reference_output, concrete_output = output
            assert (
                reference_output == concrete_output
            ), f"State machine produce wrong output, expected: {reference_output}, got: {concrete_output}"

    return FiniteStateMachine()


def parser():
    parser = argparse.ArgumentParser(
        description="Validate finite state machine implementation"
    )
    parser.add_argument("seed", type=str, help="random seed used to generate fsm")
    parser.add_argument("path", type=str, help="path to fsm implementation")
    return parser


def custom_reporter(value):
    """
    Custom reporter used to slightly modify hypothesis output
    """
    textified = f"{value}".replace("state", "machine")
    if "teardown" not in textified and "check" not in textified:
        print(textified)


if __name__ == "__main__":
    args = parser().parse_args(["shanin1000@yandex.ru", "concrete_fsm.py"])

    states = ["A", "B", "C", "D"]
    inputs = [0, 1, 2, 3]
    outputs = [0, 1, 2, 3]

    with reporter.with_value(custom_reporter):
        try:
            run_state_machine_as_test(
                lambda: state_machine_factory(
                    args.path,
                    args.seed,
                    states,
                    inputs,
                    outputs,
                ),
                settings=settings(max_examples=1000),
            )
        except AssertionError as e:
            report(e)
            report(
                "Implementation contains errors, correct them and try again!",
            )
