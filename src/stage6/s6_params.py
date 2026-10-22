"""阶段6 参数装载与校验（S6-B，契约 S6A-G0-v1.6，对应 S6-A r07）。

S6-A r05（v1.4）与 r06（v1.5）已分别通过第 5/6 轮独立复评（PASS），r07（v1.6）收尾 F1–F11 与 BLK-1；
本模块按 **v1.6** 契约装载参数，不做任何数值覆盖、不做"临时调参"入口。
`REQUIRED_PARAMETER_IDS` 覆盖行为表全部 24 项参数：删除任意一项即拒载（N-06）。

设计约束（对应 AGENTS.md 与 S6-A G0 包）：

1. 全部阶段6 阈值/指标只从 ``docs/stage6/s6a_stage6_g0_behavior_v1.json`` 读取，
   本模块不做任何数值覆盖、不做任何"临时调参"入口。
2. 装载时强制校验每个参数仍为 ``PENDING_APPROVAL``；若上游被改成其它状态，
   必须由后续任务显式改写代码与证据，而不是让实现静默跟随。
3. 上游已冻结接口常量（2A：五类顺序、class_id 0..4、≤15 框、score 口径）
   来自 ``docs/stage6/s6b_frozen_interface_v1.json`` 并复核 2A 原件 SHA-256。
4. 单位换算集中在本模块完成：时间参数统一换算为纳秒整数，帧类参数为整数，
   分数/几何/IoU 为 float64 原值。

本模块不读取摄像头、不读墙钟、不访问硬件。
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXPECTED_ARTIFACT = "s6a_stage6_g0_behavior"
EXPECTED_ARTIFACT_VERSION = "S6A-G0-v1.7"
PENDING_APPROVAL = "PENDING_APPROVAL"

# 单位换算常量只出现在装载层，不进入判定核心。
_MS_TO_NS = 1_000_000
_FRAME_TO_COUNT = 1

# 核心判定需要的阶段6 参数（缺一即拒绝启动）。
REQUIRED_PARAMETER_IDS = (
    "T6-A01",
    "T6-A02",
    "T6-A03",
    "T6-C01",
    "T6-S01",
    "T6-S02",
    "T6-S03",
    "T6-S04",
    "T6-L01",
    "T6-L02",
    "T6-K01",
    "T6-J01",
    "T6-U00_W",
    "T6-U00_N",
    "T6-U01",
    "T6-P01",
    "T6-P02",
    "T6-P03",
    "T6-P04",
    "T6-P05",
    "T6-STALE_LIMIT",
    "T6-01",
    "T6-02",
    "T6-03",
)

_REQUIRED_HARD_INVARIANTS = ("H-1", "H-2", "H-3", "H-4", "H-5", "H-6", "H-7", "H-8", "H-9", "H-10")


class ParamError(RuntimeError):
    """参数装载/校验失败。调用方必须按输入错误处理（退出码 2）。"""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ParamPack:
    """阶段6 参数包：只读快照 + 单位换算 + 待批准状态校验。"""

    def __init__(
        self,
        behavior_json: Path | str,
        interface_json: Path | str | None = None,
        project_root: Path | str | None = None,
        verify_upstream_hash: bool = True,
        expected_version: str | None = None,
    ) -> None:
        self.behavior_path = Path(behavior_json).resolve()
        self.project_root = (
            Path(project_root).resolve()
            if project_root is not None
            else self.behavior_path.parents[2]
        )
        if not self.behavior_path.is_file():
            raise ParamError(f"行为表 JSON 不存在：{self.behavior_path}")
        self.behavior_sha256 = _sha256_file(self.behavior_path)
        with self.behavior_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if data.get("artifact") != EXPECTED_ARTIFACT:
            raise ParamError(f"artifact 不符：{data.get('artifact')!r}")
        self.expected_version = expected_version or EXPECTED_ARTIFACT_VERSION
        if data.get("artifact_version") != self.expected_version:
            raise ParamError(
                f"artifact_version 不符：期望 {self.expected_version!r}，"
                f"实际 {data.get('artifact_version')!r}"
            )
        if not str(data.get("status", "")).startswith("G0_PACKET_PENDING_APPROVAL"):
            raise ParamError(
                "行为表状态不是 G0_PACKET_PENDING_APPROVAL 待批准口径，"
                f"实际为 {data.get('status')!r}；本实现只接受待批准草案值"
            )

        self.data = data
        self._params: dict[str, dict] = {}
        for item in data.get("parameters", []):
            pid = item.get("id")
            if not isinstance(pid, str) or pid in self._params:
                raise ParamError(f"参数标识非法或重复：{pid!r}")
            self._params[pid] = item
        missing = [pid for pid in REQUIRED_PARAMETER_IDS if pid not in self._params]
        if missing:
            raise ParamError(f"缺少核心必需参数：{missing}")
        for item in self._params.values():
            if item.get("approval_status") != PENDING_APPROVAL:
                raise ParamError(
                    f"参数 {item.get('id')} 的 approval_status 不是 {PENDING_APPROVAL}，"
                    f"实际为 {item.get('approval_status')!r}"
                )

        invariants = {row.get("id") for row in data.get("hard_invariants", [])}
        missing_inv = [hid for hid in _REQUIRED_HARD_INVARIANTS if hid not in invariants]
        if missing_inv:
            raise ParamError(f"缺少硬不变量：{missing_inv}")

        actions = data.get("actions", {})
        mapping = actions.get("class_action_map", [])
        if len(mapping) != 5:
            raise ParamError(f"五类动作映射必须恰为 5 条，实际 {len(mapping)}")
        self.class_action_map = {int(row["class_id"]): dict(row) for row in mapping}
        self.class_order = list(actions.get("class_order", []))
        if sorted(self.class_action_map) != list(range(len(self.class_order))):
            raise ParamError("class_action_map 的 class_id 与 class_order 不构成 0..N-1 全映射")

        # 上游冻结接口（2A）。
        if interface_json is None:
            interface_json = self.project_root / "docs/stage6/s6b_frozen_interface_v1.json"
        self.interface_path = Path(interface_json).resolve()
        if not self.interface_path.is_file():
            raise ParamError(f"冻结接口文件不存在：{self.interface_path}")
        self.interface_sha256 = _sha256_file(self.interface_path)
        with self.interface_path.open("r", encoding="utf-8") as handle:
            interface = json.load(handle)
        self.interface = interface
        if list(interface.get("class_order", [])) != self.class_order:
            raise ParamError("接口文件 class_order 与行为表 actions.class_order 不一致")
        self.class_ids = tuple(int(v) for v in interface.get("class_ids", []))
        if len(self.class_order) != 5 or list(self.class_ids) != [0, 1, 2, 3, 4]:
            raise ParamError("五类顺序/class_id 必须恰为 0..4")
        if list(self.class_ids) != sorted(self.class_action_map):
            raise ParamError("接口文件 class_ids 与行为表动作映射不一致")
        self.boxes_max = int(interface["boxes_max"])
        if verify_upstream_hash:
            upstream = interface.get("upstream", {})
            up_path = Path(upstream.get("path", ""))
            if not up_path.is_absolute():
                up_path = self.project_root / up_path
            if not up_path.is_file():
                raise ParamError(f"2A 冻结原件不存在：{up_path}")
            actual = _sha256_file(up_path)
            if actual != upstream.get("sha256"):
                raise ParamError(
                    "2A 冻结原件 SHA-256 与实际不一致："
                    f"期望 {upstream.get('sha256')}，实际 {actual}"
                )

        self.states = tuple(data.get("states", []))
        self.event_classes = dict(data.get("event_classes", {}))
        self.transitions = {row["id"]: dict(row) for row in data.get("transitions", [])}
        self.class_action_map = self.class_action_map

    # ------------------------------------------------------------------
    # 原始读取与单位换算
    # ------------------------------------------------------------------
    def has(self, pid: str) -> bool:
        return pid in self._params

    def raw(self, pid: str):
        if pid not in self._params:
            raise ParamError(f"未登记参数：{pid}")
        value = self._params[pid].get("draft_value")
        if value is None:
            raise ParamError(f"参数 {pid} 无草案值（待定），不得参与判定")
        return value

    def try_raw(self, pid: str):
        item = self._params.get(pid)
        if item is None:
            raise ParamError(f"未登记参数：{pid}")
        return item.get("draft_value")

    def _unit(self, pid: str) -> str | None:
        return self._params[pid].get("unit")

    def frames(self, pid: str) -> int:
        value = self.raw(pid)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ParamError(f"参数 {pid} 期望帧数整数，实际 {value!r}")
        if value < 0:
            raise ParamError(f"参数 {pid} 帧数不得为负：{value}")
        return int(value) * _FRAME_TO_COUNT

    def ms(self, pid: str) -> float:
        value = self.raw(pid)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ParamError(f"参数 {pid} 期望毫秒数，实际 {value!r}")
        return float(value)

    def ns(self, pid: str) -> int:
        """毫秒参数换算为纳秒整数（草案值均为整数毫秒，换算无损）。"""
        ms_value = self.ms(pid)
        ns_value = ms_value * _MS_TO_NS
        rounded = int(round(ns_value))
        if abs(ns_value - rounded) > 0:
            raise ParamError(f"参数 {pid} 换算纳秒非整数：{ns_value!r}")
        return rounded

    def value_float(self, pid: str) -> float:
        value = self.raw(pid)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ParamError(f"参数 {pid} 期望浮点值，实际 {value!r}")
        return float(value)

    # ------------------------------------------------------------------
    # 快照（证据用）
    # ------------------------------------------------------------------
    def snapshot(self) -> dict:
        return {
            "behavior_json": str(self.behavior_path),
            "behavior_sha256": self.behavior_sha256,
            "behavior_artifact_version": self.data.get("artifact_version"),
            "behavior_status": self.data.get("status"),
            "interface_json": str(self.interface_path),
            "interface_sha256": self.interface_sha256,
            "interface_version": self.interface.get("artifact_version"),
            "boxes_max": self.boxes_max,
            "class_ids": list(self.class_ids),
            "class_order": list(self.class_order),
            "parameters": [
                {
                    "id": pid,
                    "draft_value": item.get("draft_value"),
                    "unit": item.get("unit"),
                    "comparison": item.get("comparison"),
                    "approval_status": item.get("approval_status"),
                    "approval_owner": item.get("approval_owner"),
                    "draft_source": item.get("draft_source"),
                }
                for pid, item in sorted(self._params.items())
            ],
            "all_parameters_pending_approval": all(
                item.get("approval_status") == PENDING_APPROVAL
                for item in self._params.values()
            ),
            "thresholds_are_draft_not_approved": True,
            "note": (
                "全部数值为草案值，状态 PENDING_APPROVAL；本快照只证明实现读取了这些值，"
                "不构成阈值冻结或验收结论。"
            ),
        }

    def threshold_bundle(self) -> dict:
        """核心判定使用的不可变阈值束（纳秒/帧/float64 原值）。"""
        return {
            "a01_ns": self.ns("T6-A01"),
            "a02_ns": self.ns("T6-A02"),
            "c01_frames": self.frames("T6-C01"),
            "s01_ns": self.ns("T6-S01"),
            "s02_frames": self.frames("T6-S02"),
            "s04_ns": self.ns("T6-S04"),
            "l01_frames": self.frames("T6-L01"),
            "l02_ns": self.ns("T6-L02"),
            "k01_ns": self.ns("T6-K01"),
            "j01_frames": self.frames("T6-J01"),
            "u00_w": self.frames("T6-U00_W"),
            "u00_n": self.frames("T6-U00_N"),
            "u01_frames": self.frames("T6-U01"),
            "p01": self.value_float("T6-P01"),
            "p02": self.value_float("T6-P02"),
            "p03": self.value_float("T6-P03"),
            "p04": self.value_float("T6-P04"),
            "p05": self.value_float("T6-P05"),
            "stale_limit_ns": self.ns("T6-STALE_LIMIT"),
            "boxes_max": self.boxes_max,
            "class_ids": tuple(self.class_ids),
        }


def default_paths(project_root: Path | str | None = None) -> tuple[Path, Path]:
    root = Path(project_root).resolve() if project_root is not None else Path(__file__).resolve().parents[2]
    return (
        root / "docs/stage6/s6a_stage6_g0_behavior_v1.json",
        root / "docs/stage6/s6b_frozen_interface_v1.json",
    )
