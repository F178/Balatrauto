import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont
from PIL import Image, ImageTk
import json
import os

# Constants
CARDS_PER_PAGE = 15
COLUMNS = 5
ROWS = 3
PROFILE_FILE = "player_profile.json"
ICON_ROOT_DIR = "Icons"
RESIZE_DIMENSIONS = (60, 85)
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
FONT_PATH = "m6x11plus.ttf"  # Game's font
BACKGROUND_COLOR = "#1f1b24"

from data import JOKER_NAMES, DECK_NAMES, STAKE_NAMES, CATEGORIES

STAKE_TO_STICKER = {
    "White Stake": "White Sticker",
    "Red Stake": "Red Sticker",
    "Green Stake": "Green Sticker",
    "Black Stake": "Black Sticker",
    "Blue Stake": "Blue Sticker",
    "Purple Stake": "Purple Sticker",
    "Orange Stake": "Orange Sticker",
    "Gold Stake": "Gold Sticker",
    "No Sticker": "No Sticker"
}

CATEGORY_IMAGES = {
    "jokers": os.path.join(ICON_ROOT_DIR, "Jokers"),
    "decks": os.path.join(ICON_ROOT_DIR, "Decks"),
    "stakes": os.path.join(ICON_ROOT_DIR, "Stakes")
}


def load_profile():
    if not os.path.exists(PROFILE_FILE):
        return {
            "jokers": {name: False for name in JOKER_NAMES},
            "decks": {name: False for name in DECK_NAMES},
            "stakes": {name: False for name in STAKE_NAMES},
        }
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2)
    messagebox.showinfo("Saved", "Profile saved successfully!")

