"""重新计算r02生成内容并逐字节核对，不覆盖任何已生成原件。"""
from pathlib import Path
import derive_r02 as generator

WORK=Path(__file__).parent
count=0
def compare(name,text):
 """生成期输出必须与当前完整草稿、diff及输入绑定一致。"""
 global count
 assert (WORK/name).is_file() and (WORK/name).read_bytes()==text.encode('utf-8'),name
 count+=1
generator.save=compare
generator.main()
print('R02_GENERATED_BYTES_VERIFIED:'+str(count))
