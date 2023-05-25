# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json

from src.taipy.core.common.mongo_default_document import MongoDefaultDocument
from taipy.config.common.scope import Scope
from taipy.config.config import Config


def test_configure_default_data_node():
    data_node1 = Config.configure_data_node(id="input_data1")
    assert data_node1.storage_type == "pickle"
    assert data_node1.scope == Scope.SCENARIO

    Config.configure_default_data_node("in_memory", scope=Scope.GLOBAL)
    data_node2 = Config.configure_data_node(id="input_data2")
    assert data_node2.storage_type == "in_memory"
    assert data_node2.scope == Scope.GLOBAL

    Config.configure_default_data_node("csv")
    data_node3 = Config.configure_data_node(id="input_data3")
    assert data_node3.storage_type == "csv"
    assert data_node3.scope == Scope.SCENARIO


def test_configure_default_data_node_replace_old_default_config():
    Config.configure_default_data_node(
        "in_memory",
        prop1="1",
        prop2="2",
        prop3="3",
    )
    dn1 = Config.configure_data_node(id="dn1")
    assert len(dn1.properties) == 3

    Config.configure_default_data_node(
        "csv",
        prop4="4",
        prop5="5",
        prop6="6",
    )
    dn2 = Config.configure_data_node(id="dn2")
    assert dn2.storage_type == "csv"
    assert len(dn2.properties) == 5  # exposed_type and has_header too
    assert dn2.prop4 == "4"
    assert dn2.prop5 == "5"
    assert dn2.prop6 == "6"
    assert dn2.prop1 is None
    assert dn2.prop2 is None
    assert dn2.prop3 is None


def test_config_storage_type_different_from_default_data_node():
    Config.configure_default_data_node(
        storage_type="pickle",
        custom_property={"foo": "bar"},
        scope=Scope.GLOBAL,
    )

    # Config a datanode with specific "storage_type" different than "pickle"
    # should ignore the default datanode
    csv_dn = Config.configure_data_node(id="csv_dn", storage_type="csv")
    assert len(csv_dn.properties) == 2
    assert csv_dn.properties.get("custom_property") is None
    assert csv_dn.scope == Scope.SCENARIO


def test_configure_default_csv_data_node():
    Config.configure_default_data_node(
        storage_type="csv",
        default_path="default.csv",
        has_header=False,
        exposed_type="numpy",
        scope=Scope.GLOBAL,
    )

    # Config with generic config_data_node without storage_type
    # should return the default DataNode
    dn1 = Config.configure_data_node(id="dn1")
    assert dn1.storage_type == "csv"
    assert dn1.scope == Scope.GLOBAL
    assert dn1.default_path == "default.csv"
    assert dn1.has_header is False
    assert dn1.exposed_type == "numpy"

    # Config with generic config_data_node without storage_type
    # with custom properties
    dn2 = Config.configure_data_node(id="dn2", default_path="dn2.csv")
    assert dn2.storage_type == "csv"
    assert dn2.default_path == "dn2.csv"
    assert dn2.has_header is False
    assert dn2.exposed_type == "numpy"
    assert dn2.scope == Scope.GLOBAL

    # Config a datanode with specific "storage_type" = "csv"
    # should use properties from the default datanode
    dn3 = Config.configure_data_node(
        id="dn3",
        storage_type="csv",
        default_path="dn3.csv",
        scope=Scope.SCENARIO,
    )
    assert dn3.storage_type == "csv"
    assert dn3.default_path == "dn3.csv"
    assert dn3.has_header is False
    assert dn3.exposed_type == "numpy"
    assert dn3.scope == Scope.SCENARIO


def test_configure_default_json_data_node():
    class MyCustomEncoder(json.JSONEncoder):
        ...

    class MyCustomDecoder(json.JSONDecoder):
        ...

    Config.configure_default_data_node(
        storage_type="json",
        default_path="default.json",
        encoder=MyCustomEncoder,
        scope=Scope.GLOBAL,
    )

    # Config with generic config_data_node without storage_type
    # should return the default DataNode
    dn1 = Config.configure_data_node(id="dn1")
    assert dn1.storage_type == "json"
    assert dn1.default_path == "default.json"
    assert dn1.encoder == MyCustomEncoder
    assert dn1.decoder is None
    assert dn1.scope == Scope.GLOBAL

    # Config with generic config_data_node without storage_type
    # with custom properties
    dn2 = Config.configure_data_node(id="dn2", default_path="dn2.json")
    assert dn2.storage_type == "json"
    assert dn2.default_path == "dn2.json"
    assert dn2.encoder == MyCustomEncoder
    assert dn2.decoder is None
    assert dn2.scope == Scope.GLOBAL

    # Config a datanode with specific "storage_type" = "json"
    # should use properties from the default datanode
    dn3 = Config.configure_data_node(
        id="dn3",
        storage_type="json",
        default_path="dn3.json",
        decoder=MyCustomDecoder,
    )
    assert dn3.storage_type == "json"
    assert dn3.default_path == "dn3.json"
    assert dn3.encoder == MyCustomEncoder
    assert dn3.decoder == MyCustomDecoder
    assert dn3.scope == Scope.GLOBAL


