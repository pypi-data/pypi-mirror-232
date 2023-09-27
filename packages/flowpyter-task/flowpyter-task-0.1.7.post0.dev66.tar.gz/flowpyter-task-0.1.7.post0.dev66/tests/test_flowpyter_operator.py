from pendulum import datetime
import pytest

from conftest import TEST_NOTEBOOK_DIR, TEST_STATIC_DIR

TASK_ID = "test_task"
EXECUTION_DATE = datetime(2023, 1, 29)


@pytest.fixture
def base_dag(dag_setup):
    from airflow import DAG

    dag = DAG(
        start_date=EXECUTION_DATE,
        dag_id="simple_test_dag",
        schedule="@daily",
        catchup=False,
        default_args={},
    )

    def failure_callback(context):
        pytest.fail("DAG did not run to completion")

    dag.on_failure_callback = failure_callback
    return dag


@pytest.fixture()
def fp_op_with_defaults(tmp_out_dir, tmp_data_dir):
    from flowpytertask import FlowpyterOperator

    class FpOpWithDefaults(FlowpyterOperator):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                host_notebook_dir=str(TEST_NOTEBOOK_DIR),
                host_data_dir=str(tmp_data_dir),
                host_notebook_out_dir=str(tmp_out_dir),
                host_static_dir=str(TEST_STATIC_DIR),
                **kwargs
            )

    yield FpOpWithDefaults


def test_dag(base_dag, tmp_out_dir, fp_op_with_defaults):
    """
    Tests the dag runs to the end
        Caution - if there is something wrong with the callback invocation, this test will show passing
    """
    fp_op_with_defaults(
        dag=base_dag, task_id="first_task", notebook_name="test_nb.ipynb"
    )
    run = base_dag.test(
        execution_date=EXECUTION_DATE,
    )

    run.get_task_instance(task_id="first_task")
    assert (
        tmp_out_dir
        / "2023-01-29"
        / "simple_test_dag__first_task__manual__2023-01-29T00:00:00+00:00"
        / "simple_test_dag__first_task__manual__2023-01-29T00:00:00+00:00__test_nb.ipynb"
    ).exists()


def test_parameterised_dag(base_dag, tmp_out_dir, fp_op_with_defaults):
    """
    Tests the dag runs to the end
        Caution - if there is something wrong with the callback invocation, this test will show passing
    """
    fp_op_with_defaults(
        dag=base_dag,
        task_id="first_task",
        notebook_name="test_nb.ipynb",
        notebook_params={"input": "DEADBEEF"},
    )
    run = base_dag.test(
        execution_date=EXECUTION_DATE,
    )

    run.get_task_instance(task_id="first_task")
    assert (
        "DEADBEEF"
        in (
            tmp_out_dir
            / "2023-01-29"
            / "simple_test_dag__first_task__manual__2023-01-29T00:00:00+00:00"
            / "simple_test_dag__first_task__manual__2023-01-29T00:00:00+00:00__test_nb.ipynb"
        ).read_text()
    )


def test_static_asset_mount(base_dag, tmp_out_dir, fp_op_with_defaults):
    """
    Tests static asset injection runs correctly
    """
    fp_op_with_defaults(
        dag=base_dag,
        task_id="first_task",
        notebook_name="static_nb.ipynb",
    )
    run = base_dag.test(
        execution_date=EXECUTION_DATE,
    )

    run.get_task_instance(task_id="first_task")
    assert (
        "DEADBEEF"
        in (
            tmp_out_dir
            / "2023-01-29"
            / "simple_test_dag__first_task__manual__2023-01-29T00:00:00+00:00"
            / "simple_test_dag__first_task__manual__2023-01-29T00:00:00+00:00__static_nb.ipynb"
        ).read_text()
    )


def test_dependency_dag(base_dag, tmp_out_dir, fp_op_with_defaults):
    first_nb = fp_op_with_defaults(
        dag=base_dag,
        task_id="first_task",
        notebook_name="glue_nb.ipynb",
        notebook_params={"artifact_out": "test_artifact.txt"},
    )
    second_nb = fp_op_with_defaults(
        dag=base_dag,
        task_id="second_task",
        notebook_name="read_nb.ipynb",
        notebook_params={"artifact_in": "test_artifact.txt"},
    )
    first_nb >> second_nb

    base_dag.test(execution_date=EXECUTION_DATE)

    out_path = (
        tmp_out_dir
        / "2023-01-29"
        / "simple_test_dag__second_task__manual__2023-01-29T00:00:00+00:00"
        / "simple_test_dag__second_task__manual__2023-01-29T00:00:00+00:00__read_nb.ipynb"
    )
    assert "DEADBEEF" in out_path.read_text()


def test_ipynb_check(base_dag, tmp_out_dir, fp_op_with_defaults):
    from flowpytertask import NotebookExtensionError

    with pytest.raises(NotebookExtensionError):
        _ = fp_op_with_defaults(task_id="fail_task", notebook_name="test_nb")
