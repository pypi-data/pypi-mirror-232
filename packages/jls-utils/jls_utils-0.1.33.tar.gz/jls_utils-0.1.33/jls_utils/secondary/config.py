import os

# FIXME reusability
class Config:
    USERNAME = os.environ.get("GITLAB_USERNAME")
    TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")

    HOST_PORT = None
    CORE_USERNAME = None
    CORE_PASSWORD = None
    VERBOSE = False
