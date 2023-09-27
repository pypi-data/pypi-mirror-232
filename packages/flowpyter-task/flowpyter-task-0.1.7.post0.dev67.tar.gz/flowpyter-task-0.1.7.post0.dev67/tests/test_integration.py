from pathlib import Path

import pytest

@pytest.mark.skip("Skipping until we can get an entire Celery setup inside a fixture (future PR)")
def test_example_dag(monkeypatch, dag_setup):
    monkeypatch.setenv("AIRFLOW__CORE__EXECUTOR","CeleryExecutor")
    from airflow.models.dagbag import DagBag
    from airflow.utils.db import initdb
    initdb()
    dag_bag = DagBag(dag_folder=str(Path(__file__).parent), include_examples=False)
    dag_bag.collect_dags()
    dag = dag_bag.get_dag("example_dag")
    dag.run()
