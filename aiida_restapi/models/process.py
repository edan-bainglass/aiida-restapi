import typing as t

import pydantic as pdt
from aiida import orm


def _process_inputs(inputs: dict[str, t.Any]) -> dict[str, t.Any]:
    """Process the inputs dictionary converting each node UUID into the corresponding node by loading it.

    A node UUID is indicated by the key ending with the suffix ``.uuid``.

    :param inputs: The inputs dictionary.
    :type inputs: dict[str, t.Any]
    :returns: The deserialized inputs dictionary.
    :rtype: dict[str, t.Any]
    """
    uuid_suffix = '.uuid'
    results = {}

    for key, value in inputs.items():
        if isinstance(value, dict):
            results[key] = _process_inputs(value)
        elif key.endswith(uuid_suffix):
            results[key[: -len(uuid_suffix)]] = orm.load_node(uuid=value)
        else:
            results[key] = value

    return results


class SubmittedProcess(pdt.BaseModel):
    """Pydantic model for submitted processes."""

    label: str = pdt.Field(
        '',
        description='The label of the process',
        examples=['My process', 'Test calculation'],
    )
    entry_point: str = pdt.Field(
        description='The entry point of the process',
        examples=['core.arithmetic.add'],
    )
    inputs: dict[str, t.Any] = pdt.Field(
        description='The inputs of the process',
        examples=[{'x': 1, 'y': 2}],
    )

    @pdt.field_validator('inputs')
    @classmethod
    def process_inputs(cls, inputs: dict[str, t.Any]) -> dict[str, t.Any]:
        """Process the inputs dictionary.

        :param inputs: The inputs to validate.
        :type inputs: dict[str, t.Any]
        :returns: The validated inputs.
        :rtype: dict[str, t.Any]
        """
        return _process_inputs(inputs)
