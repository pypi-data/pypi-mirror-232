# Streamlit local storage

This repo is to help streamlt users manage data in a browser's local storage.


```
pip install streamlit-local-storage
```


```
from streamlit_local_storage import LocalStorage
localS = LocalStorage()
```

### store an array to local storage

```
localStorageArray = [
    {"key":"Games", "toStore":[{"name":"Basically does this work"}]},
    {"key":"Winners", "toStore":[{"name":"Basically does this work Though"}]}
]
localS.setList(localStorageArray)
```

### store individual items from local storage
```
itemKey = "camera"
itemValue = "Tarah"
localS.set(itemKey, itemValue)
```

### get list of items from local storage

```
data_ = [{"key":"camera"}, {"key":"JamesLook"}]
saved_ = localS.getList(data_)
st.write(saved_)

```

### get all items saved on local storage

```
saved_individual = localS.getAll()
st.write(saved_individual)

```

### when getting local storage items with streamlit widgets
```
st.subheader("Method 1")
localS = LocalStorage()

if "get_val" not in st.session_state:
    st.session_state["get_val"] = None

with st.form("get_data"):
    st.text_input("key", key="get_local_storage_v")
    st.form_submit_button("Submit") 

if st.session_state["get_local_storage_v"] != "":
    val_ = localS.getItem(st.session_state["get_local_storage_v"], key="test_get_item")
    st.session_state["get_val"] = val_
st.write(st.session_state["get_val"])

st.subheader("Method 2 - using callback")
localS = LocalStorage()

if "get_val_2" not in st.session_state:
    st.session_state["get_val_2"] = None

if "st_col_test" not in st.session_state:
    st.session_state["st_col_test"] = None 

def change_state_2():

    with st.session_state["st_col_test"][0]: # call method from below form
        localS.getItem(st.session_state["get_local_storage_v_2"], key="test_get_item_2") # initialise it to get the value
    

with st.form("get_data_2"):
    st.text_input("key", key="get_local_storage_v_2")
    st.form_submit_button("Submit", on_click=change_state_2)
st.session_state["st_col_test"] = st.columns(1) #to make sure rendering happens below form (or other streamlit element. Else the re-rendering of component upon re-running of up will be run at the top of the streamlit component (form here) which creates nasty ui experience.)


if "test_get_item_2" in st.session_state and st.session_state["test_get_item_2"] != None:
    st.session_state["get_val_2"] = st.session_state["test_get_item_2"] # if local storage method is initialised, get the stored value and use it throughout the app.
st.write(st.session_state["get_val_2"])


```

### delete item and item list from local storage

```
saved_individual = localS.deleteList([{"key": "ThomasKing"}, {"key":"Somethingelse"}])
localS.deleteItem('Tony')

```

### delete all
```
localS.deleteAll()

```

### get all

```
localS.getAll()

```

Remember to refresh browser if it does not pop up instantly. 
