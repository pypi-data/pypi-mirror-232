from __future__ import annotations

from pathlib import Path
from typing import Union

from airflow.models import Variable
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount


class NotebookExtensionError(Exception):
    pass


class ReservedParameterError(Exception):
    pass


class FlowpyterOperator(DockerOperator):
    """
    An operator that runs a parameterised Flowpyter notebook with a shared data area

    Parameters
    ----------
    notebook_name : str
        The name of the notebook to execute (including extension)
    host_notebook_dir
        Folder on the host containing the notebooks to be executed. Mounted read-only.
    host_notebook_out_dir
        Folder on the host that will contain the rendered and executed notebooks
    host_data_dir
        Folder on the host for intermediate data artefacts to be passed between
        tasks in the DAG - see notes
    host_static_dir
        Folder on the host containing static assets. Mounted read-only.
    notebook_params : dict, optional
        Parameters for Papermill to inject into the notebook.
    image : str, default "flowminder/flowpyterlab:api-analyst-latest"
        The Docker image to run the notebook on
    network_mode : str, optional
        The docker compose network mode; see docs for corresponding
        parameter in https://airflow.apache.org/docs/apache-airflow-providers-docker/stable/_api/airflow/providers/docker/operators/docker/index.html
    environment : dict, optional, default FlowpyterOperator.flowapi_env
        Environment variables to be injected into the running Docker environment.


    Notes
    -----

    - Every notebook has a ``data_dir`` variable injected by default - this is a shared folder that can be used to
      pass artefacts between notebooks and other tasks within a dagrun. The following jinja string should give the
      path to the shared data folder;

      ``{{ var.value.host_data_dir }}/{{ ds }}/{{ dag.id }}__{{ run_id }}``
    - The completed notebooks are saved in task-individual folders within ``host_notebook_out_dir``
    - The notebook_params keys and values can also use jinja templating, but this has not been tested yet

    The Airflow variables needed for this operator to run

    host_dag_path
        The path to the dag folder - this is needed to resolve some paths between the host, the scheduler and the
        notebook container
    flowapi_token (optional)
        A token to be passed into the notebooks for
    notebook_uid, notebook_gid
        The uid and gid to run the notebook container as

    Examples
    --------
    This example demonstrates using the data_dir injected variable to write an artefact to the shared area
    in one notebook, and read and print its contents in the other:

    >>> # glue_nb.ipynb
    ... data_dir = "unset"
    ... artifact_out = "unset"
    ... from pathlib import Path
    ... ( Path(data_dir) / artifact_out).write_text("DEADBEEF")
    ...
    ... # read_nb.ipynb
    ... data_dir = "unset"
    ... artifact_in = "unset"
    ... from pathlib import Path
    ... print(( Path(data_dir) / artifact_in).read_text())
    ...
    ... first_nb = FlowpyterOperator(
    ...    task_id="first_task",
    ...    notebook_name="glue_nb.ipynb",
    ...    notebook_params={"artifact_out": "test_artifact.txt"},
    ... )
    ... second_nb = FlowpyterOperator(
    ...    task_id="second_task",
    ...    notebook_name="read_nb.ipynb",
    ...    notebook_params={"artifact_in": "test_artifact.txt"},
    ... )
    ... first_nb >> second_nb
    """

    CONTAINER_NOTEBOOK_DIR = Path("/opt/airflow/notebooks")
    CONTAINER_DATA_DIR = Path("/opt/airflow/data")
    CONTAINER_NOTEBOOK_OUT_DIR = Path("/opt/airflow/notebooks_out")
    CONTAINER_STATIC_DIR = Path("/opt/airflow/static")

    # Note - I want this to be something that can be used as a convenience function
    # ex `foo = FlowpyterOperator(...., environment = FlowpyterOperator.flowapi_env)
    # Need to test it out.
    flowapi_env = {
        "FLOWAPI_TOKEN": Variable.get(
            "flowapi_token", "PLEASE SET AIRFLOW_VAR_FLOWAPI_TOKEN IN AIRFLOW HOST"
        ),
        "FLOWAPI_URL": "http://localhost:9090",
    }

    def __init__(
        self,
        notebook_name: str,
        host_notebook_dir: str,
        host_notebook_out_dir: str,
        host_data_dir: str,
        host_static_dir: str,
        notebook_params: dict = None,
        image: str = "flowminder/flowpyterlab:api-analyst-latest",
        network_mode: str = None,
        environment: dict = None,
        **kwargs,
    ) -> None:
        self.log.info(f"Creating docker task to run for {notebook_name}")
        if environment is None:
            environment = self.flowapi_env
        if notebook_params is None:
            notebook_params = {}

        if "data_dir" in notebook_params.keys():
            raise ReservedParameterError("data_dir is a reserved parameter")

        if Path(notebook_name).suffix not in [".json", ".ipynb"]:
            raise NotebookExtensionError("Notebooks must have ipynb or json extension")
        self.notebook_name = notebook_name
        self.notebook_uid = Variable.get("notebook_uid")
        self.notebook_gid = Variable.get("notebook_gid")
        self.nb_params = notebook_params

        super().__init__(
            image=image,
            mount_tmp_dir=False,
            environment=environment,
            network_mode=network_mode,
            command="TO BE FILLED",
            user=f"{self.notebook_uid}:{self.notebook_gid}",
            auto_remove="force",
            **kwargs,
        )
        self.host_notebook_dir = self._handle_paths(host_notebook_dir)
        self.host_notebook_out_dir = self._handle_paths(host_notebook_out_dir)
        self.host_data_dir = self._handle_paths(host_data_dir)
        self.host_static_dir = self._handle_paths(host_static_dir)
        self.mounts += [
            Mount(
                source=str(self.host_notebook_dir),
                target=str(self.CONTAINER_NOTEBOOK_DIR),
                type="bind",
                read_only=True,
            ),
            Mount(
                source=str(self.host_static_dir),
                target=str(self.CONTAINER_STATIC_DIR),
                type="bind",
                read_only=True,
            ),
            Mount(
                source=str(self.host_data_dir),
                target=str(self.CONTAINER_DATA_DIR),
                type="bind",
            ),
            Mount(
                source=str(self.host_notebook_out_dir),
                target=str(self.CONTAINER_NOTEBOOK_OUT_DIR),
                type="bind",
            ),
        ]
        mount_string = "\n".join(f"{m['Source']} to {m['Target']}" for m in self.mounts)
        self.log.info(f"Mounts:\n {mount_string}")

    def _handle_paths(self, path: Union[str, Path]) -> Path:
        """Replaces any part of `path` that is above the dag folder with the path to the dag folder on the host"""
        # Reviewer note - I'm not entirely happy this is right, but we need a CeleryExecutor test env to test it
        # properly
        abs_path = Path(path).absolute()
        host_dag_path = Path(Variable.get("host_dag_path"))
        local_dag_path = Path(self.dag.relative_fileloc)
        try:
            rel_to_dag = local_dag_path.relative_to(path)
            return host_dag_path / rel_to_dag
        except ValueError:
            self.log.info(f"{path} is not relative to dag folder, assuming absolute")
            return abs_path

    def execute(self, context):
        self.log.info(f"Executing {self.notebook_name}")
        # Building context-dependent paths on host
        container_in_path = self.CONTAINER_NOTEBOOK_DIR / self.notebook_name
        context_str = (
            f"{context['dag'].dag_id}__{context['ti'].task_id}__{context['run_id']}"
        )
        notebook_out_name = f"{context_str}__{self.notebook_name}"
        context_stem = Path(context["ds"]) / context_str
        task_out_path = (
            self.CONTAINER_NOTEBOOK_OUT_DIR / context_stem / notebook_out_name
        )
        dagrun_data_stem = (
            Path(context["ds"]) / f"{context['dag'].dag_id}__{context['run_id']}"
        )
        host_task_out_dir = self.host_notebook_out_dir / context_stem
        host_dagrun_data_dir = self.host_data_dir / dagrun_data_stem
        container_dagrun_data_dir = self.CONTAINER_DATA_DIR / dagrun_data_stem
        host_dagrun_data_dir.mkdir(parents=True, exist_ok=True)
        host_task_out_dir.mkdir(parents=True)
        self.log.info(f"Dagrun data dir at {host_dagrun_data_dir}")
        self.log.info(f"Finished notebooks at {host_task_out_dir}")

        # Injecting the shared data_dir and static_dir params for accessing inside the notebook
        context_params = {
            "data_dir": container_dagrun_data_dir,
            "static_dir": self.CONTAINER_STATIC_DIR,
        }
        self.nb_params.update(context_params)

        # Building and executing the papermill command
        cmd_string = self._build_papermill_command(
            container_in_path,
            task_out_path,
        )

        self.command = self.format_command(cmd_string)

        # By default, the DockerOperator returns either the last line or all of stdout;
        # but I don't think we want that here
        self.log.info(f"Papermill command: {self.command}")
        super().execute(context)

    def _build_papermill_command(
        self,
        in_path: Path,
        out_path: Path,
    ) -> str:
        param_string = " ".join(
            f"-p {key} {value}" for (key, value) in self.nb_params.items()
        )
        return f"papermill {param_string} {in_path} {out_path}"
