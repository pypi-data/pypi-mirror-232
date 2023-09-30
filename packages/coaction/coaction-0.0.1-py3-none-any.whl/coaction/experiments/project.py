"""A project that contains multiple experiments."""

import multiprocessing as mp

from coaction.experiments.config import ProjectConfig
from coaction.experiments.experiment import Experiment
from coaction.experiments.multiprocessing import DummySemaphore


class Project:
    """A project that contains multiple experiments."""

    def __init__(self, config: ProjectConfig):
        self.config = config

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.config.name})"

    def run(self):
        """Run the project."""
        if self.config.global_config.num_parallel_experiments is not None:
            semaphore = mp.Semaphore(self.config.global_config.num_parallel_experiments)
        else:
            semaphore = DummySemaphore()

        experiments: list[Experiment] = []
        for experiment_config in self.config.experiments:
            experiment = Experiment(self.config, experiment_config, semaphore)
            experiments.append(experiment)
            experiment.start()

        for experiment in experiments:
            experiment.join()
