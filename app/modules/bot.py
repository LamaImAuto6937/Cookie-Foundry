import pychrome
import requests
import time
import json
import threading

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

    def get_cookies_production(self):
        result = self.game_tab.call_method("Runtime.evaluate", expression="Game.cookiesPs")
        return result["result"]["value"]

    def get_wrinklers(self):
        result = self.game_tab.call_method(
            "Runtime.evaluate",
            expression="""
            JSON.stringify(
                Game.wrinklers
                    .filter(w => w.phase === 2)
                    .map(w => ({id: w.id, health: w.hp, age: w.age, type: w.type}))
            )
            """
        )
        if "exceptionDetails" in result:
            print("JS-Error:", result["exceptionDetails"])
            return []
        return json.loads(result["result"]["value"])

    def click_wrinkler_by_id(self, wrinkler_id):
        expression = f"""
        (function() {{
            var w = Game.wrinklers.find(function(wr) {{ return wr.id === {wrinkler_id}; }});
            if (w) {{ w.hp = 0; return true; }}
            return false;
        }})()
        """
        result = self.game_tab.call_method("Runtime.evaluate", expression=expression)
        return result.get("result", {}).get("value", False)
    
    def wrinkler_watcher(self, max_wrinklers, stop_event):
        while not stop_event.is_set():
            wrinklers = self.get_wrinklers()
            if len(wrinklers) >= max_wrinklers:
                for wrinkler in wrinklers:
                    while not stop_event.is_set():
                        current_wrinklers = self.get_wrinklers()
                        current_wrinkler = next(
                            (w for w in current_wrinklers if w.get("id") == wrinkler["id"]),
                            None,
                        )
                        if not current_wrinkler or current_wrinkler.get("health", 0) <= 0:
                            break
                        self.click_wrinkler_by_id(wrinkler["id"])
                        time.sleep(0.1)


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
