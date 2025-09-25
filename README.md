Run these commands one by one in your terminal:

bash
pip install streamlit
pip install pymongo
pip install dnspython
pip install firebase-admin
pip install pyrebase4
pip install python-dotenv
For pandas, try this special command:

bash
pip install pandas --no-build-isolation

Three Python modules—main.py, components/auth.py and components/database.py—cover the UI, authentication logic and MongoDB Atlas operations with proper indexes.

Folder locations
frontend/main.py – Streamlit entry point.

frontend/components/auth.py – Email / password auth with Pyrebase plus a demo fallback.

frontend/components/database.py – Atlas connection, create_index calls and CRUD helpers.