def test_configure_default_parquet_data_node():
    Config.configure_default_data_node(
        storage_type="parquet",
        default_path="default.parquet",
        compression="gzip",
        exposed_type="numpy",
        scope=Scope.GLOBAL,
    )

    # Config with generic config_data_node without storage_type
    # should return the default DataNode
    dn1 = Config.configure_data_node(id="dn1")
    assert dn1.storage_type == "parquet"
    assert dn1.default_path == "default.parquet"
    assert dn1.engine == "pyarrow"
    assert dn1.compression == "gzip"
    assert dn1.read_kwargs is None
    assert dn1.write_kwargs is None
    assert dn1.exposed_type == "numpy"
    assert dn1.scope == Scope.GLOBAL

    # Config with generic config_data_node without storage_type
    # with custom properties
    dn2 = Config.configure_data_node(
        id="dn2",
        default_path="dn2.parquet",
        engine="fastparquet",
    )
    assert dn2.storage_type == "parquet"
    assert dn2.default_path == "dn2.parquet"
    assert dn2.engine == "fastparquet"
    assert dn2.compression == "gzip"
    assert dn2.read_kwargs is None
    assert dn2.write_kwargs is None
    assert dn2.exposed_type == "numpy"
    assert dn2.scope == Scope.GLOBAL

    # Config a datanode with specific "storage_type" = "parquet"
    # should use properties from the default datanode
    dn3 = Config.configure_data_node(
        id="dn3",
        storage_type="parquet",
        default_path="dn3.parquet",
        read_kwargs={"filter": "foo"},
        scope=Scope.SCENARIO,
    )
    assert dn3.storage_type == "parquet"
    assert dn3.default_path == "dn3.parquet"
    assert dn3.engine == "pyarrow"
    assert dn3.compression == "gzip"
    assert dn3.read_kwargs == {"filter": "foo"}
    assert dn3.write_kwargs is None
    assert dn3.exposed_type == "numpy"
    assert dn3.scope == Scope.SCENARIO


def test_configure_default_excel_data_node():
    Config.configure_default_data_node(
        storage_type="excel",
        default_path="default.xlsx",
        has_header=False,
        exposed_type="numpy",
        scope=Scope.GLOBAL,
    )

    # Config with generic config_data_node without storage_type
    # should return the default DataNode
    dn1 = Config.configure_data_node(id="dn1")
    assert dn1.storage_type == "excel"
    assert dn1.scope == Scope.GLOBAL
    assert dn1.default_path == "default.xlsx"
    assert dn1.has_header is False
    assert dn1.sheet_name is None
    assert dn1.exposed_type == "numpy"

    # Config with generic config_data_node without storage_type
    # with custom properties
    dn2 = Config.configure_data_node(id="dn2", default_path="dn2.xlsx", sheet_name="sheet_1")
    assert dn2.storage_type == "excel"
    assert dn2.default_path == "dn2.xlsx"
    assert dn2.has_header is False
    assert dn2.sheet_name == "sheet_1"
    assert dn2.exposed_type == "numpy"
    assert dn2.scope == Scope.GLOBAL

    # Config a datanode with specific "storage_type" = "excel"
    # should use properties from the default datanode
    dn3 = Config.configure_data_node(
        id="dn3",
        storage_type="excel",
        default_path="dn3.xlsx",
        scope=Scope.SCENARIO,
    )
    assert dn3.storage_type == "excel"
    assert dn3.default_path == "dn3.xlsx"
    assert dn3.has_header is False
    assert dn3.sheet_name is None
    assert dn3.exposed_type == "numpy"
    assert dn3.scope == Scope.SCENARIO


