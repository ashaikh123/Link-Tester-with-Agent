import tkinter as tk
from tkinter import messagebox
from app.profile import generate_profile
from app.driver import init_driver
from app.survey_bot import run_survey

def launch_gui():
    def start_bot():
        url = entry.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Invalid URL", "Please enter a valid survey URL.")
            return
        root.destroy()
        profile = generate_profile()
        print("Generated Profile:", profile)
        driver = init_driver()
        run_survey(driver, url, profile)

    root = tk.Tk()
    root.title("Survey Bot")

    tk.Label(root, text="Enter Survey Link:").pack(padx=10, pady=(10, 0))
    entry = tk.Entry(root, width=60)
    entry.pack(padx=10, pady=5)
    entry.insert(0, "https://surveydau.pureprofile.com/survey/selfserve/5e1/2507119?list=testing&ptest=1")

    tk.Button(root, text="Start Survey Bot", command=start_bot).pack(pady=10)
    root.mainloop()

if __name__ == '__main__':
    launch_gui()
