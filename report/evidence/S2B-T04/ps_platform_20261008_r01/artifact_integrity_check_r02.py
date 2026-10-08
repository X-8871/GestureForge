"""核验 PS-only 候选的源表、BD/HWH、wrapper 与无位流 XSA。"""

import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

root = Path(__file__).absolute().parents[4]
evidence = root / "report/evidence/S2B-T04/ps_platform_20261008_r01"
final = evidence / "rebuild_attempt4"
fields = json.loads((root / "board/ps_platform_fields.json").read_text(encoding="utf-8"))
assert fields["part"] == "xc7z020clg400-2"
with (final / "readback.tsv").open(encoding="utf-8", newline="") as handle:
    actual = {row["parameter"]: row["actual"] for row in csv.DictReader(handle, delimiter="\t")}
assert len(actual) == len(fields["fields"]) == 73
for field in fields["fields"]:
    assert actual[field["parameter"]] == field["actual"]
    assert field["source_ids"] and all(source in fields["sources"] for source in field["source_ids"])
    if field["role"] == "requested":
        assert field["candidate"] == actual[field["parameter"]]
assert sum(field["role"] == "requested" for field in fields["fields"]) == 50
script = (root / "vivado/s2b_ps_platform.tcl").read_text(encoding="utf-8")
requested_text = script.split("proc ::s2b_ps_platform::requested {} {", 1)[1].split("proc ::s2b_ps_platform::configure", 1)[0]
requested = dict(re.findall(r"(CONFIG\.[A-Z0-9_]+) \{([^}]*)\}", requested_text))
assert len(requested) == 50
assert all(actual[key] == value for key, value in requested.items())
bd = json.loads((final / "s2b_ps_only.bd").read_text(encoding="utf-8"))["design"]
assert bd["design_info"]["device"] == fields["part"]
assert bd["design_info"]["validated"] == "true"
assert list(bd["components"]) == ["ps7"]
assert set(bd["interface_ports"]) == {"DDR_0", "FIXED_IO_0"}
ports = bd["interface_ports"]["DDR_0"]["port_maps"]
assert (ports["DQ"]["left"], ports["DQ"]["right"]) == ("31", "0")
assert (ports["ADDR"]["left"], ports["BA"]["left"]) == ("14", "2")
assert bd["interface_ports"]["FIXED_IO_0"]["port_maps"]["MIO"]["left"] == "53"
with ZipFile(final / "s2b_ps_only.xsa") as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    assert all(not name.lower().endswith((".bit", ".bin", ".mcs")) for name in names)
    assert all(name in names for name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl", "s2b_ps_only.hwh"))
    hwh = ET.fromstring(archive.read("s2b_ps_only.hwh"))
    modules = hwh.findall(".//MODULE")
    assert len(modules) == 1 and modules[0].attrib["MODTYPE"] == "processing_system7"
    assert modules[0].attrib["IS_PL"] == "FALSE"
    names_requested = {key.removeprefix("CONFIG.") for key in requested}
    rows = [item for item in modules[0].findall(".//PARAMETER") if item.attrib.get("NAME") in names_requested]
    assert len(rows) == len(names_requested)
    parameters = {item.attrib["NAME"]: item.attrib["VALUE"] for item in rows}
    assert all(parameters[key.removeprefix("CONFIG.")] == value for key, value in requested.items())
    for name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl"):
        assert (final / name).read_bytes() == archive.read(name)
wrapper = (final / "s2b_ps_only_wrapper.v").read_text(encoding="utf-8")
assert re.search(r"inout\s*\[31:0\]\s*DDR_0_dq", wrapper)
assert not re.search(r"\b[MS]_AXI_|FCLK_", wrapper)
for path in (root / "vivado/s2b_ps_platform.tcl", root / "board/ps_platform_fields.json", root / "board/ps_platform.md"):
    raw = path.read_bytes()
    raw.decode("utf-8")
    assert b"\r" not in raw
print(json.dumps({"status": "ARTIFACT_CHECKS_OK", "requested_parameters": len(requested), "readback_parameters": len(actual), "bd_cells": list(bd["components"]), "external_interfaces": list(bd["interface_ports"]), "xsa_entries": names, "contains_bitstream": False, "python": sys.version.split()[0], "script_sha256": hashlib.sha256(script.encode("utf-8")).hexdigest()}, ensure_ascii=False, indent=2))
