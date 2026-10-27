from pathlib import Path
import stat
import sys
import tempfile
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configure import configure

examples = [
    'model = "example"\n[tui]\nnotice = true\n[tui.other]\ncount = 4\n',
    '[tui]\nfullscreen_transcript = true\n\n[profiles.work]\nname = "keep me"\n',
    'model = "example"\n',
    '[tui] # comment\nnotice = true',
    '',
]
with tempfile.TemporaryDirectory() as directory:
    for i, original in enumerate(examples):
        path = Path(directory) / f'config-{i}.toml'
        path.write_text(original)
        path.chmod(0o600)
        before = tomllib.loads(original)
        backup = configure(path)
        assert backup.read_text() == original
        after = tomllib.loads(path.read_text())
        assert after['tui'].pop('fullscreen_transcript') is False
        before.setdefault('tui', {}).pop('fullscreen_transcript', None)
        assert after == before
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        assert configure(path) is None
        configure(path, fullscreen=True)
        assert tomllib.loads(path.read_text())['tui']['fullscreen_transcript'] is True
print('PASS: unrelated TOML settings, nested sections, backups, file permissions, repeated setup, undo')