class UnlockSelector:
    def __init__(self, root, category_index):
        self.root = root
        self.category_index = category_index
        self.category, self.names = CATEGORIES[category_index]
        self.image_dir = CATEGORY_IMAGES[self.category]
        self.page = 0
        self.profile = load_profile()
        self.unlocked = self.profile.get(self.category, {name: False for name in self.names})
        self.image_refs = []

        self.container = tk.Frame(root, bg=BACKGROUND_COLOR)
        self.container.pack(padx=10, pady=10)

        self.nav_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
        self.nav_frame.pack(pady=10)

        self.prev_page_button = tk.Button(self.nav_frame, text="<", command=self.prev_page)
        self.prev_page_button.grid(row=0, column=0, padx=5)

        self.page_label = tk.Label(self.nav_frame, text="", bg=BACKGROUND_COLOR, fg="white")
        self.page_label.grid(row=0, column=1, padx=5)

        self.next_page_button = tk.Button(self.nav_frame, text=">", command=self.next_page)
        self.next_page_button.grid(row=0, column=2, padx=5)

        self.prev_category_button = tk.Button(self.nav_frame, text="Previous Section", command=self.go_to_previous_category)
        self.prev_category_button.grid(row=0, column=3, padx=10)
        if self.category_index == 0:
            self.prev_category_button.config(state="disabled")

        self.next_category_button = tk.Button(self.nav_frame, text="Next Section", command=self.go_to_next_category)
        self.next_category_button.grid(row=0, column=4, padx=10)
        if self.category_index == len(CATEGORIES) - 1:
            self.next_category_button.config(state="disabled")

        self.mode = tk.StringVar(value="Decks")
        if self.category == "decks":
            self.button_bar = tk.Frame(root, bg=BACKGROUND_COLOR)
            self.button_bar.pack(pady=(0, 10), side="bottom")

            self.save_button = tk.Button(self.button_bar, text="Save", command=self.save, bg="#FFBB00", font=("Arial", 10, "bold"))
            self.save_button.pack(side="left", padx=10)

            self.mode_toggle = tk.Button(self.button_bar, textvariable=self.mode, command=self.toggle_mode, bg="#4444FF", fg="white", font=("Arial", 10, "bold"))
            self.mode_toggle.pack(side="left")
        else:
            

            self.save_button = tk.Button(root, text="Save", command=self.save, bg="#FFBB00", font=("Arial", 10, "bold"))
            self.save_button.pack(pady=(0, 10), side="bottom")

        try:
            self.custom_font = tkFont.Font(file=FONT_PATH, size=10)
        except:
            self.custom_font = tkFont.Font(family="Courier", size=10)

        self.render_page()

    def select_stake_popup(self, deck_name):
        popup = tk.Toplevel(self.root)
        popup.title(f"Select Stake for {deck_name}")
        popup.configure(bg=BACKGROUND_COLOR)

        stake_options = STAKE_NAMES  # exclude "No Sticker" for main grid
        for i, stake in enumerate(stake_options):
            img_path = os.path.join(ICON_ROOT_DIR, "Stakes", f"{stake}.png")
            if not os.path.exists(img_path):
                continue
            try:
                img_raw = Image.open(img_path).convert("RGBA")
                img_raw.thumbnail(RESIZE_DIMENSIONS, Image.LANCZOS)
                img = Image.new("RGBA", RESIZE_DIMENSIONS, (0, 0, 0, 0))
                img.paste(img_raw, ((RESIZE_DIMENSIONS[0] - img_raw.width) // 2, (RESIZE_DIMENSIONS[1] - img_raw.height) // 2), img_raw)
                tk_img = ImageTk.PhotoImage(img)
                btn = tk.Button(popup, image=tk_img, command=lambda s=stake: self.set_stake(deck_name, s, popup), bd=0, highlightthickness=0, bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR)
                btn.image = tk_img
                btn.grid(row=i // 4, column=i % 4, padx=5, pady=5)
                self.image_refs.append(tk_img)
            except:
                pass

        # Add remove sticker button at bottom
        def remove_sticker():
            self.set_stake(deck_name, "No Sticker", popup)

        remove_btn = tk.Button(popup, text="Remove Stake Sticker", command=remove_sticker, bg="#cc4444", fg="white", font=("Arial", 10, "bold"))
        remove_btn.grid(row=2, column=0, columnspan=4, pady=(10, 5))

    def set_stake(self, deck_name, stake_name, popup_window):
        self.profile.setdefault("stakes", {})[deck_name] = stake_name
        popup_window.destroy()
        self.render_page()

    def toggle_unlock(self, name):
        self.unlocked[name] = not self.unlocked.get(name, False)
        self.render_page()

    def toggle_mode(self):
        self.mode.set("Stakes" if self.mode.get() == "Decks" else "Decks")
        self.render_page()

    def render_page(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.image_refs.clear()

        start = self.page * CARDS_PER_PAGE
        end = min(start + CARDS_PER_PAGE, len(self.names))
        page_items = self.names[start:end]

        self.page_label.config(text=f"Page {self.page + 1} / {(len(self.names) - 1) // CARDS_PER_PAGE + 1}")

        for i, name in enumerate(page_items):
            frame = tk.Frame(self.container, bd=0, bg=BACKGROUND_COLOR, width=100, height=110)
            frame.grid_propagate(False)
            frame.grid(row=i // COLUMNS, column=i % COLUMNS, padx=5, pady=5)

            if self.category == "jokers":
                image_name = f"{name}.png" if self.unlocked.get(name, False) else "Locked_Joker.png"
                fallback_image = os.path.join(self.image_dir, "Joker.png")
            elif self.category == "decks":
                image_name = f"{name}.png" if (self.unlocked.get(name, False) or name == "Red Deck") else "LockedDeck.png"
                fallback_image = os.path.join(self.image_dir, "LockedDeck.png")
            else:
                image_name = "LockedDeck.png"
                fallback_image = os.path.join(self.image_dir, "LockedDeck.png")

            image_path = os.path.join(self.image_dir, image_name)
            if not os.path.exists(image_path):
                image_path = fallback_image

            if os.path.exists(image_path):
                img_raw = Image.open(image_path).convert("RGBA")
                img_raw.thumbnail(RESIZE_DIMENSIONS, Image.LANCZOS)
                img = Image.new("RGBA", RESIZE_DIMENSIONS, (0, 0, 0, 0))
                img.paste(img_raw, ((RESIZE_DIMENSIONS[0] - img_raw.width) // 2, (RESIZE_DIMENSIONS[1] - img_raw.height) // 2), img_raw)

                if self.category == "decks":
                    stake_name = self.profile.get("stakes", {}).get(name, "No Sticker")
                    sticker_key = STAKE_TO_STICKER.get(stake_name, "No Sticker")
                    sticker_path = os.path.join(ICON_ROOT_DIR, "Stickers", f"{sticker_key}.png")
                    if os.path.exists(sticker_path):
                        sticker_img_raw = Image.open(sticker_path).convert("RGBA")
                        sticker_img_raw.thumbnail(RESIZE_DIMENSIONS, Image.LANCZOS)
                        sticker_img = Image.new("RGBA", RESIZE_DIMENSIONS, (0, 0, 0, 0))
                        sticker_img.paste(sticker_img_raw, ((RESIZE_DIMENSIONS[0] - sticker_img_raw.width) // 2, (RESIZE_DIMENSIONS[1] - sticker_img_raw.height) // 2), sticker_img_raw)
                        img = Image.alpha_composite(img, sticker_img)

                tk_img = ImageTk.PhotoImage(img)
                self.image_refs.append(tk_img)

                if self.category == "decks":
                    def on_deck_click(n=name):
                        if self.mode.get() == "Decks":
                            if n != "Red Deck":
                                self.toggle_unlock(n)
                        else:
                            if self.unlocked.get(n, False) or n == "Red Deck":
                                self.select_stake_popup(n)
                    btn = tk.Button(frame, image=tk_img, command=on_deck_click, bd=0, highlightthickness=0, cursor="hand2", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR)
                else:
                    btn = tk.Button(frame, image=tk_img, command=lambda n=name: self.toggle_unlock(n), bd=0, highlightthickness=0, cursor="hand2", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR)

                btn.image = tk_img
                btn.pack()

                font_size = 10
                try:
                    temp_font = tkFont.Font(file=FONT_PATH, size=font_size)
                except:
                    temp_font = tkFont.Font(family="Courier", size=font_size)
                while temp_font.measure(name) > 80 and font_size > 6:
                    font_size -= 1
                    temp_font.configure(size=font_size)

                name_label = tk.Label(frame, text=name, wraplength=80, justify="center", font=temp_font, bg=BACKGROUND_COLOR, fg="white")
                name_label.pack(pady=2)
            else:
                tk.Label(frame, text="[No Image]", bg=BACKGROUND_COLOR, fg="white").pack()

    def save(self):
        self.profile[self.category] = self.unlocked
        save_profile(self.profile)

    def next_page(self):
        if (self.page + 1) * CARDS_PER_PAGE < len(self.names):
            self.page += 1
            self.render_page()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.render_page()

    def go_to_next_category(self):
        next_index = self.category_index + 1
        if next_index < len(CATEGORIES):
            self.cleanup()
            UnlockSelector(self.root, next_index)

    def go_to_previous_category(self):
        prev_index = self.category_index - 1
        if prev_index >= 0:
            self.cleanup()
            UnlockSelector(self.root, prev_index)

    def cleanup(self):
        self.container.destroy()
        self.nav_frame.destroy()
        self.save_button.destroy()

def launch_gui():
    root = tk.Tk()
    root.title("Balatrauto - Unlock Tracker")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.configure(bg=BACKGROUND_COLOR)
    root.resizable(False, False)

    UnlockSelector(root, 0)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
