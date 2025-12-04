# auto_crop_yolo.py
import os, glob, cv2, math

# ===== CONFIG =====
IN_IMG = r"C:\Users\2026.MARTIN.Yohan\Downloads\Dataset_v24_flip_test_out\test\images"   # images source
IN_LBL = r"C:\Users\2026.MARTIN.Yohan\Downloads\Dataset_v24_flip_test_out\test\labels"           # labels YOLO associés (même stem + .txt)
OUT_IMG = r"C:\Users\2026.MARTIN.Yohan\Downloads\Dataset_v24_flip_test_out\test\crop\images"
OUT_LBL = r"C:\Users\2026.MARTIN.Yohan\Downloads\Dataset_v24_flip_test_out\test\crop\labels"
os.makedirs(OUT_IMG, exist_ok=True); os.makedirs(OUT_LBL, exist_ok=True)

# Marges asymétriques autour de la bbox principale (multiples de la bbox)
# ex: 300% gauche, 20% droite, 10% haut, -55% bas
MARGINS = {
    "left":   3.00,
    "right":  0.20,
    "top":    0.10,
    "bottom": -0.55,
}

# Contraintes: la bbox occupe AU PLUS cette fraction du crop (optionnel)
# ex: 0.5 => la bbox <= 50% de la largeur/hauteur du crop
TARGET_FRAC_X = None
TARGET_FRAC_Y = None

# Autres options
MIN_CROP_W = 128   # px
MIN_CROP_H = 128   # px
MIN_AREA_RATIO = 0.20  # garde une bbox si (aire_intersection / aire_bbox_source) >= 0.20
SKIP_EMPTY = True
IMG_EXTS={".jpg",".jpeg",".png",".bmp",".tif",".tiff"}
# ==================

def list_images(d):
    P=[]
    for e in IMG_EXTS: P += glob.glob(os.path.join(d,f"*{e}"))
    return P

def load_yolo(p):
    R=[]
    if not os.path.exists(p): return R
    with open(p,"r",encoding="utf-8") as f:
        for L in f:
            t=L.strip().split()
            if len(t)==5:
                R.append([int(t[0]), float(t[1]), float(t[2]), float(t[3]), float(t[4])])
    return R

def abs_from_norm(r,W,H):
    c,xc,yc,w,h=r
    bw, bh = w*W, h*H
    cx, cy = xc*W, yc*H
    x1, y1 = cx - bw/2, cy - bh/2
    x2, y2 = cx + bw/2, cy + bh/2
    return c,x1,y1,x2,y2

def norm_from_abs(c,x1,y1,x2,y2,Wc,Hc):
    bw, bh = max(0,x2-x1), max(0,y2-y1)
    cx, cy = x1 + bw/2, y1 + bh/2
    return [c, cx/Wc, cy/Hc, bw/Wc, bh/Hc]

def intersect(a,b):
    x1=max(a[0],b[0]); y1=max(a[1],b[1]); x2=min(a[2],b[2]); y2=min(a[3],b[3])
    if x2<=x1 or y2<=y1: return None
    return (x1,y1,x2,y2)

def area(b): return max(0,b[2]-b[0]) * max(0,b[3]-b[1])

def pick_primary_box(rows, W,H):
    if not rows: return None
    boxes=[abs_from_norm(r,W,H) for r in rows]
    boxes.sort(key=lambda b: area((b[1],b[2],b[3],b[4])), reverse=True)
    return boxes[0]  # (c,x1,y1,x2,y2)

