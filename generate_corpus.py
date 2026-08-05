from pathlib import Path
import string 
import csv
import secrets
import shutil
import re

def split_into_docs():
 # Read the input
 text = Path("./corpus/input.txt").read_text(encoding="utf-8").strip()

 # Split into sentences
 sentences = [s.strip() + "." for s in text.split(".") if s.strip()]

 # Create output directory
 output_dir = Path("corpus/original")
 output_dir.mkdir(exist_ok=True)

 # Write one sentence per file
 for i, sentence in enumerate(sentences, start=1):
    if sentence.strip():
        (output_dir / f"doc_{i}.txt").write_text(
            sentence.strip(),
            encoding="utf-8"
        )

def split_into_docs():
    base_dir = Path(__file__).parent

    input_file = base_dir / "corpus" / "input.txt"
    original_dir = base_dir / "corpus" / "original"

    original_dir.mkdir(parents=True, exist_ok=True)

    text = input_file.read_text(encoding="utf-8")

    # Split only on periods
    sentences = [s.strip() + "." for s in text.split(".") if s.strip()]

    for i, sentence in enumerate(sentences, start=1):
        doc_path = original_dir / f"doc_{i}.txt"
        doc_path.write_text(sentence, encoding="utf-8")

    print(f"Created {len(sentences)} original docs.")


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
