import re
import threading
from alvik_control import BLEDevice

def parse_command(cmd):
    """
    Zerlegt einen Befehl im Format "forward(30,cm)" oder "left(90,grad)" in seine Bestandteile.
    Bei Erfolg wird der BLE-Befehl als String im Format "F;30;cm" bzw. "L;90;grad" zurückgegeben.
    """
    pattern = r"(\w+)\((\d+),(\w+)\)"
    match = re.match(pattern, cmd.strip())
    if match:
        action, value, unit = match.groups()
        action_lower = action.lower()
        action_map = {
            "forward": "F",
            "backward": "B",
            "left": "L",
            "right": "R"
        }
        if action_lower in action_map:
            # Für Drehbefehle (left, right) muss als Einheit "grad" verwendet werden.
            if action_lower in ["left", "right"] and unit.lower() != "grad":
                print("Für Drehbefehle muss die Einheit 'grad' verwendet werden.")
                return None
            return f"{action_map[action_lower]};{value};{unit.lower()}"
    return None

# BLEDevice-Instanz erstellen und verbinden
device = BLEDevice("AvilkRoboterMohi")

def input_loop():
    """
    Diese Schleife läuft in einem separaten Thread und wartet auf Eingaben.
    Jeder gültige Befehl wird geparst und der Nachrichtenwarteschlange hinzugefügt.
    """
    print("Verfügbare Befehle:")
    print("  forward(30,cm)  - Vorwärts fahren")
    print("  backward(30,cm) - Rückwärts fahren")
    print("  left(90,grad)   - Links drehen")
    print("  right(90,grad)  - Rechts drehen")
    while True:
        cmd = input("Befehl: ")
        if cmd.lower() == "exit":
            device.send(None)
            break
        parsed = parse_command(cmd)
        if parsed:
            device.send(parsed)
        else:
            print("Ungültiger Befehl. Bitte z.B. 'forward(30,cm)' oder 'left(90,grad)' eingeben.")

# Starte die Eingabeschleife in einem eigenen Thread
threading.Thread(target=input_loop, daemon=True).start()

# Starte den asynchronen Loop, der die Verbindung herstellt und Befehle sendet
device.run()
