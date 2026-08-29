#!/usr/bin/env python3
"""
=============================================================
 Zombie Survival — Multiplayer Server
 Compatible with zombie.py (create / join / lobby / start / state)
=============================================================
 Run FIRST before any game clients:

   python multiplayer_server.py

 Default port: 5050
 Clients use SERVER_HOST = "127.0.0.1" (same PC) or your LAN IP.
=============================================================
"""
from __future__ import annotations

import json
import random
import socket
import string
import threading
import traceback
import uuid

HOST = "0.0.0.0"
PORT = 5050
MAX_PLAYERS = 4
CODE_LEN = 6

LOBBY_COLORS = [
    (200, 40, 40),
    (40, 100, 220),
    (40, 180, 80),
    (230, 180, 40),
    (180, 60, 180),
    (40, 200, 200),
    (230, 120, 40),
    (240, 140, 180),
]

lock = threading.Lock()
rooms: dict = {}  # code -> room


def gen_code() -> str:
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=CODE_LEN))
        if code not in rooms:
            return code


def send(conn: socket.socket, obj: dict) -> None:
    try:
        conn.sendall((json.dumps(obj, separators=(",", ":")) + "\n").encode("utf-8"))
    except OSError:
        pass


def broadcast(room: dict, obj: dict, exclude_id: str | None = None) -> None:
    dead = []
    for pid, p in list(room["players"].items()):
        if exclude_id and pid == exclude_id:
            continue
        try:
            p["conn"].sendall((json.dumps(obj, separators=(",", ":")) + "\n").encode("utf-8"))
        except OSError:
            dead.append(pid)
    for pid in dead:
        room["players"].pop(pid, None)


def lobby_snapshot(room: dict) -> dict:
    players = []
    for pid, p in room["players"].items():
        players.append({
            "id": pid,
            "username": p.get("username") or "PLAYER",
            "character": p.get("character") or "Survivor",
            "gun_skin": p.get("gun_skin") or "steel",
            "ready": bool(p.get("ready")),
            "host": pid == room["host_id"],
            "color": list(p.get("color", LOBBY_COLORS[0])),
            "slot": int(p.get("slot", 0)),
        })
    players.sort(key=lambda x: x.get("slot", 0))
    return {
        "type": "lobby",
        "players": players,
        "code": room["code"],
        "difficulty": room.get("difficulty", "normal"),
        "started": bool(room.get("started")),
        "max": MAX_PLAYERS,
    }


def players_msg(room: dict) -> dict:
    return {
        "type": "players",
        "players": [
            {
                "id": pid,
                "username": p.get("username") or "PLAYER",
                "character": p.get("character") or "Survivor",
                "host": pid == room["host_id"],
            }
            for pid, p in room["players"].items()
        ],
    }


def assign_slot_color(room: dict):
    used_slots = {p.get("slot") for p in room["players"].values()}
    used_colors = {tuple(p.get("color", (0, 0, 0))) for p in room["players"].values()}
    slot = 0
    while slot in used_slots:
        slot += 1
    color = LOBBY_COLORS[slot % len(LOBBY_COLORS)]
    for c in LOBBY_COLORS:
        if tuple(c) not in used_colors:
            color = c
            break
    return slot, color


def find_room_for(pid: str):
    for code, room in rooms.items():
        if pid in room["players"]:
            return code, room
    return None, None


def remove_player(pid: str, room_code: str | None = None) -> None:
    with lock:
        room = None
        if room_code and room_code in rooms:
            room = rooms[room_code]
        else:
            room_code, room = find_room_for(pid)
        if not room or pid not in room["players"]:
            return
        print(f"  leave {pid} from {room_code}")
        del room["players"][pid]
        if not room["players"]:
            rooms.pop(room_code, None)
            print(f"  room {room_code} closed")
            return
        if room["host_id"] == pid:
            room["host_id"] = next(iter(room["players"]))
            print(f"  new host {room['host_id']}")
        snap = lobby_snapshot(room)
        broadcast(room, snap)
        broadcast(room, players_msg(room))


