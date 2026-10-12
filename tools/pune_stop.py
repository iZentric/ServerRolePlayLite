#!/usr/bin/env python3
"""Pune un repeating_command_block (stop) intr-un .mca — chirurgie NBT 1.16.5.
Folosire: pune_stop.py <region.mca> <bx> <by> <bz> [comanda]
Backup: <region.mca>.bak se scrie automat."""
import sys, struct, zlib, math, gzip, shutil, io
import nbtlib
from nbtlib import Byte, Int, String, Compound, List, LongArray

def read_region(path):
    raw = open(path, 'rb').read()
    chunks = {}
    for i in range(1024):
        off = struct.unpack('>I', b'\x00' + raw[i*4:i*4+3])[0]
        cnt = raw[i*4+3]
        if off == 0:
            continue
        start = off * 4096
        ln = struct.unpack('>I', raw[start:start+4])[0]
        comp = raw[start+4]
        payload = raw[start+5:start+4+ln]
        chunks[i] = (comp, payload)
    return raw, chunks

def write_region(path, raw_orig, chunks):
    out = bytearray(4096)  # doar tabela de locatii; timestampurile = ts
    ts = bytearray(4096)
    body = bytearray()
    for i in sorted(chunks):
        comp, payload = chunks[i]
        data = bytes([comp]) + payload
        ln = len(data)
        start_sec = (8192 + len(body)) // 4096
        sectors = (ln + 4 + 4095) // 4096
        if start_sec + sectors > 255 * 256:
            raise SystemExit('regiune plina')
        struct.pack_into('>I', out, i*4, (start_sec << 8) & 0xFFFFFF00)
        out[i*4+3] = sectors
        body += struct.pack('>I', ln) + data
        body += b'\x00' * (sectors * 4096 - ln - 4)
    open(path, 'wb').write(bytes(out) + bytes(ts) + bytes(body))

def repack(states, palette_len, idx, value):
    bits = max(4, math.ceil(math.log2(palette_len))) if palette_len > 1 else 4
    per = 4096
    new_len = (per * bits + 63) // 64
    vals = []
    mask = (1 << bits) - 1
    total_bits = per * bits
    acc = 0
    for s in states:
        acc = (acc << 64) | (s & 0xFFFFFFFFFFFFFFFF)
    # reconstruct flat values (values SPAN longs — format 1.16+)
    acc_bits = len(states) * 64
    # align: the array is packed from the low end of the first long
    flat = []
    # easier: bitstream from the END of each long? NU — 1.16: value k occupies bits [k*bits, (k+1)*bits) of the concatenated stream starting at bit 0 = LSB of long 0
    stream = 0
    for s in states:
        stream |= (s & 0xFFFFFFFFFFFFFFFF) << (64 * states.index(s)) if False else 0
    # rebuild properly
    stream = 0
    for i, s in enumerate(states):
        stream |= (s & 0xFFFFFFFFFFFFFFFF) << (64 * i)
    for k in range(per):
        flat.append((stream >> (k * bits)) & mask)
    flat[idx] = value
    out_states = [0] * new_len
    for k, v in enumerate(flat):
        bitpos = k * bits
        li, lo = divmod(bitpos, 64)
        out_states[li] |= (v & mask) << lo
        hi = lo + bits
        if hi > 64:
            out_states[li + 1] |= (v & mask) >> (64 - lo)
        out_states[li] &= 0xFFFFFFFFFFFFFFFF
    return [nbtlib.Long(s if s < 2**63 else s - 2**64) for s in out_states], bits

def main():
    region_path, bx, by, bz = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    cmd = sys.argv[5] if len(sys.argv) > 5 else 'stop'
    cx, cz = bx >> 4, bz >> 4
    idx_in_region = ((cx & 31) + (cz & 31) * 32)
    raw, chunks = read_region(region_path)
    if idx_in_region not in chunks:
        raise SystemExit('chunk-ul nu exista in regiune')
    comp, payload = chunks[idx_in_region]
    data = zlib.decompress(payload) if comp == 2 else gzip.decompress(payload)
    nbt = nbtlib.File.parse(io.BytesIO(data))
    level = nbt['Level']
    sy = by >> 4
    sec = None
    for s in level['Sections']:
        if int(s['Y']) == sy:
            sec = s
            break
    if sec is None:
        sec = Compound({'Y': nbtlib.Byte(sy), 'Palette': List([Compound({'Name': String('minecraft:air')})]),
                        'BlockStates': LongArray([0]*256), 'BlockLight': nbtlib.ByteArray([0]*2048),
                        'SkyLight': nbtlib.ByteArray([-1]*2048)})
        level['Sections'].append(sec)
    palette = list(sec['Palette'])
    name = 'minecraft:repeating_command_block'
    pal_names = [str(p['Name']) for p in palette]
    if name in pal_names:
        pidx = pal_names.index(name)
    else:
        palette.append(Compound({'Name': String(name)}))
        pidx = len(palette) - 1
        sec['Palette'] = List(palette)
    states = list(sec['BlockStates'])
    block_idx = (by & 15) * 256 + (bz & 15) * 16 + (bx & 15)
    new_states, bits = repack(states, len(palette), block_idx, pidx)
    sec['BlockStates'] = LongArray(new_states)
    # tile entity
    tes = level.setdefault('TileEntities', List[Compound]([]))
    rest = [t for t in tes if not (int(t['x']) == bx and int(t['y']) == by and int(t['z']) == bz)]
    rest.append(Compound({
        'id': String('minecraft:repeating_command_block'), 'x': Int(bx), 'y': Int(by), 'z': Int(bz),
        'Command': String(cmd), 'auto': Byte(1), 'UpdateLastExecution': Byte(1),
        'TrackOutput': Byte(0), 'LastOutput': String(''),
    }))
    level['TileEntities'] = List[Compound](rest)
    shutil.copy2(region_path, region_path + '.bak')
    buf = io.BytesIO(); nbt.write(buf); out = zlib.compress(buf.getvalue())
    chunks[idx_in_region] = (2, out)
    write_region(region_path, raw, chunks)
    print(f'OK: repeating_command_block "{cmd}" la {bx},{by},{bz} in chunk {cx},{cz} (bits={bits}, palette={len(palette)})')

if __name__ == '__main__':
    main()
