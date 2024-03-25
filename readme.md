# This is a demo user interface program for `Natural Language Database`

The program is developed based on python, `streamlit` library. [Streamlit • A faster way to build and share data apps](https://streamlit.io/)

# Project Structure

1. `ai` is the RESD-SQL and GPT2. It is only used for developing and testing. In deployed version, this part should be replaced by other models or APIs.
2. `aiserver.py` is a RESTful web api server that provides AI responses to the streamlit program. It is only used for developing and testing. In deployed version, this part will be a real remote server.
3. `main.py` is the entrance of the streamlit program.
4. `dialogue.py` takes responsible to build the dialogue page, maintain contexts and handle user inputs.
5. `utils` is used to parse user-upload-database-schema, but according to the requirements, user upload is not allowed.