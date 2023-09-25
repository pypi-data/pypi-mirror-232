
from os import path

from rsidatasciencetools.sqlutils.sql_connect import DbConnectGenerator
from rsidatasciencetools.sqlutils.sqlconfig import SQLConfig


def test_sql_config_auto_import():
    fdir = path.dirname(path.abspath(__file__))
    cfg = SQLConfig(fdir, auto_update_paths=True)

    assert cfg._config == {
        "dialect_driver": "sqlite",
        "host": path.join(fdir,"sql-check-db.sqlite3"),
        "localfile": True,
        "table": "designations_table"}