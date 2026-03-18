from langchain_core.messages import HumanMessage
from app.graph.agent_graph import chatbot

thread_id = "test-thread-1"

config = {
    "configurable": {"thread_id": thread_id}
}

while True:
    user_input = input("\nYou: ")
    print("this is input-> ",user_input)

    if user_input.lower() in ["exit", "quit"]:
        break

    response = chatbot.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )

    print("\nAI:", response["messages"][-1].content)