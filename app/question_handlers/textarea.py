# app/question_handlers.py

def answer_textarea(textarea, answer, DEBUG_MODE=False):
    """
    Sends an answer to a textarea element.
    """
    if textarea.is_displayed() and textarea.is_enabled():
        print(f"✅ textarea found")
        textarea.clear()
        textarea.send_keys(answer)
        print(f"Answer {answer}")
        if DEBUG_MODE:
            input("🔍 Press Enter to proceed to next step...")
        return True
    return False
