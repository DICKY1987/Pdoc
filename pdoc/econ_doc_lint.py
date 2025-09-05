
#!/usr/bin/env python3
import re, sys

ID_RE = re.compile(r"^<!-- BEGIN:(ECON\.\d{3}\.\d{3}\.\d{3}\.(DEF|REQ|TABLE|FLOW|ALERT|ARCH|CTRL|EXAMPLE|ACCEPTANCE)\.[a-z0-9_]+) -->$")
END_RE = re.compile(r"^<!-- END:(ECON\.\d{3}\.\d{3}\.\d{3}\.(DEF|REQ|TABLE|FLOW|ALERT|ARCH|CTRL|EXAMPLE|ACCEPTANCE)\.[a-z0-9_]+) -->$")
REF_RE = re.compile(
    r"@ECON\.\d{3}\.\d{3}(?:\.\d{3}\.(?:DEF|REQ|TABLE|FLOW|ALERT|ARCH|CTRL|EXAMPLE|ACCEPTANCE)\.[a-z0-9_]+)?"
)

def main():
    if len(sys.argv) < 2:
        print("Usage: econ_doc_lint.py <spec.md>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    errors = []
    stack = []
    ids = set()

    for i, line in enumerate(lines, 1):
        m = ID_RE.match(line.strip())
        if m:
            bid = m.group(1)
            stack.append((bid, i))
            ids.add(bid)
            continue
        m = END_RE.match(line.strip())
        if m:
            eid = m.group(1)
            if not stack:
                errors.append(f"{i}: END without BEGIN: {eid}")
            else:
                bid, bi = stack.pop()
                if bid != eid:
                    errors.append(f"{i}: END id mismatch. BEGIN at {bi} was {bid}, END is {eid}")
            continue

    if stack:
        for bid, bi in stack:
            errors.append(f"{bi}: Unclosed BEGIN: {bid}")

    text = "\n".join(lines)

    # Cross-ref sanity: section prefix resolution and full block matching
    for ref in REF_RE.findall(text):
        try:
            parts = ref.split(".")
            if len(parts) == 6:
                _, major, minor, block, btype, name = parts
                full_id = (
                    f"ECON.{int(major):03d}.{int(minor):03d}.{int(block):03d}.{btype}.{name}"
                )
                if full_id not in ids:
                    errors.append(f"Cross-ref {ref} has no matching block ID")
            elif len(parts) == 3:
                _, major, minor = parts
                prefix = f"ECON.{int(major):03d}.{int(minor):03d}."
                if not any(x.startswith(prefix) for x in ids):
                    errors.append(
                        f"Cross-ref {ref} has no matching section prefix among block IDs"
                    )
            else:
                errors.append(f"Malformed cross-ref: {ref}")
        except Exception:
            errors.append(f"Malformed cross-ref: {ref}")

    # CSV required meta fields appear at least once in the doc
    for required in ["file_seq", "created_at_utc", "checksum_sha256"]:
        if required not in text:
            errors.append(f"Missing required CSV meta field in doc: {required}")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("OK: Lint passed")

if __name__ == "__main__":
    main()
