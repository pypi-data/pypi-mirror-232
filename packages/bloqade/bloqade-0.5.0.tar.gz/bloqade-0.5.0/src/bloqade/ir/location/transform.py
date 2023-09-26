from bloqade.builder.typing import ScalarType
from beartype.typing import List, Tuple, Optional, Union, TYPE_CHECKING
from beartype.vale import Is
from typing import Annotated
from beartype import beartype
import numpy as np
from bloqade.ir.scalar import cast

if TYPE_CHECKING:
    from bloqade.ir.location.list import ListOfLocations


def check_position_array(array):
    return (
        array.ndim == 2
        and (
            np.issubdtype(array.dtype, np.floating)
            or np.issubdtype(array.dtype, np.integer)
        )
        and array.shape[1] == 2
    )


def check_bool_array(array):
    return array.ndim == 1 and np.issubdtype(array.dtype, np.bool_)


PositionArray = Annotated[np.ndarray, Is[check_position_array]]
BoolArray = Annotated[np.ndarray, Is[check_bool_array]]


class TransformTrait:
    @beartype
    def scale(self, scale: ScalarType):
        from .list import ListOfLocations
        from .base import LocationInfo

        scale = cast(scale)
        location_list = []
        for location_info in self.enumerate():
            x, y = location_info.position
            new_position = (scale * x, scale * y)
            location_list.append(
                LocationInfo(new_position, bool(location_info.filling.value))
            )

        return ListOfLocations(location_list)

    @beartype
    def _add_position(
        self, position: Tuple[ScalarType, ScalarType], filling: Optional[bool] = None
    ):
        from .list import ListOfLocations
        from .base import LocationInfo

        if filling is None:
            filling = True

        location_list = list(self.enumerate())
        location_list.append(LocationInfo(position, filling))

        return ListOfLocations(location_list)

    @beartype
    def _add_position_list(
        self,
        position: List[Tuple[ScalarType, ScalarType]],
        filling: Optional[List[bool]] = None,
    ):
        from .list import ListOfLocations
        from .base import LocationInfo

        location_list = list(self.enumerate())

        assert (
            len(position) == len(filling) if filling else True
        ), "Length of positions and filling must be the same"

        if filling:
            for position, filling in zip(position, filling):
                location_list.append(LocationInfo(position, filling))

        else:
            for position in position:
                location_list.append(LocationInfo(position, True))

        return ListOfLocations(location_list)

    @beartype
    def _add_numpy_position(
        self, position: PositionArray, filling: Optional[BoolArray] = None
    ):
        return self._add_position_list(
            list(map(tuple, position.tolist())),
            filling.tolist() if filling is not None else None,
        )

    def add_position(
        self,
        position: Union[
            Tuple[ScalarType, ScalarType],
            List[Tuple[ScalarType, ScalarType]],
            PositionArray,
        ],
        filling: Optional[Union[bool, list[bool], BoolArray]] = None,
    ) -> "ListOfLocations":
        """add a position or list of positions to existing atom arrangement.

        Args:
            position (Tuple[ScalarType, ScalarType]
            | List[Tuple[ScalarType, ScalarType]
            | numpy.array with shape (n, 2)]):
                position to add
            filling (bool | list[bool]
            | numpy.array with shape (n, ) | None, optional):
                filling of the added position(s). Defaults to None.

        Returns:
            ListOfLocations: new atom arrangement with added positions

        """
        if isinstance(position, tuple) and isinstance(filling, (bool, type(None))):
            return self._add_position(position, filling)
        elif isinstance(position, list) and isinstance(filling, (list, type(None))):
            return self._add_position_list(position, filling)
        elif isinstance(position, np.ndarray) and isinstance(
            filling, (np.ndarray, type(None))
        ):
            return self._add_numpy_position(position, filling)
        else:
            raise TypeError(
                f"cannot interpret arguments, got {type(position)} "
                f"for position and {type(filling)} for filling"
            )

    @beartype
    def apply_defect_count(
        self, n_defects: int, rng: np.random.Generator = np.random.default_rng()
    ):
        """apply n_defects randomly to existing atom arrangement."""
        from .list import ListOfLocations
        from .base import LocationInfo, SiteFilling

        location_list = []
        for location_info in self.enumerate():
            location_list.append(location_info)

        filled_sites = []

        for index, location_info in enumerate(location_list):
            if location_info.filling is SiteFilling.filled:
                filled_sites.append(index)

        if n_defects >= len(filled_sites):
            raise ValueError(
                f"n_defects {n_defects} must be less than the number of filled sites "
                f"({len(filled_sites)})"
            )

        for _ in range(n_defects):
            index = rng.choice(filled_sites)
            location_list[index] = LocationInfo(
                location_list[index].position,
                (False if location_list[index].filling is SiteFilling.filled else True),
            )
            filled_sites.remove(index)

        return ListOfLocations(location_list)

    @beartype
    def apply_defect_density(
        self,
        defect_probability: float,
        rng: np.random.Generator = np.random.default_rng(),
    ):
        """apply defect_probability randomly to existing atom arrangement."""
        from .list import ListOfLocations
        from .base import LocationInfo, SiteFilling

        p = min(1, max(0, defect_probability))
        location_list = []

        for location_info in self.enumerate():
            if rng.random() < p:
                location_list.append(
                    LocationInfo(
                        location_info.position,
                        (
                            False
                            if location_info.filling is SiteFilling.filled
                            else True
                        ),
                    )
                )
            else:
                location_list.append(location_info)

        return ListOfLocations(location_list=location_list)

    def remove_vacant_sites(self):
        """remove all vacant sites from the register."""
        from .base import SiteFilling
        from .list import ListOfLocations

        new_locations = []
        for location_info in self.enumerate():
            if location_info.filling is SiteFilling.filled:
                new_locations.append(location_info)

        return ListOfLocations(new_locations)
