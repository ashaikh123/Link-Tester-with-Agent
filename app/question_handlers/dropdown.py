def answer_dropdown(select, DEBUG_MODE=False):
    try:
        options = select.find_elements(By.TAG_NAME, 'option')
        if not options or len(options) < 2:
            print("⚠️ No valid options found in dropdown.")
            return False

        print(f"✅ dropdown found")
        options[1].click()

        if DEBUG_MODE:
            input("🔍 Press Enter to proceed to next step...")
        return True

    except Exception as e:
        print(f"⚠️ Dropdown handling failed: {e}")
        return False
