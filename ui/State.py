from dataclasses import dataclass

@dataclass
class AppState:
    database_name: str = ""
    collection_name: str = ""
    username: str = ""
    password: str = ""