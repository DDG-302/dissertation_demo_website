import random
import numpy as np

topk_table_num = 4
topk_column_num = 5

def get_db_schemas(db):
    db_schemas = {}

    table_names_original = db["table_names_original"]
    table_names = db["table_names"]
    column_names_original = db["column_names_original"]
    column_names = db["column_names"]
    column_types = db["column_types"]

    
    primary_keys, foreign_keys = [], []
    # record primary keys
    for pk_column_idx in db["primary_keys"]:
        if isinstance(pk_column_idx, list):
            # resdsql can't handle composite PK
            continue
        # print("============================")
        # print(table_names_original)
        # print(column_names_original)
        # print(pk_column_idx)
        # print("============================")
        pk_table_name_original = table_names_original[column_names_original[pk_column_idx][0]]
        pk_column_name_original = column_names_original[pk_column_idx][1]
        
        primary_keys.append(
            {
                "table_name_original": pk_table_name_original.lower(), 
                "column_name_original": pk_column_name_original.lower()
            }
        )

    db_schemas["pk"] = primary_keys

    # record foreign keys
    for source_column_idx, target_column_idx in db["foreign_keys"]:
        fk_source_table_name_original = table_names_original[column_names_original[source_column_idx][0]]
        fk_source_column_name_original = column_names_original[source_column_idx][1]

        fk_target_table_name_original = table_names_original[column_names_original[target_column_idx][0]]
        fk_target_column_name_original = column_names_original[target_column_idx][1]
        
        foreign_keys.append(
            {
                "source_table_name_original": fk_source_table_name_original.lower(),
                "source_column_name_original": fk_source_column_name_original.lower(),
                "target_table_name_original": fk_target_table_name_original.lower(),
                "target_column_name_original": fk_target_column_name_original.lower(),
            }
        )
    db_schemas["fk"] = foreign_keys

    db_schemas["schema_items"] = []
    for idx, table_name_original in enumerate(table_names_original):
        column_names_original_list = []
        column_names_list = []
        column_types_list = []
        
        for column_idx, (table_idx, column_name_original) in enumerate(column_names_original):
            if idx == table_idx:
                column_names_original_list.append(column_name_original.lower())
                column_names_list.append(column_names[column_idx][1].lower())
                column_types_list.append(column_types[column_idx])
        
        db_schemas["schema_items"].append({
            "table_name_original": table_name_original.lower(),
            "table_name": table_names[idx].lower(), 
            "column_names": column_names_list, 
            "column_names_original": column_names_original_list,
            "column_types": column_types_list
        })

    return db_schemas

def prepare_input_and_output(ranked_data):
    question = ranked_data["question"]

    schema_sequence = ""
    for table_id in range(len(ranked_data["db_schema"])):
        table_name_original = ranked_data["db_schema"][table_id]["table_name_original"]
        # add table name
        schema_sequence += " | " + table_name_original + " : "
        
        column_info_list = []
        for column_id in range(len(ranked_data["db_schema"][table_id]["column_names_original"])):
            # extract column name
            column_name_original = ranked_data["db_schema"][table_id]["column_names_original"][column_id]
            db_contents = ranked_data["db_schema"][table_id]["db_contents"][column_id]
             # use database contents if opt.use_contents = True
            if True and len(db_contents) != 0:
                column_contents = " , ".join(db_contents)
                column_info = table_name_original + "." + column_name_original + " ( " + column_contents + " ) "
            else:
                column_info = table_name_original + "." + column_name_original

            column_info_list.append(column_info)
        
        column_info_list.append(table_name_original + ".*")
    
        # add column names
        schema_sequence += " , ".join(column_info_list)

    
    # remove additional spaces in the schema sequence
    while "  " in schema_sequence:
        schema_sequence = schema_sequence.replace("  ", " ")

    # input_sequence = question + schema sequence
    input_sequence = question + schema_sequence
        
    output_sequence = ranked_data["natsql_skeleton"] + " | " + ranked_data["norm_natsql"]


    return input_sequence, output_sequence


