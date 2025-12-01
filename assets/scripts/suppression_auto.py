#!/usr/bin/env python3
from pathlib import Path

# === PARAMÈTRES À MODIFIER ===
IMAGES_DIR = Path(r"/chemin/vers/le/dossier/images")
ANNOTATIONS_DIR = Path(r"/chemin/vers/le/dossier/annotations")
IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "bmp", "webp", "tif", "tiff"]
DRY_RUN = False  # mettre True pour tester sans supprimer
# ==============================

def collect_image_stems(images_dir, image_exts):
    image_exts = {e.lower().lstrip(".") for e in image_exts}
    return {
        p.stem
        for p in images_dir.iterdir()
        if p.is_file() and p.suffix.lower().lstrip(".") in image_exts
    }

def clean_annotations(images_dir, ann_dir, image_exts, dry_run=False):
    if not images_dir.is_dir():
        raise SystemExit(f"Dossier images introuvable: {images_dir}")
    if not ann_dir.is_dir():
        raise SystemExit(f"Dossier annotations introuvable: {ann_dir}")

    image_stems = collect_image_stems(images_dir, image_exts)
    to_delete = []

    for p in ann_dir.iterdir():
        if p.is_file() and p.suffix.lower() == ".txt":
            if p.stem not in image_stems:
                to_delete.append(p)

    for p in to_delete:
        if dry_run:
            print(f"[SIMULATION] Suppression: {p}")
        else:
            try:
                p.unlink()
                print(f"Supprimé: {p}")
            except Exception as e:
                print(f"Erreur suppression {p}: {e}")

    print(f"Total fichiers supprimés: {len(to_delete)}")
    if dry_run:
        print("Aucune suppression réelle effectuée (mode test).")

if __name__ == "__main__":
    clean_annotations(IMAGES_DIR, ANNOTATIONS_DIR, IMAGE_EXTENSIONS, DRY_RUN)
