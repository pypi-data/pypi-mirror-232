from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import xarray as xr
import xtgeo

from .parameter_config import ParameterConfig

if TYPE_CHECKING:
    from ert.storage import EnsembleReader


# pylint: disable=too-many-instance-attributes
@dataclass
class SurfaceConfig(ParameterConfig):  # pylint: disable=too-many-instance-attributes
    ncol: int
    nrow: int
    xori: int
    yori: int
    xinc: int
    yinc: int
    rotation: int
    yflip: int
    forward_init_file: str
    output_file: Path
    base_surface_path: str

    def read_from_runpath(self, run_path: Path, real_nr: int) -> xr.Dataset:
        file_name = self.forward_init_file
        if "%d" in file_name:
            file_name = file_name % real_nr
        file_path = run_path / file_name
        if not file_path.exists():
            raise ValueError(
                "Failed to initialize parameter "
                f"'{self.name}' in file {file_name}: "
                "File not found\n"
            )
        surface = xtgeo.surface_from_file(file_path, fformat="irap_ascii")

        da = xr.DataArray(
            surface.values,
            name="values",
            dims=["x", "y"],
        )

        return da.to_dataset()

    def write_to_runpath(
        self, run_path: Path, real_nr: int, ensemble: EnsembleReader
    ) -> None:
        data = ensemble.load_parameters(self.name, real_nr)

        surf = xtgeo.RegularSurface(
            ncol=self.ncol,
            nrow=self.nrow,
            xori=self.xori,
            yori=self.yori,
            xinc=self.xinc,
            yinc=self.yinc,
            rotation=self.rotation,
            yflip=self.yflip,
            values=data.values,
        )

        file_path = run_path / self.output_file
        file_path.parent.mkdir(exist_ok=True, parents=True)
        surf.to_file(file_path, fformat="irap_ascii")
