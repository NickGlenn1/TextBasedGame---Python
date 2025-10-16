#!/usr/bin/env python3
"""
Pirate Islands — a text based game

Theme
-----
You're a pirate sailing between small islands. Explore, collect the pirate
loot, and return to Pirate Cove once you have everything to claim victory.

How to run
----------
python3 pirate_islands.py

Basic commands
--------------
- go <north|south|east|west>  (aliases: n, s, e, w)
- take <item>                 (alias: get <item>, pick <item>)
- drop <item>
- look                        (alias: l)
- inventory                   (aliases: i, inv, bag)
- help                        (alias: h, ?)
- quit                        (alias: exit)

Goal
----
Collect all TREASURE_ITEMS and return to 'Pirate Cove'.


"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set
import textwrap

# ---------------------------
# Game Data
# ---------------------------

TREASURE_ITEMS: Set[str] = {
    "cutlass", "compass", "doubloon", "rum", "spyglass", "map piece"
}

@dataclass
class Island:
    name: str
    description: str
    items: List[str] = field(default_factory=list)
    exits: Dict[str, str] = field(default_factory=dict)  # direction -> island.name

# World layout: a simple graph. 
WORLD: Dict[str, Island] = {
    "Pirate Cove": Island(
        name="Pirate Cove",
        description=(
            "Your secret hideout: a crescent beach with a beached skiff and a fire pit.\n"
            "Legends say a captain who returns with the full trove becomes ruler of the winds."
        ),
        items=["note"],
        exits={"east": "Skull Key", "south": "Mermaid Shoals"},
    ),
    "Skull Key": Island(
        name="Skull Key",
        description=(
            "A jagged islet shaped like a skull. Gulls circle overhead; something glints in a crevice."
        ),
        items=["spyglass"],
        exits={"west": "Pirate Cove", "east": "Blackwater Cay"},
    ),
    "Blackwater Cay": Island(
        name="Blackwater Cay",
        description=(
            "Waters here are inky and calm. A half‑sunken sloop lists against coral."
        ),
        items=["compass"],
        exits={"west": "Skull Key", "south": "Rumrunner Atoll"},
    ),
    "Rumrunner Atoll": Island(
        name="Rumrunner Atoll",
        description=(
            "Palm shadows dapple caches of old bottles. Footprints criss‑cross the sand."
        ),
        items=["rum"],
        exits={"north": "Blackwater Cay", "west": "Mermaid Shoals"},
    ),
    "Mermaid Shoals": Island(
        name="Mermaid Shoals",
        description=(
            "Shallow turquoise flats sing with the tide. A carved stone points somewhere unseen."
        ),
        items=["map piece"],
        exits={"north": "Pirate Cove", "east": "Rumrunner Atoll", "south": "Cutlass Bay"},
    ),
    "Cutlass Bay": Island(
        name="Cutlass Bay",
        description=(
            "Crescent bay where waves sharpen on a reef. Something metallic lies under kelp."
        ),
        items=["cutlass"],
        exits={"north": "Mermaid Shoals", "east": "Doubloon Point"},
    ),
    "Doubloon Point": Island(
        name="Doubloon Point",
        description=(
            "A rocky spit with tide pools full of tiny stars. A coin winks in the foam."
        ),
        items=["doubloon"],
        exits={"west": "Cutlass Bay"},
    ),
}

START_ISLAND = "Pirate Cove"

# ---------------------------
# Game Engine
# ---------------------------

@dataclass
class Player:
    location: str = START_ISLAND
    inventory: List[str] = field(default_factory=list)

    def has_all_treasure(self) -> bool:
        return TREASURE_ITEMS.issubset(set(self.inventory))


def wrap(text: str) -> str:
    return textwrap.fill(text, width=80)


def title(text: str) -> None:
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)


def show_instructions() -> None:
    title("How to Play")
    print(wrap(
        "Sail between islands, collect pirate loot, and return to Pirate Cove with the lot.\n"
        "Use simple commands like 'go east', 'take compass', 'inventory', and 'look'."
    ))
    print("\nCommands: go <n|s|e|w>, look, take <item>, drop <item>, inventory, help, quit")


def show_location(player: Player) -> None:
    island = WORLD[player.location]
    title(island.name)
    print(wrap(island.description))
    if island.items:
        print("\nYou spot: " + ", ".join(island.items))
    if island.exits:
        exit_str = ", ".join(f"{d} -> {name}" for d, name in island.exits.items())
        print("Exits: " + exit_str)


def parse_direction(token: str) -> str | None:
    mapping = {
        "n": "north", "north": "north",
        "s": "south", "south": "south",
        "e": "east",  "east":  "east",
        "w": "west",  "west":  "west",
    }
    return mapping.get(token.lower())


def handle_go(player: Player, args: List[str]) -> None:
    if not args:
        print("Go where? Try 'go north' or 'go n'.")
        return
    direction = parse_direction(args[0])
    if not direction:
        print("That's not a direction. Use north/south/east/west (or n/s/e/w).")
        return
    island = WORLD[player.location]
    if direction not in island.exits:
        print("No passage that way.")
        return
    player.location = island.exits[direction]
    show_location(player)


def handle_look(player: Player) -> None:
    show_location(player)


def handle_take(player: Player, args: List[str]) -> None:
    if not args:
        print("Take what?")
        return
    item = " ".join(args).lower()
    island = WORLD[player.location]
    # support simple partial matches
    matches = [i for i in island.items if item in i.lower()]
    if not matches:
        print("You don't see that here.")
        return
    found = matches[0]
    island.items.remove(found)
    player.inventory.append(found)
    print(f"You take the {found}.")
    if player.has_all_treasure() and player.location == "Pirate Cove":
        print_victory()


def handle_drop(player: Player, args: List[str]) -> None:
    if not args:
        print("Drop what?")
        return
    item = " ".join(args).lower()
    # partial match from inventory
    matches = [i for i in player.inventory if item in i.lower()]
    if not matches:
        print("You aren't carrying that.")
        return
    found = matches[0]
    player.inventory.remove(found)
    WORLD[player.location].items.append(found)
    print(f"You drop the {found}.")


def handle_inventory(player: Player) -> None:
    if not player.inventory:
        print("Your bag is empty.")
        return
    print("You carry: " + ", ".join(player.inventory))
    missing = TREASURE_ITEMS - set(player.inventory)
    if missing:
        print("Still missing: " + ", ".join(sorted(missing)))
    else:
        print("You've collected the full trove! Return to Pirate Cove to claim victory.")


def print_victory() -> None:
    title("Victory!")
    print(wrap(
        "You slam the chest on the sand and spill the treasures at the fire pit. The winds\n"
        "shift in your favor. Songs will be sung of your name — Captain of the Isles!"
    ))


def check_victory_on_move(player: Player) -> None:
    if player.location == "Pirate Cove" and player.has_all_treasure():
        print_victory()


def handle_help() -> None:
    show_instructions()


def handle_command(player: Player, command: str) -> bool:
    tokens = [t for t in command.strip().split() if t]
    if not tokens:
        return True  # continue game loop
    verb, *args = tokens
    verb = verb.lower()

    if verb in {"go", "move"}:
        handle_go(player, args)
        check_victory_on_move(player)
        return True
    if verb in {"n", "s", "e", "w", "north", "south", "east", "west"}:
        handle_go(player, [verb])
        check_victory_on_move(player)
        return True
    if verb in {"look", "l"}:
        handle_look(player)
        return True
    if verb in {"take", "get", "pick"}:
        handle_take(player, args)
        return True
    if verb == "drop":
        handle_drop(player, args)
        return True
    if verb in {"inventory", "inv", "i", "bag"}:
        handle_inventory(player)
        return True
    if verb in {"help", "h", "?"}:
        handle_help()
        return True
    if verb in {"quit", "exit"}:
        print("Fair winds, captain.")
        return False

    print("I don't understand that command. Type 'help' for options.")
    return True


# ---------------------------
# Menu & Game Loop
# ---------------------------

def main_menu() -> None:
    title("PIRATE ISLANDS — Text Adventure")
    print("1) Start Game")
    print("2) Instructions")
    print("3) Quit")


def start_game() -> None:
    player = Player()
    show_location(player)
    while True:
        try:
            cmd = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\nFair winds, captain.")
            break
        if not handle_command(player, cmd):
            break


def run() -> None:
    while True:
        main_menu()
        choice = input("Select: ").strip()
        if choice == "1":
            start_game()
        elif choice == "2":
            show_instructions()
            input("\n(Press Enter to return to menu)")
        elif choice == "3":
            print("Goodbye!")
            return
        else:
            print("Choose 1, 2, or 3.")


if __name__ == "__main__":
    run()