def test_configure_default_pickle_data_node():
    Config.configure_default_data_node(
        storage_type="pickle",
        default_data=1,
        exposed_type="numpy",
        scope=Scope.GLOBAL,
    )

    # Config with generic config_data_node without storage_type
    # should return the default DataNode
    dn1 = Config.configure_data_node(id="dn1")
    assert dn1.storage_type == "pickle"
    assert dn1.scope == Scope.GLOBAL
    assert dn1.default_path is None
    assert dn1.default_data == 1
    assert dn1.exposed_type == "numpy"

    # Config with generic config_data_node without storage_type
    # with custom properties
    dn2 = Config.configure_data_node(id="dn2", default_path="dn2.pkl", default_data=2)
    assert dn2.storage_type == "pickle"
    assert dn2.default_path == "dn2.pkl"
    assert dn2.default_data == 2
    assert dn2.exposed_type == "numpy"
    assert dn2.scope == Scope.GLOBAL

    # Config a datanode with specific "storage_type" = "pickle"
    # should use properties from the default datanode
    dn3 = Config.configure_data_node(
        id="dn3",
        storage_type="pickle",
        default_path="dn3.pkl",
        scope=Scope.SCENARIO,
    )
    assert dn3.storage_type == "pickle"
    assert dn3.default_path == "dn3.pkl"
    assert dn3.default_data == 1
    assert dn3.exposed_type == "numpy"
    assert dn3.scope == Scope.SCENARIO


def test_configure_default_sql_table_data_node():
    Config.configure_default_data_node(
        storage_type="sql_table",
        db_username="default_user",
        db_password="default_pwd",
        db_name="default_db_name",
        db_engine="mssql",
        table_name="default_table",
        db_port=1010,
        db_host="default_host",
        db_driver="default server",
        db_extra_args={"default": "default"},
        scope=Scope.GLOBAL,
    )

    # Config with generic config_data_node without storage_type
    # should return the default DataNode
    dn1 = Config.configure_data_node(id="dn1")
    assert dn1.storage_type == "sql_table"
    assert dn1.db_username == "default_user"
    assert dn1.db_password == "default_pwd"
    assert dn1.db_name == "default_db_name"
    assert dn1.db_engine == "mssql"
    assert dn1.table_name == "default_table"
    assert dn1.db_port == 1010
    assert dn1.db_host == "default_host"
    assert dn1.db_driver == "default server"
    assert dn1.db_extra_args == {"default": "default"}
    assert dn1.scope == Scope.GLOBAL

    # Config with generic config_data_node without storage_type
    # with custom properties
    dn2 = Config.configure_data_node(
        id="dn2",
        table_name="table_2",
        db_port=2020,
        db_host="host_2",
    )
    assert dn2.storage_type == "sql_table"
    assert dn2.db_username == "default_user"
    assert dn2.db_password == "default_pwd"
    assert dn2.db_name == "default_db_name"
    assert dn2.db_engine == "mssql"
    assert dn2.table_name == "table_2"
    assert dn2.db_port == 2020
    assert dn2.db_host == "host_2"
    assert dn2.db_driver == "default server"
    assert dn2.db_extra_args == {"default": "default"}
    assert dn2.scope == Scope.GLOBAL

    # Config a datanode with specific "storage_type" = "sql_table"
    # should use properties from the default datanode
    dn3 = Config.configure_data_node(
        id="dn3",
        storage_type="sql_table",
        db_username="user_3",
        db_password="pwd_3",
        db_name="db_3",
        db_engine="postgresql",
        table_name="table_3",
    )
    assert dn3.storage_type == "sql_table"
    assert dn3.db_username == "user_3"
    assert dn3.db_password == "pwd_3"
    assert dn3.db_name == "db_3"
    assert dn3.db_engine == "postgresql"
    assert dn3.table_name == "table_3"
    assert dn3.db_port == 1010
    assert dn3.db_host == "default_host"
    assert dn3.db_driver == "default server"
    assert dn3.db_extra_args == {"default": "default"}
    assert dn3.scope == Scope.GLOBAL


