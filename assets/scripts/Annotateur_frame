"""
Annotateur volley par frames (extraction d'images + log CSV)

Touches :
  0..4       -> enregistre image + log CSV   (0=service 1=reception 2=passe 3=attaque 4=bloc)
  ESPACE/P   -> pause / reprise
  ← / →      -> -1 / +1 frame (met en pause)
  J / K      -> -1s / +1s   (met en pause, calcul en frames)
  C / V / B  -> vitesse 0.5x / 1.0x / 1.5x
  H          -> aide on/off
  Q / ESC    -> quitter

Nom de fichier image :
  <nom_video>_<abbr>_<HH-MM-SS>.<ext>
  abbr: s=service, r=reception, p=passe, a=attaque, b=bloc

CSV colonnes :
  image_path,label,frame_idx,video_name,md5
"""

# ========= PARAMÈTRES À PERSONNALISER =========
VIDEO_PATH    = r"C:\Users\XXXXX.mp4"
OUTPUT_DIR    = r"C:\Users\YYYYY"
OUTPUT_CSV    = r"C:\Users\ZZZZZ.csv"
IMG_FORMAT    = "png"              # "png" ou "jpg"
INITIAL_SPEED = 1.0                # 0.5, 1.0, 6
START_AT      = "00:11:10"         # HH:MM:SS -> point de départ réel dans la vidéo
WINDOW_NAME   = "Annotateur Volley - Frames"
# ==============================================

import os, csv, cv2, hashlib, math
from datetime import timedelta

LABELS = {"0": "service", "1": "reception", "2": "passe", "3": "attaque", "4": "bloc"}
ABBR   = {"service": "s", "reception": "r", "passe": "p", "attaque": "a", "bloc": "b"}
SPEED_PRESETS = {"c": 0.5, "v": 1.0, "b": 6.0}

# Codes flèches (Windows/GTK) + fallback (81/83)
KEY_LEFTS  = {2424832, 81}
KEY_RIGHTS = {2555904, 83}

def hms_to_seconds(hms: str) -> float:
    h, m, s = map(int, hms.split(":"))
    return h * 3600 + m * 60 + s

