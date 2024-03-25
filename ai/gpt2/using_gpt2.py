from transformers import GPT2Tokenizer, GPT2Model, GPTJForCausalLM, AutoConfig, AutoModelForCausalLM, pipeline

# config = AutoConfig.from_pretrained(
#   "gpt2",
#   trust_remote_code=True,
#   max_new_tokens=2024,
#   max_length = 800,
#   return_full_text=False,
# )
# tokenizer:GPT2Tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
# print(tokenizer.eos_token_id)
# print(tokenizer.pad_token_id)
# tokenizer.pad_token_id = -1
# tokenizer.pad_token = tokenizer.eos_token

# model = GPT2Tokenizer.from_pretrained('gpt2')
# model = AutoModelForCausalLM.from_config(config)

pipe = pipeline(model="gpt2",  return_full_text=False, max_new_tokens=200)
def get_response(sql:str, question:str, external_knowledge: str=""):
    if external_knowledge is None or external_knowledge == "":
        external_knowledge = "False"
    text = f"\n-- SCHEMA:\n{sql}\n-- External Knowledge: {external_knowledge}\n-- Using valid SQLite and understanding External Knowledge, answer the following questions for the tables provided above.\n-- QUESTION: {question}\nGenerate the SQL after thinking step by step:\nSELECT"

    # text = "hello, my name is danny "
    return pipe(text, pad_token_id=100000)[0]["generated_text"]
    
    # encoded_input = tokenizer(text, return_tensors='pt')
    # output = model.generate(**encoded_input)
    # for token in output[0]:
    #     if int(token) == tokenizer.eos_token_id or int(token) == tokenizer.pad_token_id:
    #         print(int(token) == tokenizer.eos_token_id)
    # exit()
    # return tokenizer.decode(output[0], skip_special_tokens=True)

if __name__ == "__main__":
    with open("data/sql/TESTUSER/activity_1.sql", "r") as f:
        sql = f.read()
    print(get_response(sql, "find all students information"))