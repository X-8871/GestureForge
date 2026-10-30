"""离线读取XSDB的PE导入及厂商启动脚本；不加载DLL或执行厂商程序。"""
from pathlib import Path
import hashlib
import json
import os
import struct

run = Path(__file__).resolve().parent
install = Path('D:/Xilinx/2026.1/Vitis')
exe = install / 'bin/unwrapped/win64.o/xsdb.exe'
content = exe.read_bytes()
pe = struct.unpack_from('<I', content, 0x3c)[0]
assert content[pe:pe + 4] == b'PE\0\0'
n_sections = struct.unpack_from('<H', content, pe + 6)[0]
optional_size = struct.unpack_from('<H', content, pe + 20)[0]
optional = pe + 24
magic = struct.unpack_from('<H', content, optional)[0]
assert magic in (0x10b, 0x20b)
directory = optional + (112 if magic == 0x20b else 96)
imports_rva = struct.unpack_from('<I', content, directory + 8)[0]
sections = []
for i in range(n_sections):
    pos = optional + optional_size + i * 40
    virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from('<IIII', content, pos + 8)
    sections.append((virtual_address, max(virtual_size, raw_size), raw_offset))

def offset(rva):
    for address, size, raw in sections:
        if address <= rva < address + size:
            return raw + rva - address
    raise ValueError('RVA不落在PE节中')

imports = []
pos = offset(imports_rva)
while any(content[pos:pos + 20]):
    name_rva = struct.unpack_from('<I', content, pos + 12)[0]
    start = offset(name_rva)
    end = content.index(b'\0', start)
    name = content[start:end].decode('ascii')
    imports.append({'dll': name, 'in_executable_dir': (exe.parent / name).is_file(),
                    'in_vendor_lib_dir': (install / 'lib/win64.o' / name).is_file()})
    pos += 20
sources = []
for name in ('xsdb.bat', 'setupEnv.bat', 'loader.bat'):
    path = install / 'bin' / name
    raw = path.read_bytes()
    sources.append({'path': str(path), 'hash_basis': 'worktree_disk',
                    'sha256': hashlib.sha256(raw).hexdigest(),
                    'relevant_lines': [{'line': i, 'text': line} for i, line in enumerate(raw.decode('utf-8').splitlines(), 1)
                                       if ('setupEnv.bat' in line or 'loader.bat' in line or
                                           'set RDI_LIBDIR=' in line or 'set PATH=%RDI_LIBDIR%' in line)]})
vendor_lib = install / 'lib/win64.o'
path_parts = [Path(p) for p in os.environ.get('PATH', '').split(os.pathsep) if p]
result = {'method': '仅静态PE与启动脚本读取', 'hardware_called': False, 'vendor_executable_started': False,
          'failure_code_hex': '0xC0000135', 'direct_imports': imports,
          'vendor_lib_in_current_path': any(str(p).lower().replace('\\', '/') == str(vendor_lib).lower() for p in path_parts),
          'vendor_launcher_sources': sources,
          'finding': '厂商xsdb.bat先调用setupEnv与loader；loader将RDI_LIBDIR加入PATH。直接裸exe入口未执行这些准备，与当前加载失败一致。',
          'limitations': ['没有捕获系统加载器的精确缺失DLL报告，不能仅凭静态导入确认唯一缺失项',
                          '未执行修正入口、未重试枚举；下次需先用不含connect的离线Tcl验证厂商入口，并独立审查进程树清理',
                          '下次真实枚举需新RunId与重新核验的独占窗口；本轮失败原样保留']}
with (run / 'static_startup_diagnosis.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
