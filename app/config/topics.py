# app/config/topics.py

def generate_room_topics(room: str) -> list[str]:
    prefix = f"weintek/ripening/{room}"

    def s(*suffixes):
        return [f"{prefix}/{suf}" for suf in suffixes]

    topics = []

    # --- STATUS TEMPERATURE ---
    topics += s(*[
        "status/temperature/reg_temp",
        *[f"status/temperature/sensor{i}" for i in range(1, 6)],
        "status/temperature/change_over",
        "status/temperature/cool_valve_status",
        "status/temperature/heat_valve_status",
        "status/temperature/disch_temp",
    ])

    # --- ALARMS TEMPERATURE ---
    topics += s(*[f"alarms/temperature/sensor{i}" for i in range(1, 6)])

    # --- STATUS RH ---
    topics += s(*[
        "status/rh/reg_rh",
        *[f"status/rh/sensor{i}" for i in range(1, 6)],
        "status/rh/change_over",
        "status/rh/dh_valve_status",
        "status/rh/hm_valve_status",
    ])

    # --- ALARMS RH ---
    topics += s(*[f"alarms/rh/sensor{i}" for i in range(1, 6)])

    # --- PARAM TEMPERATURE ---
    topics += s(*[
        "param/temperature/target",
        "param/temperature/differential",
        "param/temperature/k_change_over",
        "param/temperature/cool_nz",
        "param/temperature/heat_nz",
        "param/temperature/ovd_cool",
        "param/temperature/ovd_cool_percent",
        "param/temperature/ovd_heat",
        "param/temperature/ovd_heat_percent",
        "param/temperature/chover_delay",
        *[f"param/temperature/monitor{i}" for i in range(1, 6)],
        "param/temperature/control_sensor",
        "param/temperature/enable_control",
        "param/temperature/humidity_mode",
        "param/temperature/heat_mode",
        "param/temperature/vent_mode",
        "param/temperature/dich_monitor",
    ])

    # --- PARAM RH ---
    topics += s(*[
        "param/rh/target",
        "param/rh/differential",
        "param/rh/k_change_over",
        "param/rh/dh_nz",
        "param/rh/hm_nz",
        "param/rh/ovd_dh",
        "param/rh/ovd_dh_percent",
        "param/rh/ovd_hm",
        "param/rh/ovd_hm_percent",
        "param/rh/chover_delay",
        *[f"param/rh/monitor{i}" for i in range(1, 6)],
        "param/rh/control_sensor",
    ])

    # --- PARAM GAS & VENT ---
    topics += s(*[
        "param/gas/inyec_time",
        "param/gas/gas_on_off",
        "param/gas/ovd_gas",
        "param/vent/vent_interval",
        "param/vent/vent_delay",
        "param/vent/ovd_vent",
    ])

    return topics


# Diccionario final por sala
ROOM_TOPICS = {
    "room1": generate_room_topics("room1"),
    "room2": generate_room_topics("room2"),
    "room3": generate_room_topics("room3"),
}

ALL_TOPICS = [topic for topics in ROOM_TOPICS.values() for topic in topics]
