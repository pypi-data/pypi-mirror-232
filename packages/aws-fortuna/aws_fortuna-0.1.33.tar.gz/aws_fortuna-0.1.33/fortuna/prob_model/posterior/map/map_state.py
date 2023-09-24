from __future__ import annotations

import jax.numpy as jnp

from fortuna.prob_model.posterior.state import PosteriorState
from fortuna.utils.strings import convert_string_to_jnp_array


class MAPState(PosteriorState):
    """
    Attributes
    ----------
    encoded_name: jnp.ndarray
        MAP state name encoded as an array.
    """

    encoded_name: jnp.ndarray = convert_string_to_jnp_array("MAPState")
