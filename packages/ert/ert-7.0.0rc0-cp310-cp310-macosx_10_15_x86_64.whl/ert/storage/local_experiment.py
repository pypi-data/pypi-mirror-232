from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Union
from uuid import UUID

import numpy as np
import xtgeo

from ert.config import (
    ExtParamConfig,
    Field,
    GenDataConfig,
    GenKwConfig,
    SummaryConfig,
    SurfaceConfig,
)
from ert.config.response_config import ResponseConfig

if TYPE_CHECKING:
    from ert.config.parameter_config import ParameterConfig
    from ert.storage.local_ensemble import LocalEnsembleAccessor, LocalEnsembleReader
    from ert.storage.local_storage import LocalStorageAccessor, LocalStorageReader


_KNOWN_PARAMETER_TYPES = {
    GenKwConfig.__name__: GenKwConfig,
    SurfaceConfig.__name__: SurfaceConfig,
    Field.__name__: Field,
    ExtParamConfig.__name__: ExtParamConfig,
}


_KNOWN_RESPONSE_TYPES = {
    SummaryConfig.__name__: SummaryConfig,
    GenDataConfig.__name__: GenDataConfig,
}


class LocalExperimentReader:
    _parameter_file = Path("parameter.json")
    _responses_file = Path("responses.json")
    _simulation_arguments_file = Path("simulation_arguments.json")

    def __init__(self, storage: LocalStorageReader, uuid: UUID, path: Path) -> None:
        self._storage: Union[LocalStorageReader, LocalStorageAccessor] = storage
        self._id = uuid
        self._path = path

    @property
    def ensembles(self) -> Generator[LocalEnsembleReader, None, None]:
        yield from (
            ens for ens in self._storage.ensembles if ens.experiment_id == self.id
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def mount_point(self) -> Path:
        return self._path

    @property
    def parameter_info(self) -> Dict[str, Any]:
        info: Dict[str, Any]
        path = self.mount_point / self._parameter_file
        if not path.exists():
            raise ValueError(f"{str(self._parameter_file)} does not exist")
        with open(path, encoding="utf-8", mode="r") as f:
            info = json.load(f)
        return info

    @property
    def response_info(self) -> Dict[str, Any]:
        info: Dict[str, Any]
        path = self.mount_point / self._responses_file
        if not path.exists():
            raise ValueError(f"{str(self._responses_file)} does not exist")
        with open(path, encoding="utf-8", mode="r") as f:
            info = json.load(f)
        return info

    def get_surface(self, name: str) -> xtgeo.RegularSurface:
        return xtgeo.surface_from_file(
            str(self.mount_point / f"{name}.irap"),
            fformat="irap_ascii",
            dtype=np.float32,
        )

    @property
    def parameter_configuration(self) -> Dict[str, ParameterConfig]:
        params = {}
        for data in self.parameter_info.values():
            param_type = data.pop("_ert_kind")
            params[data["name"]] = _KNOWN_PARAMETER_TYPES[param_type](**data)
        return params

    @property
    def response_configuration(self) -> Dict[str, ResponseConfig]:
        params = {}
        for data in self.response_info.values():
            param_type = data.pop("_ert_kind")
            params[data["name"]] = _KNOWN_RESPONSE_TYPES[param_type](**data)
        return params


class LocalExperimentAccessor(LocalExperimentReader):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        storage: LocalStorageAccessor,
        uuid: UUID,
        path: Path,
        parameters: Optional[List[ParameterConfig]] = None,
        responses: Optional[List[ResponseConfig]] = None,
    ) -> None:
        self._storage: LocalStorageAccessor = storage
        self._id = uuid
        self._path = path

        parameter_data = {}
        parameters = [] if parameters is None else parameters
        parameter_file_path = Path(self.mount_point / self._parameter_file)

        if Path.exists(parameter_file_path):
            with open(parameter_file_path, "r", encoding="utf-8") as f:
                parameter_data = json.load(f)

        for parameter in parameters:
            parameter.save_experiment_data(self._path)
            parameter_data.update({parameter.name: parameter.to_dict()})

        with open(self.mount_point / self._parameter_file, "w", encoding="utf-8") as f:
            json.dump(parameter_data, f)

        responses = [] if responses is None else responses
        response_file = self.mount_point / self._responses_file
        response_data = (
            json.loads(response_file.read_text(encoding="utf-8"))
            if response_file.exists()
            else {}
        )

        for response in responses:
            response_data.update({response.name: response.to_dict()})
        with open(response_file, "w", encoding="utf-8") as f:
            json.dump(response_data, f, default=str)

    @property
    def ensembles(self) -> Generator[LocalEnsembleAccessor, None, None]:
        yield from super().ensembles  # type: ignore

    def create_ensemble(
        self,
        *,
        ensemble_size: int,
        iteration: int = 0,
        name: str,
        prior_ensemble: Optional[LocalEnsembleReader] = None,
    ) -> LocalEnsembleAccessor:
        return self._storage.create_ensemble(
            self,
            ensemble_size=ensemble_size,
            iteration=iteration,
            name=name,
            prior_ensemble=prior_ensemble,
        )

    def write_simulation_arguments(self, info: Dict[str, Any]) -> None:
        with open(
            self.mount_point / self._simulation_arguments_file, "w", encoding="utf-8"
        ) as f:
            json.dump(info, f)
