from typing import Callable, Final

from mimesis import Person


def _closure_make_french_name() -> Callable[[], str]:
    """A namespace for bound variables in make_french_name."""

    french_man: Final = Person("fr")

    def inner_make_french_name() -> str:
        """Make a French-sounding name using Mimesis library."""

        return french_man.first_name()

    return inner_make_french_name


make_french_name = _closure_make_french_name()
