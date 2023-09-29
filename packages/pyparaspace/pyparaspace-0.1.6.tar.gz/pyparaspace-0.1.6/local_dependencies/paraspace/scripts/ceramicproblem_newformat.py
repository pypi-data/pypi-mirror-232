import json

for n_kilns, n_pieces in [(1, 2), (2, 4), (2, 6), (4, 6), (1, 10), (5, 10), (2, 16), (3, 16)]:
    timelines = []
    kiln_timelines = []

    for kiln_idx in range(n_kilns):
        kiln_name = f"kiln{kiln_idx}"
        kiln_timelines.append(kiln_name)
        timelines.append({
            "name": kiln_name,
            "static_tokens": [{"value": "Ready", "capacity": 0, "const_time": {"Fact": [0, None]}, "conditions": []}],
            "token_types": [
                {"value": "Ready", "duration_limits": [1, None], "conditions":[[
                    {"timeline_ref": kiln_name, "temporal_relationship": "MetBy", "value": "Fire", "amount": 0}
                ]], "capacity": 0},
                {"value": "Fire", "duration_limits": [20,20], "conditions":[[
                    {"timeline_ref": kiln_name, "temporal_relationship": "MetBy", "value": "Ready", "amount": 0}
                ]], "capacity": 2}
            ]
        })

    piece_param_types = [(5, 2), (8, 3), (11, 1)]
    pieces = []
    while len(pieces) < n_pieces:
        pieces.append(piece_param_types[len(pieces) % len(piece_param_types)])

    for piece_idx, (bake_time, treat_time) in enumerate(pieces):
        piece_name = f"piece{piece_idx}"
        timelines.append({
            "name": piece_name,
            "static_tokens": [],
            "token_types": [
                {"value": "Baking", "duration_limits": [bake_time, bake_time], "conditions":[[
                    {"timeline_ref": kiln_name, "temporal_relationship": "Cover", "value": "Fire", "amount": 1}
                    for kiln_name in kiln_timelines
                ]], "capacity": 0},
                {"value": "Baked", "duration_limits": [1, None], "conditions":[[
                    {"timeline_ref": piece_name, "temporal_relationship": "MetBy", "value": "Baking", "amount": 0}
                ]], "capacity": 0},
                {"value": "Treating", "duration_limits": [treat_time,treat_time], "conditions":[[
                    {"timeline_ref": piece_name, "temporal_relationship": "MetBy", "value": "Baked", "amount": 0}
                ]], "capacity": 0},
                {"value": "Treated", "duration_limits": [1, None], "conditions":[[
                    {"timeline_ref": piece_name, "temporal_relationship": "MetBy", "value": "Treating", "amount": 0}
                ]], "capacity": 0},
            ]
        })

    for structure_idx in range(n_pieces // 2):
        structure_name = f"structure{structure_idx}"
        timelines.append({
            "name": structure_name,
            "static_tokens": [{"value": "Baked", "capacity": 0, "const_time": "Goal", "conditions": []}],
            "token_types": [
                {"value": "Assembling", "duration_limits": [1, 1], "conditions":[[
                    {"timeline_ref": f"piece{2*structure_idx}", "temporal_relationship": "Cover", "value": "Treated", "amount": 0}
                ],[
                    {"timeline_ref": f"piece{2*structure_idx+1}", "temporal_relationship": "Cover", "value": "Treated", "amount": 0}
                ]], "capacity": 0},
                {"value": "Assembled", "duration_limits": [treat_time,treat_time], "conditions":[[
                    {"timeline_ref": structure_name, "temporal_relationship": "MetBy", "value": "Assembling", "amount": 0}
                ]], "capacity": 0},
                {"value": "Baking", "duration_limits": [3, 3], "conditions":[[
                    {"timeline_ref": structure_name, "temporal_relationship": "MetBy", "value": "Assembled", "amount": 0}
                ],[
                    {"timeline_ref": kiln_name, "temporal_relationship": "Cover", "value": "Fire", "amount": 1}
                    for kiln_name in kiln_timelines
                ]], "capacity": 0},
                {"value": "Baked", "duration_limits": [1, None], "conditions":[[
                    {"timeline_ref": structure_name, "temporal_relationship": "MetBy", "value": "Baking", "amount": 0}
                ]], "capacity": 0},
            ]
        })

    with open(f"examples/ceramic_{n_kilns}m_{n_pieces}j.json", "w") as f:
        json.dump({"timelines": timelines}, f)
