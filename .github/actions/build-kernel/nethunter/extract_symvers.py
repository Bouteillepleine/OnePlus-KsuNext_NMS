import sys, struct
from elftools.elf.elffile import ELFFile

ko, modname, out = sys.argv[1], sys.argv[2], sys.argv[3]
f = open(ko,'rb'); elf = ELFFile(f)

# section index -> (name, data)
secs = {i:(s.name, s.data()) for i,s in enumerate(elf.iter_sections())}
# which section indices are the crc tables
crc_secs = {i:name for i,(name,_) in secs.items() if name in ('__kcrctab','__kcrctab_gpl')}

symtab = elf.get_section_by_name('.symtab')
rows = []
for sym in symtab.iter_symbols():
    n = sym.name
    if not n.startswith('__crc_'):
        continue
    shndx = sym['st_shndx']
    if shndx not in crc_secs:
        continue
    off = sym['st_value']
    data = secs[shndx][1]
    crc = struct.unpack_from('<I', data, off)[0]
    export = 'EXPORT_SYMBOL_GPL' if crc_secs[shndx]=='__kcrctab_gpl' else 'EXPORT_SYMBOL'
    rows.append((crc, n[len('__crc_'):], export))

rows.sort(key=lambda r:r[1])
with open(out,'w') as o:
    for crc, name, export in rows:
        o.write(f"0x{crc:08x}\t{name}\tnet/wireless/{modname}\t{export}\t\n")
print(f"wrote {len(rows)} symbols -> {out}")
