import numpy as np
import cv2, json, glob, os

BASE       = "/jetson-ssd/compute/edge/depth-anything-v3-marine/ESPERANZA/T1_20m/V1/"
FRAMES_DIR = BASE + "frames/"
DEPTH_DIR  = BASE + "depth/"
CFD_DIR    = BASE + "cfd/detections/"
OUT_DIR    = BASE + "fused_overlay/"
os.makedirs(OUT_DIR, exist_ok=True)
FPB = 8

def get_dvis(fn):
    return os.path.join(DEPTH_DIR, f"batch_{fn//FPB:04d}", "depth_vis", f"{fn%FPB:04d}.jpg")

def depth_color_at(dvis, cx, cy):
    h,w = dvis.shape[:2]
    cx,cy = min(max(cx,0),w-1), min(max(cy,0),h-1)
    b,g,r = [int(v) for v in dvis[cy,cx]]
    return (b,g,r)

def draw_boxes(img, dets, dvis=None):
    for d in dets:
        x1,y1,x2,y2 = [int(v) for v in d["bbox"]]
        dv = d.get("likely_diver", False)
        if dvis is not None:
            cx,cy = (x1+x2)//2, (y1+y2)//2
            c = depth_color_at(dvis, cx, cy)
        else:
            c = (0,100,255) if dv else (0,220,80)
        cv2.rectangle(img,(x1,y1),(x2,y2),c,3)
        label = f"{'D' if dv else 'F'} {d['confidence']:.2f}"
        cv2.putText(img,label,(x1+2,max(y1-6,18)),
                    cv2.FONT_HERSHEY_SIMPLEX,0.55,c,2,cv2.LINE_AA)
    return img

def add_minimap(img, dvis, scale=0.25):
    h,w = img.shape[:2]
    mw,mh = int(w*scale), int(h*scale)
    mini = cv2.resize(dvis,(mw,mh),interpolation=cv2.INTER_LANCZOS4)
    cv2.rectangle(mini,(0,0),(mw-1,mh-1),(255,255,255),3)
    margin = 10
    y1,y2 = h-mh-margin, h-margin
    x1,x2 = w-mw-margin, w-margin
    roi = img[y1:y2, x1:x2]
    cv2.addWeighted(mini, 0.85, roi, 0.15, 0, roi)
    img[y1:y2, x1:x2] = roi
    cv2.putText(img,"DEPTH",(x1+6,y1+20),
                cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
    return img

def banner(img, text):
    h,w = img.shape[:2]
    ov = img.copy(); cv2.rectangle(ov,(0,0),(w,52),(0,0,0),-1)
    cv2.addWeighted(ov,0.6,img,0.4,0,img)
    cv2.putText(img,text,(12,36),cv2.FONT_HERSHEY_SIMPLEX,0.8,(80,255,160),2,cv2.LINE_AA)
    return img

for fn in [117,118,119,120,121]:
    stem = f"{fn:06d}"
    fp = os.path.join(FRAMES_DIR, stem+".png")
    jp = os.path.join(CFD_DIR, stem+".json")
    dp = get_dvis(fn)
    if not os.path.exists(fp) or not os.path.exists(jp): continue
    with open(jp) as f: det = json.load(f)
    fish_n = det.get("fish_count_filtered",0)
    divers = det.get("diver_detections",0)
    img = cv2.imread(fp); h,w = img.shape[:2]
    dvis = cv2.resize(cv2.imread(dp),(w,h)) if os.path.exists(dp) else None
    draw_boxes(img, det.get("detections",[]), dvis)
    if dvis is not None:
        add_minimap(img, dvis)
    banner(img, f"CFD+Depth | {stem} | {fish_n} fish | {divers} divers")
    out = cv2.resize(img,(3840,int(h*3840/w)),interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(os.path.join(OUT_DIR,f"{stem}_fused.jpg"),out,[cv2.IMWRITE_JPEG_QUALITY,97])
    print(f"  Saved {stem}_fused.jpg  ({out.shape[1]}x{out.shape[0]})")

print("Building filmstrip...")
all_j = sorted(glob.glob(os.path.join(CFD_DIR,"*.json")))
spaced = [int(os.path.splitext(os.path.basename(all_j[i]))[0]) for i in np.linspace(0,len(all_j)-1,5,dtype=int)]
all_strip = sorted(set(spaced+[119,120,121]))[:8]
SW,SH = 640,360
panels = []
for fn in all_strip:
    stem=f"{fn:06d}"; jp=os.path.join(CFD_DIR,stem+".json")
    fp=os.path.join(FRAMES_DIR,stem+".png"); dp=get_dvis(fn)
    fish_n=0; dets=[]
    if os.path.exists(jp):
        with open(jp) as f: d=json.load(f)
        fish_n=d.get("fish_count_filtered",0); dets=d.get("detections",[])
    if not os.path.exists(fp): continue
    img = cv2.imread(fp); h,w = img.shape[:2]
    dvis = cv2.resize(cv2.imread(dp),(w,h)) if os.path.exists(dp) else None
    draw_boxes(img, dets, dvis)
    if dvis is not None:
        add_minimap(img, dvis, scale=0.3)
    panel = cv2.resize(img,(SW,SH),interpolation=cv2.INTER_LANCZOS4)
    hot = fn in [119,120,121]
    if hot:
        cv2.rectangle(panel,(0,0),(SW-1,SH-1),(0,180,255),3)
    lb = np.full((40,SW,3),15,dtype=np.uint8)
    tag = "* " if hot else ""
    cv2.putText(lb,f"{tag}{stem} | {fish_n} fish",(6,28),
                cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,200,255) if hot else (80,255,160),1,cv2.LINE_AA)
    panels.append(np.vstack([panel,lb]))

gap = np.full((panels[0].shape[0],8,3),25,dtype=np.uint8)
strip = panels[0]
for p in panels[1:]: strip = np.hstack([strip,gap,p])
hdr = np.full((70,strip.shape[1],3),15,dtype=np.uint8)
cv2.putText(hdr,"ESPERANZA T1 | CFD + Depth-Colored Boxes + Minimap | * = hotspot",(16,48),
            cv2.FONT_HERSHEY_SIMPLEX,0.85,(80,255,160),2,cv2.LINE_AA)
filmstrip = np.vstack([hdr,strip])
cv2.imwrite(os.path.join(OUT_DIR,"filmstrip_fused.jpg"),filmstrip,[cv2.IMWRITE_JPEG_QUALITY,97])
print("Filmstrip saved.")
print("Files:",os.listdir(OUT_DIR))
