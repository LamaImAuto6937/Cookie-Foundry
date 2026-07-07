import pychrome
import requests
import time
import json
import threading
import tkinter as tk
import queue

class CookieFoundry:
    def __init__(self):
        self.browser = pychrome.Browser(url="http://127.0.0.1:9222")
        self.tabs_raw = requests.get("http://127.0.0.1:9222/json").json()

        self._stop_events = {}
        self.get_game_tab()
        self.game_tab.start()

    # Threading management for modes
    def start_mode(self, name, target_method, *args):
        stop_event = threading.Event()
        thread = threading.Thread(target=target_method, args=(*args, stop_event), daemon=True)
        thread.start()
        self._stop_events[name] = (thread, stop_event)

    def stop_mode(self, name):
        if name in self._stop_events:
            thread, stop_event = self._stop_events[name]
            stop_event.set()
            thread.join()
            del self._stop_events[name]

    def get_game_tab(self):
        for entry in self.tabs_raw:
            if "Cookie Clicker" in entry["title"]:
                self.game_tab = self.browser.list_tab()[self.tabs_raw.index(entry)]
                return

        print("Tab not found")
        exit(1)
    
    def get_cookies(self):
        result = self.game_tab.call_method("Runtime.evaluate", expression="Game.cookies")
        return result["result"]["value"]
    
    def get_shimmers(self):
        # Golden Cookies are called shimmers ingame
        result = self.game_tab.call_method(
            "Runtime.evaluate",
            expression="JSON.stringify(Game.shimmers.map(s => ({id: s.id, type: s.type, wrath: s.wrath})))"
        )
        if "exceptionDetails" in result:
            print("JS-Error:", result["exceptionDetails"])
            return []
        return json.loads(result["result"]["value"])

    def click_shimmer_by_id(self, shimmer_id):
        expression = f"""
        (function() {{
            var s = Game.shimmers.find(function(sh) {{ return sh.id === {shimmer_id}; }});
            if (s) {{ s.pop(); return true; }}
            return false;
        }})()
        """
        result = self.game_tab.call_method("Runtime.evaluate", expression=expression)
        return result.get("result", {}).get("value", False)

    def golden_cookie_watcher(self, delay_seconds, stop_event):
        known_shimmers = {}

        while not stop_event.is_set():
            shimmers = self.get_shimmers()
            current_ids = set()

            for shimmer in shimmers:
                if shimmer["type"] != "golden":
                    continue
                sid = shimmer["id"]
                current_ids.add(sid)

                if sid not in known_shimmers:
                    known_shimmers[sid] = time.time()

            for sid in list(known_shimmers):
                if sid not in current_ids:
                    del known_shimmers[sid]
                    continue

                elapsed = time.time() - known_shimmers[sid]
                if elapsed >= delay_seconds:
                    self.click_shimmer_by_id(sid)
                    del known_shimmers[sid]

            stop_event.wait(0.5)

    def auto_clicker(self, clicks_per_second, stop_event):
        while not stop_event.is_set():
            self.game_tab.call_method("Runtime.evaluate", expression="Game.ClickCookie()")
            stop_event.wait(1 / clicks_per_second)

class CookieFoundryGUI:
    def __init__(self, cookie_foundry):
        self.foundry = cookie_foundry
        self.log_queue = queue.Queue()

        self.root = tk.Tk()
        self.root.title("Cookie Foundry")
        self.root.geometry("400x300")

        self._build_widgets()
        self._poll_log_queue()

    def _build_widgets(self):
        # Auto-Clicker Steuerung
        tk.Label(self.root, text="Auto-Clicker (Klicks/Sekunde):").pack(pady=(10, 0))
        self.clicks_entry = tk.Entry(self.root)
        self.clicks_entry.insert(0, "60")
        self.clicks_entry.pack()

        self.clicker_button = tk.Button(
            self.root, text="Auto-Clicker starten", command=self.toggle_clicker
        )
        self.clicker_button.pack(pady=5)

        # Golden Cookie Watcher Steuerung
        tk.Label(self.root, text="Golden Cookie Delay (Sekunden):").pack(pady=(10, 0))
        self.delay_entry = tk.Entry(self.root)
        self.delay_entry.insert(0, "2")
        self.delay_entry.pack()

        self.watcher_button = tk.Button(
            self.root, text="Golden Cookie Watcher starten", command=self.toggle_watcher
        )
        self.watcher_button.pack(pady=5)

        # Log-Ausgabe
        self.log_text = tk.Text(self.root, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    def toggle_clicker(self):
        if "auto_clicker" in self.foundry._stop_events:
            self.foundry.stop_mode("auto_clicker")
            self.clicker_button.config(text="Auto-Clicker starten")
        else:
            cps = float(self.clicks_entry.get())
            self.foundry.start_mode("auto_clicker", self.foundry.auto_clicker, cps)
            self.clicker_button.config(text="Auto-Clicker stoppen")

    def toggle_watcher(self):
        if "golden_cookie_watcher" in self.foundry._stop_events:
            self.foundry.stop_mode("golden_cookie_watcher")
            self.watcher_button.config(text="Golden Cookie Watcher starten")
        else:
            delay = float(self.delay_entry.get())
            self.foundry.start_mode("golden_cookie_watcher", self.foundry.golden_cookie_watcher, delay)
            self.watcher_button.config(text="Golden Cookie Watcher stoppen")

    def log(self, message):
        self.log_queue.put(message)

    def _poll_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get_nowait()
            self.log_text.config(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(200, self._poll_log_queue)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    cookie_foundry = CookieFoundry()
    gui = CookieFoundryGUI(cookie_foundry)
    gui.run()

