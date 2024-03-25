import streamlit as st



if __name__ == "__main__":


    st.set_page_config(
        "Text2SQL - TEST",
        initial_sidebar_state="expanded",
        menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        }
    )
    # to make sure st.set_page_config are called at the very beginning
    from dialogue import chatBot
    from performance import performance 
    with st.sidebar:
        st.image(
            "assets/img/logo2.png",
            caption="test img",
            # width=300
        )
        st.caption(
            "version: 1.0"
        )
        pages_options = ("AI", "Database detail", "Performance")
        with st.sidebar:
            page = st.selectbox(
                "Pages",
                pages_options
            )
    if page == pages_options[0]:
        chatBot.dialogue_page()
    elif page == pages_options[1]:
        chatBot.database_detail_page()
    elif page == pages_options[2]:
        performance.performance_page()

    
    # prompt = st.chat_input("Input your query")
    # # Initialize chat history
    # if "messages" not in st.session_state:
    #     st.session_state.messages = []


    # # Display chat messages from history on app rerun
    # for message in st.session_state.messages:
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])
            
    #         if(message.get("data", None) is not None):
    #             with st.container(height=400):
    #                 st.table(message["data"])
    #         if(message.get("error", None) is not None):
    #             st.write(message["error"])

    #     # React to user input

    # if prompt:
    #     # Display user message in chat message container
    #     with st.chat_message("user"):
    #         st.markdown(prompt)
            
    #     # Add user message to chat history
    #     st.session_state.messages.append({"role": "user", "content": prompt})
    #     if(st.session_state.Input_Options == "Natural Language"):
    #         import ai.ddeval
    #         response = ai.ddeval.get_sql(prompt)
    #         # response = requests.post("http://127.0.0.1:5000/post_query",  json={"prompt": prompt}).json()["response"]
    #     else:
    #         response = prompt
    
    #     # Display assistant response in chat message container
    #     er = None
    #     df = None
    #     with st.chat_message("assistant"):
    #         random_col_num = random.randint(1, 15)
    #         st.markdown(response)
            
    #         # df = pd.DataFrame(np.random.randn(5, random_col_num), columns=("col %d" % i for i in range(random_col_num)))
    #         from sqlite3 import DatabaseError
    #         try:
    #             df = conn.query(response)
    #             cont = st.container(height=400)
    #             cont.table(df)
    #         except Exception as e:
    #             # print(type(e))
    #             st.write(e.args)
    #         # with st.container(height=100):
                
    #         #     st.table(df)
    #     # Add assistant response to chat history
        
    #     st.session_state.messages.append({"role": "assistant", "content": response, "data": df, "error": er})
