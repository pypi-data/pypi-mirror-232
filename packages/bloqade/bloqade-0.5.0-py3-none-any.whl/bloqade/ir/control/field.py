from ..scalar import Scalar, cast
from ..tree_print import Printer
from .waveform import Waveform
from bloqade.visualization import get_field_figure
from pydantic.dataclasses import dataclass
from typing import Dict, List
from decimal import Decimal
from bloqade.visualization import display_ir
from bloqade.visualization import get_ir_figure


class FieldExpr:
    pass


__all__ = [
    "Field",
    "Location",
    "SpatialModulation",
    "Uniform",
    "RunTimeVector",
    "ScaledLocations",
]


@dataclass(frozen=True)
class Location(FieldExpr):
    value: int

    def __repr__(self) -> str:
        ph = Printer()
        ph.print(self)
        return ph.get_value()

    def _repr_pretty_(self, p, cycle):
        Printer(p).print(self, cycle)

    def __str__(self):
        return f"Location({str(self.value)})"

    def children(self):
        return []

    def print_node(self):
        return f"Location({str(self.value)})"


@dataclass
class SpatialModulation(FieldExpr):
    def __hash__(self) -> int:
        raise NotImplementedError

    def __repr__(self) -> str:
        ph = Printer()
        ph.print(self)
        return ph.get_value()

    def _repr_pretty_(self, p, cycle):
        Printer(p).print(self, cycle)

    def _get_data(self, **assignment):
        return {}

    def figure(self, **assignment):
        raise NotImplementedError


@dataclass
class UniformModulation(SpatialModulation):
    def __hash__(self) -> int:
        return hash(self.__class__)

    def __str__(self):
        return "Uniform"

    def print_node(self):
        return "UniformModulation"

    def children(self):
        return []

    def _get_data(self, **assignment):
        return ["uni"], ["all"]

    def figure(self, **assignment):
        return get_ir_figure(self, **assignment)

    def show(self, **assignment):
        display_ir(self, **assignment)


Uniform = UniformModulation()


@dataclass
class RunTimeVector(SpatialModulation):
    name: str

    def __hash__(self) -> int:
        return hash(self.name) ^ hash(self.__class__)

    def __str__(self):
        return f"RunTimeVector({str(self.name)})"

    def print_node(self):
        return "RunTimeVector"

    def children(self):
        return [self.name]

    def figure(self, **assginment):
        return get_ir_figure(self, **assginment)

    def _get_data(self, **assignment):
        return [self.name], ["vec"]

    def show(self, **assignment):
        display_ir(self, **assignment)


@dataclass
class AssignedRunTimeVector(SpatialModulation):
    name: str
    value: List[Decimal]

    def __hash__(self) -> int:
        return hash(self.name) ^ hash(self.__class__) ^ hash(tuple(self.value))

    def __str__(self):
        return f"AssignedRunTimeVector({str(self.name), str(self.value)})"

    def print_node(self):
        return "AssgiendRunTimeVector"

    def children(self):
        return [self.name, *self.value]

    def figure(self, **assginment):
        return get_ir_figure(self, **assginment)

    def _get_data(self, **assignment):
        return [self.name], ["vec"]

    def show(self, **assignment):
        display_ir(self, **assignment)


@dataclass(init=False, repr=False)
class ScaledLocations(SpatialModulation):
    value: Dict[Location, Scalar]

    def __init__(self, pairs):
        value = dict()
        for k, v in pairs.items():
            if isinstance(k, int):
                k = Location(k)
            elif isinstance(k, Location):
                pass
            else:
                raise ValueError(f"expected Location or int, got {k}")

            value[k] = cast(v)
        self.value = value

    def __hash__(self) -> int:
        return hash(frozenset(self.value.items())) ^ hash(self.__class__)

    def __str__(self):
        ## formatting location: scale pair:
        tmp = {f"{str(key.value)}": val for key, val in self.value.items()}
        return f"ScaledLocations({str(tmp)})"

    def _get_data(self, **assignments):
        names = []
        scls = []

        for loc, scl in self.value.items():
            names.append("loc[%d]" % (loc.value))
            scls.append(str(scl(**assignments)))

        return names, scls

    def print_node(self):
        return self.__str__()

    def children(self):
        # can return list or dict
        # should return dict consisting of Location and Scalar
        annotated_children = {}
        for loc, scalar in self.value.items():
            annotated_children[loc.print_node()] = scalar

        return annotated_children

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        assert isinstance(key, Location)
        self.value[key] = cast(value)

    def __bool__(self):
        return bool(self.value)

    def figure(self, **assignments):
        return get_ir_figure(self, **assignments)

    def show(self, **assignment):
        display_ir(self, assignment)


@dataclass
class Field(FieldExpr):
    """Field node in the IR. Which contains collection(s) of
    [`Waveform`][bloqade.ir.control.waveform.Waveform]

    ```bnf
    <field> ::= ('field' <spatial modulation>  <padded waveform>)*
    ```
    """

    value: Dict[SpatialModulation, Waveform]

    def __hash__(self) -> int:
        return hash(frozenset(self.value.items())) ^ hash(self.__class__)

    def __repr__(self) -> str:
        ph = Printer()
        ph.print(self)
        return ph.get_value()

    def _repr_pretty_(self, p, cycle):
        Printer(p).print(self, cycle)

    def __str__(self):
        ## formatting location: scale pair:
        tmp = {str(key): str(val) for key, val in self.value.items()}

        return f"Field({str(tmp)})"

    def add(self, other):
        if not isinstance(other, Field):
            raise ValueError(f"Cannot add Field and {other.__class__}")

        out = Field(dict(self.value))

        for spatial_modulation, waveform in other.value.items():
            if spatial_modulation in self.value:
                out.value[spatial_modulation] = out.value[spatial_modulation] + waveform
            else:
                out.value[spatial_modulation] = waveform

        return out

    def print_node(self):
        return "Field"

    def children(self):
        # return dict with annotations
        return {spatial_mod.print_node(): wf for spatial_mod, wf in self.value.items()}

    def figure(self, **assignments):
        return get_field_figure(self, "Field", None, **assignments)

    def show(self, **assignments):
        """
        Interactive visualization of the Field

        Args:
            **assignments: assigning the instance value (literal) to the
                existing variables in the Field

        """
        display_ir(self, assignments)
