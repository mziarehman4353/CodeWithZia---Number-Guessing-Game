import random
import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
import os
import platform

# Only import winsound on Windows
if platform.system() == "Windows":
    import winsound
else:
    winsound = None

LEADERBOARD_FILE = "leaderboard.txt"

class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeWithZia - Guessing Game 🎯")
        self.root.geometry("400x450")
        self.style = Style("morph")

        self.user_name = ""
        self.max_number = 100
        self.number_to_guess = 0
        self.attempts = 0
        self.total_games = 0
        self.score = 0
        self.time_limit = 30
        self.remaining_time = self.time_limit
        self.timer_id = None

        self.quotes = [
            "Don't watch the clock — do what it does: keep going.",
            "Failure is the opportunity to begin again more intelligently.",
            "Mistakes are proof you're trying!",
            "You never lose; either you win or you learn.",
            "Keep trying, genius is patience in disguise!"
        ]

        self.build_welcome_ui()

    def play_sound(self, sound_type):
        if not winsound:
            return  # Skip on non-Windows systems

        sounds = {
            "success": winsound.MB_ICONASTERISK,
            "error": winsound.MB_ICONHAND,
            "timeout": winsound.MB_ICONEXCLAMATION,
            "notify": winsound.MB_OK,
        }

        winsound.MessageBeep(sounds.get(sound_type, winsound.MB_OK))

    def build_welcome_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.name_entry = ttk.Entry(self.root)
        self.name_entry.insert(0, "Enter your name")
        self.name_entry.pack(pady=15)

        ttk.Button(self.root, text="Start Game", command=self.start_game).pack(pady=5)
        ttk.Button(self.root, text="View Leaderboard", command=self.show_leaderboard).pack(pady=5)

    def start_game(self):
        name = self.name_entry.get().strip()
        self.user_name = name if name else "User"
        Messagebox.show_info("Welcome", f"Hi {self.user_name}!\nWelcome to CodeWithZia 🎉")
        self.select_difficulty()

    def select_difficulty(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text=f"{self.user_name}, choose your difficulty:").pack(pady=10)

        ttk.Button(self.root, text="Easy (1–50)", command=lambda: self.setup_game("easy")).pack(pady=5)
        ttk.Button(self.root, text="Medium (1–100)", command=lambda: self.setup_game("medium")).pack(pady=5)
        ttk.Button(self.root, text="Hard (1–200)", command=lambda: self.setup_game("hard")).pack(pady=5)

    def setup_game(self, level):
        levels = {"easy": 50, "medium": 100, "hard": 200}
        self.max_number = levels.get(level, 100)
        self.number_to_guess = random.randint(1, self.max_number)
        self.attempts = 0
        self.remaining_time = self.time_limit

        self.play_game_ui()
        self.start_timer()

    def play_game_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.timer_label = ttk.Label(self.root, text=f"⏱️ Time Left: {self.remaining_time}s")
        self.timer_label.pack(pady=10)

        ttk.Label(self.root, text=f"Guess a number between 1 and {self.max_number}").pack(pady=5)

        self.guess_entry = ttk.Entry(self.root)
        self.guess_entry.pack(pady=10)
        self.guess_entry.focus()

        ttk.Button(self.root, text="Submit Guess", command=self.check_guess).pack(pady=10)

        self.feedback_label = ttk.Label(self.root, text="")
        self.feedback_label.pack(pady=5)

    def start_timer(self):
        self.update_timer()

    def update_timer(self):
        self.timer_label.config(text=f"⏱️ Time Left: {self.remaining_time}s")
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.time_up()

    def cancel_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def time_up(self):
        self.total_games += 1
        quote = random.choice(self.quotes)
        self.feedback_label.config(text=f"⏰ Time's Up!\n💡 {quote}")
        self.play_sound("timeout")
        self.save_to_leaderboard()
        self.root.after(4000, self.ask_play_again)

    def check_guess(self):
        guess = self.guess_entry.get().strip()
        if not guess.isdigit():
            self.feedback_label.config(text="❌ Please enter a valid number.")
            self.play_sound("error")
            return

        guess = int(guess)
        self.attempts += 1

        if guess < self.number_to_guess:
            self.feedback_label.config(text="🔼 Too low! Try a higher number.")
            self.play_sound("error")
        elif guess > self.number_to_guess:
            self.feedback_label.config(text="🔽 Too high! Try a lower number.")
            self.play_sound("error")
        else:
            self.cancel_timer()
            self.score += 1
            self.total_games += 1
            self.play_sound("success")
            Messagebox.show_info("🎉 Correct!", f"Well done {self.user_name}!\nGuessed in {self.attempts} attempts.")
            self.save_to_leaderboard()
            self.ask_play_again()

    def ask_play_again(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.play_sound("notify")
        answer = Messagebox.yesno("Play Again?", f"Score: {self.score}/{self.total_games}\nWant to play another round?")
        if answer:
            self.select_difficulty()
        else:
            Messagebox.show_info("Goodbye!", f"Thanks for playing with CWZ, {self.user_name} 👋")
            self.root.destroy()

    def save_to_leaderboard(self):
        record = f"{self.user_name},{self.score},{self.attempts},{self.total_games}\n"
        with open(LEADERBOARD_FILE, "a") as file:
            file.write(record)

    def show_leaderboard(self):
        if not os.path.exists(LEADERBOARD_FILE):
            Messagebox.show_info("Leaderboard", "No scores yet!")
            return

        with open(LEADERBOARD_FILE, "r") as file:
            lines = file.readlines()

        scores = {}
        for line in lines:
            parts = line.strip().split(",")
            if len(parts) == 4:
                name, score, _, games = parts
                score, games = int(score), int(games)
                if name in scores:
                    prev_score, prev_games = scores[name]
                    scores[name] = (prev_score + score, prev_games + games)
                else:
                    scores[name] = (score, games)

        sorted_scores = sorted(scores.items(), key=lambda x: (-x[1][0], x[1][1]))

        leaderboard_text = ""
        for i, (name, (score, games)) in enumerate(sorted_scores[:5], start=1):
            leaderboard_text += f"{i}. {name} - Score: {score} | Games: {games}\n"

        Messagebox.show_info("🏆 Leaderboard", leaderboard_text if leaderboard_text else "No entries yet.")

# Start the app
if __name__ == "__main__":
    root = tk.Tk()
    app = NumberGuessingGame(root)
    root.mainloop()
