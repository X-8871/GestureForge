/* 阶段2B隔离CPU BRESP诊断；此ELF不替代正式推理程序。 */
.syntax unified
.arch armv7-a
.arm

.equ CSR_BASE,              0x43c00000
.equ CSR_COMMAND,           0x008
.equ CSR_STATUS,            0x00c
.equ CSR_FRAME,             0x014
.equ CSR_INPUT_ADDR,        0x018
.equ CSR_INPUT_BYTES,       0x01c
.equ CSR_WEIGHT_ADDR,       0x020
.equ CSR_WEIGHT_BYTES,      0x024
.equ CSR_CORE_TIMEOUT,      0x028
.equ CSR_DRAIN_TIMEOUT,     0x02c
.equ CSR_EPOCH_LO,          0x050
.equ CSR_EPOCH_HI,          0x054
.equ CSR_RESULT_FRAME,      0x058
.equ CSR_LAST_REJECT,       0x064
.equ CSR_AXI_PROGRESS,      0x068
.equ APP_TTB_BASE,          0x00110000
.equ STATE_IDLE,            0
.equ STATE_ARMING,          1
.equ STATE_RUN,             2
.equ OWNER_PL,              (1 << 8)
.equ SAFE_REUSE,            (1 << 10)
.equ TERMINAL,              (1 << 11)
.equ AXI_PENDING,           (1 << 12)
.equ FIRST_PENDING,         (1 << 13)
.equ MAILBOX,               0x0002e000
.equ STACK_TOP,             0x0002d000
.equ DDIAG_MAGIC_STARTED,   0x42524453
.equ DDIAG_MAGIC_SLVERR,    0x4252444f
.equ DDIAG_MAGIC_UNKNOWN,   0x4252554e
.equ DDIAG_MAGIC_FAIL,      0x42524641

.section .vectors,"ax",%progbits
.balign 32
.global __diag_vectors
__diag_vectors:
    b _diag_start
    b _diag_unexpected
    b _diag_unexpected
    b _diag_unexpected
    b _diag_data_abort
    b _diag_unexpected
    b _diag_unexpected
    b _diag_unexpected

.section .text.boot,"ax",%progbits
.balign 4
.global _diag_start
.global diag_busy_start_store
.global diag_busy_start_store_end
_diag_start:
    cpsid   if
    cps     #0x13
    ldr     sp, =STACK_TOP
    cps     #0x17
    ldr     sp, =STACK_TOP
    cps     #0x13

    ldr     r0, =MAILBOX
    mov     r1, #0
    mov     r2, #64
