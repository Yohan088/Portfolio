#!/usr/bin/env python3
from pathlib import Path
import shutil
import cv2
import sys

# ========= PARAMÈTRES À MODIFIER =========
IMAGES_DIR      = Path(r"/chemin/source/images")        # dossier images source
ANNOTATIONS_DIR = Path(r"/chemin/source/annotations")   # dossier .txt source

KEEP_IMAGES_DIR = Path(r"/chemin/keep/images")          # destination images
KEEP_ANN_DIR    = Path(r"/chemin/keep/annotations")     # destination annotations

IMAGE_EXTS = {"jpg", "jpeg", "png", "bmp", "webp", "tif", "tiff"}
OVERWRITE  = False   # écraser si déjà présent dans la sortie
DRY_RUN    = False   # True = ne fait que logguer les actions
# =========================================

def list_images(img_dir: Path):
    return sorted(
        [p for p in img_dir.iterdir() if p.is_file() and p.suffix.lower().lstrip(".") in IMAGE_EXTS],
        key=lambda p: p.name.lower()
    )

def safe_imread(path_str: str):
    if USE_SAFE_READ:
        arr = np.fromfile(path_str, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return cv2.imread(path_str)

def wait_key():
    return (cv2.waitKeyEx(0) if hasattr(cv2, "waitKeyEx") else cv2.waitKey(0)) & 0xFFFFFFFF

LEFT_KEYS  = {2424832, 65361, 81, 0x250000, 0x51}
RIGHT_KEYS = {2555904, 65363, 83, 0x270000, 0x53}
def is_left(code):  return (code in LEFT_KEYS) or (code & 0xFF in LEFT_KEYS)
def is_right(code): return (code in RIGHT_KEYS) or (code & 0xFF in RIGHT_KEYS)

def ensure_dirs():
    KEEP_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    KEEP_ANN_DIR.mkdir(parents=True, exist_ok=True)

def dst_paths_for(img: Path):
    return KEEP_IMAGES_DIR / img.name, KEEP_ANN_DIR / f"{img.stem}.txt"

def copy_now(img: Path):
    """Copie image + .txt si présent. Ne touche pas aux sources."""
    ensure_dirs()
    dst_img, dst_ann = dst_paths_for(img)

    # image
    if dst_img.exists() and not OVERWRITE:
        print(f"[SKIP] existe déjà: {dst_img}")
    else:
        if DRY_RUN:
            print(f"[SIMULATION] copy image -> {dst_img}")
        else:
            shutil.copy2(img, dst_img)
            print(f"[OK] copié image -> {dst_img}")

    # annotation
    ann_src = ANNOTATIONS_DIR / f"{img.stem}.txt"
    if ann_src.exists():
        if dst_ann.exists() and not OVERWRITE:
            print(f"[SKIP] existe déjà: {dst_ann}")
        else:
            if DRY_RUN:
                print(f"[SIMULATION] copy ann -> {dst_ann}")
            else:
                shutil.copy2(ann_src, dst_ann)
                print(f"[OK] copié ann -> {dst_ann}")
    else:
        print(f"[INFO] pas d'annotation: {img.stem}.txt")

def remove_copy(img: Path):
    """Supprime UNIQUEMENT les copies dans la sortie pour cette image."""
    dst_img, dst_ann = dst_paths_for(img)

    # sécurité: n'effacer que dans les dossiers de sortie
    for p, root in [(dst_img, KEEP_IMAGES_DIR), (dst_ann, KEEP_ANN_DIR)]:
        try:
            if p.exists() and root in p.parents:
                if DRY_RUN:
                    print(f"[SIMULATION] delete -> {p}")
                else:
                    p.unlink()
                    print(f"[DEL] {p}")
        except Exception as e:
            print(f"[ERR] suppression {p}: {e}")

def status_flag(img: Path):
    dst_img, _ = dst_paths_for(img)
    return "COPIÉ" if dst_img.exists() else "NON COPIÉ"

def show_and_drive(images):
    i = 0
    n = len(images)
    window = "Tri"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    while 0 <= i < n:
        img_path = images[i]
        img = safe_imread(str(img_path))
        if img is None:
            print(f"[WARN] lecture impossible: {img_path}")
            i += 1
            continue

        flag = status_flag(img_path)
        title = f"[{i+1}/{n}] {img_path.name} | ←/→ défiler | k copier | A annuler copie | q finir | état={flag}"
        cv2.imshow(window, img)
        cv2.setWindowTitle(window, title)

        key = wait_key()
        if key in (ord('q'), ord('Q')):
            break
        elif key in (ord('k'), ord('K')):
            copy_now(img_path)
        elif key in (ord('a'), ord('A')):
            remove_copy(img_path)
        elif is_right(key) and i < n - 1:
            i += 1
        elif is_left(key) and i > 0:
            i -= 1
        # autres touches: aucune action

    cv2.destroyAllWindows()

def main():
    if not IMAGES_DIR.is_dir():
        raise SystemExit(f"Dossier images introuvable: {IMAGES_DIR}")
    if not ANNOTATIONS_DIR.is_dir():
        raise SystemExit(f"Dossier annotations introuvable: {ANNOTATIONS_DIR}")

    images = list_images(IMAGES_DIR)
    if not images:
        raise SystemExit("Aucune image trouvée.")

    print("Commandes: ←/→ défiler | k copier | A annuler copie | q finir")
    show_and_drive(images)
    print("Terminé.")

# Lecture robuste sous Windows de chemins Unicode
USE_SAFE_READ = False
try:
    import numpy as np
    USE_SAFE_READ = True
except Exception:
    pass

if __name__ == "__main__":
    if not hasattr(cv2, "waitKeyEx"):
        print("Note: OpenCV sans waitKeyEx. Les flèches peuvent varier selon l'OS.", file=sys.stderr)
    main()
