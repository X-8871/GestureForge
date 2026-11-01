# 2026-11-01 板级窗口证据索引

- 生成时间：2026-11-01T04:51:29+08:00
- 覆盖范围：`D:\codex-worktrees\w4\report\evidence\S6-T01` 下 mtime ≥ 2026-11-01 00:30 的窗口（今晚主线，共 20 个）
- 说明：`conclusion` 来自 `results.json`（脚本判定），`关键行` 来自 `S10_uart.log`/`window_close.txt`

| RunId | 时段 | 结论 | 关键行 | 文件数 |
|---|---|---|---|---|
| `disp_realpath_20261101_r01` | 03:33:19–03:34:21 | DISP_REALPATH_PARTIAL | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>vsize=CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800<br>sr_after_1s=CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF <br>src=S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0 | 40 |
| `disp_realpath_20261101_r02` | 03:35:59–03:36:09 | - |  | 7 |
| `disp_realpath_20261101_r03` | 03:36:27–03:37:31 | DISP_S5RS_PATH_OK | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>vsize=CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800<br>sr_after_1s=CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF <br>src=S5DISP frame=60 lat=65535 age=65535 st=B sr=11000 src=real nbox=1 | 43 |
| `mvp_ack_20261101_r01` | 03:47:33–03:52:45 | MVP_CHAIN_OK | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>vsize=CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800<br>sr_after_1s=CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF <br>raw_nz=MVP TIME t0_pre=177927 t1_pl=225384 t2_decode=225391 t3_pub=225391 dt_ | 61 |
| `mvp_chain_20261101_r01` | 01:02:58–01:06:15 | MVP_CHAIN_PARTIAL | raw_nz=MVP TIME t0_pre=55821 t1_pl=103305 t2_decode=103312 t3_pub=103312 dt_p<br>src=S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0<br>gesture_changed=APP: gesture_changed from=none to=拳头<br>weights=MVP WEIGHTS: GFINT8W1 OK @0x10100000 | 64 |
| `mvp_chain_20261101_r02` | 01:09:49–01:13:04 | MVP_CHAIN_PARTIAL | CAM init=CAM: init OK chip=0x5640 640x480 stride=3840 raw=0x12000000 (24bpp BGR<br>raw_nz=MVP TIME t0_pre=55071 t1_pl=102561 t2_decode=102567 t3_pub=102567 dt_p<br>src=S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0<br>gesture_changed=APP: gesture_changed from=none to=拳头 | 68 |
| `mvp_chain_20261101_r03` | 01:16:14–01:19:30 | MVP_CHAIN_PARTIAL | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>raw_nz=MVP TIME t0_pre=55152 t1_pl=102635 t2_decode=102642 t3_pub=102642 dt_p<br>src=S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0<br>gesture_changed=APP: gesture_changed from=none to=拳头 | 68 |
| `mvp_chain_20261101_r04` | 01:22:09–01:25:29 | MVP_CHAIN_PARTIAL | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>raw_nz=MVP TIME t0_pre=58585 t1_pl=106087 t2_decode=106093 t3_pub=106093 dt_p<br>src=S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0<br>gesture_changed=APP: gesture_changed from=none to=拳头 | 68 |
| `mvp_chain_20261101_r05` | 02:06:24–02:09:39 | MVP_CHAIN_PARTIAL | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>raw_nz=MVP TIME t0_pre=54762 t1_pl=102256 t2_decode=102263 t3_pub=102263 dt_p<br>src=S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0<br>gesture_changed=APP: gesture_changed from=none to=拳头 | 64 |
| `mvp_chain_20261101_r06` | 02:12:18–02:15:33 | MVP_CHAIN_PARTIAL | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>sr_after_1s=CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF <br>raw_nz=MVP TIME t0_pre=55048 t1_pl=102523 t2_decode=102530 t3_pub=102530 dt_p<br>src=S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0 | 64 |
| `mvp_chain_20261101_r07` | 02:43:34–02:44:00 | - |  | 9 |
| `mvp_chain_20261101_r08` | 02:46:10–02:49:36 | MVP_CHAIN_OK | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>vsize=CAM: vsize=727 hsize=3840 stride=3840 frame_bytes=2791680<br>sr_after_1s=CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF <br>raw_nz=MVP TIME t0_pre=59598 t1_pl=107077 t2_decode=107084 t3_pub=107084 dt_p | 64 |
| `mvp_chain_20261101_r09` | 02:51:28–02:55:22 | MVP_CHAIN_OK | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>vsize=CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800<br>sr_after_1s=CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF <br>raw_nz=MVP TIME t0_pre=90797 t1_pl=138278 t2_decode=138285 t3_pub=138285 dt_p | 64 |
| `mvp_chain_20261101_r11` | ?–? | - |  | 33 |
| `mvp_chain_20261101_r11b` | 04:45:57–04:49:21 | MVP_CHAIN_PARTIAL | CAM init=CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BG<br>vsize=CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800<br>sr_after_1s=CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF <br>raw_nz=MVP TIME t0_pre=63995 t1_pl=111483 t2_decode=111489 t3_pub=111489 dt_p | 68 |
| `mvp_vsize727_probe_20261101_r01` | 02:36:41–02:36:51 | - |  | 10 |
| `mvp_vsize727_probe_20261101_r02` | 02:37:35–02:38:38 | VSIZE727_STILL_FSZ_MORE |  | 39 |
| `mvp_vsize727_probe_20261101_r03` | ?–? | - |  | 1 |
| `r53a_hud_ok` | 00:19:40–00:20:43 | HUD_OK_视觉待确认 | CAM init=- `CAM:`：['CAM: init OK chip=0x5640 640x480 stride=3840 raw=0x12000000<br>gesture_changed=- H1 HUD 逻辑：`APP: gesture=<中文>` 或 `APP: gesture_changed` 出现：**PASS** [ | 38 |
| `s6e_e1_recover_20261101_r05` | ?–? | **S6E_E1_ENUM_OK** |  | 8 |

## 关键窗口详述

### `disp_realpath_20261101_r01` — DISP_REALPATH_PARTIAL

- 时段：03:33:19–03:34:21
- frame_source：`jtag_injected_test_pattern`
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- vsize：`CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800`
- sr_after_1s：`CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF phase/hw)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":1,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":29,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":18`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\disp_realpath_20261101_r01`

### `disp_realpath_20261101_r02` — -

- 时段：03:35:59–03:36:09
- frame_source：`jtag_injected_test_pattern`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\disp_realpath_20261101_r02`

### `disp_realpath_20261101_r03` — DISP_S5RS_PATH_OK

- 时段：03:36:27–03:37:31
- frame_source：`jtag_injected_test_pattern`
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- vsize：`CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800`
- sr_after_1s：`CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF phase/hw)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- src：`S5DISP frame=60 lat=65535 age=65535 st=B sr=11000 src=real nbox=1`
- RESULT：`S5DISP RESULT={"pass":1,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":29,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":65535,"age_ms":65535,"vdma_err":0,"fr`
- gesture_changed：`APP: gesture_changed from=none to=数字一`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\disp_realpath_20261101_r03`

### `mvp_ack_20261101_r01` — MVP_CHAIN_OK

- 时段：03:47:33–03:52:45
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- vsize：`CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800`
- sr_after_1s：`CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF phase/hw)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- raw_nz：`MVP TIME t0_pre=177927 t1_pl=225384 t2_decode=225391 t3_pub=225391 dt_pre=87 dt_pl=47456 dt_dec=7 dt_all=47550 raw_nz=1024`
- S5RS：`MVP S5RS frame=0 n_dets=0 magic=0x53355253 status=0x1`
- src：`S5DISP frame=60 lat=65535 age=65535 st=B sr=11000 src=real nbox=1`
- RESULT：`S5DISP RESULT={"pass":1,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":3,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":28415,"age_ms":65535,"vdma_err":0,"fra`
- gesture_changed：`APP: gesture_changed from=none to=数字一`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_ack_20261101_r01`

### `mvp_chain_20261101_r01` — MVP_CHAIN_PARTIAL

- 时段：01:02:58–01:06:15
- raw_nz：`MVP TIME t0_pre=55821 t1_pl=103305 t2_decode=103312 t3_pub=103312 dt_pre=86 dt_pl=47484 dt_dec=6 dt_all=47578 raw_nz=40`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":0,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":5,"fps_dis_idle":0,"idle_period_us":0,"latency_mMVP ERR network rc=-2 frame=39`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r01`

### `mvp_chain_20261101_r02` — MVP_CHAIN_PARTIAL

- 时段：01:09:49–01:13:04
- CAM init：`CAM: init OK chip=0x5640 640x480 stride=3840 raw=0x12000000 (24bpp BGR888)`
- raw_nz：`MVP TIME t0_pre=55071 t1_pl=102561 t2_decode=102567 t3_pub=102567 dt_pre=86 dt_pl=47490 dt_dec=6 dt_all=47583 raw_nz=40`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":0,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":5,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":180`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r02`

### `mvp_chain_20261101_r03` — MVP_CHAIN_PARTIAL

- 时段：01:16:14–01:19:30
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- raw_nz：`MVP TIME t0_pre=55152 t1_pl=102635 t2_decode=102642 t3_pub=102642 dt_pre=86 dt_pl=47483 dt_dec=6 dt_all=47577 raw_nz=40`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":0,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":5,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":180`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r03`

### `mvp_chain_20261101_r04` — MVP_CHAIN_PARTIAL

- 时段：01:22:09–01:25:29
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- raw_nz：`MVP TIME t0_pre=58585 t1_pl=106087 t2_decode=106093 t3_pub=106093 dt_pre=86 dt_pl=47501 dt_dec=6 dt_all=47594 raw_nz=40`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":0,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":6,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":180`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r04`

### `mvp_chain_20261101_r05` — MVP_CHAIN_PARTIAL

- 时段：02:06:24–02:09:39
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- raw_nz：`MVP TIME t0_pre=54762 t1_pl=102256 t2_decode=102263 t3_pub=102263 dt_pre=86 dt_pl=47494 dt_dec=6 dt_all=47587 raw_nz=40`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":0,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":5,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":180`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r05`

### `mvp_chain_20261101_r06` — MVP_CHAIN_PARTIAL

- 时段：02:12:18–02:15:33
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- sr_after_1s：`CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF phase/hw)`
- geom：`CAM: geom dvpho=1280 dvpvo=727 hts=1892 vts=740 (expect 1280/720/1892/740)`
- raw_nz：`MVP TIME t0_pre=55048 t1_pl=102523 t2_decode=102530 t3_pub=102530 dt_pre=86 dt_pl=47474 dt_dec=7 dt_all=47568 raw_nz=40`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":0,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":5,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":180`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r06`

### `mvp_chain_20261101_r07` — -

- 时段：02:43:34–02:44:00
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r07`

### `mvp_chain_20261101_r08` — MVP_CHAIN_OK

- 时段：02:46:10–02:49:36
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- vsize：`CAM: vsize=727 hsize=3840 stride=3840 frame_bytes=2791680`
- sr_after_1s：`CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF phase/hw)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- raw_nz：`MVP TIME t0_pre=59598 t1_pl=107077 t2_decode=107084 t3_pub=107084 dt_pre=86 dt_pl=47478 dt_dec=6 dt_all=47572 raw_nz=101`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":1,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":5,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":180`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r08`

### `mvp_chain_20261101_r09` — MVP_CHAIN_OK

- 时段：02:51:28–02:55:22
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- vsize：`CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800`
- sr_after_1s：`CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF phase/hw)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- raw_nz：`MVP TIME t0_pre=90797 t1_pl=138278 t2_decode=138285 t3_pub=138285 dt_pre=86 dt_pl=47480 dt_dec=7 dt_all=47575 raw_nz=101`
- src：`S5DISP frame=60 lat=0 age=0 st=1 sr=11000 src=real_nobox nbox=0`
- RESULT：`S5DISP RESULT={"pass":1,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":5,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":180`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r09`

### `mvp_chain_20261101_r11` — -

- 时段：?–?
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r11`

