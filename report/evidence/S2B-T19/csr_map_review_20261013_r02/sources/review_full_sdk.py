"""在无设备节点上执行原厂完整映射与HWH字段计算路径。"""
from pathlib import Path
import ast

source=Path(__file__).with_name("review_sdk_cases.py").read_text(encoding="utf-8")
source=source.replace('("loadhw","unloadhw","__clear_memmap")','("loadhw","unloadhw","__set_memmap","__clear_memmap")')
source=source.replace('sdk_fixture_r02','sdk_fixture_r03').replace('sdk_cases_result.json','full_sdk_cases_result.json')
source=source.replace('    def close(self):state["closed"]+=1','''    def close(self):state["closed"]+=1
    def get_cells(self,filter,hierarchical):
        return [SimpleNamespace(IP_NAME="ps7_cortexa9",NAME="ps7_cortexa9_0")] if filter=="IP_TYPE==PROCESSOR" else []
    def get_mem_ranges(self,of_object,filter):
        return [SimpleNamespace(NAME="infer",BASE_VALUE="0x43C00000",HIGH_VALUE="0x43C0FFFF",SLAVE_INTERFACE="S_AXI",MEM_TYPE="REGISTER",ACCESS_TYPE="READ_WRITE",TRUSTZONE="") ] if filter=="MEM_TYPE!=MEMORY" else []''')
source=source.replace('Target=env["Target"]',r'''Target=env["Target"]
hsi_path=Path(r"D:\Xilinx\2026.1\Vitis\cli\hsiutils\__init__.py")
hsi_tree=ast.parse(hsi_path.read_text(encoding="utf-8-sig"))
hsi_function=next(row for row in hsi_tree.body if isinstance(row,ast.FunctionDef) and row.name=="get_address_range")
hsi_env={"get_hier_name":lambda design,mem:mem.NAME}
exec(compile(ast.fix_missing_locations(ast.Module(body=[hsi_function],type_ignores=[])),str(hsi_path),"exec"),hsi_env)
env["hsiutils"]=SimpleNamespace(get_address_range=hsi_env["get_address_range"],get_all_register_data=lambda design,p:{})
env["dict_get_value_or_error_out"]=lambda data,key:data[key]
props={"apu":{"ParentID":""},"cpu0":{"ParentID":"apu","CPUType":"ARM","ARMType":"Cortex-A9","CoreNo":0},"cpu1":{"ParentID":"apu","CPUType":"ARM","ARMType":"Cortex-A9","CoreNo":1}}
nodes={ctx:SimpleNamespace(id=ctx,get_run_context=lambda ctx=ctx:SimpleNamespace(getProperties=lambda:props[ctx])) for ctx in props}
env["exec_as_runnable"]=lambda function,node:node.get_run_context()
''')
source=source.replace('apu._Target__get_current_node=lambda:SimpleNamespace()','apu._Target__get_current_node=lambda:nodes["apu"]\ncase.session._model=SimpleNamespace(get_nodes=lambda:nodes)')
source=source.replace('    apu._Target__set_memmap=valid_set','    apu._Target__set_memmap=Target._Target__set_memmap.__get__(apu,Target)')
source=source.replace('"official_load_unload_success"','"official_full_set_hsi_load_unload_success"')
exec(compile(source,str(Path(__file__)),"exec"))
