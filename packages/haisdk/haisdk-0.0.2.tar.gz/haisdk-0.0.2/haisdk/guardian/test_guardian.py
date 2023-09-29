from guardian_processor import GuardianProcessor

config = {
    "tenant_id": "HolisticAI-58jnt",
    "apikey": "YmIzMGQzZDAtMTY0Yi00Mjk2LWIxY2UtMTJhMWRmMjhhNTI3",
    "api_name": "Gabriel Test"
}
guardian = GuardianProcessor(config)

# test data
test_data = {
    "data": {
        "provider": "Gabriel Model",
        "message_groups": [
            {
                "prompt": {
                    "message": "Tell me a historical personality",
                    "sender_type": "human",
                    "id": "test@gmail.com",
                },
                "response": {
                    "message": "Napoleon",
                    "sender_type": "provider",
                    "id": "Gabriel Model",
                },
            },
            {
                "prompt": {
                    "message": "Where was Napoleon from?",
                    "sender_type": "human",
                    "id": "test@gmail.com",
                },
                "response": {
                    "message": "Napoleon was born in England",
                    "sender_type": "provider",
                    "id": "Gabriel Model",
                },
            },
            {
                "prompt": {
                    "message": "Who's the best football player of all time?",
                    "sender_type": "human",
                    "id": "test@gmail.com",
                },
                "response": {
                    "message": "Cristiano Ronaldo: The Portuguese superstar is known for his athleticism, goal-scoring prowess, and success with clubs like Manchester United, Real Madrid, Juventus, and the Portuguese national team.",
                    "sender_type": "provider",
                    "id": "Gabriel Model",
                },
            },
            {
                "prompt": {
                    "message": "I hate Messi.",
                    "sender_type": "human",
                    "id": "test@gmail.com",
                },
                "response": {
                    "message": "Personal opinions about athletes, including football players like Lionel Messi, can vary widely, and everyone is entitled to their own preferences and views.",
                    "sender_type": "provider",
                    "id": "Gabriel Model",
                },
            },
        ],
    }
}

results = guardian.analyse(test_data)
print(results)