def handle_client(conn: socket.socket, addr) -> None:
    pid = uuid.uuid4().hex[:8]
    room_code = None
    buf = ""
    print(f"[+] connect {addr} -> {pid}")
    try:
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except OSError:
        pass
    try:
        while True:
            try:
                data = conn.recv(16384)
            except OSError:
                break
            if not data:
                break
            buf += data.decode("utf-8", errors="ignore")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(msg, dict):
                    continue
                action = msg.get("action")

                # ---------- CREATE ----------
                if action == "create":
                    with lock:
                        code = gen_code()
                        rooms[code] = {
                            "code": code,
                            "host_id": pid,
                            "difficulty": "normal",
                            "started": False,
                            "players": {
                                pid: {
                                    "conn": conn,
                                    "username": str(msg.get("username") or "HOST")[:20],
                                    "character": str(msg.get("character") or "Survivor")[:24],
                                    "gun_skin": str(msg.get("gun_skin") or "steel")[:24],
                                    "ready": True,
                                    "color": LOBBY_COLORS[0],
                                    "slot": 0,
                                }
                            },
                        }
                        room_code = code
                    send(conn, {"type": "created", "code": code, "id": pid})
                    send(conn, lobby_snapshot(rooms[code]))
                    send(conn, players_msg(rooms[code]))
                    print(f"[*] room {code} created by {pid}")

                # ---------- JOIN ----------
                elif action == "join":
                    code = str(msg.get("code", "")).upper().strip()
                    with lock:
                        room = rooms.get(code)
                        if not room:
                            send(conn, {"type": "error", "message": "ROOM NOT FOUND"})
                            continue
                        if room.get("started"):
                            send(conn, {"type": "error", "message": "GAME ALREADY STARTED"})
                            continue
                        if len(room["players"]) >= MAX_PLAYERS:
                            send(conn, {"type": "error", "message": "ROOM FULL (4/4)"})
                            continue
                        # already in another room?
                        if room_code and room_code in rooms and pid in rooms[room_code]["players"]:
                            del rooms[room_code]["players"][pid]
                        slot, color = assign_slot_color(room)
                        room["players"][pid] = {
                            "conn": conn,
                            "username": str(msg.get("username") or "PLAYER")[:20],
                            "character": str(msg.get("character") or "Survivor")[:24],
                            "gun_skin": str(msg.get("gun_skin") or "steel")[:24],
                            "ready": False,
                            "color": color,
                            "slot": slot,
                        }
                        room_code = code
                        is_host = pid == room["host_id"]
                    send(conn, {"type": "joined", "code": code, "id": pid, "host": is_host})
                    with lock:
                        if code in rooms:
                            broadcast(rooms[code], lobby_snapshot(rooms[code]))
                            broadcast(rooms[code], players_msg(rooms[code]))
                    print(f"[*] {pid} joined {code}")

                # ---------- LEAVE ----------
                elif action == "leave":
                    remove_player(pid, room_code)
                    room_code = None

                # ---------- LOBBY UPDATE (class / gun / ready / name) ----------
                elif action == "lobby":
                    with lock:
                        room = rooms.get(room_code) if room_code else None
                        if not room or pid not in room["players"]:
                            continue
                        p = room["players"][pid]
                        if msg.get("username"):
                            p["username"] = str(msg["username"])[:20]
                        if msg.get("character"):
                            p["character"] = str(msg["character"])[:24]
                        if msg.get("gun_skin"):
                            p["gun_skin"] = str(msg["gun_skin"])[:24]
                        if "ready" in msg:
                            p["ready"] = bool(msg["ready"])
                            if pid == room["host_id"]:
                                p["ready"] = True
                        broadcast(room, lobby_snapshot(room))
                        broadcast(room, players_msg(room))

                # ---------- START ----------
                elif action == "start":
                    with lock:
                        room = rooms.get(room_code) if room_code else None
                        if not room:
                            send(conn, {"type": "error", "message": "NOT IN A ROOM"})
                            continue
                        if pid != room["host_id"]:
                            send(conn, {"type": "error", "message": "ONLY HOST CAN START"})
                            continue
                        diff = msg.get("difficulty", room.get("difficulty", "normal"))
                        if diff not in ("normal", "hardcore", "nightmare"):
                            diff = "normal"
                        room["difficulty"] = diff
                        room["started"] = True
                        broadcast(room, {"type": "start", "difficulty": diff})
                    print(f"[*] room {room_code} STARTED ({diff})")

                # ---------- GAME STATE RELAY ----------
                elif action == "state":
                    with lock:
                        room = rooms.get(room_code) if room_code else None
                        if not room:
                            continue
                        out = {
                            "type": "state",
                            "id": pid,
                            "x": msg.get("x", 0),
                            "y": msg.get("y", 0),
                            "character": msg.get("character", "Survivor"),
                            "username": msg.get("username", "PLAYER"),
                            "shooting": bool(msg.get("shooting", False)),
                            "dead": bool(msg.get("dead", False)),
                            "wave": int(msg.get("wave", 1) or 1),
                            "difficulty": msg.get("difficulty", room.get("difficulty", "normal")),
                        }
                        broadcast(room, out, exclude_id=pid)

                # ---------- KICK ----------
                elif action == "kick":
                    with lock:
                        room = rooms.get(room_code) if room_code else None
                        if not room or pid != room["host_id"]:
                            continue
                        target = msg.get("id")
                        if target and target in room["players"] and target != pid:
                            tconn = room["players"][target]["conn"]
                            send(tconn, {"type": "error", "message": "KICKED BY HOST"})
                            try:
                                tconn.close()
                            except OSError:
                                pass
                            del room["players"][target]
                            broadcast(room, lobby_snapshot(room))
                            broadcast(room, players_msg(room))

                # ---------- PING ----------
                elif action == "ping":
                    send(conn, {"type": "pong"})

    except Exception:
        traceback.print_exc()
    finally:
        remove_player(pid, room_code)
        try:
            conn.close()
        except OSError:
            pass
        print(f"[-] disconnect {addr} id={pid}")


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((HOST, PORT))
    except OSError as e:
        print(f"ERROR: cannot bind {HOST}:{PORT} — {e}")
        print("Is another server already running on this port?")
        return
    srv.listen(32)
    print("=" * 50)
    print(" Zombie Survival multiplayer server")
    print(f" Listening on {HOST}:{PORT}")
    print(" Clients: SERVER_HOST=127.0.0.1  SERVER_PORT=5050")
    print(" LAN: set SERVER_HOST to this PC's IP in zombie.py")
    print("=" * 50)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
