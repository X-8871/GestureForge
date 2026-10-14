# T19 R02 的 HP0 路由拓扑只读核查

本Run在Vivado 2026.1已完成实现的 `impl_1` 设计上，对T19 R02 visibility0 routed DCP做只读查询。未打开其他检查点，未运行综合、实现、优化或位流生成，也未操作板卡、JTAG或Flash。

## 输入与执行

- DCP：`tmp/2B/S2B-T19/visibility0_hp_rebuild_20261014_r02/project/s2b_inference_candidate.runs/impl_1/s2b_inference_wrapper_routed.dcp`
- DCP SHA-256：`64f42f2eb1ee582a8b5d206e9cdc862acda01bfa178f8dc3d09c795b773022fc`，大小 `12065570` 字节。
- 为使本Run可独立复查，原DCP逐字节复制到 `input_routed_r02.dcp`；副本大小与SHA-256相同。清单以 `role=diagnostic` 及 `keep_reason` 记录保留用途。
- DCP生成源码提交：`f38bf9e557e05a15636ee2d571b4523668d04260`。adapter、inference top与platform Tcl当前文件哈希均与T19 R02清单一致；具体值见 `query_summary.json` 和 `delivery_manifest.json`。
- 查询使用 `query_hp0_r02.tcl`；Vivado由ROSS会话 `vivado-20261014-133318-6fec06f6` 执行，原始Tcl-list输出保存于 `query_output.tcldict`。
- BREADY/RREADY驱动补充查询使用 `query_ready_drivers_r02.tcl`，结果保存于 `query_ready_drivers_output.tcldict`。补充查询记录相同的 `impl_1`、实现目录和器件。

## 观测结果

实现中有一个PS7单元，HP0共317个引脚；按本查询分类，所需引脚未连接数为0，另有26个复位/计数输出未连接。八个 `ARCACHE/AWCACHE` 位均由 `s2b_inference_i/infer/GND/G` 拉低。十个握手信号的叶级端点均包含PS7及adapter层级单元。BREADY与RREADY各有19个net segments和9个leaf pins，唯一输出驱动均为 `s2b_inference_i/infer/VCC/P (VCC)`。原端点列表中的guard层级CARRY4是共享高电平网络上的输入负载，不是BREADY/RREADY的输出逻辑。RTL源码也将两路ready直接赋值为常数1；这意味着本实现不对B/R响应施加背压。T11回执仍只支持当前adapter源码快照的行为审查范围，不替代当前DCP驱动核查。

## 结论边界

这份证据只说明指定visibility0 DCP的静态连线和常量值，不代表G0接口冻结、visibility1授权、AXI/DDR真实事务、缓存一致性、器件身份、冷启动或模型上板通过。照片丝印与工程目标的XA/XC差异仍需在部署前处理。旧缓存探针与旧pre-enable回执绑定的不是当前完整产物，故未重绑定，也未作为当前版本通过证据。

历史pre-enable回执SHA-256为 `1d7f6a2807b718bba0eeafe079a4af3ee43cf612c503c8e50a3324ded6a0d9d0`，批准的旧proof SHA-256为 `eb8f86fd97c3c6ed8c8f925f870d8363cbac4cd9f6cd65482dfe841d54962bca`，基线提交为 `aa6fd7248ef9271bbcc79fefe097c78fec8fb36a`，范围仅允许该旧基线进入visibility=1 build verification。由于当前源码映射已变化，该receipt不能授权当前HEAD或当前R02构建；receipt与其HP/cache子证明以精确哈希作为历史输入列入清单。

G0、当前R02 PS cache探针、visibility1最终构建与时序、冻结tiny416模型的109样本黄金比对、1000次连续任务、恢复/负向检查以及G3/G4/G5仍未完成。
