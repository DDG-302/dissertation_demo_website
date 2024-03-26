text2natsql_model_save_path = r"D:\work\polyu\sem2\dissertation\text2sql\m2\RESDSQL-main\models/text2natsql-t5-base/checkpoint-14352"
text2natsql_model_bs=1

model_name = "resdsql_base_natsql"


db_path=r"D:/work/polyu/sem2/dissertation/demo/bird/dev/dev_databases/dev_databases"




import os
import json
import torch

from tqdm import tqdm
from tokenizers import AddedToken


from transformers import T5TokenizerFast, T5ForConditionalGeneration
from ai.utils.text2sql_decoding_utils import decode_natsqls
    
# initialize tokenizer
tokenizer = T5TokenizerFast.from_pretrained(
    text2natsql_model_save_path,
    add_prefix_space = True
)

if isinstance(tokenizer, T5TokenizerFast):
    tokenizer.add_tokens([AddedToken(" <="), AddedToken(" <")])


model_class = T5ForConditionalGeneration

# initialize model
model = model_class.from_pretrained(text2natsql_model_save_path)
if torch.cuda.is_available():
    model = model.cuda()

model.eval()

def _test(batch, preprocessed_data):    
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    
    # tables = [preprocessed_data]
    tables = [preprocessed_data]
    table_dict = {}
    for t in tables:
        table_dict[t["db_id"]] = t

    
    predict_sqls = []

    batch_inputs = [data[0] for data in batch]
    batch_db_ids = [data[1] for data in batch]
    batch_tc_original = [data[2] for data in batch]
    
    tokenized_inputs = tokenizer(
        batch_inputs, 
        return_tensors="pt",
        padding = "max_length",
        max_length = 512,
        truncation = True
    )
    
    encoder_input_ids = tokenized_inputs["input_ids"]
    encoder_input_attention_mask = tokenized_inputs["attention_mask"]
    if torch.cuda.is_available():
        encoder_input_ids = encoder_input_ids.cuda()
        encoder_input_attention_mask = encoder_input_attention_mask.cuda()

    with torch.no_grad():
        model_outputs = model.generate(
            input_ids = encoder_input_ids,
            attention_mask = encoder_input_attention_mask,
            max_length = 256,
            decoder_start_token_id = model.config.decoder_start_token_id,
            num_beams = 8,
            num_return_sequences = 8
        )

        model_outputs = model_outputs.view(len(batch_inputs), 8, model_outputs.shape[1])

        predict_sql = decode_natsqls(
            db_path, 
            model_outputs, 
            batch_db_ids, 
            batch_inputs, 
            tokenizer, 
            batch_tc_original, 
            table_dict
        )
    
    return predict_sql[0]
 
async def get_sql(question: str, preprocessed_data: dict, original_data: dict):
    import ai.dd_text2natsql

    # get schema linking
    input_dict = ai.dd_text2natsql.get_input_dict(question, preprocessed_data, original_data)

    input_sequences = input_dict["input_sequence"]
    db_ids = input_dict["db_id"]
    all_tc_original =input_dict["tc_original"]
    batch = (input_sequences, db_ids, all_tc_original)

    return _test([batch], preprocessed_data)

if __name__ == "__main__":

    import db_detail
    question = "how many singers?"

    print(get_sql(question, db_detail.preprocess, db_detail.detail))
    exit()
    


