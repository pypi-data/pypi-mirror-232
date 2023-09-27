# stdlib
from typing import Any, Dict, Tuple
# libs
import jinja2
from jinja import meta


__all__ = [
    'check_template_data',
    'JINJA_ENV',
]

JINJA_ENV = jinja2.Environment(
    loader=jinja2.PackageLoader('templates'),
    trim_blocks=True,
)


def check_template_data(template_data: Dict[str, Any], template_name: str) -> Tuple[bool, str]:
    """
    Verifies for any key in template_data is missing.
    :param template_name: The template path to be verified
    :param template_data: dictionary object that must have all the template_keys.
    :return: tuple of boolean flag, success and the error string if any
    """
    parsed = JINJA_ENV.parse(name=template_name)
    required_keys = meta.find_undeclared_variables(parsed)
    success = False
    err = ''
    for k in required_keys:
        if k not in template_data:
            err += f'Key {k} not found in template data\n'
    return success, err
