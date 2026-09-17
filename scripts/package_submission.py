"""Build a clean handoff archive from tracked files and the verified executable."""
import hashlib
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "交付_一箭又一箭"
OUT.mkdir(exist_ok=True)
bundle = OUT / "arrow-game.bundle"
subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=ROOT, check=True)
subprocess.run(["git", "bundle", "verify", str(bundle)], cwd=ROOT, check=True)
files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8").split("\0")
archive = OUT / "一箭又一箭_杜玉鹤_162404109.zip"
notice = """一箭又一箭 — 杜玉鹤 162404109

启动游戏：双击 dist/ArrowGame.exe，不需要另外安装 Python。
查看博客：docs/blog.md；博客园粘贴版为 docs/blog-cnblogs.md。
运行素材：docs/images/demo.gif 及各界面 PNG。
提交清单：docs/submission.md。
关键代码讲解：docs/code-guide.md。

GitHub 已上传：https://github.com/myp208116/arrow-game
尚需本人完成：三关实际试玩、PSP 实际耗时、心得核对和博客发布提交。
包内附有线上同步历史及原始本地开发历史，编号对应见 docs/publication.md。

恢复 Git 历史（在能运行 git 的终端）：
git clone arrow-game.bundle arrow-game
cd arrow-game
git remote set-url origin https://github.com/myp208116/arrow-game.git
git push -u origin main

不要上传密码或令牌，不要强制覆盖远端已有提交。
"""
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for name in files:
        if name:
            z.write(ROOT / name, "一箭又一箭/" + name)
    z.write(ROOT / "dist/ArrowGame.exe", "一箭又一箭/dist/ArrowGame.exe")
    z.write(bundle, "一箭又一箭/arrow-game.bundle")
    z.writestr("一箭又一箭/先读我.txt", notice)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert not any(".venv" in n or "/.git/" in n for n in z.namelist())
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(OUT / "SHA256.txt").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
print(f"Archive: {archive}\nBytes: {archive.stat().st_size}\nSHA256: {digest}")
