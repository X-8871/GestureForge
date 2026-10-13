"""原样筛选有效Basic授权，在私有目录保存，并复用已审查的Bitgen控制器。"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
RUN = Path(__file__).resolve().parent
SOURCE = Path("C:/Users/22061/Downloads/Xilinx.lic")
SOURCE_SHA = "0ade29bca5b51f0586cd662d39535de659876ef0273fbf582be17b66398fbec6"
CONTROLLER_SHA = "eb11cbd7285b6b647444c265be805c47d7ef3e2f18334a9c7ff9756f7f634441"
LMUTIL = Path(r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\lmutil.exe")
sys.path.insert(0, r"C:\Espressif\python_env\idf5.5_py3.12_env\Lib\site-packages")
sys.path.insert(0, str(ROOT / "verification"))
import s15_direct_vivado_bitgen as controller


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_file(path):
    """复用控制器的精确路径及重解析点核验。"""
    return Path(controller._assert_path_chain(str(path), "file"))


def records(data):
    """按完整续行块读取，不改变块内任何字节。"""
    data.decode("utf-8")
    lines = data.splitlines(keepends=True)
    index = 0
    result = []
    while index < len(lines):
        line = lines[index]
        index += 1
        if not re.match(rb"^(PACKAGE|INCREMENT|FEATURE)\s", line):
            continue
        block = line
        while line.rstrip(b"\r\n").rstrip().endswith(b"\\"):
            if index >= len(lines):
                raise RuntimeError("授权块续行不完整")
            line = lines[index]
            index += 1
            block += line
        tokens = re.sub(rb"\\\r?\n\s*", b" ", block).split()
        result.append((tokens, block))
    return result


def select_basic(data):
    """只选择厂商原签名的Basic包及有效功能，不改名、不改日期、不重签名。"""
    names = {b"Vivado_Basic_Package", b"Vivado_Implementation", b"Vivado_Synthesis", b"Vivado_Simulation"}
    selected = []
    public = []
    for tokens, block in records(data):
        if tokens[1] not in names:
            continue
        if tokens[0] in (b"INCREMENT", b"FEATURE") and tokens[4] != b"07-aug-2027":
            continue
        if tokens[2] != b"xilinxd" or tokens[3] != b"2027.08":
            raise RuntimeError("Basic授权厂商或版本不符合已核验记录")
        selected.append(block)
        public.append({"record": tokens[0].decode(), "feature": tokens[1].decode(),
                       "version": tokens[3].decode(), "sha256": digest(block),
                       "expiry": tokens[4].decode() if tokens[0] != b"PACKAGE" else None})
    expected = {("PACKAGE", "Vivado_Basic_Package"), ("INCREMENT", "Vivado_Basic_Package"),
                ("INCREMENT", "Vivado_Implementation"), ("INCREMENT", "Vivado_Synthesis"),
                ("INCREMENT", "Vivado_Simulation")}
    if len(public) != 5 or {(item["record"], item["feature"]) for item in public} != expected:
        raise RuntimeError("有效Basic授权块集合不完整或存在重复")
    return b"".join(selected), public


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def diagnose(path, feature):
    """仅保存脱敏诊断结论，不输出主机标识、邮箱、签名或密钥。"""
    result = subprocess.run([str(checked_file(LMUTIL)), "lmdiag", "-n", "-c", str(path), feature],
                            capture_output=True, timeout=30)
    text = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    return {"feature": feature, "native_exit_code": result.returncode,
            "correct_node": "This is the correct node" in text,
            "expired": "license has expired" in text.lower(),
            "cannot_checkout": "cannot be checked out" in text,
            "no_such_feature": "No such feature" in text,
            "flexnet_errors": re.findall(r"FlexNet Licensing error:\s*(-?\d+(?:,\d+)*)(?=\s|$)", text),
            "raw_output_not_retained_reason": "保护邮箱、主机标识及厂商授权元数据"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--attempt", default="r01", choices=("r01", "r02"))
    args = parser.parse_args()
    checked_file(SOURCE)
    checked_file(ROOT / "verification" / "s15_direct_vivado_bitgen.py")
    if digest((ROOT / "verification" / "s15_direct_vivado_bitgen.py").read_bytes()) != CONTROLLER_SHA:
        raise RuntimeError("已审查控制器版本发生变化")
    original = SOURCE.read_bytes()
    if digest(original) != SOURCE_SHA:
        raise RuntimeError("用户许可证与已核验SHA不一致")
    selected, public = select_basic(original)
    if not args.execute:
        if (RUN / "private_selection.json").exists():
            raise RuntimeError("拒绝覆盖既有隔离记录")
        profile, audit = controller._create_private_appdata_profile("basic_license_isolation_20261013_r01")
        target = Path(profile) / "basic_only.lic"
        with target.open("xb") as stream:
            stream.write(selected)
        checked_file(target)
        controller._inspect_directory_security(profile, controller._current_process_token_sids()[0], require_private_dacl=True)
        info = {"source_sha256": SOURCE_SHA, "selected_sha256": digest(selected),
                "private_license_path": str(target), "profile_acl_verified": True,
                "records": public, "signed_blocks_unchanged": True}
        write_json(RUN / "private_selection.json", info)
        output = {key: val for key, val in info.items() if key != "private_license_path"}
        output["diagnostics"] = [diagnose(target, feature) for feature in
                                 ("Vivado_Basic_Package", "Vivado_Implementation", "Vivado_Synthesis")]
        if any(item["native_exit_code"] != 0 or not item["correct_node"] or item["cannot_checkout"]
               for item in output["diagnostics"]):
            raise RuntimeError("有效Basic授权诊断失败，拒绝启动Vivado")
        write_json(RUN / "selection_result.json", output)
        print(json.dumps(output, ensure_ascii=False))
        return 0
    info = json.loads((RUN / "private_selection.json").read_text(encoding="utf-8"))
    result_path = RUN / ("execution_result.json" if args.attempt == "r01" else "execution_result_r02.json")
    if result_path.exists():
        raise RuntimeError("拒绝覆盖既有执行记录")
    target = checked_file(Path(info["private_license_path"]))
    if target.read_bytes() != selected or digest(selected) != info["selected_sha256"]:
        raise RuntimeError("私有Basic授权与原样筛选结果不一致")
    controller._inspect_directory_security(str(target.parent), controller._current_process_token_sids()[0], require_private_dacl=True)
    diagnostic = diagnose(target, "Vivado_Implementation")
    if diagnostic["native_exit_code"] or not diagnostic["correct_node"] or diagnostic["cannot_checkout"]:
        raise RuntimeError("启动前实现授权诊断失败")
    evidence_root = Path(controller.EVIDENCE_ROOT)
    existing = set(evidence_root.glob("direct_bitgen_*"))
    previous = {name: os.environ.get(name) for name in controller.LICENSE_ENVIRONMENT_NAMES}
    started = time.monotonic()
    try:
        # 既有循环在采样结束后再等待；缩短等待以给身份采集留裕量，所有硬停止阈值不变。
        if args.attempt == "r02":
            controller.SAMPLE_INTERVAL_SECONDS = 0.25
        os.environ["XILINXD_LICENSE_FILE"] = str(target)
        os.environ.pop("LM_LICENSE_FILE", None)
        code = controller.main(["--execute-frozen-bitgen"])
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    created = sorted(str(path.relative_to(ROOT)) for path in set(evidence_root.glob("direct_bitgen_*")) - existing)
    result = {"controller_exit_code": code, "elapsed_seconds": time.monotonic() - started,
              "new_bitgen_runs": created, "selected_license_sha256": digest(selected),
              "sampling_target_seconds": controller.SAMPLE_INTERVAL_SECONDS,
              "original_license_unchanged": digest(SOURCE.read_bytes()) == SOURCE_SHA,
              "utc_finished": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    write_json(result_path, result)
    print(json.dumps(result, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
