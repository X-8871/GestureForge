#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""比较ELF PT_LOAD布局与内容，仅屏蔽GNU build-id note描述字段。"""
import hashlib, json, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
E=ROOT/"report/evidence/S2B-T15/recovery_inputs_20261019_r02"
T=ROOT/"tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_03/fresh_build"
ART=ROOT/"report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts"

def sha(b): return hashlib.sha256(b).hexdigest()
def elf(path):
    d=Path(path).read_bytes()
    if d[:4]!=b"\x7fELF" or d[4]!=1 or d[5]!=1: raise ValueError("仅支持ELF32 little-endian")
    h=struct.unpack_from("<16sHHIIIIIHHHHHH",d,0)
    entry,phoff,shoff=h[4],h[5],h[6]
    phentsz,phnum=h[9],h[10]
    shentsz,shnum,shstrndx=h[11],h[12],h[13]
    programs=[]
    for i in range(phnum):
        row=struct.unpack_from("<IIIIIIII",d,phoff+i*phentsz)
        programs.append({"type":row[0],"offset":row[1],"vaddr":row[2],"paddr":row[3],"filesz":row[4],"memsz":row[5],"flags":row[6],"align":row[7]})
    raw_sections=[]
    for i in range(shnum): raw_sections.append(struct.unpack_from("<IIIIIIIIII",d,shoff+i*shentsz))
    names_sec=raw_sections[shstrndx]
    names=d[names_sec[4]:names_sec[4]+names_sec[5]]
    sections=[]
    for s in raw_sections:
        end=names.find(b"\0",s[0]); name=names[s[0]:end].decode("ascii","replace")
        sections.append({"name":name,"type":s[1],"flags":s[2],"addr":s[3],"offset":s[4],"size":s[5]})
    note=None
    for s in sections:
        if s["name"]!=".note.gnu.build-id": continue
        at=s["offset"]; namesz,descsz,typ=struct.unpack_from("<III",d,at)
        nstart=at+12; nend=nstart+((namesz+3)&~3)
        if d[nstart:nstart+namesz]!=b"GNU\0" or typ!=3: continue
        note={"section":s["name"],"descriptor_offset":nend,"descriptor_size":descsz,"build_id_hex":d[nend:nend+descsz].hex()}
    if note is None:
        # GCC init ELF可能把GNU note放在未命名section布局中，按ELF note格式精确定位GNU type=3记录。
        for s in sections:
            if s["type"]!=7: continue
            pos=s["offset"]; stop=pos+s["size"]
            while pos+12<=stop:
                ns,ds,typ=struct.unpack_from("<III",d,pos); nn=pos+12; dd=nn+((ns+3)&~3)
                if ns>=4 and d[nn:nn+4]==b"GNU\0" and typ==3:
                    note={"section":s["name"],"descriptor_offset":dd,"descriptor_size":ds,"build_id_hex":d[dd:dd+ds].hex()}; break
                pos=dd+((ds+3)&~3)
            if note: break
    if note is None:
        marker=struct.pack("<III",4,20,3)+b"GNU\0"
        at=d.find(marker)
        if at>=0 and at+len(marker)+20<=len(d):
            note={"section":"embedded GNU build-id note", "descriptor_offset":at+len(marker),"descriptor_size":20,"build_id_hex":d[at+len(marker):at+len(marker)+20].hex()}
    return d,entry,programs,sections,note

def compare(orig,new):
    a=elf(orig); b=elf(new); da,ea,pa,sa,na=a; db,eb,pb,sb,nb=b
    la=[x for x in pa if x["type"]==1 and x["memsz"]]
    lb=[x for x in pb if x["type"]==1 and x["memsz"]]
    layout_a=[{k:x[k] for k in ("paddr","vaddr","filesz","memsz","flags")} for x in la]
    layout_b=[{k:x[k] for k in ("paddr","vaddr","filesz","memsz","flags")} for x in lb]
    segments=[]
    for i,(x,y) in enumerate(zip(la,lb)):
        xa=bytearray(da[x["offset"]:x["offset"]+x["filesz"]]); yb=bytearray(db[y["offset"]:y["offset"]+y["filesz"]])
        diffs=[]
        if len(xa)==len(yb):
            for j,(av,bv) in enumerate(zip(xa,yb)):
                if av!=bv: diffs.append(j)
        mask_a=[]; mask_b=[]
        for note,seg,data in ((na,x,xa),(nb,y,yb)):
            if note:
                lo=max(note["descriptor_offset"],seg["offset"]); hi=min(note["descriptor_offset"]+note["descriptor_size"],seg["offset"]+seg["filesz"])
                if lo<hi:
                    start=lo-seg["offset"]; end=hi-seg["offset"]; data[start:end]=b"\0"*(end-start)
                    (mask_a if seg is x else mask_b).append([start,end])
        segments.append({"index":i,"orig_layout":layout_a[i],"rebuilt_layout":layout_b[i],"orig_payload_sha256":sha(bytes(xa)),"rebuilt_payload_sha256":sha(bytes(yb)),"raw_differing_offsets":diffs[:128],"raw_difference_count":len(diffs),"orig_masked_build_id_ranges":mask_a,"rebuilt_masked_build_id_ranges":mask_b,"normalized_equal":len(xa)==len(yb) and xa==yb})
    # 可装载section摘要只报告SHF_ALLOC部分，供复核定位。
    alloc_a=[s for s in sa if s["flags"]&2]; alloc_b=[s for s in sb if s["flags"]&2]
    return {"original":{"path":str(orig),"sha256":sha(da),"entry":ea,"build_id":na,"pt_load_layout":layout_a,"alloc_sections":alloc_a},"rebuilt":{"path":str(new),"sha256":sha(db),"entry":eb,"build_id":nb,"pt_load_layout":layout_b,"alloc_sections":alloc_b},"entry_equal":ea==eb,"pt_load_layout_equal":layout_a==layout_b,"pt_load_count_equal":len(la)==len(lb),"pt_load_segments":segments,"all_pt_load_payload_equal_after_only_build_id_descriptor_mask":len(la)==len(lb) and all(s["normalized_equal"] for s in segments),"interpretation":"只将GNU build-id note的描述字段按段内对应位置归零；其余PT_LOAD文件字节逐字节比较。不同的ELF非装载元数据不等于运行载荷不同。"}

def main():
    out={}
    for app in ("infer","init"):
        orig=ART/(app+".elf"); new=T/app/(app+".elf")
        out[app]=compare(orig,new)
    target=E/"comparison.json"
    if target.exists(): raise FileExistsError(target)
    target.write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps({k:{"entry_equal":v["entry_equal"],"layout_equal":v["pt_load_layout_equal"],"payload_equal":v["all_pt_load_payload_equal_after_only_build_id_descriptor_mask"],"orig_build_id":v["original"]["build_id"],"new_build_id":v["rebuilt"]["build_id"]} for k,v in out.items()},indent=2))

if __name__=="__main__": main()
