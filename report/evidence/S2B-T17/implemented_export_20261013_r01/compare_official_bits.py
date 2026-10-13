"""只读比较官方 XSA 内外两份 bit 的全部头字段和配置 payload。"""
from pathlib import Path
import hashlib
import json
import struct
import zipfile

ROOT = Path(__file__).absolute().parents[4]
RUN = ROOT / "report/evidence/S2B-T17/direct_bitgen_20261013T054357Z_ccbeeb35a2053320"


def parse(raw):
    """精确解析 a 至 e 字段并拒绝越界或尾随内容。"""
    offset = 2 + struct.unpack_from(">H", raw, 0)[0]
    if struct.unpack_from(">H", raw, offset)[0] != 1:
        raise RuntimeError("bit 头 marker 错误")
    offset += 2
    fields = {}
    for tag in ("a", "b", "c", "d"):
        if chr(raw[offset]) != tag:
            raise RuntimeError("bit 头字段顺序错误")
        offset += 1
        size = struct.unpack_from(">H", raw, offset)[0]
        offset += 2
        value = raw[offset:offset + size]
        fields[tag] = {"raw_hex": value.hex(), "text": value.rstrip(bytes([0])).decode("ascii")}
        offset += size
    if chr(raw[offset]) != "e":
        raise RuntimeError("bit payload marker 错误")
    size = struct.unpack_from(">I", raw, offset + 1)[0]
    offset += 5
    if offset + size != len(raw):
        raise RuntimeError("bit payload 长度错误")
    if fields["b"]["text"] != "7z020clg400":
        raise RuntimeError("bit 器件错误")
    payload = raw[offset:]
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "fields": fields,
        "header_bytes": offset, "header_sha256": hashlib.sha256(raw[:offset]).hexdigest(),
        "payload_bytes": size, "payload_sha256": hashlib.sha256(payload).hexdigest()}, payload


def main():
    """输出全部差异位置，不改写原 bit 或 XSA。"""
    external = (RUN / "s2b_inference_wrapper_postroute_physopt.bit").read_bytes()
    with zipfile.ZipFile(RUN / "s2b_inference_implemented.xsa") as stream:
        embedded = stream.read("s2b_inference_implemented.bit")
    left, left_payload = parse(external)
    right, right_payload = parse(embedded)
    differences = [index for index, pair in enumerate(zip(external, embedded)) if pair[0] != pair[1]]
    result = {"schema_version": 1, "external": left, "embedded": right,
        "same_complete_bytes": external == embedded, "same_payload_bytes": left_payload == right_payload,
        "payload_difference_count": sum(a != b for a, b in zip(left_payload, right_payload)) + abs(len(left_payload) - len(right_payload)),
        "complete_difference_offsets": differences, "complete_length_difference": len(external) - len(embedded),
        "differences_only_in_header": all(index < min(left["header_bytes"], right["header_bytes"]) for index in differences)
            and left_payload == right_payload}
    output = Path(__file__).absolute().parent / "official_bit_payload_facts_r01.json"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
