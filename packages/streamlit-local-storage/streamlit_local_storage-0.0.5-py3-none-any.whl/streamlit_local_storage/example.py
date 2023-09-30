import streamlit as st
from __init__ import LocalStorage


st.subheader("Method 1")
localS = LocalStorage()

if "button_to_get_storage_val" not in st.session_state:
    st.session_state["button_to_get_storage_val"] = False

if "get_val" not in st.session_state:
    st.session_state["get_val"] = None

with st.form("get_data"):
    st.text_input("key", key="get_local_storage_v")
    st.form_submit_button("Submit") 

if st.session_state["get_local_storage_v"] != "":
    val_ = localS.getItem(st.session_state["get_local_storage_v"], key="test_get_item")
    st.session_state["get_val"] = val_
st.write(st.session_state["get_val"])



st.subheader("Method 2")
localS = LocalStorage()

if "button_to_get_storage_val_2" not in st.session_state:
    st.session_state["button_to_get_storage_val_2"] = False

if "get_val_2" not in st.session_state:
    st.session_state["get_val_2"] = None

if "st_col_test" not in st.session_state:
    st.session_state["st_col_test"] = None 

def change_state_2():

    with st.session_state["st_col_test"][0]:
        localS.getItem(st.session_state["get_local_storage_v_2"], key="test_get_item_2")
    

with st.form("get_data_2"):
    st.text_input("key", key="get_local_storage_v_2")
    st.form_submit_button("Submit", on_click=change_state_2)
st.session_state["st_col_test"] = st.columns(1)


test_var = None
if "test_get_item_2" in st.session_state and st.session_state["test_get_item_2"] != None:
    st.session_state["get_val_2"] = st.session_state["test_get_item_2"]
    test_var = st.session_state["test_get_item_2"]
st.write(st.session_state["get_val_2"])
st.write(test_var)

st.button("hiya-")


st.subheader("Method 3")
localS = LocalStorage()

if "button_to_get_storage_val_3" not in st.session_state:
    st.session_state["button_to_get_storage_val_3"] = False

if "get_val_3" not in st.session_state:
    st.session_state["get_val_3"] = None

def change_state_3():

    if st.session_state["get_local_storage_v_3"] is not "":
        localS.getItem(st.session_state["get_local_storage_v_3"], key="test_get_item_3")
        st.session_state["get_val_3"] = st.session_state["test_get_item_3"]
    # if st.session_state["button_to_get_storage_val_3"] != "":
    #     localS.getItem(st.session_state["button_to_get_storage_val_3"], key="test_get_item_3")
    #     st.session_state["get_val_3"] = st.session_state["test_get_item_3"]
    

with st.form("get_data_3"):
    st.text_input("key", key="get_local_storage_v_3")
    st.form_submit_button("Submit", on_click=change_state_3)


if "test_get_item_3" in st.session_state and st.session_state["test_get_item_3"] != None:
    st.write( st.session_state["get_val_3"] )
#     st.session_state["get_val_2"] = st.session_state["test_get_item_2"]
# st.write( st.session_state["get_val_3"])

st.button("hiya-2")


# st.subheader("#2")

# if "saved_data" not in st.session_state:
#     st.session_state["saved_data"] = None

# if "test_get_item_2" not in st.session_state:
#     st.session_state["test_get_item_2"] = None

# def change_state():
#     localS.getAll(key="test_get_item_2") #st.session_state["get_local_storage_v2"], key="test_get_item_2")
#     if st.session_state["test_get_item_2"] != None:
#         st.session_state["saved_data"]= st.session_state["test_get_item_2"]
#     # st.session_state["button_to_get_storage_val"] = True

# with st.form("get_data_2"):
#     st.text_input("key", key="get_local_storage_v2")
#     st.form_submit_button("Submit", on_click=change_state)

# # if st.session_state["test_get_item_2"] != None:
# #     st.write(st.session_state["test_get_item_2"])
#     # st.session_state["saved_data"] = st.session_state["test_get_item_2"]

# st.button("Hi")
# st.write(st.session_state["saved_data"])

