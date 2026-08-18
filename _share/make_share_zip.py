# -*- coding: utf-8 -*-
"""Create CCF_share_YYYY-MM-DD.zip from local D:\\download\\CCF,
excluding caches/environments and obvious credential files."""
import os
import zipfile

ROOT = r'D:\download\CCF'
OUT = os.path.join(ROOT, 'CCF_share_2026-08-17.zip')

EXCLUDE_DIR_NAMES = {
    '.git', '.hg', '.svn', '__pycache__', '.pytest_cache', '.mypy_cache',
    'node_modules', '.venv', 'venv', '.pixi', '.npm-tmp-cache', '.cache',
}
EXCLUDE_DIR_PREFIXES = {
    os.path.join('_ssh', '.pixi'),
}
EXCLUDE_FILE_NAMES = {
    'config.json',  # _ssh/config.json contains server password
    'session.jsonl',  # conversation log with credentials
    '2026.8.17.zip',  # archived conversation log with credentials
    '2026.8.18.zip',  # archived conversation log with credentials
}
EXCLUDE_FILE_SUFFIXES = {'.pyc', '.pyo'}

def excluded_dir(relpath):
    parts = relpath.replace('\\', '/').split('/')
    for p in parts:
        if p in EXCLUDE_DIR_NAMES:
            return True
    for prefix in EXCLUDE_DIR_PREFIXES:
        if relpath == prefix or relpath.startswith(prefix + os.sep):
            return True
    return False

def excluded_file(relpath, name):
    if name in EXCLUDE_FILE_NAMES:
        return True
    low = name.lower()
    if low.endswith(tuple(EXCLUDE_FILE_SUFFIXES)):
        return True
    if name == '.env' or name.startswith('.env.') and name not in ('.env.template', '.env.example'):
        return True
    return False

def main():
    if os.path.exists(OUT):
        os.remove(OUT)
    count = 0
    total = 0
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for base, dirs, files in os.walk(ROOT):
            relbase = os.path.relpath(base, ROOT)
            if relbase == '.':
                relbase = ''
            # prune excluded dirs in-place
            dirs[:] = [d for d in dirs if not excluded_dir(os.path.join(relbase, d) if relbase else d)]
            for name in files:
                rel = os.path.join(relbase, name) if relbase else name
                if excluded_file(rel, name):
                    continue
                full = os.path.join(base, name)
                # skip the output zip itself
                if os.path.abspath(full) == os.path.abspath(OUT):
                    continue
                zf.write(full, rel)
                count += 1
                total += os.path.getsize(full)
    print('WROTE', OUT)
    print('FILES', count)
    print('BYTES', total)
    print('SIZE', os.path.getsize(OUT))

if __name__ == '__main__':
    main()
