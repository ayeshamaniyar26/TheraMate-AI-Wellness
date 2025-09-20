# test_chat.py
from llm_adapter import call_gemini, take_who5, suggest_exercise

print("=== Gemini Mental Wellness Chatbot (Phase 2) ===")
print("Type 'exit' to quit, 'who5' for daily WHO-5, 'exercise' for a suggestion.\n")

while True:
    user_input = input("You: ").strip().lower()
    if user_input in ["exit", "quit"]:
        print("Ending session. Stay safe! 🌸")
        break
    elif user_input == "who5":
        take_who5()
    elif user_input == "exercise":
        print(suggest_exercise())
    else:
        try:
            response = call_gemini(user_input)
            print("Gemini:", response)
        except Exception as e:
            print("Error:", e)
