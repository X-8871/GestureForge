"""保全已检查的准备源码并补充本轮资源原件绑定，只写独占cache。"""
from collection_common import *
receipt=read(WORK/'prepared_receipt.json')
target=mkdir_new(WORK/'prepared_sources')
copies=[]
for row in receipt['prepared_scripts']:
    source=exact(ROOT/row['path'])
    require(binding(source)==row,'准备源码已变化，不能补造历史版本')
    copies.append(rawcopy(source,target/source.name))
save(WORK/'prepared_source_mapping.json',{'status':'PREPARED_SOURCES_EXACTLY_PRESERVED_BEFORE_COLLECTION_ADAPTATION','prepared_receipt':binding(WORK/'prepared_receipt.json'),'files':copies,'note':'收集阶段新增关闭门禁与资源适配前保留原准备版本；正式包将另存当前运行代码，不把原preparation核验归于修改后的代码。'})
files=[binding(CACHE/name) for name in ('resource_preflight_tool.json','resource_at_launch_tool.json')]
save(WORK/'supplemental_closed_inputs.json',{'status':'S7_CLOSED_ADDITIONAL_RESOURCES_BOUND','root_explicit_signal':'CLOSED_INPUTS_READY','files':files,'gate_builder_execution':{'command':['C:\\Users\\22061\\AppData\\Local\\Programs\\Python\\Python312\\python.exe','-B',str(WORK/'build_closed_gate.py')],'host_tool_chunk_id':'ad92c4','host_shell_exit_code':0,'native_exit_code':None,'reason':'门禁创建经PowerShell/Git Bash宿主执行，未另行捕获子进程returncode；实际关闭门禁内容与SHA另绑，不伪填native0。'},'git_read_authorization':'ROOT澄清允许40次只读明确a5 Git对象，禁止Git写入/暂存/提交/切换/重置/维护。'})
print(json.dumps({'prepared_sources':len(copies),'resource_files':files,'prepared_source_mapping':binding(WORK/'prepared_source_mapping.json'),'supplemental_closed_inputs':binding(WORK/'supplemental_closed_inputs.json')},ensure_ascii=False))
