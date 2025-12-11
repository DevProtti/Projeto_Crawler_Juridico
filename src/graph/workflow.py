from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

class State(BaseModel):
    pass


# TODO - Verificar necessidade de ser um node assíncrono
def ingestion_node(state: State) -> State: 
    pass


# TODO - Verificar necessidade de ser um node assíncrono
def processing_info_node(state: State)-> State:
    pass


def filter_node(state: State) -> State:
    pass


def editorial_node(state: State) -> State: 
    pass


builder = StateGraph(State)

# Adiconando nodes
builder.add_node("ingestion", ingestion_node)
builder.add_node("processing_info", processing_info_node)
builder.add_node("filter", filter_node)
builder.add_node("ingestion", ingestion_node)