1:
    str     r1, [r0], #4
    subs    r2, r2, #1
    bne     1b

    mrc     p15, 0, r0, c1, c0, 0
    bic     r0, r0, #(1 << 13)
    mcr     p15, 0, r0, c1, c0, 0
    ldr     r0, =__diag_vectors
    mcr     p15, 0, r0, c12, c0, 0
    dsb     sy
    isb

    /* 绑定A9，避免把其他核的异常寄存器语义混作证据。 */
    mrc     p15, 0, r0, c0, c0, 0
    ldr     r1, =0xff0ffff0
    and     r2, r0, r1
    ldr     r1, =0x410fc090
    cmp     r2, r1
    bne     _diag_fail_midr
    ldr     r1, =MAILBOX
    mov     r6, r1
    str     r0, [r1, #4]

    mrc     p15, 0, r0, c1, c0, 0
    str     r0, [r6, #8]
    tst     r0, #1
    beq     _diag_fail_mmu_off

    /* 本流程依赖短描述符、TTBR0覆盖完整地址空间及身份映射CSR。 */
    mrc     p15, 0, r0, c2, c0, 2
    str     r0, [r6, #12]
    cmp     r0, #0
    bne     _diag_fail_ttbcr
    mrc     p15, 0, r4, c2, c0, 0
    str     r4, [r6, #16]
    ldr     r0, =0xffffc000
    and     r4, r4, r0
    ldr     r0, =APP_TTB_BASE
    cmp     r4, r0
    bne     _diag_fail_ttb_base
    ldr     r5, =__diag_ttb_start
    /* 该16KiB OCM表是隔离保留区，先清理并失效其旧缓存行。 */
    mov     r2, r5
    ldr     r3, =(__diag_ttb_start + 0x4000)
10:
    mcr     p15, 0, r2, c7, c14, 1
    add     r2, r2, #32
    cmp     r2, r3
    blo     10b
    dsb     sy
    mov     r2, #4096
8:
    ldr     r3, [r4], #4
    str     r3, [r5], #4
    subs    r2, r2, #1
    bne     8b

    /* 只清理隔离OCM中的新表，不写回原DDR表或arena。 */
    ldr     r2, =__diag_ttb_start
    ldr     r3, =(__diag_ttb_start + 0x4000)
9:
    mcr     p15, 0, r2, c7, c10, 1
    add     r2, r2, #32
    cmp     r2, r3
    blo     9b
    dsb     sy

    /* 仅在隔离副本中把CSR 1MiB项从Device改为Strongly-ordered。 */
    ldr     r4, =(__diag_ttb_start + 0x10f0)
    str     r4, [r6, #20]
    ldr     r0, =0x43c00000
    ldr     r5, [r4]
    str     r5, [r6, #24]
    and     r2, r5, #3
    cmp     r2, #2
    bne     _diag_fail_l1_type
    tst     r5, #(1 << 18)
    bne     _diag_fail_supersection
    ldr     r2, =0xfff00000
    and     r2, r5, r2
    cmp     r2, r0
    bne     _diag_fail_l1_address
    /* 正式CSR项须为DEVICE_MEMORY：TEX=000、C=0、B=1。 */
    tst     r5, #0x7000
    bne     _diag_fail_old_attr
    tst     r5, #0x8
    bne     _diag_fail_old_attr
    tst     r5, #0x4
    beq     _diag_fail_old_attr
    ldr     r2, =0xffff8ff3
    and     r5, r5, r2
    str     r5, [r4]
    str     r5, [r6, #28]
    mov     r2, r4
    mcr     p15, 0, r2, c7, c10, 1
    dsb     sy

    /* 复制原TTBR0的遍历属性，只把基址切到独立OCM表。 */
    mrc     p15, 0, r4, c2, c0, 0
    ldr     r2, =0x00003fff
    and     r4, r4, r2
    ldr     r2, =__diag_ttb_start
    orr     r4, r4, r2
    str     r2, [r6, #152]
    dsb     sy
    mcr     p15, 0, r4, c2, c0, 0
    dsb     sy
    mov     r0, #0
    mcr     p15, 0, r0, c8, c7, 0
    dsb     sy
    isb
    /* 诊断代码位于未用OCM；清I-cache并同步，不触碰D-cache arena行。 */
    mov     r2, #0
    mcr     p15, 0, r2, c7, c5, 0
    dsb     sy
    isb

    ldr     r4, =CSR_BASE
    ldr     r0, [r4, #CSR_STATUS]
    str     r0, [r6, #32]
    and     r2, r0, #7
    cmp     r2, #STATE_IDLE
    bne     _diag_fail_not_idle
    tst     r0, #SAFE_REUSE
    beq     _diag_fail_not_safe
    tst     r0, #(OWNER_PL | TERMINAL | AXI_PENDING | FIRST_PENDING)
    bne     _diag_fail_pending
    ldr     r2, [r4, #CSR_AXI_PROGRESS]
    str     r2, [r6, #36]
    cmp     r2, #0
    bne     _diag_fail_ledger
    ldr     r2, [r4, #CSR_LAST_REJECT]
    str     r2, [r6, #40]

    /* 安全终态外的epoch/frame以稳定读作为本诊断起点记录。 */
    bl      _diag_read_epoch
    str     r0, [r6, #44]
    str     r2, [r6, #48]
    ldr     r3, [r4, #CSR_RESULT_FRAME]
    str     r3, [r6, #52]

    /* 使用R07已验证的sample000逻辑地址、长度和timeout参数。 */
    mov     r0, #0
    str     r0, [r4, #CSR_FRAME]
    str     r0, [r4, #CSR_INPUT_ADDR]
    ldr     r0, =519168
    str     r0, [r4, #CSR_INPUT_BYTES]
    ldr     r0, =0x00100000
    str     r0, [r4, #CSR_WEIGHT_ADDR]
    ldr     r0, =5903100
    str     r0, [r4, #CSR_WEIGHT_BYTES]
    mvn     r0, #0
    str     r0, [r4, #CSR_CORE_TIMEOUT]
    str     r0, [r4, #CSR_DRAIN_TIMEOUT]
    dsb     sy
    mov     r0, #1
    str     r0, [r4, #CSR_COMMAND]
    dsb     sy

    /* 观察本次合法任务进入RUN后立即执行唯一一次busy拒绝写。 */
    ldr     r5, =0x10000000
    mov     r8, #0
2:
    ldr     r0, [r4, #CSR_STATUS]
    and     r2, r0, #7
    cmp     r2, #STATE_ARMING
    bne     7f
    cmp     r8, #0
    bne     7f
    str     r0, [r6, #128]
    bl      _diag_read_epoch
    str     r0, [r6, #132]
    str     r2, [r6, #136]
    ldr     r3, [r4, #CSR_RESULT_FRAME]
    str     r3, [r6, #140]
    ldr     r3, [r4, #CSR_LAST_REJECT]
    str     r3, [r6, #144]
    mov     r8, #1
7:
    ldr     r0, [r4, #CSR_STATUS]
    and     r2, r0, #7
    cmp     r2, #STATE_RUN
    beq     3f
    subs    r5, r5, #1
    bne     2b
    mov     r0, #1
    b       _diag_fail_no_run
3:
    str     r0, [r6, #56]
    tst     r0, #OWNER_PL
    beq     _diag_fail_no_owner
    tst     r0, #(SAFE_REUSE | TERMINAL | AXI_PENDING | FIRST_PENDING)
    bne     _diag_fail_run_status
    ldr     r2, [r4, #CSR_LAST_REJECT]
    str     r2, [r6, #60]
    cmp     r2, #0
    bne     _diag_fail_reject_before
    bl      _diag_read_epoch
    str     r0, [r6, #64]
    str     r2, [r6, #68]
    ldr     r0, [r6, #44]
    adds    r0, r0, #1
    ldr     r7, [r6, #48]
    adc     r7, r7, #0
    ldr     r2, [r6, #64]
    cmp     r0, r2
    bne     _diag_fail_run_epoch
    ldr     r2, [r6, #68]
    cmp     r7, r2
    bne     _diag_fail_run_epoch
    ldr     r3, [r4, #CSR_RESULT_FRAME]
    str     r3, [r6, #72]
    cmp     r3, #0
    bne     _diag_fail_run_frame
    ldr     r0, =DDIAG_MAGIC_STARTED
    str     r0, [r6]
    dsb     sy
    mov     r1, #1
    ldr     r0, =CSR_BASE
    add     r0, r0, #CSR_COMMAND
diag_busy_start_store:
    str     r1, [r0]
diag_busy_start_store_end:
    dsb     sy
    mov     r0, #2
    b       _diag_fail_no_abort

/* 返回R0=epoch low、R2=epoch high，R3保留为读状态临时值。 */
.type _diag_read_epoch,%function
_diag_read_epoch:
    ldr     r1, =CSR_BASE
4:
    ldr     r2, [r1, #CSR_EPOCH_HI]
    ldr     r0, [r1, #CSR_EPOCH_LO]
    ldr     r3, [r1, #CSR_EPOCH_HI]
    cmp     r2, r3
    bne     4b
    bx      lr

.type _diag_data_abort,%function
_diag_data_abort:
    /* 同步External Abort才有可归因的LR_abt/DFAR；无条件只封存并停驻。 */
    ldr     r8, =MAILBOX
    mrs     r9, spsr
    str     r9, [r8, #80]
    mov     r9, lr
    str     r9, [r8, #84]
    sub     r10, r9, #8
    str     r10, [r8, #88]
    mrc     p15, 0, r12, c5, c0, 0
    str     r12, [r8, #76]
    mrc     p15, 0, r12, c6, c0, 0
    str     r12, [r8, #96]
    ldr     r0, =diag_busy_start_store
    cmp     r10, r0
    bne     _diag_abort_unknown
    ldr     r11, [r10]
    str     r11, [r8, #92]
    ldr     r0, =CSR_BASE
    add     r0, r0, #CSR_COMMAND
    cmp     r12, r0
    bne     _diag_abort_unknown
    ldr     r0, [r8, #92]
    ldr     r2, =0xe5801000
    cmp     r0, r2
    bne     _diag_abort_unknown
    ldr     r4, =CSR_BASE
    ldr     r12, [r4, #CSR_STATUS]
    str     r12, [r8, #100]
    bl      _diag_read_epoch_abort
    str     r0, [r8, #104]
    str     r2, [r8, #108]
    ldr     r12, [r4, #CSR_RESULT_FRAME]
    str     r12, [r8, #112]
    ldr     r12, [r4, #CSR_LAST_REJECT]
    str     r12, [r8, #116]
    ldr     r12, [r4, #CSR_AXI_PROGRESS]
    str     r12, [r8, #120]

    /* 校验同步外部写、SLVERR、目标DFAR与唯一STR的PC/机器码。 */
    /* r12现为AXI_PROGRESS；重新读取保存在mailbox的DFSR。 */
    ldr     r12, [r8, #76]
    and     r0, r12, #0xf
    cmp     r0, #0x008
    bne     _diag_abort_unknown
    tst     r12, #(1 << 10)
    bne     _diag_abort_unknown
    tst     r12, #(1 << 11)
    beq     _diag_abort_unknown
    tst     r12, #(1 << 12)
    beq     _diag_abort_unknown
    ldr     r0, [r8, #56]
    and     r0, r0, #7
    cmp     r0, #STATE_RUN
    bne     _diag_abort_unknown
    ldr     r0, [r8, #56]
    tst     r0, #OWNER_PL
    beq     _diag_abort_unknown
    ldr     r0, [r8, #60]
    cmp     r0, #0
    bne     _diag_abort_unknown
    ldr     r0, [r8, #116]
    cmp     r0, #1
    bne     _diag_abort_unknown
    ldr     r0, [r8, #64]
    ldr     r2, [r8, #104]
    cmp     r0, r2
    bne     _diag_abort_unknown
    ldr     r0, [r8, #68]
    ldr     r2, [r8, #108]
    cmp     r0, r2
    bne     _diag_abort_unknown
    ldr     r0, [r8, #72]
    ldr     r2, [r8, #112]
    cmp     r0, r2
    bne     _diag_abort_unknown
    ldr     r0, =DDIAG_MAGIC_SLVERR
    str     r0, [r8]
    b       _diag_park

_diag_abort_unknown:
    ldr     r0, =DDIAG_MAGIC_UNKNOWN
    str     r0, [r8]
    b       _diag_park

/* Abort模式下另取稳定epoch；不调用会改写用户态栈的通用ABI函数。 */
.type _diag_read_epoch_abort,%function
_diag_read_epoch_abort:
    ldr     r1, =CSR_BASE
5:
    ldr     r2, [r1, #CSR_EPOCH_HI]
    ldr     r0, [r1, #CSR_EPOCH_LO]
    ldr     r3, [r1, #CSR_EPOCH_HI]
    cmp     r2, r3
    bne     5b
    bx      lr

_diag_unexpected:
    ldr     r1, =MAILBOX
    mov     r0, #3
    str     r0, [r1, #124]
    ldr     r0, =DDIAG_MAGIC_FAIL
    str     r0, [r1]
    dsb     sy
    b       _diag_park

_diag_fail_midr:             mov r0, #1;  b _diag_fail
_diag_fail_mmu_off:          mov r0, #2;  b _diag_fail
_diag_fail_ttbcr:             mov r0, #3;  b _diag_fail
_diag_fail_l1_type:           mov r0, #4;  b _diag_fail
_diag_fail_supersection:      mov r0, #5;  b _diag_fail
_diag_fail_l1_address:        mov r0, #6;  b _diag_fail
_diag_fail_old_attr:          mov r0, #7;  b _diag_fail
_diag_fail_not_idle:          mov r0, #8;  b _diag_fail
_diag_fail_not_safe:          mov r0, #9;  b _diag_fail
_diag_fail_pending:           mov r0, #10; b _diag_fail
_diag_fail_ledger:            mov r0, #11; b _diag_fail
_diag_fail_no_run:            mov r0, #12; b _diag_fail
_diag_fail_no_owner:          mov r0, #13; b _diag_fail
_diag_fail_run_status:        mov r0, #14; b _diag_fail
_diag_fail_reject_before:     mov r0, #15; b _diag_fail
_diag_fail_no_abort:          mov r0, #16; b _diag_fail
_diag_fail_run_epoch:          mov r0, #17; b _diag_fail
_diag_fail_run_frame:          mov r0, #18; b _diag_fail
_diag_fail_ttb_base:           mov r0, #19; b _diag_fail
_diag_fail:
    ldr     r1, =MAILBOX
    str     r0, [r1, #124]
    ldr     r0, =DDIAG_MAGIC_FAIL
    str     r0, [r1]
    dsb     sy
_diag_park:
    /* mailbox位于cacheable OCM；逐行clean供DAP只读取证。 */
    ldr     r0, =MAILBOX
    mov     r1, #8
11:
    mcr     p15, 0, r0, c7, c10, 1
    add     r0, r0, #32
    subs    r1, r1, #1
    bne     11b
    dsb     sy
    bkpt    #0
6:
    wfe
    b       6b

.section .diag_ttb,"aw",%nobits
.balign 0x4000
.global __diag_ttb_start
__diag_ttb_start:
    .space 0x4000

.section .note.GNU-stack,"",%progbits
