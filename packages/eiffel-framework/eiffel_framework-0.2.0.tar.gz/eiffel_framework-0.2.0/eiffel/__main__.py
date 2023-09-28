"""Entrypoint for the Eiffel CLI."""

import json
import logging
import textwrap
from pathlib import Path
from typing import Any

import hydra
from flwr.simulation.ray_transport.utils import enable_tf_gpu_growth
from hydra.utils import instantiate
from omegaconf import DictConfig, ListConfig, OmegaConf
from omegaconf.errors import InterpolationToMissingValueError, MissingMandatoryValue

from eiffel.core.experiment import Experiment


def collect_missing(cfg: Any, missing=[]) -> list:
    """Collect missing fields.

    Recursively collect missing fields from a configuration object using the
    InterpolationToMissingValueError and MissingMandatoryValue exceptions.
    """
    if isinstance(cfg, ListConfig):
        for item in cfg:
            collect_missing(item, missing)
    elif isinstance(cfg, DictConfig):
        for k in cfg.keys():
            try:
                collect_missing(cfg[k], missing)
            except MissingMandatoryValue as e:
                missing.append(k)
            except InterpolationToMissingValueError as e:
                pass
    return missing


@hydra.main(version_base="1.3", config_path="conf", config_name="eiffel")
def main(cfg: DictConfig):
    """Entrypoint for the Eiffel CLI."""
    log = logging.getLogger(__name__)

    enable_tf_gpu_growth()

    log.info("Starting Eiffel")
    if cfg.is_empty():
        log.critical("Empty configuration.")
        exit(1)

    missings = collect_missing(cfg)
    if missings:
        log.critical(f"Missing fields: {missings}")
        exit(1)

    log.debug(
        "Dumping configuration.\n"
        + textwrap.indent(OmegaConf.to_yaml(cfg, resolve=True), "\t")
    )

    ex = Experiment(cfg.experiment)
    Path("./stats.json").write_text(json.dumps(ex.data_stats(), indent=4))
    hist = ex.run()
    hist.save("distributed")


if __name__ == "__main__":
    main()
