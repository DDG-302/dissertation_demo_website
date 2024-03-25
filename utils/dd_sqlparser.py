import json
import re

from sqlglot import parse_one, exp
import sqlparse

def __get_db_schema(create_statements: str):
    # stmts = sqlparse.parse(create_statements)
    stmts = remove_non_create(create_statements)
    table_list = []
    table_2_idx = {}
    column_list = []
    column_2_idx = {}
    datatype_list = []
    pk_list = []
    fk_list = [] # (source_col_idx, col_idx)
    raw_fk_list = [] # (source_table_name, source_col_name, col_idx)
    current_table_idx = 0
    for stmt in stmts:
        # if stmt.get_type() != 'CREATE':
        #     continue
        # parsed = parse_one(stmt.value)
        parsed = parse_one(stmt)
        schema = parsed.find(exp.Schema)

        # 1. get table name
        table_name = schema.find(exp.Table).name
        table_list.append(table_name)
        table_2_idx[table_name] = current_table_idx
        # 2. get column defination(column name && column type)
        for s1 in schema.find_all(exp.ColumnDef):
            for dt, id in zip(s1.find_all(exp.DataType), s1.find_all(exp.Identifier)):
                column_2_idx[(current_table_idx, id.name)] = len(column_list)
                column_list.append([current_table_idx, id.name])
                datatype_list.append(dt.this.name)
                if(s1.find(exp.PrimaryKeyColumnConstraint)):
                    pk_list.append(len(column_list) - 1)
        for pk in schema.find_all(exp.PrimaryKey):
            id = pk.find(exp.Identifier).name
            col_id = column_2_idx[(current_table_idx, id)]
            pk_list.append(col_id)

        for fk in schema.find_all(exp.ForeignKey):
            ref = fk.find(exp.Reference)
            # source table may have not been defined
            # so only save the string to the raw fk list
            source_table= ref.find(exp.Table).name 
            source_col_name = ref.find(exp.Identifier).name

            id = fk.find(exp.Identifier).name
            col_id = column_2_idx[(current_table_idx, id)]
            raw_fk_list.append((source_table, source_col_name, col_id))
        current_table_idx += 1

    # transfer raw fk list to fk list
    for fk_raw in raw_fk_list:
        source_table_idx = table_2_idx.get(fk_raw[0], None)
        if(source_table_idx is None):
            raise Exception(f"Table {fk_raw[0]} is not in CREATE statements. Please check the foreign key definition of table {fk_raw[2]}.")
        col_idx = column_2_idx.get((source_table_idx, fk_raw[1]), None)
        if(col_idx is None):
            raise Exception(f"Column {fk_raw[1]} is not in table {fk_raw[0]}, Please check the foreign key definition of table {fk_raw[2]}.")
        fk_list.append([fk_raw[2], col_idx])
    return table_list, column_list,datatype_list, pk_list, fk_list   

def remove_non_create(statements: str):
    stmts = sqlparse.parse(statements)
    create_statements = []
    for stmt in stmts:
        if stmt.get_type() == 'CREATE':
            create_statements.append(stmt.value)
    return create_statements

def get_db_schema(create_statements: str, database_name: str)->dict:
    table_list, column_list,datatype_list, pk_list, fk_list  = __get_db_schema(create_statements)
    output_schema_data = {}
    # {
    # "column_names": [],
    # "column_names_original": [],
    # "column_types": [],
    # "db_id": "",
    # "foreign_keys": [],
    # "primary_keys": [],
    # "table_names": [],
    # "table_names_original": [],
    # }

    output_schema_data["table_names"] = [re.sub("_+", " ", tb_name) for tb_name in table_list]
    output_schema_data["table_names_original"] = table_list

    output_schema_data["column_names_original"] = column_list
    output_schema_data["column_names"] =  [[db_idx, re.sub("_+", " ", col_name)] for db_idx,col_name in column_list]

    output_schema_data["column_types"] = datatype_list

    output_schema_data["primary_keys"] = pk_list
    output_schema_data["foreign_keys"] = fk_list
    output_schema_data["db_id"] = database_name
    return output_schema_data

if __name__ == "__main__":

    idx = 0
    pk_idx = 0
    with open("activity_1.sql", "r") as f:
        stmts = f.read()
    output_schema = get_db_schema(stmts, "test db")
    with open("activity_1.json", "w") as f:
        json.dump(output_schema, f, indent=2)
    exit()
    # with open(r"data\nasdsql\database_raw\TESTUSER/perpetrator.json", "r") as f:
    #     data:dict = json.loads(f.read())
    #     print(type(data))
    # print("{")
    # for k, v in data.items():
    #     if(isinstance(v, dict)):
    #         val = "{}"
    #     elif(isinstance(v, list)):
    #         val = "[]"
    #     elif(isinstance(v, str)):
    #         val = "\"\""
    #     print(f"\"{k}\": {val},")
    # print("}")
    # exit()

    output_schema_data = {
        "column_names": [],
        "column_names_original": [],
        "column_types": [],
        "db_id": "",
        "foreign_keys": [],
        "primary_keys": [],
        "table_names": [],
        "table_names_original": [],
    }

    


    with open("test_dbschema.json", "w") as f:
        json.dump(output_schema_data, f)
        