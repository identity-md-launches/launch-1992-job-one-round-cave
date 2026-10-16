#!/usr/bin/env python3
"""Verify gathering 23 records, bytes, preserved pixels and gallery coverage."""
import hashlib
import json
from pathlib import Path

from check_delivery import jpeg_dimensions, png


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parent.parent
    if Path.cwd().resolve() != root:
        raise SystemExit('run from repository root')
    old = Path('artifacts/gathering/wall-v3.png').read_bytes()
    wall = Path('artifacts/gathering/wall-v4.png').read_bytes()
    assert Path('artifacts/gathering/wall.png').is_symlink()
    assert Path('artifacts/gathering/wall.png').readlink() == Path('wall-v4.png')
    assert not Path('artifacts/gathering/wall-v4.png').is_symlink()
    assert Path('artifacts/gathering/wall.png').read_bytes() == wall
    dimensions_old, pixels_old = png(old)
    dimensions, pixels = png(wall)
    assert dimensions_old == dimensions == (1254, 1254)
    preservation = json.loads(Path('gathering/preservation-23.json').read_text())
    assert preservation['inherited_wall_sha256'] == sha(old)
    assert preservation['output_sha256'] == sha(wall)
    x, y, width, height = preservation['mark_rectangle']
    assert (x, y, width, height) == (920, 335, 215, 187)
    protected_old = hashlib.sha256()
    protected_new = hashlib.sha256()
    changed = 0
    stride = 1254 * 3
    for row_number in range(1254):
        start = row_number * stride
        before = pixels_old[start:start+stride]
        after = pixels[start:start+stride]
        if y <= row_number < y + height:
            protected_old.update(before[:x*3]); protected_old.update(before[(x+width)*3:])
            protected_new.update(after[:x*3]); protected_new.update(after[(x+width)*3:])
            for column in range(x, x + width):
                lo = column * 3
                changed += before[lo:lo+3] != after[lo:lo+3]
        else:
            protected_old.update(before); protected_new.update(after)
    assert protected_old.digest() == protected_new.digest()
    assert preservation['protected_rgb_sha256'] == protected_new.hexdigest()
    assert preservation['pixels_changed_outside'] == 0
    assert preservation['changed_pixels_inside'] == changed == 4743

    preview = Path('dist/gathering/23.jpg').read_bytes()
    assert jpeg_dimensions(preview) == (512, 512) and len(preview) < 100000
    record = json.loads(Path('dist/gathering/23.json').read_text())
    assert list(record) == ['name', 'image', 'attributes']
    assert record['image'] == 'https://api.imd.fun/artifacts/' + sha(wall)
    traits = {item['trait_type']: item['value'] for item in record['attributes']}
    assert set(traits) == {'Cave', 'Wall', 'Number', 'Left behind', 'Meaning', 'One thing'}
    assert traits['Cave'] == 'Lava' and traits['Wall'] == traits['One thing'] == 'Gathering'
    assert type(traits['Number']) is int and traits['Number'] == 23
    review = json.loads(Path('gathering/review-23.json').read_text())
    assert review['wall_dimensions'] == [1254, 1254]
    assert review['preview_dimensions'] == [512, 512]
    assert review['wall_sha256'] == sha(wall)
    assert review['visual_requirements_unmet'] == []

    goals = [{'line': n, 'goal': Path(f'line-{n}/GOAL.md').read_text().strip()}
             for n in range(1, 5)]
    assert json.loads(Path('dist/goals.json').read_text()) == goals
    page = Path('dist/index.html').read_text()
    count = 0
    for folder in [f'line-{n}' for n in range(1, 5)] + ['gathering']:
        for path in Path('dist', folder).glob('*.json'):
            assert f'href="{folder}/{path.name}"' in page
            count += 1
        for number in range(2, 22):
            placeholder = Path('dist', folder, f'{number:02}.json')
            assert json.loads(placeholder.read_text())['name'] == 'Not painted yet'
            assert not placeholder.with_suffix('.jpg').exists()
        assert page.index(f'href="{folder}/23.json"') < page.index(f'href="{folder}/22.json"')
    assert count == 115
    sources = json.loads(Path('shared/api_bundle/SOURCES.json').read_text())
    for destination, entry in sources.items():
        assert sha(Path(entry['source']).read_bytes()) == entry['source_sha256']
        assert sha(Path('shared/api_bundle', destination).read_bytes()) == entry['sha256']
    print('PASS: 115 gallery records, four goals, source hashes, PNG/JPEG, 4743 mark pixels, preserved ancestors')


if __name__ == '__main__':
    main()
