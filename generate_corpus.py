from pathlib import Path
import string 
import csv
import secrets
import shutil
import re

def split_into_docs():
    base_dir = Path(__file__).parent

    input_file = base_dir / "corpus" / "input.txt"
    output_dir = base_dir / "corpus" / "original"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Read each line as a separate document
    lines = input_file.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines, start=1):
        line = line.strip()

        if not line:
            continue

        doc_path = output_dir / f"doc_{i}.txt"
        doc_path.write_text(line, encoding="utf-8")

    print(f"Created {len([l for l in lines if l.strip()])} documents.")


def encrypt_doc_ids():
    base_dir = Path(__file__).parent

    original_dir = base_dir / "corpus" / "original"
    encrypted_dir = base_dir / "corpus" / "encrypted"

    encrypted_dir.mkdir(parents=True, exist_ok=True)

    alphabet = string.ascii_lowercase + string.digits

    def generate_id(length=6):
        return "".join(secrets.choice(alphabet) for _ in range(length))

    mapping = []

    for doc in original_dir.glob("doc_*.txt"):
        while True:
            opaque_id = generate_id()
            new_path = encrypted_dir / f"{opaque_id}.txt"

            if not new_path.exists():
                break

        # Copy contents, don't rename originals
        shutil.copy(doc, new_path)

        mapping.append({
            "original": doc.name,
            "opaque": new_path.name
        })

    # Keep this outside encrypted folder
    with open(base_dir / "mapping.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["original", "opaque"])
        writer.writeheader()
        writer.writerows(mapping)

encrypt_doc_ids()