def compute_crop_around_bbox(bx, W, H):
    _, x1, y1, x2, y2 = bx
    bw, bh = x2 - x1, y2 - y1

    # marges absolues en pixels (peuvent être négatives)
    L = MARGINS.get("left", 0.0)   * bw
    R = MARGINS.get("right", 0.0)  * bw
    T = MARGINS.get("top", 0.0)    * bh
    B = MARGINS.get("bottom", 0.0) * bh

    # crop brut avant contraintes
    x1c = int(round(x1 - L))
    y1c = int(round(y1 - T))
    x2c = int(round(x2 + R))
    y2c = int(round(y2 + B))

    # contraintes de fraction max (augmentent le crop si nécessaire)
    if TARGET_FRAC_X and TARGET_FRAC_X > 0:
        cw = x2c - x1c
        cw_min = max(MIN_CROP_W, int(math.ceil(bw / TARGET_FRAC_X)))
        if cw < cw_min:
            pad = (cw_min - cw) // 2
            x1c -= pad; x2c += pad
    if TARGET_FRAC_Y and TARGET_FRAC_Y > 0:
        ch = y2c - y1c
        ch_min = max(MIN_CROP_H, int(math.ceil(bh / TARGET_FRAC_Y)))
        if ch < ch_min:
            pad = (ch_min - ch) // 2
            y1c -= pad; y2c += pad

    # clamp au cadre
    x1c = max(0, x1c); y1c = max(0, y1c)
    x2c = min(W, x2c); y2c = min(H, y2c)

    # tailles mini
    if x2c - x1c < MIN_CROP_W:
        d = MIN_CROP_W - (x2c - x1c)
        x1c = max(0, x1c - d//2); x2c = min(W, x2c + d - d//2)
    if y2c - y1c < MIN_CROP_H:
        d = MIN_CROP_H - (y2c - y1c)
        y1c = max(0, y1c - d//2); y2c = min(H, y2c + d - d//2)

    if x2c <= x1c or y2c <= y1c:
        return (0,0,W,H)
    return (x1c,y1c,x2c,y2c)

def process_one(img_path):
    img = cv2.imread(img_path)
    if img is None: return 0,0
    H,W = img.shape[:2]
    stem = os.path.splitext(os.path.basename(img_path))[0]
    lbl_path = os.path.join(IN_LBL, stem + ".txt")
    rows = load_yolo(lbl_path)

    primary = pick_primary_box(rows, W,H)
    if primary is None:
        return (0,1) if SKIP_EMPTY else (0,0)

    crop_box = compute_crop_around_bbox(primary, W,H)  # (x1,y1,x2,y2)
    x1,y1,x2,y2 = crop_box
    crop = img[y1:y2, x1:x2]
    Wc, Hc = x2-x1, y2-y1

    new_rows=[]
    abs_boxes=[abs_from_norm(r,W,H) for r in rows]
    for (c,bx1,by1,bx2,by2) in abs_boxes:
        inter = intersect((bx1,by1,bx2,by2), crop_box)
        if not inter: continue
        if area(inter) / max(1e-6, area((bx1,by1,bx2,by2))) < MIN_AREA_RATIO:
            continue
        ix1,iy1,ix2,iy2 = inter
        ix1,iy1,ix2,iy2 = ix1-x1, iy1-y1, ix2-x1, iy2-y1
        ix1,iy1 = max(0,ix1), max(0,iy1)
        ix2,iy2 = min(Wc,ix2), min(Hc,iy2)
        if ix2<=ix1 or iy2<=iy1: continue
        new_rows.append(norm_from_abs(c, ix1,iy1,ix2,iy2, Wc,Hc))

    if SKIP_EMPTY and not new_rows:
        return 0,1

    out_img = os.path.join(OUT_IMG, f"{stem}_auto.jpg")
    out_lbl = os.path.join(OUT_LBL, f"{stem}_auto.txt")
    cv2.imwrite(out_img, crop, [cv2.IMWRITE_JPEG_QUALITY,95])
    with open(out_lbl,"w",encoding="utf-8") as f:
        for c,xc,yc,w,h in new_rows:
            f.write(f"{c} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
    return 1,0

def main():
    imgs = list_images(IN_IMG)
    made=0; skipped=0
    for p in imgs:
        m,s = process_one(p)
        made+=m; skipped+=s
    print(f"Crops écrits: {made} | Sautés: {skipped}")
    print("Out:", OUT_IMG, "et", OUT_LBL)

if __name__=="__main__":
    main()
