
_STACK_SIZE = 0x6000;
_HEAP_SIZE = 0x0800;

MEMORY
{
  ocm : ORIGIN = 0x00000000, LENGTH = 0x00040000
}

ENTRY(_vector_table)

SECTIONS
{
.text 0x00000000 : {
   KEEP (*(.vectors))
   *(.boot)
   *(.text)
   *(.text.*)
   *(.rodata)
   *(.rodata.*)
   *(.sdata2)
   *(.sdata2.*)
   *(.data)
   *(.data.*)
   *(.got)
   *(.got.plt)
   *(.ARM.extab)
   *(.ARM.exidx*)
} > ocm

.bss (NOLOAD) : {
   __bss_start = .;
   *(.bss)
   *(.bss.*)
   *(.sbss)
   *(.sbss.*)
   *(COMMON)
   __bss_end = .;
   _bss_end = .;
} > ocm

.heap (NOLOAD) : {
   . = ALIGN(16);
   _heap = .;
   _heap_start = .;
   . += _HEAP_SIZE;
   _heap_end = .;
} > ocm

.stack (NOLOAD) : {
   . = ALIGN(16);
   _stack_end = .;
   . += _STACK_SIZE;
   . = ALIGN(16);
   _stack = .;
   __stack = _stack;
} > ocm

/* 常用别名（startup / newlib 可能引用） */
__data_start = ADDR(.text);
__data_end = ADDR(.text) + SIZEOF(.text);
__rodata_start = ADDR(.text);
__rodata_end = ADDR(.text) + SIZEOF(.text);
__sdata2_start = ADDR(.text);
__sdata2_end = ADDR(.text) + SIZEOF(.text);
__sbss2_start = __bss_start;
__sbss2_end = __bss_start;
_sdata_start = ADDR(.text);
_sdata_end = ADDR(.text) + SIZEOF(.text);
__tdata_start = __bss_start;
__tdata_end = __bss_start;
__tbss_start = __bss_start;
__tbss_end = __bss_end;
__sbss_start = __bss_start;
__sbss_end = __bss_start;
_sbss = __bss_start;
__fiq_stack = _stack;
__undef_stack = _stack;
__irq_stack = _stack;
__supervisor_stack = _stack;
__abort_stack = _stack;
__CTOR_LIST__ = __bss_start;
__CTOR_END__ = __bss_start;
__DTOR_LIST__ = __bss_start;
__DTOR_END__ = __bss_start;
end = .;
ASSERT((end <= 0x00040000), "probe OCM overflow")
}