### `mvp_chain_20261101_r11b` — MVP_CHAIN_PARTIAL

- 时段：04:45:57–04:49:21
- CAM init：`CAM: init OK chip=0x5640 1280x720 stride=3840 raw=0x12000000 (24bpp BGR888)`
- vsize：`CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800`
- sr_after_1s：`CAM: sr_after_1s=0x14810 (0x14810 => FSZ_MORE recurs per frame -> SOF phase/hw)`
- geom：`CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740 (expect 1280/720/1892/740)`
- raw_nz：`MVP TIME t0_pre=63995 t1_pl=111483 t2_decode=111489 t3_pub=111489 dt_pre=86 dt_pl=47487 dt_dec=5 dt_all=47580 raw_nz=0`
- S5RS：`MVP S5RS frame=0 n_dets=0 magic=0x53355253 status=0x1`
- src：`S5DISP frame=60 lat=0 age=0 st=3 sr=11000 src=real nbox=0`
- RESULT：`S5DISP RESULT={"pass":0,"fps_cap":0,"fps_inf":0,"fps_dis":60,"fps_upd":3,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":23895,"age_ms":65535,"vdma_err":0,"fra`
- gesture_changed：`APP: gesture_changed from=none to=拳头`
- weights：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_chain_20261101_r11b`

### `mvp_vsize727_probe_20261101_r01` — -

- 时段：02:36:41–02:36:51
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_vsize727_probe_20261101_r01`

