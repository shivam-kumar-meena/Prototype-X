import json, os, re

class MemoryStore:
    def __init__(self, path="data/memory.json"):
        self.path = path
        self.data = {"facts": {}, "history": []}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_history(self, role, content):
        self.data["history"].append({"role": role, "content": content})
        self.save()

    def clear(self):
        self.data = {"facts": {}, "history": []}
        self.save()

    def get_fact(self, key):
        return self.data["facts"].get(key)

    def update_from_text(self, text):
        lowered = text.lower()
        if "mera naam" in lowered or "my name is" in lowered:
            match = re.search(r"(?:mera naam|my name is)\s+([A-Za-z\u0900-\u097F]+)", lowered)
            if match:
                name = match.group(1).capitalize()
                self.data["facts"]["name"] = name
        if "i live in" in lowered or "main" in lowered and "se" in lowered and "hu" in lowered:
            city = re.search(r"(?:i live in|main)\s+([A-Za-z\u0900-\u097F]+)", lowered)
            if city:
                self.data["facts"]["city"] = city.group(1).capitalize()
        self.save()
        return self.data["facts"]

    def summary_prompt(self):
        if not self.data["facts"]:
            return ""
        facts = ", ".join([f"{k}: {v}" for k, v in self.data["facts"].items()])
        return f"User facts → {facts}"