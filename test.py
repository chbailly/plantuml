participants = ["A", "B", "C"]

stack = [
    "B.func1->ret2", [
        "loop myloop", [
            "alt ok", [
                "B._test$func3", [
                    ".func5", [
                        ".func2", [
                            "C.CREATE",
                            ".func4"
                        ]
                    ],
                    ".func6"
                ]
            ],
            "else test1", [".ok"],
            "else test2", [".nok"],
            "C.func"
        ]
    ]
]



c = participants[0]

def display(current, node, level, fmt='mermaid'):
    """Recursively traverse `node` and return a list of sequence diagram lines.

    Returns a list of strings (lines). Caller can join/print them.
    """
    lines = []
    indent = " " * (level * 3)
    i = 0

    is_mermaid = (fmt.lower() == 'mermaid')

    while i < len(node):
        x = node[i]

        # If a list occurs by itself, recurse using the same current participant.
        if isinstance(x, list):
            lines.extend(display(current, x, level, fmt))
            i += 1
            continue

        # Branching constructs: alt / opt with optional else blocks.
        if x.startswith(("alt", "opt")):
            lines.append(f"{indent}{x}")
            if i + 1 < len(node) and isinstance(node[i + 1], list):
                lines.extend(display(current, node[i + 1], level + 1, fmt))
                i += 2
            else:
                i += 1

            while i < len(node) and isinstance(node[i], str) and node[i].startswith("else"):
                lines.append(f"{indent}{node[i]}")
                if i + 1 < len(node) and isinstance(node[i + 1], list):
                    lines.extend(display(current, node[i + 1], level + 1, fmt))
                    i += 2
                else:
                    i += 1

            lines.append(f"{indent}end")
            continue

        # loop construct
        if x.startswith("loop"):
            lines.append(f"{indent}{x}")
            if i + 1 < len(node) and isinstance(node[i + 1], list):
                lines.extend(display(current, node[i + 1], level + 1, fmt))
                i += 2
            else:
                i += 1
            lines.append(f"{indent}end")
            continue

        # self-invocation: .method (optionally followed by a nested block)
        if x.startswith("."):
            elem = x[1:].replace("$", ".")
            if i + 1 < len(node) and isinstance(node[i + 1], list):
                # self-invocation with nested block
                arrow_call = f"{indent}{current} -> {current}: {elem}"
                lines.append(arrow_call)
                lines.append(f"{indent}activate {current}")
                lines.extend(display(current, node[i + 1], level + 1, fmt))
                lines.append(f"{indent}deactivate {current}")
                i += 2
            else:
                # simple self call: choose arrow style per format
                if is_mermaid:
                    lines.append(f"{indent}{current} ->> {current}: {elem}")
                else:
                    lines.append(f"{indent}{current} -> {current}: {elem}")
                i += 1
            continue

        # cross-participant call: e.g. "B.func" or "B.func->ret"
        if "." in x:
            pos = x.find(".")
            ret = "ret"
            if "->" in x:
                pos2 = x.find("->")
                elem = x[pos + 1:pos2]
                ret = x[pos2 + 2 :]
            else:
                elem = x[pos + 1 :]

            elem = elem.replace("$", ".")
            new = x[:pos]
            # cross-participant call start
            if is_mermaid:
                lines.append(f"{indent}{current} ->>+ {new}: {elem}")
            else:
                lines.append(f"{indent}{current} -> {new}: {elem}")
            if i + 1 < len(node) and isinstance(node[i + 1], list):
                lines.extend(display(new, node[i + 1], level + 1, fmt))
                i += 2
            else:
                i += 1
            # cross-participant return
            if is_mermaid:
                lines.append(f"{indent}{new} ->>- {current}: {ret}")
            else:
                lines.append(f"{indent}{new} --> {current}: {ret}")
            continue

        # default: simple self message
        lines.append(f"{indent}{current} -> {current}: {x}")
        i += 1

    return lines

# choose format: 'mermaid' or 'plantuml'
fmt = 'mermaid'

lines = []
if fmt == 'mermaid':
    lines.append("```mermaid")
    lines.append("sequenceDiagram")
    for p in participants:
        lines.append(f"participant {p}")
    lines.extend(display(participants[0], stack, 0, fmt=fmt))
    lines.append("```")
else:
    # PlantUML sequence diagram
    lines.append("@startuml")
    for p in participants:
        lines.append(f"participant {p}")
    lines.extend(display(participants[0], stack, 0, fmt=fmt))
    lines.append("@enduml")

print("\n".join(lines))
                
