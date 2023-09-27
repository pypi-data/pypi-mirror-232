"""Test Event class"""
import operator
from typing import List, Any, Optional, Dict
from .errors import ExpectationError
from .expectation import Expectation


class TestEvent:
    """Base Test Event class which will store and generate expectations for all the fields passed
    to it.

    This class is expected to be subclassed and then the subclass passed to the add_event function.

    All fields in the subclass should be able to be encoded in json.
    """

    def __init__(self, event_source: str, event_type: Any, **kwargs):
        self.event_source = event_source
        self.event_type = event_type
        self.__dict__.update(kwargs)

    def get_expectations(self, custom_operators: Optional[Dict] = None) -> List[Expectation]:
        """Get the default expectations, unless specified otherwise via the custom_operators all
        expectations will be generated with an Equals operator.

        :param custom_operators: An optional dictionary of field name to operator that should be
                                 used for comparison.
        :return: A list of expectations
        :raises ExpectationError: The event was not found
        """
        if custom_operators is None:
            custom_operators = {}

        expectations = []

        fields = self.__dict__

        # Check the custom operator field names all exist
        for key in custom_operators:
            if key not in fields.keys():
                raise ExpectationError(
                    f"The field {key} provided in the custom_operators does not exist on the event"
                )

        # Build the expectations for each field
        for name, value in fields.items():
            if name in custom_operators:
                expectations.append(Expectation(name, custom_operators[name], value))
                continue

            expectations.append(Expectation(name, operator.eq, value))

        return expectations
