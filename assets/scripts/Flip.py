# build_flip_only.py
import os, glob, cv2

# ==== CONFIG ====
TRAIN_ROOT = r"C:\Users\2026.MARTIN.Yohan\Downloads\Datasets\v2_flip\train"
OUT_ROOT   = r"C:\Users\2026.MARTIN.Yohan\Downloads\Datasets\v2_flip\train"
# =================

DIR_IMG = os.path.join(TRAIN_ROOT, "images")
DIR_LBL = os.path.join(TRAIN_ROOT, "labels")

OUT_IMG = os.path.join(OUT_ROOT, "images")
OUT_LBL = os.path.join(OUT_ROOT, "labels")
os.makedirs(OUT_IMG, exist_ok=True)
os.makedirs(OUT_LBL, exist_ok=True)

IMG_EXTS = {".jpg",".jpeg",".png",".bmp",".tif",".tiff"}

def list_images(folder):
    paths=[]
    for ext in IMG_EXTS:
        paths += glob.glob(os.path.join(folder, f"*{ext}"))
    return paths

def stem(path):
    return os.path.splitext(os.path.basename(path))[0]

def load_yolo(lbl_path):
    rows=[]
    if not os.path.exists(lbl_path):
        return rows
    with open(lbl_path,"r",encoding="utf-8") as f:
        for line in f:
            p=line.strip().split()
            if len(p)==5:
                try:
                    c=int(p[0]); xc=float(p[1]); yc=float(p[2]); w=float(p[3]); h=float(p[4])
                    rows.append([c,xc,yc,w,h])
                except ValueError:
                    pass
    return rows

def save_yolo(lbl_path, rows):
    with open(lbl_path,"w",encoding="utf-8") as f:
        for c,xc,yc,w,h in rows:
            f.write(f"{c} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")

def flip_labels_horiz(rows):
    return [[c, 1.0 - xc, yc, w, h] for c,xc,yc,w,h in rows]

def main():
    imgs = list_images(DIR_IMG)
    if not imgs:
        print("Aucune image trouvée dans:", DIR_IMG)
        return

    done = 0
    skipped = 0
    missing_lbl = 0
    unreadable = 0

    for ip in imgs:
        img = cv2.imread(ip)
        if img is None:
            unreadable += 1
            continue

        s = stem(ip)
        lp = os.path.join(DIR_LBL, s + ".txt")
        rows = load_yolo(lp)
        if not rows:
            missing_lbl += 1
            continue

        # flip image
        img_flip = cv2.flip(img, 1)

        # outputs
        base, ext = os.path.splitext(os.path.basename(ip))
        out_img_flip = os.path.join(OUT_IMG, base + "_flip" + ext)
        out_lbl_flip = os.path.join(OUT_LBL, base + "_flip.txt")

        # write
        ok = cv2.imwrite(out_img_flip, img_flip)
        if not ok:
            skipped += 1
            continue
        save_yolo(out_lbl_flip, flip_labels_horiz(rows))
        done += 1

    print(f"Flips générés: {done} / {len(imgs)}")
    if missing_lbl:
        print(f"Labels manquants ou vides: {missing_lbl}")
    if unreadable:
        print(f"Images illisibles: {unreadable}")
    if skipped:
        print(f"Échecs d'écriture: {skipped}")
    print("Sortie:", OUT_IMG, "et", OUT_LBL)

if __name__ == "__main__":
    main()