### `mvp_vsize727_probe_20261101_r02` — VSIZE727_STILL_FSZ_MORE

- 时段：02:37:35–02:38:38
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_vsize727_probe_20261101_r02`

### `mvp_vsize727_probe_20261101_r03` — -

- 时段：?–?
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\mvp_vsize727_probe_20261101_r03`

### `r53a_hud_ok` — HUD_OK_视觉待确认

- 时段：00:19:40–00:20:43
- CAM init：`- `CAM:`：['CAM: init OK chip=0x5640 640x480 stride=3840 raw=0x12000000 (24bpp BGR888)', 'CAM: sr=0x10000 frames=1', 'CAM: sr=0x10000 frames=1', 'CAM: sr=0x10000`
- RESULT：`- H2 显示链：`S5DISP RESULT` 行出现：**PASS** ["S5DISP RESULT={\"pass\":1,\"fps_cap\":0,\"fps_inf\":0,\"fps_dis\":60,\"fps_upd\":29,\"fps_dis_idle\":0,\"idle_period_us\`
- gesture_changed：`- H1 HUD 逻辑：`APP: gesture=<中文>` 或 `APP: gesture_changed` 出现：**PASS** ["APP: gesture=拳头 cls=0 conf=0.00 latency_ms=0", "APP: gesture=拳头 cls=0 conf=0.00 latency_m`
- 目录：`D:\codex-worktrees\w4\report\evidence\S6-T01\r53a_hud_ok`


## 附录：更早窗口（10-31 18:00 – 11-01 00:30，上一班次/前序）

| RunId | 结论 | 说明 |
|---|---|---|
| `ecam_diag_20261031_r33` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r34` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r35` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r36` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r37` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r38` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r39` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r40` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r41` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r42` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r43` | - | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r44` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r45` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r46` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r47` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r48` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r49a` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r50` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `ecam_diag_20261031_r51` | ECAM_DIAG_FAIL | ECAM 诊断窗（CR.RESET/VDMA 复位问题排查期） |
| `s3_camera_repro` | - |  |
| `s6e_e1_recover_20261031_r21` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r22` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r23` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r24` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r25` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r26` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r27` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r28` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r29` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r30` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r31` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r32` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r33` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r34` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r35` | **S6E_E1_ENUM_OK** |  |
| `s6e_e1_recover_20261031_r36` | **S6E_E1_ENUM_OK** |  |

