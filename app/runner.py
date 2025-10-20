# app/runner.py
import os, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DISTORTED = os.path.join(ROOT, "distorted")
RECTIFIED = os.path.join(ROOT, "rectified")

def _safe_mkdir(p):
    os.makedirs(p, exist_ok=True)

def _clear_dir(p):
    if os.path.isdir(p):
        for n in os.listdir(p):
            fp = os.path.join(p, n)
            if os.path.isdir(fp):
                shutil.rmtree(fp)
            else:
                os.remove(fp)

def _is_img(fn):
    ext = os.path.splitext(fn)[1].lower()
    return ext in [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"]

def _copy_images(src_dir, dst_dir):
    cnt = 0
    for n in sorted(os.listdir(src_dir)):
        if _is_img(n):
            shutil.copy2(os.path.join(src_dir, n), os.path.join(dst_dir, n))
            cnt += 1
    return cnt

def _run_inference():
    py = sys.executable
    cmd = [py, os.path.join(ROOT, "inference.py")]
    return subprocess.call(cmd, cwd=ROOT)

def run_batch(input_dir, output_dir, log_fn=print):
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)
    _safe_mkdir(output_dir)
    _safe_mkdir(DISTORTED)
    _safe_mkdir(RECTIFIED)

    ok = 0
    fail = 0

    # 单批输入：把 input_dir 当作一册（全拷贝）
    _clear_dir(DISTORTED)
    _clear_dir(RECTIFIED)
    n = _copy_images(input_dir, DISTORTED)
    if n == 0:
        log_fn("⚠ 未发现图片，已跳过\n")
        return ok, fail + 1

    log_fn(f"· 已准备 {n} 张图片\n")
    ret = _run_inference()
    if ret != 0:
        log_fn(f"❌ 失败：inference.py 返回码 {ret}\n")
        return ok, fail + 1

    moved = 0
    for name in sorted(os.listdir(RECTIFIED)):
        src = os.path.join(RECTIFIED, name)
        dst = os.path.join(output_dir, name)
        shutil.move(src, dst)
        moved += 1
    log_fn(f"✅ 输出 {moved} 张 → {output_dir}\n")
    return ok + 1, fail
