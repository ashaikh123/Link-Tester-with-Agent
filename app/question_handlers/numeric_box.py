def answer_numeric_box(input_box, answer, DEBUG_MODE=False):
    try:
        if input_box.is_displayed() and input_box.is_enabled():
            print(f"✅ Numeric box found")
            input_box.clear()
            input_box.send_keys(answer)
            print(f"Answer {answer}")
            if DEBUG_MODE:
                input("🔍 Press Enter to proceed to next step...")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Failed to handle input box: {e}")
        return False
