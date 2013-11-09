import os
static_path = os.path.join(os.path.dirname(__file__), "..", "static")

apiurl = "http://localhost:8000/api/%s"

local_store = os.path.join(static_path, "graphs")
local_store_url = "http://localhost:8000/static/graphs"

nodename = "lg"
nodepwd = "lg@home"
