from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict
from uuid import UUID

from ert.ensemble_evaluator import EvaluatorServerConfig
from ert.realization_state import RealizationState
from ert.run_context import RunContext
from ert.storage import EnsembleAccessor, StorageAccessor

from .base_run_model import BaseRunModel

if TYPE_CHECKING:
    from ert.config import QueueConfig
    from ert.enkf_main import EnKFMain


# pylint: disable=too-many-arguments
class EnsembleExperiment(BaseRunModel):
    def __init__(
        self,
        simulation_arguments: Dict[str, Any],
        ert: EnKFMain,
        storage: StorageAccessor,
        queue_config: QueueConfig,
        id_: UUID,
    ):
        super().__init__(simulation_arguments, ert, storage, queue_config, id_)

    def runSimulations__(
        self,
        run_msg: str,
        evaluator_server_config: EvaluatorServerConfig,
    ) -> RunContext:
        self.setPhaseName(run_msg, indeterminate=False)
        current_case = self._simulation_arguments["current_case"]
        try:
            ensemble = self._storage.get_ensemble_by_name(current_case)
            assert isinstance(ensemble, EnsembleAccessor)
        except KeyError:
            ensemble = self._storage.create_ensemble(
                self._experiment_id,
                name=current_case,
                ensemble_size=self._ert.getEnsembleSize(),
                iteration=self._simulation_arguments.get("item_num", 0),
            )
        self.set_env_key("_ERT_ENSEMBLE_ID", str(ensemble.id))

        prior_context = self._ert.ensemble_context(
            ensemble,
            self._simulation_arguments["active_realizations"],
            iteration=self._simulation_arguments.get("iter_num", 0),
        )

        if not prior_context.sim_fs.realizations_initialized(
            prior_context.active_realizations
        ):
            self.ert().sample_prior(
                prior_context.sim_fs,
                prior_context.active_realizations,
            )
        else:
            state_map = prior_context.sim_fs.state_map
            for realization_nr in prior_context.active_realizations:
                if state_map[realization_nr] in [
                    RealizationState.UNDEFINED,
                    RealizationState.LOAD_FAILURE,
                ]:
                    state_map[realization_nr] = RealizationState.INITIALIZED

        self._evaluate_and_postprocess(prior_context, evaluator_server_config)

        self.setPhase(1, "Simulations completed.")

        return prior_context

    def run_experiment(
        self, evaluator_server_config: EvaluatorServerConfig
    ) -> RunContext:
        return self.runSimulations__(
            "Running ensemble experiment...", evaluator_server_config
        )

    @classmethod
    def name(cls) -> str:
        return "Ensemble experiment"

    def check_if_runpath_exists(self) -> bool:
        iteration = self._simulation_arguments.get("iter_num", 0)
        active_mask = self._simulation_arguments.get("active_realizations", [])
        active_realizations = [i for i in range(len(active_mask)) if active_mask[i]]
        run_paths = self.facade.get_run_paths(active_realizations, iteration)
        return any(Path(run_path).exists() for run_path in run_paths)