def test_configure_default_sql_data_node():
    def query_builder():
        ...

    Config.configure_default_data_node(
        storage_type="sql",
        db_username="default_user",
        db_password="default_pwd",
        db_name="default_db_name",
        db_engine="mssql",
        read_query="SELECT * FROM default_table",
        write_query_builder=query_builder,
        db_port=1010,
        db_host="default_host",
        db_driver="default server",
        db_extra_args={"default": "default"},
        scope=Scope.GLOBAL,
    )

    # Config with generic config_data_node without storage_type
    # should return the default DataNode
    dn1 = Config.configure_data_node(id="dn1")
    assert dn1.storage_type == "sql"
    assert dn1.db_username == "default_user"
    assert dn1.db_password == "default_pwd"
    assert dn1.db_name == "default_db_name"
    assert dn1.db_engine == "mssql"
    assert dn1.read_query == "SELECT * FROM default_table"
    assert dn1.write_query_builder == query_builder
    assert dn1.db_port == 1010
    assert dn1.db_host == "default_host"
    assert dn1.db_driver == "default server"
    assert dn1.db_extra_args == {"default": "default"}
    assert dn1.scope == Scope.GLOBAL

    # Config with generic config_data_node without storage_type
    # with custom properties
    dn2 = Config.configure_data_node(
        id="dn2", table_name="table_2", db_port=2020, db_host="host_2", read_query="SELECT * FROM table_2"
    )
    assert dn2.storage_type == "sql"
    assert dn2.db_username == "default_user"
    assert dn2.db_password == "default_pwd"
    assert dn2.db_name == "default_db_name"
    assert dn2.db_engine == "mssql"
    assert dn2.read_query == "SELECT * FROM table_2"
    assert dn2.write_query_builder == query_builder
    assert dn2.db_port == 2020
    assert dn2.db_host == "host_2"
    assert dn2.db_driver == "default server"
    assert dn2.db_extra_args == {"default": "default"}
    assert dn2.scope == Scope.GLOBAL

    # Config a datanode with specific "storage_type" = "sql"
    # should use properties from the default datanode
    dn3 = Config.configure_data_node(
        id="dn3",
        storage_type="sql",
        db_username="user_3",
        db_password="pwd_3",
        db_name="db_3",
        db_engine="postgresql",
        read_query="SELECT * FROM table_3",
        write_query_builder=query_builder,
    )
    assert dn3.storage_type == "sql"
    assert dn3.db_username == "user_3"
    assert dn3.db_password == "pwd_3"
    assert dn3.db_name == "db_3"
    assert dn3.db_engine == "postgresql"
    assert dn3.read_query == "SELECT * FROM table_3"
    assert dn3.write_query_builder == query_builder
    assert dn3.db_port == 1010
    assert dn3.db_host == "default_host"
    assert dn3.db_driver == "default server"
    assert dn3.db_extra_args == {"default": "default"}
    assert dn3.scope == Scope.GLOBAL


def test_configure_default_mongo_collection_data_node():
    Config.configure_default_data_node(
        storage_type="mongo_collection",
        db_name="default_db_name",
        collection_name="default_collection",
        db_port=1010,
        db_host="default_host",
        db_driver="default server",
        db_extra_args={"default": "default"},
        scope=Scope.GLOBAL,
    )

    # Config with generic config_data_node without storage_type
    # should return the default DataNode
    dn1 = Config.configure_data_node(id="dn1")
    assert dn1.storage_type == "mongo_collection"
    assert dn1.db_username == ""
    assert dn1.db_password == ""
    assert dn1.db_name == "default_db_name"
    assert dn1.collection_name == "default_collection"
    assert dn1.custom_document == MongoDefaultDocument
    assert dn1.db_host == "default_host"
    assert dn1.db_port == 1010
    assert dn1.db_extra_args == {"default": "default"}
    assert dn1.scope == Scope.GLOBAL

    # Config with generic config_data_node without storage_type
    # with custom properties
    dn2 = Config.configure_data_node(
        id="dn2",
        collection_name="collection_2",
        db_port=2020,
        db_host="host_2",
    )
    assert dn2.storage_type == "mongo_collection"
    assert dn2.db_username == ""
    assert dn2.db_password == ""
    assert dn2.db_name == "default_db_name"
    assert dn2.collection_name == "collection_2"
    assert dn2.custom_document == MongoDefaultDocument
    assert dn2.db_host == "host_2"
    assert dn2.db_port == 2020
    assert dn2.db_extra_args == {"default": "default"}
    assert dn2.scope == Scope.GLOBAL

    # Config a datanode with specific "storage_type" = "mongo_collection"
    # should use properties from the default datanode
    dn3 = Config.configure_data_node(
        id="dn3",
        storage_type="mongo_collection",
        db_name="db_3",
        collection_name="collection_3",
        db_username="user_3",
        db_password="pwd_3",
    )
    assert dn3.storage_type == "mongo_collection"
    assert dn3.db_username == "user_3"
    assert dn3.db_password == "pwd_3"
    assert dn3.db_name == "db_3"
    assert dn3.collection_name == "collection_3"
    assert dn3.custom_document == MongoDefaultDocument
    assert dn3.db_port == 1010
    assert dn3.db_host == "default_host"
    assert dn3.db_driver == "default server"
    assert dn3.db_extra_args == {"default": "default"}
    assert dn3.scope == Scope.GLOBAL