def generate_eval_ranked_dataset(question: str, input_table_pred_probs: list, input_column_pred_probs: list, original_data):


    ranked_data = dict()
    ranked_data["question"] = question
    preprocessed_data = {}
    preprocessed_data["db_schema"] = []
    db_schema = get_db_schemas(original_data)
    preprocessed_data["pk"] = db_schema["pk"]
    preprocessed_data["fk"] = db_schema["fk"]
    for table in db_schema["schema_items"]:
            preprocessed_data["db_schema"].append({
                "table_name_original":table["table_name_original"],
                "table_name":table["table_name"],
                "column_names":table["column_names"],
                "column_names_original":table["column_names_original"],
                "column_types":table["column_types"],
                "db_contents": [[] for i in range(len(table["column_types"]))]
            })

    # ranked_data["sql"] = data["sql"]
    # ranked_data["norm_sql"] = data["norm_sql"]
    # ranked_data["sql_skeleton"] = data["sql_skeleton"]
    # ranked_data["natsql"] = data["natsql"]
    # ranked_data["norm_natsql"] = data["norm_natsql"]
    # ranked_data["natsql_skeleton"] = data["natsql_skeleton"]
    ranked_data["db_id"] = "concert_singer"
    ranked_data["db_schema"] = []
    ranked_data["natsql_skeleton"] = ""
    ranked_data["norm_natsql"] = ""
    # db_schema =  [
    #   {
    #     "table_name_original": "stadium",
    #     "table_name": "stadium",
    #     "column_names": [
    #       "stadium id",
    #       "location",
    #       "name",
    #       "capacity",
    #       "highest",
    #       "lowest",
    #       "average"
    #     ],
    #     "column_names_original": [
    #       "stadium_id",
    #       "location",
    #       "name",
    #       "capacity",
    #       "highest",
    #       "lowest",
    #       "average"
    #     ],
    #     "column_types": [
    #       "number",
    #       "text",
    #       "text",
    #       "number",
    #       "number",
    #       "number",
    #       "number"
    #     ],
    #     "db_contents": [
    #       [],
    #       [],
    #       [],
    #       [],
    #       [],
    #       [],
    #       []
    #     ]
    #   },
    #   {
    #     "table_name_original": "singer",
    #     "table_name": "singer",
    #     "column_names": [
    #       "singer id",
    #       "name",
    #       "country",
    #       "song name",
    #       "song release year",
    #       "age",
    #       "is male"
    #     ],
    #     "column_names_original": [
    #       "singer_id",
    #       "name",
    #       "country",
    #       "song_name",
    #       "song_release_year",
    #       "age",
    #       "is_male"
    #     ],
    #     "column_types": [
    #       "number",
    #       "text",
    #       "text",
    #       "text",
    #       "text",
    #       "number",
    #       "others"
    #     ],
    #     "db_contents": [
    #       [],
    #       [],
    #       [],
    #       [],
    #       [],
    #       [],
    #       []
    #     ]
    #   },
    #   {
    #     "table_name_original": "concert",
    #     "table_name": "concert",
    #     "column_names": [
    #       "concert id",
    #       "concert name",
    #       "theme",
    #       "stadium id",
    #       "year"
    #     ],
    #     "column_names_original": [
    #       "concert_id",
    #       "concert_name",
    #       "theme",
    #       "stadium_id",
    #       "year"
    #     ],
    #     "column_types": [
    #       "number",
    #       "text",
    #       "text",
    #       "text",
    #       "text"
    #     ],
    #     "db_contents": [
    #       [],
    #       [],
    #       [],
    #       [],
    #       []
    #     ]
    #   },
    #   {
    #     "table_name_original": "singer_in_concert",
    #     "table_name": "singer in concert",
    #     "column_names": [
    #       "concert id",
    #       "singer id"
    #     ],
    #     "column_names_original": [
    #       "concert_id",
    #       "singer_id"
    #     ],
    #     "column_types": [
    #       "number",
    #       "text"
    #     ],
    #     "db_contents": [
    #       [],
    #       []
    #     ]
    #   }
    # ]
    
    db_schema = preprocessed_data
    # fk_list = [
    #   {
    #     "source_table_name_original": "concert",
    #     "source_column_name_original": "stadium_id",
    #     "target_table_name_original": "stadium",
    #     "target_column_name_original": "stadium_id"
    #   },
    #   {
    #     "source_table_name_original": "singer_in_concert",
    #     "source_column_name_original": "singer_id",
    #     "target_table_name_original": "singer",
    #     "target_column_name_original": "singer_id"
    #   },
    #   {
    #     "source_table_name_original": "singer_in_concert",
    #     "source_column_name_original": "concert_id",
    #     "target_table_name_original": "concert",
    #     "target_column_name_original": "concert_id"
    #   }
    # ]

    table_pred_probs = list(map(lambda x:round(x,4), input_table_pred_probs))
    # find ids of tables that have top-k probability
    topk_table_ids = np.argsort(-np.array(table_pred_probs), kind="stable")[:topk_column_num].tolist()    
    # print(db_schema)
    # record top-k1 tables and top-k2 columns for each table
    for table_id in topk_table_ids:
        new_table_info = dict()
        new_table_info["table_name_original"] = db_schema["db_schema"][table_id]["table_name_original"]

        column_pred_probs = list(map(lambda x:round(x,2), input_column_pred_probs[table_id]))
        topk_column_ids = np.argsort(-np.array(column_pred_probs), kind="stable")[:topk_column_num].tolist()
        
        new_table_info["column_names_original"] = [db_schema["db_schema"][table_id]["column_names_original"][column_id] for column_id in topk_column_ids]
        new_table_info["db_contents"] = [db_schema["db_schema"][table_id]["db_contents"][column_id] for column_id in topk_column_ids]
        
        ranked_data["db_schema"].append(new_table_info)
        
    # record foreign keys among selected tables
    table_names_original = [table["table_name_original"] for table in db_schema["db_schema"]]
    needed_fks = []
    for fk in db_schema["fk"]:
        source_table_id = table_names_original.index(fk["source_table_name_original"])
        target_table_id = table_names_original.index(fk["target_table_name_original"])
        if source_table_id in topk_table_ids and target_table_id in topk_table_ids:
            needed_fks.append(fk)
    ranked_data["fk"] = needed_fks
    
    input_sequence, output_sequence = prepare_input_and_output(ranked_data)
    
    # record table_name_original.column_name_original for subsequent correction function during inference
    tc_original = []
    for table in ranked_data["db_schema"]:
        for column_name_original in table["column_names_original"] + ["*"]:
            tc_original.append(table["table_name_original"] + "." + column_name_original)
    return {
                "db_id": original_data["db_id"],
                "input_sequence": input_sequence, 
                "output_sequence": output_sequence,
                "tc_original": tc_original
            }

def get_input_dict(question: str, preprocessed_data: dict, original_data: dict):
    import ai.ddpre
    total_table_pred_probs, total_column_pred_probs = ai.ddpre.test(question, preprocessed_data, original_data)

    return generate_eval_ranked_dataset(question, total_table_pred_probs[0], total_column_pred_probs[0], original_data)