def seconds_to_hms(sec_total: float) -> str:
    sec_total = max(0.0, sec_total)
    h = int(sec_total // 3600)
    m = int((sec_total % 3600) // 60)
    s = int(sec_total % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def ensure_csv_header(path):
    hdr = ["image_path","label","frame_idx","video_name","md5"]
    if not (os.path.isfile(path) and os.path.getsize(path)>0):
        with open(path,"w",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow(hdr)

def load_existing(path):
    seen_hash, seen_key = set(), set()
    if os.path.isfile(path) and os.path.getsize(path)>0:
        with open(path,"r",newline="",encoding="utf-8") as f:
            for row in csv.DictReader(f):
                seen_hash.add(row["md5"])
                try:
                    seen_key.add((row["video_name"], int(row["frame_idx"])))
                except:
                    pass
    return seen_hash, seen_key

def md5_of_image(bgr):
    ok, buf = cv2.imencode(".png", bgr)  # hash stable
    if not ok:
        return None
    return hashlib.md5(buf.tobytes()).hexdigest()

def overlay(frame, lines, xy=(10,22)):
    x,y = xy
    for i, line in enumerate(lines):
        p = (x, y+i*22)
        cv2.putText(frame, line, p, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 3, cv2.LINE_AA)
        cv2.putText(frame, line, p, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)

def main():
    ensure_dir(OUTPUT_DIR)
    ensure_csv_header(OUTPUT_CSV)
    seen_hash, seen_key = load_existing(OUTPUT_CSV)

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        raise SystemExit(f"Impossible d'ouvrir : {VIDEO_PATH}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    start_sec = hms_to_seconds(START_AT)
    start_frame = int(round(start_sec * fps))
    # Positionne via frames (plus fiable que POS_MSEC)
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(start_frame, max(0, nframes-1))))

    speed = INITIAL_SPEED if INITIAL_SPEED in (0.5, 1.0, 4.0) else 1.0
    paused, show_help = False, True
    video_name = os.path.splitext(os.path.basename(VIDEO_PATH))[0]

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    def current_index() -> int:
        return int(cap.get(cv2.CAP_PROP_POS_FRAMES))

    def goto_frame(idx: int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(idx, max(0, nframes-1))))

    def read_current_frame():
        idx = current_index()
        goto_frame(idx)
        ok, frame = cap.read()
        if not ok:
            return None, idx
        # revenir sur cette frame pour éviter l'avance
        goto_frame(idx)
        return frame, idx

    def absolute_hms_from_frame(idx: int) -> str:
        # Horodatage absolu = START_AT + idx/fps
        t = (idx / max(fps, 1e-6))
        return seconds_to_hms(t)

    def draw_and_show():
        frame, idx = read_current_frame()
        if frame is None:
            return False
        hms = absolute_hms_from_frame(idx)
        info = [
            f"Video: {video_name} | Frame {idx}/{nframes-1} | {hms}",
            f"Vitesse: {speed}x | FPS: {fps:.2f} | Pause: {'oui' if paused else 'non'}"
        ]
        if show_help:
            info += [
                "0..4: label   ESPACE/P: pause   <-/->: +/-1 frame   J/K: +/-3s",
                "C/V/B: 0.5x/1x/6x   H: aide   Q/Esc: quitter"
            ]
        overlay(frame, info)
        cv2.imshow(WINDOW_NAME, frame)
        return True

    while True:
        if not paused:
            ok, frame = cap.read()
            if not ok:
                break
            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKeyEx(max(1, int(1000/(fps*max(speed,0.1)))))  # waitKeyEx pour flèches
        else:
            if not draw_and_show():
                break
            key = cv2.waitKeyEx(0)

        # Quitter
        if key in (27, ord('q'), ord('Q')):
            break

        # Pause / reprise
        if key in (ord(' '), ord('p'), ord('P')):
            paused = not paused
            continue

        # Aide
        if key in (ord('h'), ord('H')):
            show_help = not show_help
            continue

        # Vitesse
        if 0 <= key < 256 and chr(key).lower() in SPEED_PRESETS:
            speed = SPEED_PRESETS[chr(key).lower()]
            continue

        # Navigation fine -> met en pause
        if key in KEY_LEFTS | KEY_RIGHTS | {ord('j'), ord('J'), ord('k'), ord('K')}:
            paused = True
            idx = current_index()

            if key in KEY_LEFTS:       # -1 frame
                goto_frame(idx - 1)
                continue
            if key in KEY_RIGHTS:      # +1 frame
                goto_frame(idx + 1)
                continue
            if key in (ord('j'), ord('J')):   # -1s en frames
                goto_frame(idx - int(round(3*fps)))
                continue
            if key in (ord('k'), ord('K')):   # +1s en frames
                goto_frame(idx + int(round(3*fps)))
                continue

        # Étiquetage 0..4 -> enregistre image + log
        if 0 <= key < 256 and chr(key) in LABELS:
            label = LABELS[chr(key)]
            frame, idx = read_current_frame()
            if frame is None:
                continue

            # Anti-doublons par md5 + (video,frame)
            md5 = md5_of_image(frame)
            if md5 is None:
                continue
            if (video_name, idx) in seen_key or md5 in seen_hash:
                cv2.rectangle(frame, (0,0),(frame.shape[1],frame.shape[0]), (0,140,255), 18)
                overlay(frame,[f"Doublon ignoré  label={label}  frame={idx}"])
                cv2.imshow(WINDOW_NAME, frame)
                cv2.waitKeyEx(250)
                continue

            out_dir = os.path.join(OUTPUT_DIR, label)
            ensure_dir(out_dir)

            hms = absolute_hms_from_frame(idx).replace(":", "-")  # pour le nom de fichier
            abbr = ABBR[label]
            fname = f"{video_name}_{abbr}_{hms}.{IMG_FORMAT}"
            img_path = os.path.join(out_dir, fname)

            # Collision rare -> suffixe
            suffix = 1
            while os.path.exists(img_path):
                fname = f"{video_name}_{abbr}_{hms}_{suffix}.{IMG_FORMAT}"
                img_path = os.path.join(out_dir, fname)
                suffix += 1

            # Écriture image
            if IMG_FORMAT.lower() == "jpg":
                cv2.imwrite(img_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            else:
                cv2.imwrite(img_path, frame)

            # Log CSV
            with open(OUTPUT_CSV,"a",newline="",encoding="utf-8") as f:
                csv.writer(f).writerow([img_path, label, idx, video_name, md5])

            seen_key.add((video_name, idx))
            seen_hash.add(md5)

            # Feedback
            cv2.rectangle(frame, (0,0),(frame.shape[1],frame.shape[0]), (0,180,0), 18)
            overlay(frame,[f"Enregistré  {label}  -> {os.path.basename(img_path)}"])
            cv2.imshow(WINDOW_NAME, frame)
            cv2.waitKeyEx(180)
            continue

    cap.release()
    cv2.destroyAllWindows()
    print(f"Fini. Images: {OUTPUT_DIR} | Log: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
