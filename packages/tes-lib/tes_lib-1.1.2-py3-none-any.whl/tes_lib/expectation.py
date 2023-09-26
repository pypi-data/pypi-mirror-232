"""
Expectation definition
"""
from inspect import signature
from typing import Any, Callable, List, Dict
from enum import Enum


class Expectation:
    """
    Expectation definition - should be used with the event helper functions
    """

    UNSET_VALUE = "TES_LIB_EXPECTATION_UNSET_VALUE"

    def __init__(
        self,
        event_field_name: str,
        comparison_function: Callable,
        comparison_value: Any = UNSET_VALUE,
    ) -> None:
        sig = signature(comparison_function)
        param_count = len(sig.parameters)

        if param_count == 1:
            if comparison_value != Expectation.UNSET_VALUE:
                raise TypeError(
                    "The comparison function {} takes 1 parameter but a comparison value of {}"
                    " was provided. Either remove the comparison value or use a comparison"
                    " function that takes two parameters.".format(
                        comparison_function.__name__,
                        comparison_value,
                    )
                )
        elif param_count == 2:
            if comparison_value == Expectation.UNSET_VALUE:
                raise TypeError(
                    "The comparison function {} takes 2 parameters but no comparison value"
                    " was provided. Either provide a comparison value or use a comparison"
                    " function that takes one parameter.".format(
                        comparison_function.__name__,
                    )
                )
        else:
            raise TypeError(
                "The comparison function {} takes {} parameters which is invalid."
                " Either provide a comparison function that takes 2 parameters alongside a"
                "comparison value or a comparison function that takes one parameter.".format(
                    comparison_function.__name__,
                    param_count,
                )
            )

        self.event_field_name = event_field_name
        self.comparison_function = comparison_function
        self.comparison_value = comparison_value

    def __repr__(self) -> str:
        if self.comparison_value == Expectation.UNSET_VALUE:
            return "{} {}(<No Expected Value>)".format(
                self.event_field_name,
                self.comparison_function.__name__,
            )

        return "{} {}('{}': {})".format(
            self.event_field_name,
            self.comparison_function.__name__,
            self.comparison_value,
            type(self.comparison_value).__name__,
        )

    def compare(self, actual_value: Any) -> bool:
        if self.comparison_value == Expectation.UNSET_VALUE:
            return self.comparison_function(actual_value)

        return self.comparison_function(actual_value, self.comparison_value)


class ExpectationFailureType(Enum):
    COMPARISON_FAILURE = 1
    FIELD_NOT_FOUND = 2


class FailedExpectation:
    """
    A wrapper around an expectation that has failed with additional information
    """

    def __init__(
        self,
        expectation: Expectation,
        failure_type: ExpectationFailureType,
        event_value: Any = None,
    ) -> None:
        self.expectation = expectation
        self.failure_type = failure_type
        self.event_value = event_value

    def __repr__(self) -> str:
        if self.failure_type == ExpectationFailureType.FIELD_NOT_FOUND:
            return "ExpectationFailure: {} field not found".format(
                self.expectation,
            )

        # COMPARISON_FAILURE logic is the default behaviour
        return "ExpectationFailure: {} got '{}': {}".format(
            self.expectation,
            self.event_value,
            type(self.event_value).__name__,
        )


class PartialMatch:
    def __init__(self, event: Dict, expectation_failures: List[FailedExpectation]) -> None:
        self.event = event
        self.expectation_failures = expectation_failures
