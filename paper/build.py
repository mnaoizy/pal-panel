"""Clean-build the paper; fail on overfull boxes or unresolved references."""
from pathlib import Path
import shutil, subprocess
ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode: raise SystemExit(r.stdout[-4000:])
    return r.stdout
if BUILD.exists(): shutil.rmtree(BUILD)
BUILD.mkdir()
latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory=build", "main.tex"]
run(latex); run(["bibtex", "build/main"]); run(latex); log = run(latex)
bad = [l for l in log.splitlines() if "Overfull" in l or ("LaTeX Warning:" in l and ("undefined" in l or "changed" in l))]
if bad: raise SystemExit("\n".join(bad))
(ROOT / "output").mkdir(exist_ok=True); shutil.copy2(BUILD / "main.pdf", ROOT / "output/pal_icassp2027.pdf"); print("built", ROOT / "output/pal_icassp2027.pdf")
