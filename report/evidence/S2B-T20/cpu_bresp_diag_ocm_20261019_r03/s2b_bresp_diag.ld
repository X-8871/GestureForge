ENTRY(_diag_start)
MEMORY {
  DIAG (rwx) : ORIGIN = 0x0000c000, LENGTH = 0x4000
  TTB (rw) : ORIGIN = 0x00010000, LENGTH = 0x4000
}
SECTIONS {
  .vectors ORIGIN(DIAG) : ALIGN(32) { KEEP(*(.vectors)) } > DIAG
  .text : ALIGN(4) { *(.text.boot) *(.text*) *(.rodata*) } > DIAG
  __diag_end = .;
  .diag_ttb ORIGIN(TTB) (NOLOAD) : ALIGN(0x4000) { KEEP(*(.diag_ttb)) } > TTB
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) *(.ARM.attributes) }
}
ASSERT(__diag_end <= 0x00010000, "诊断代码越过保留低OCM范围")
ASSERT(SIZEOF(.diag_ttb) == 0x4000, "独立L1表必须为16KiB")
