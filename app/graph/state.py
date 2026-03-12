class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
