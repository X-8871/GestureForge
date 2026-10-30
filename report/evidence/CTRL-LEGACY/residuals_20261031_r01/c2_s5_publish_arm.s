	.cpu cortex-a9
	.arch armv7-a
	.fpu vfpv3
	.arch_extension mp
	.arch_extension sec
	.eabi_attribute 28, 1
	.eabi_attribute 20, 1
	.eabi_attribute 21, 1
	.eabi_attribute 23, 3
	.eabi_attribute 24, 1
	.eabi_attribute 25, 1
	.eabi_attribute 26, 1
	.eabi_attribute 30, 6
	.eabi_attribute 34, 1
	.eabi_attribute 18, 4
	.file	"c2_s5_publish.c"
	.text
	.align	2
	.syntax unified
	.arm
	.type	c2_put_u16, %function
c2_put_u16:
	@ args = 0, pretend = 0, frame = 8
	@ frame_needed = 1, uses_anonymous_args = 0
	@ link register save eliminated.
	str	fp, [sp, #-4]!
	add	fp, sp, #0
	sub	sp, sp, #12
	str	r0, [fp, #-8]
	mov	r3, r1
	strh	r3, [fp, #-10]	@ movhi
	ldrh	r3, [fp, #-10]	@ movhi
	uxtb	r2, r3
	ldr	r3, [fp, #-8]
	strb	r2, [r3]
	ldrh	r3, [fp, #-10]
	lsr	r3, r3, #8
	uxth	r2, r3
	ldr	r3, [fp, #-8]
	add	r3, r3, #1
	uxtb	r2, r2
	strb	r2, [r3]
	nop
	add	sp, fp, #0
	@ sp needed
	ldr	fp, [sp], #4
	bx	lr
	.size	c2_put_u16, .-c2_put_u16
	.align	2
	.syntax unified
	.arm
	.type	c2_put_u32, %function
c2_put_u32:
	@ args = 0, pretend = 0, frame = 8
	@ frame_needed = 1, uses_anonymous_args = 0
	@ link register save eliminated.
	str	fp, [sp, #-4]!
	add	fp, sp, #0
	sub	sp, sp, #12
	str	r0, [fp, #-8]
	str	r1, [fp, #-12]
	ldr	r3, [fp, #-12]
	uxtb	r2, r3
	ldr	r3, [fp, #-8]
	strb	r2, [r3]
	ldr	r3, [fp, #-12]
	lsr	r2, r3, #8
	ldr	r3, [fp, #-8]
	add	r3, r3, #1
	uxtb	r2, r2
	strb	r2, [r3]
	ldr	r3, [fp, #-12]
	lsr	r2, r3, #16
	ldr	r3, [fp, #-8]
	add	r3, r3, #2
	uxtb	r2, r2
	strb	r2, [r3]
	ldr	r3, [fp, #-12]
	lsr	r2, r3, #24
	ldr	r3, [fp, #-8]
	add	r3, r3, #3
	uxtb	r2, r2
	strb	r2, [r3]
	nop
	add	sp, fp, #0
	@ sp needed
	ldr	fp, [sp], #4
	bx	lr
	.size	c2_put_u32, .-c2_put_u32
	.align	2
	.syntax unified
	.arm
	.type	c2_store_seqlock, %function
c2_store_seqlock:
	@ args = 0, pretend = 0, frame = 8
	@ frame_needed = 1, uses_anonymous_args = 0
	@ link register save eliminated.
	str	fp, [sp, #-4]!
	add	fp, sp, #0
	sub	sp, sp, #12
	str	r0, [fp, #-8]
	str	r1, [fp, #-12]
	ldr	r3, [fp, #-8]
	ldr	r2, [fp, #-12]
	str	r2, [r3]
	nop
	add	sp, fp, #0
	@ sp needed
	ldr	fp, [sp], #4
	bx	lr
	.size	c2_store_seqlock, .-c2_store_seqlock
	.align	2
	.syntax unified
	.arm
	.type	c2_write_detection, %function
c2_write_detection:
	@ args = 0, pretend = 0, frame = 8
	@ frame_needed = 1, uses_anonymous_args = 0
	push	{fp, lr}
	add	fp, sp, #4
	sub	sp, sp, #8
	str	r0, [fp, #-8]
	str	r1, [fp, #-12]
	ldr	r3, [fp, #-12]
	ldrh	r3, [r3]
	mov	r1, r3
	ldr	r0, [fp, #-8]
	bl	c2_put_u16
	ldr	r3, [fp, #-8]
	add	r2, r3, #2
	ldr	r3, [fp, #-12]
	ldrh	r3, [r3, #2]
	mov	r1, r3
	mov	r0, r2
	bl	c2_put_u16
	ldr	r3, [fp, #-8]
	add	r2, r3, #4
	ldr	r3, [fp, #-12]
	ldrh	r3, [r3, #4]
	mov	r1, r3
	mov	r0, r2
	bl	c2_put_u16
	ldr	r3, [fp, #-8]
	add	r2, r3, #6
	ldr	r3, [fp, #-12]
	ldrh	r3, [r3, #6]
	mov	r1, r3
	mov	r0, r2
	bl	c2_put_u16
	ldr	r3, [fp, #-8]
	add	r3, r3, #8
	ldr	r2, [fp, #-12]
	ldrb	r2, [r2, #8]	@ zero_extendqisi2
	strb	r2, [r3]
	ldr	r3, [fp, #-8]
	add	r3, r3, #9
	ldr	r2, [fp, #-12]
	ldrb	r2, [r2, #9]	@ zero_extendqisi2
	strb	r2, [r3]
	ldr	r3, [fp, #-8]
	add	r3, r3, #10
	mov	r1, #0
	mov	r0, r3
	bl	c2_put_u16
	ldr	r3, [fp, #-8]
	add	r3, r3, #12
	mov	r1, #0
	mov	r0, r3
	bl	c2_put_u32
	nop
	sub	sp, fp, #4
	@ sp needed
	pop	{fp, pc}
	.size	c2_write_detection, .-c2_write_detection
	.align	2
	.syntax unified
	.arm
	.type	c2_round_edge, %function
c2_round_edge:
	@ args = 0, pretend = 0, frame = 32
	@ frame_needed = 1, uses_anonymous_args = 0
	@ link register save eliminated.
	str	fp, [sp, #-4]!
	add	fp, sp, #0
	sub	sp, sp, #36
	vstr.64	d0, [fp, #-28]
	str	r0, [fp, #-32]
	str	r1, [fp, #-36]
	ldr	r3, [fp, #-36]
	cmp	r3, #0
	beq	.L6
	vldr.64	d16, [fp, #-28]
	vabs.f64	d16, d16
	vldr.64	d17, .L12
	vcmp.f64	d16, d17
	vmrs	APSR_nzcv, FPSCR
	bhi	.L6
	vldr.64	d16, [fp, #-28]
	vcmpe.f64	d16, #0
	vmrs	APSR_nzcv, FPSCR
	bmi	.L6
	vldr.64	d16, [fp, #-28]
	vmov.f64	d17, #1.0e+0
	vcmpe.f64	d16, d17
	vmrs	APSR_nzcv, FPSCR
	ble	.L11
.L6:
	mov	r3, #0
	b	.L9
.L11:
	ldr	r3, [fp, #-32]
	vmov	s15, r3	@ int
	vcvt.f64.u32	d16, s15
	vldr.64	d17, [fp, #-28]
	vmul.f64	d16, d17, d16
	vstr.64	d16, [fp, #-12]
	vldr.64	d16, [fp, #-12]
	vmov.f64	d17, #5.0e-1
	vadd.f64	d7, d16, d17
	vcvt.u32.f64	s15, d7
	vstr.32	s15, [fp, #-16]	@ int
	ldr	r2, [fp, #-16]
	ldr	r3, [fp, #-32]
	cmp	r2, r3
	bls	.L10
	mov	r3, #0
	b	.L9
.L10:
	ldr	r3, [fp, #-36]
	ldr	r2, [fp, #-16]
	str	r2, [r3]
	mov	r3, #1
.L9:
	mov	r0, r3
	add	sp, fp, #0
	@ sp needed
	ldr	fp, [sp], #4
	bx	lr
.L13:
	.align	3
.L12:
	.word	-1
	.word	2146435071
	.size	c2_round_edge, .-c2_round_edge
	.align	2
	.syntax unified
	.arm
	.type	c2_encode_detection, %function
c2_encode_detection:
	@ args = 0, pretend = 0, frame = 40
	@ frame_needed = 1, uses_anonymous_args = 0
	push	{fp, lr}
	add	fp, sp, #4
	sub	sp, sp, #40
	str	r0, [fp, #-32]
	str	r1, [fp, #-36]
	ldr	r3, [fp, #-32]
	cmp	r3, #0
	beq	.L15
	ldr	r3, [fp, #-36]
	cmp	r3, #0
	beq	.L15
	ldr	r3, [fp, #-32]
	ldr	r3, [r3]
	cmp	r3, #0
	blt	.L15
	ldr	r3, [fp, #-32]
	ldr	r3, [r3]
	cmp	r3, #4
	bgt	.L15
	ldr	r3, [fp, #-32]
	vldr.64	d16, [r3, #8]
	vabs.f64	d16, d16
	vldr.64	d17, .L19
	vcmp.f64	d16, d17
	vmrs	APSR_nzcv, FPSCR
	bhi	.L15
	ldr	r3, [fp, #-32]
	vldr.64	d16, [r3, #8]
	vcmpe.f64	d16, #0
	vmrs	APSR_nzcv, FPSCR
	bmi	.L15
	ldr	r3, [fp, #-32]
	vldr.64	d16, [r3, #8]
	vmov.f64	d17, #1.0e+0
	vcmpe.f64	d16, d17
	vmrs	APSR_nzcv, FPSCR
	bgt	.L15
	ldr	r3, [fp, #-32]
	vldr.64	d16, [r3, #16]
	sub	r3, fp, #16
	mov	r1, r3
	mov	r0, #640
	vmov.f64	d0, d16
	bl	c2_round_edge
	mov	r3, r0
	cmp	r3, #0
	beq	.L15
	ldr	r3, [fp, #-32]
	vldr.64	d16, [r3, #24]
	sub	r3, fp, #20
	mov	r1, r3
	mov	r0, #480
	vmov.f64	d0, d16
	bl	c2_round_edge
	mov	r3, r0
	cmp	r3, #0
	beq	.L15
	ldr	r3, [fp, #-32]
	vldr.64	d16, [r3, #32]
	sub	r3, fp, #24
	mov	r1, r3
	mov	r0, #640
	vmov.f64	d0, d16
	bl	c2_round_edge
	mov	r3, r0
	cmp	r3, #0
	beq	.L15
	ldr	r3, [fp, #-32]
	vldr.64	d16, [r3, #40]
	sub	r3, fp, #28
	mov	r1, r3
	mov	r0, #480
	vmov.f64	d0, d16
	bl	c2_round_edge
	mov	r3, r0
	cmp	r3, #0
	beq	.L15
	ldr	r3, [fp, #-16]
	cmp	r3, #640
	bcs	.L15
	ldr	r3, [fp, #-20]
	cmp	r3, #480
	bcs	.L15
	ldr	r2, [fp, #-24]
	ldr	r3, [fp, #-16]
	cmp	r2, r3
	bls	.L15
	ldr	r2, [fp, #-28]
	ldr	r3, [fp, #-20]
	cmp	r2, r3
	bhi	.L16
.L15:
	mov	r3, #0
	b	.L18
.L16:
	ldr	r3, [fp, #-32]
	vldr.64	d16, [r3, #8]
	vldr.64	d17, .L19+8
	vmul.f64	d16, d16, d17
	vmov.f64	d17, #5.0e-1
	vadd.f64	d16, d16, d17
	vstr.64	d16, [fp, #-12]
	ldr	r3, [fp, #-16]
	uxth	r2, r3
	ldr	r3, [fp, #-36]
	strh	r2, [r3]	@ movhi
	ldr	r3, [fp, #-20]
	uxth	r2, r3
	ldr	r3, [fp, #-36]
	strh	r2, [r3, #2]	@ movhi
	ldr	r3, [fp, #-24]
	uxth	r2, r3
	ldr	r3, [fp, #-16]
	uxth	r3, r3
	sub	r3, r2, r3
	uxth	r2, r3
	ldr	r3, [fp, #-36]
	strh	r2, [r3, #4]	@ movhi
	ldr	r3, [fp, #-28]
	uxth	r2, r3
	ldr	r3, [fp, #-20]
	uxth	r3, r3
	sub	r3, r2, r3
	uxth	r2, r3
	ldr	r3, [fp, #-36]
	strh	r2, [r3, #6]	@ movhi
	ldr	r3, [fp, #-32]
	ldr	r3, [r3]
	uxtb	r2, r3
	ldr	r3, [fp, #-36]
	strb	r2, [r3, #8]
	vldr.64	d7, [fp, #-12]
	vcvt.u32.f64	s15, d7
	vstr.32	s15, [fp, #-40]	@ int
	ldrb	r3, [fp, #-40]
	uxtb	r2, r3
	ldr	r3, [fp, #-36]
	strb	r2, [r3, #9]
	mov	r3, #1
.L18:
	mov	r0, r3
	sub	sp, fp, #4
	@ sp needed
	pop	{fp, pc}
.L20:
	.align	3
.L19:
	.word	-1
	.word	2146435071
	.word	0
	.word	1081073664
	.size	c2_encode_detection, .-c2_encode_detection
	.align	2
	.syntax unified
	.arm
	.type	c2_poison, %function
c2_poison:
	@ args = 0, pretend = 0, frame = 8
	@ frame_needed = 1, uses_anonymous_args = 0
	@ link register save eliminated.
	str	fp, [sp, #-4]!
	add	fp, sp, #0
	sub	sp, sp, #12
	str	r0, [fp, #-8]
	mov	r3, r1
	strb	r3, [fp, #-9]
	ldr	r3, [fp, #-8]
	mov	r2, #1
	str	r2, [r3, #24]
	ldr	r3, [fp, #-8]
	mov	r2, #0
	str	r2, [r3, #20]
	ldrsb	r3, [fp, #-9]
	mov	r0, r3
	add	sp, fp, #0
	@ sp needed
	ldr	fp, [sp], #4
	bx	lr
	.size	c2_poison, .-c2_poison
	.align	2
	.global	C2Publisher_Init
	.syntax unified
	.arm
	.type	C2Publisher_Init, %function
C2Publisher_Init:
	@ args = 8, pretend = 0, frame = 24
	@ frame_needed = 1, uses_anonymous_args = 0
	push	{fp, lr}
	add	fp, sp, #4
	sub	sp, sp, #24
	str	r0, [fp, #-16]
	strd	r2, [fp, #-28]
	ldr	r3, [fp, #-16]
	cmp	r3, #0
	bne	.L24
	mvn	r3, #0
	b	.L25
.L24:
	mov	r2, #28
	mov	r1, #0
	ldr	r0, [fp, #-16]
	bl	memset
	ldr	r3, [fp, #4]
	cmp	r3, #0
	bne	.L26
	mvn	r3, #1
	b	.L25
.L26:
	ldr	r3, [fp, #4]
	cmp	r3, #1
	bne	.L27
	ldr	r3, [fp, #8]
	cmp	r3, #65536
	bcc	.L28
.L27:
	mvn	r3, #0
	b	.L25
.L28:
	ldrd	r0, [fp, #-28]
	mov	r2, #0
	mov	r3, #0
	lsr	r2, r0, #10
	orr	r2, r2, r1, lsl #22
	lsr	r3, r1, #10
	mov	r3, r2
	uxth	r3, r3
	str	r3, [fp, #-8]
	ldr	r2, [fp, #-8]
	ldr	r3, [fp, #8]
	cmp	r2, r3
	bne	.L29
	mov	r3, #0
	str	r3, [fp, #-12]
	b	.L30
.L31:
	ldr	r3, [fp, #-8]
	add	r3, r3, #1
	uxth	r3, r3
	str	r3, [fp, #-8]
	ldr	r3, [fp, #-12]
	add	r3, r3, #1
	str	r3, [fp, #-12]
.L30:
	ldr	r3, [fp, #-12]
	cmp	r3, #7
	bhi	.L29
	ldr	r2, [fp, #-8]
	ldr	r3, [fp, #8]
	cmp	r2, r3
	beq	.L31
.L29:
	ldr	r2, [fp, #-8]
	ldr	r3, [fp, #8]
	cmp	r2, r3
	bne	.L32
	mvn	r3, #2
	b	.L25
.L32:
	ldr	r3, [fp, #-16]
	ldr	r2, [fp, #-8]
	str	r2, [r3]
	ldr	r3, [fp, #-16]
	mov	r2, #0
	str	r2, [r3, #8]
	ldr	r3, [fp, #-16]
	mov	r2, #1
	str	r2, [r3, #16]
	mov	r3, #0
.L25:
	mov	r0, r3
	sub	sp, fp, #4
	@ sp needed
	pop	{fp, pc}
	.size	C2Publisher_Init, .-C2Publisher_Init
	.align	2
	.global	C2_ClassifyBusinessState
	.syntax unified
	.arm
	.type	C2_ClassifyBusinessState, %function
C2_ClassifyBusinessState:
	@ args = 0, pretend = 0, frame = 16
	@ frame_needed = 1, uses_anonymous_args = 0
	@ link register save eliminated.
	str	fp, [sp, #-4]!
	add	fp, sp, #0
	sub	sp, sp, #20
	str	r0, [fp, #-8]
	str	r1, [fp, #-12]
	strd	r2, [fp, #-20]
	ldr	r3, [fp, #-8]
	cmp	r3, #7
	bhi	.L34
	ldr	r3, [fp, #-8]
	and	r3, r3, #1
	cmp	r3, #0
	beq	.L34
	ldr	r3, [fp, #-8]
	and	r3, r3, #2
	cmp	r3, #0
	bne	.L34
	ldr	r3, [fp, #-12]
	cmp	r3, #14
	bls	.L35
.L34:
	mov	r3, #0
	b	.L36
.L35:
	ldr	r3, [fp, #-8]
	and	r3, r3, #4
	cmp	r3, #0
	bne	.L37
	ldrd	r2, [fp, #-20]
	movw	r1, #16557
	movt	r1, 1017
	cmp	r2, r1
	sbcs	r3, r3, #0
	bcc	.L38
.L37:
	mov	r3, #1
	b	.L36
.L38:
	ldr	r3, [fp, #-12]
	cmp	r3, #0
	bne	.L39
	mov	r3, #2
	b	.L36
.L39:
	mov	r3, #3
.L36:
	mov	r0, r3
	add	sp, fp, #0
	@ sp needed
	ldr	fp, [sp], #4
	bx	lr
	.size	C2_ClassifyBusinessState, .-C2_ClassifyBusinessState
	.global	__aeabi_uldivmod
	.align	2
	.global	C2_AgePublishMs
	.syntax unified
	.arm
	.type	C2_AgePublishMs, %function
C2_AgePublishMs:
	@ args = 4, pretend = 0, frame = 72
	@ frame_needed = 1, uses_anonymous_args = 0
	push	{r4, r5, r6, r7, r8, r9, fp, lr}
	add	fp, sp, #28
	sub	sp, sp, #72
	strd	r0, [fp, #-68]
	strd	r2, [fp, #-76]
	ldr	r3, [fp, #4]
	cmp	r3, #0
	bne	.L41
	mov	r3, #0
	b	.L42
.L41:
	ldr	r3, [fp, #4]
	mov	r2, #0
	str	r2, [r3]
	ldrd	r0, [fp, #-68]
	ldrd	r2, [fp, #-76]
	cmp	r0, r2
	sbcs	r3, r1, r3
	bcs	.L43
	mov	r3, #0
	b	.L42
.L43:
	ldrd	r0, [fp, #-68]
	ldrd	r2, [fp, #-76]
	subs	r4, r0, r2
	sbc	r5, r1, r3
	strd	r4, [fp, #-36]
	ldrd	r0, [fp, #-36]
	adr	r3, .L47
	ldrd	r2, [r3]
	bl	__aeabi_uldivmod
	mov	r2, r0
	mov	r3, r1
	strd	r2, [fp, #-44]
	ldrd	r0, [fp, #-36]
	adr	r3, .L47
	ldrd	r2, [r3]
	bl	__aeabi_uldivmod
	strd	r2, [fp, #-52]
	ldrd	r2, [fp, #-44]
	movw	r1, #35128
	movt	r1, 65
	cmp	r2, r1
	sbcs	r3, r3, #0
	bcc	.L44
	ldr	r3, [fp, #4]
	mov	r2, #1
	str	r2, [r3]
	mvn	r3, #0
	b	.L42
.L44:
	ldrd	r0, [fp, #-44]
	mov	r2, r0
	mov	r3, r1
	mov	r4, #0
	mov	r5, #0
	lsl	r5, r3, #5
	orr	r5, r5, r2, lsr #27
	lsl	r4, r2, #5
	mov	r2, r4
	mov	r3, r5
	subs	r6, r2, r0
	sbc	r7, r3, r1
	mov	r2, #0
	mov	r3, #0
	lsl	r3, r7, #2
	orr	r3, r3, r6, lsr #30
	lsl	r2, r6, #2
	mov	r6, r2
	mov	r7, r3
	adds	r3, r6, r0
	str	r3, [fp, #-84]
	adc	r3, r7, r1
	str	r3, [fp, #-80]
	mov	r2, #0
	mov	r3, #0
	ldrd	r0, [fp, #-84]
	mov	ip, r1
	lsl	r3, ip, #3
	mov	ip, r0
	orr	r3, r3, ip, lsr #29
	mov	r1, r0
	lsl	r2, r1, #3
	mov	r6, r2
	mov	r7, r3
	ldrd	r0, [fp, #-52]
	mov	r2, r0
	mov	r3, r1
	mov	r4, #0
	mov	r5, #0
	lsl	r5, r3, #5
	orr	r5, r5, r2, lsr #27
	lsl	r4, r2, #5
	mov	r2, r4
	mov	r3, r5
	subs	r8, r2, r0
	sbc	r9, r3, r1
	mov	r2, #0
	mov	r3, #0
	lsl	r3, r9, #2
	orr	r3, r3, r8, lsr #30
	lsl	r2, r8, #2
	mov	r8, r2
	mov	r9, r3
	adds	r3, r8, r0
	str	r3, [fp, #-92]
	adc	r3, r9, r1
	str	r3, [fp, #-88]
	mov	r2, #0
	mov	r3, #0
	ldrd	r0, [fp, #-92]
	mov	ip, r1
	lsl	r3, ip, #3
	mov	ip, r0
	orr	r3, r3, ip, lsr #29
	mov	r1, r0
	lsl	r2, r1, #3
	mov	r0, r2
	mov	r1, r3
	adr	r3, .L47
	ldrd	r2, [r3]
	bl	__aeabi_uldivmod
	mov	r2, r0
	mov	r3, r1
	adds	r1, r6, r2
	str	r1, [fp, #-100]
	adc	r3, r7, r3
	str	r3, [fp, #-96]
	ldrd	r2, [fp, #-100]
	strd	r2, [fp, #-60]
	ldr	r3, [fp, #4]
	mov	r2, #1
	str	r2, [r3]
	ldrd	r2, [fp, #-60]
	cmp	r3, #1
	bcs	.L45
	ldr	r3, [fp, #-60]
	b	.L42
.L45:
	mvn	r3, #0
.L42:
	mov	r0, r3
	sub	sp, fp, #28
	@ sp needed
	pop	{r4, r5, r6, r7, r8, r9, fp, pc}
.L48:
	.align	3
.L47:
	.word	333333343
	.word	0
	.size	C2_AgePublishMs, .-C2_AgePublishMs
	.align	2
	.global	C2Publisher_Publish
	.syntax unified
	.arm
	.type	C2Publisher_Publish, %function
C2Publisher_Publish:
	@ args = 8, pretend = 0, frame = 224
	@ frame_needed = 1, uses_anonymous_args = 0
	push	{r4, r5, fp, lr}
	add	fp, sp, #12
	sub	sp, sp, #224
	str	r0, [fp, #-224]
	str	r1, [fp, #-228]
	str	r2, [fp, #-232]
	str	r3, [fp, #-236]
	mov	r3, #0
	str	r3, [fp, #-16]
	mov	r3, #0
	strb	r3, [fp, #-25]
	ldr	r3, [fp, #-224]
	cmp	r3, #0
	beq	.L50
	ldr	r3, [fp, #-228]
	cmp	r3, #0
	beq	.L50
	ldr	r3, [fp, #-236]
	cmp	r3, #0
	beq	.L50
	ldr	r3, [fp, #4]
	cmp	r3, #0
	beq	.L50
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #4]
	cmp	r3, #0
	beq	.L50
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #8]
	cmp	r3, #0
	beq	.L50
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	cmp	r3, #0
	beq	.L50
	ldr	r3, [fp, #-232]
	cmp	r3, #288
	bcc	.L50
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #16]
	cmp	r3, #0
	bne	.L51
.L50:
	mvn	r3, #0
	b	.L84
.L51:
	ldr	r3, [fp, #-228]
	and	r3, r3, #3
	cmp	r3, #0
	beq	.L53
	mvn	r3, #9
	b	.L84
.L53:
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #24]
	cmp	r3, #0
	beq	.L54
	mvn	r3, #6
	b	.L84
.L54:
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #20]
	cmp	r3, #0
	beq	.L55
	mvn	r3, #5
	b	.L84
.L55:
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #12]
	cmp	r3, #7
	bls	.L56
	mvn	r3, #0
	b	.L84
.L56:
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #8]
	cmn	r3, #3
	bls	.L57
	mvn	r3, #4
	b	.L84
.L57:
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #12]
	cmp	r3, #0
	beq	.L58
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #4]
	cmn	r3, #1
	bne	.L58
	mvn	r3, #3
	b	.L84
.L58:
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #12]
	cmp	r3, #0
	beq	.L59
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #4]
	add	r3, r3, #1
	b	.L60
.L59:
	mov	r3, #0
.L60:
	str	r3, [fp, #-32]
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #8]
	add	r3, r3, #1
	str	r3, [fp, #-36]
	ldr	r3, [fp, #-224]
	ldr	r3, [r3, #8]
	add	r3, r3, #2
	str	r3, [fp, #-40]
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #12]
	and	r3, r3, #6
	str	r3, [fp, #-24]
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #12]
	and	r3, r3, #2
	cmp	r3, #0
	beq	.L61
	ldr	r3, [fp, #-24]
	orr	r3, r3, #2
	str	r3, [fp, #-24]
	mov	r3, #1
	strb	r3, [fp, #-25]
	b	.L62
.L61:
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #12]
	and	r3, r3, #1
	cmp	r3, #0
	beq	.L63
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #36]
	cmp	r3, #14
	bls	.L64
	ldr	r3, [fp, #-24]
	orr	r3, r3, #2
	str	r3, [fp, #-24]
	mov	r3, #2
	strb	r3, [fp, #-25]
	b	.L62
.L64:
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #4]
	cmp	r3, #640
	bne	.L66
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #8]
	cmp	r3, #480
	bne	.L66
	ldr	r3, [fp, #-236]
	ldrd	r0, [r3, #24]
	ldr	r3, [fp, #-236]
	ldrd	r2, [r3, #16]
	cmp	r0, r2
	sbcs	r3, r1, r3
	bcc	.L66
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #36]
	cmp	r3, #0
	beq	.L67
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #32]
	cmp	r3, #0
	bne	.L67
.L66:
	mov	r3, #1
	strb	r3, [fp, #-25]
	b	.L62
.L67:
	mov	r3, #0
	str	r3, [fp, #-20]
	b	.L68
.L71:
	ldr	r3, [fp, #-236]
	ldr	r1, [r3, #32]
	ldr	r2, [fp, #-20]
	mov	r3, r2
	lsl	r3, r3, #1
	add	r3, r3, r2
	lsl	r3, r3, #4
	add	r0, r1, r3
	sub	r1, fp, #184
	ldr	r2, [fp, #-16]
	mov	r3, r2
	lsl	r3, r3, #2
	add	r3, r3, r2
	lsl	r3, r3, #1
	add	r3, r1, r3
	mov	r1, r3
	bl	c2_encode_detection
	mov	r3, r0
	cmp	r3, #0
	bne	.L69
	mov	r3, #3
	strb	r3, [fp, #-25]
	b	.L70
.L69:
	ldr	r3, [fp, #-16]
	add	r3, r3, #1
	str	r3, [fp, #-16]
	ldr	r3, [fp, #-20]
	add	r3, r3, #1
	str	r3, [fp, #-20]
.L68:
	ldr	r3, [fp, #-236]
	ldr	r3, [r3, #36]
	ldr	r2, [fp, #-20]
	cmp	r2, r3
	bcc	.L71
.L70:
	ldrsb	r3, [fp, #-25]
	cmp	r3, #0
	bne	.L62
	ldr	r3, [fp, #-24]
	orr	r3, r3, #1
	str	r3, [fp, #-24]
	b	.L62
.L63:
	mov	r3, #1
	strb	r3, [fp, #-25]
.L62:
	ldrsb	r3, [fp, #-25]
	cmp	r3, #0
	beq	.L72
	ldr	r3, [fp, #-24]
	bic	r3, r3, #1
	str	r3, [fp, #-24]
	mov	r3, #0
	str	r3, [fp, #-16]
.L72:
	ldr	r3, [fp, #-24]
	and	r3, r3, #2
	cmp	r3, #0
	beq	.L73
	ldr	r3, [fp, #-24]
	bic	r3, r3, #1
	str	r3, [fp, #-24]
	mov	r3, #0
	str	r3, [fp, #-16]
.L73:
	ldr	r3, [fp, #-224]
	mov	r2, #1
	str	r2, [r3, #20]
	ldr	r3, [fp, #-228]
	add	r3, r3, #280
	ldr	r1, [fp, #-36]
	mov	r0, r3
	bl	c2_store_seqlock
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	mov	r0, r2
	blx	r3
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #8]
	ldr	r2, [fp, #4]
	ldr	r0, [r2]
	ldr	r1, [fp, #-228]
	mov	r2, #288
	blx	r3
	mov	r3, r0
	cmp	r3, #0
	bne	.L74
	mvn	r1, #8
	ldr	r0, [fp, #-224]
	bl	c2_poison
	mov	r3, r0
	b	.L84
.L74:
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	mov	r0, r2
	blx	r3
	movw	r1, #21075
	movt	r1, 21301
	ldr	r0, [fp, #-228]
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r2, r3, #4
	ldr	r3, [fp, #-236]
	ldr	r3, [r3]
	mov	r1, r3
	mov	r0, r2
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r3, r3, #8
	ldr	r1, [fp, #-16]
	mov	r0, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r0, r3, #12
	ldr	r3, [fp, #-236]
	ldrd	r2, [r3, #16]
	mov	r3, r2
	mov	r1, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	ip, r3, #16
	ldr	r3, [fp, #-236]
	ldrd	r0, [r3, #16]
	mov	r2, #0
	mov	r3, #0
	mov	r2, r1
	mov	r3, #0
	mov	r3, r2
	mov	r1, r3
	mov	r0, ip
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r0, r3, #20
	ldr	r3, [fp, #-236]
	ldrd	r2, [r3, #24]
	mov	r3, r2
	mov	r1, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	ip, r3, #24
	ldr	r3, [fp, #-236]
	ldrd	r0, [r3, #24]
	mov	r2, #0
	mov	r3, #0
	mov	r2, r1
	mov	r3, #0
	mov	r3, r2
	mov	r1, r3
	mov	r0, ip
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r3, r3, #28
	ldr	r1, [fp, #-24]
	mov	r0, r3
	bl	c2_put_u32
	mov	r3, #0
	str	r3, [fp, #-20]
	b	.L75
.L78:
	sub	r3, fp, #216
	mov	r2, #0
	str	r2, [r3]
	str	r2, [r3, #4]
	strh	r2, [r3, #8]	@ movhi
	ldr	r3, [fp, #-20]
	add	r3, r3, #2
	lsl	r3, r3, #4
	ldr	r2, [fp, #-228]
	add	r3, r2, r3
	str	r3, [fp, #-44]
	ldr	r2, [fp, #-20]
	ldr	r3, [fp, #-16]
	cmp	r2, r3
	bcs	.L76
	sub	r1, fp, #184
	ldr	r2, [fp, #-20]
	mov	r3, r2
	lsl	r3, r3, #2
	add	r3, r3, r2
	lsl	r3, r3, #1
	add	r3, r1, r3
	b	.L77
.L76:
	sub	r3, fp, #216
.L77:
	mov	r1, r3
	ldr	r0, [fp, #-44]
	bl	c2_write_detection
	ldr	r3, [fp, #-20]
	add	r3, r3, #1
	str	r3, [fp, #-20]
.L75:
	ldr	r3, [fp, #-20]
	cmp	r3, #13
	bls	.L78
	ldr	r3, [fp, #-228]
	add	r3, r3, #256
	movw	r1, #22577
	movt	r1, 21301
	mov	r0, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r3, r3, #260
	mov	r1, #1
	mov	r0, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r2, r3, #264
	ldr	r3, [fp, #-224]
	ldr	r3, [r3]
	mov	r1, r3
	mov	r0, r2
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r3, r3, #268
	ldr	r1, [fp, #-32]
	mov	r0, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r3, r3, #272
	mov	r1, #0
	mov	r0, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r3, r3, #276
	mov	r1, #0
	mov	r0, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	r3, r3, #284
	mov	r1, #0
	mov	r0, r3
	bl	c2_put_u32
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	mov	r0, r2
	blx	r3
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #8]
	ldr	r2, [fp, #4]
	ldr	r0, [r2]
	ldr	r1, [fp, #-228]
	mov	r2, #288
	blx	r3
	mov	r3, r0
	cmp	r3, #0
	bne	.L79
	mvn	r1, #8
	ldr	r0, [fp, #-224]
	bl	c2_poison
	mov	r3, r0
	b	.L84
.L79:
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	mov	r0, r2
	blx	r3
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #4]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	sub	r1, fp, #196
	mov	r0, r2
	blx	r3
	mov	r3, r0
	cmp	r3, #0
	bne	.L80
	mvn	r1, #7
	ldr	r0, [fp, #-224]
	bl	c2_poison
	mov	r3, r0
	b	.L84
.L80:
	ldr	r3, [fp, #-228]
	add	r0, r3, #272
	ldrd	r2, [fp, #-196]
	mov	r3, r2
	mov	r1, r3
	bl	c2_put_u32
	ldr	r3, [fp, #-228]
	add	ip, r3, #276
	ldrd	r0, [fp, #-196]
	mov	r2, #0
	mov	r3, #0
	mov	r2, r1
	mov	r3, #0
	mov	r3, r2
	mov	r1, r3
	mov	r0, ip
	bl	c2_put_u32
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	mov	r0, r2
	blx	r3
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #8]
	ldr	r2, [fp, #4]
	ldr	r0, [r2]
	ldr	r2, [fp, #-228]
	add	r2, r2, #256
	mov	r1, r2
	mov	r2, #32
	blx	r3
	mov	r3, r0
	cmp	r3, #0
	bne	.L81
	mvn	r1, #8
	ldr	r0, [fp, #-224]
	bl	c2_poison
	mov	r3, r0
	b	.L84
.L81:
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	mov	r0, r2
	blx	r3
	ldr	r3, [fp, #-228]
	add	r3, r3, #280
	ldr	r1, [fp, #-40]
	mov	r0, r3
	bl	c2_store_seqlock
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	mov	r0, r2
	blx	r3
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #8]
	ldr	r2, [fp, #4]
	ldr	r0, [r2]
	ldr	r2, [fp, #-228]
	add	r2, r2, #256
	mov	r1, r2
	mov	r2, #32
	blx	r3
	mov	r3, r0
	cmp	r3, #0
	bne	.L82
	mvn	r1, #8
	ldr	r0, [fp, #-224]
	bl	c2_poison
	mov	r3, r0
	b	.L84
.L82:
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #12]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	mov	r0, r2
	blx	r3
	ldr	r3, [fp, #-224]
	ldr	r2, [fp, #-40]
	str	r2, [r3, #8]
	ldr	r3, [fp, #-224]
	ldr	r2, [fp, #-32]
	str	r2, [r3, #4]
	ldr	r3, [fp, #-224]
	mov	r2, #1
	str	r2, [r3, #12]
	ldr	r3, [fp, #-224]
	mov	r2, #0
	str	r2, [r3, #20]
	ldr	r3, [fp, #8]
	cmp	r3, #0
	beq	.L83
	mov	r2, #56
	mov	r1, #0
	ldr	r0, [fp, #8]
	bl	memset
	ldr	r3, [fp, #-224]
	ldr	r2, [r3]
	ldr	r3, [fp, #8]
	str	r2, [r3]
	ldr	r3, [fp, #8]
	ldr	r2, [fp, #-32]
	str	r2, [r3, #4]
	ldr	r3, [fp, #8]
	ldr	r2, [fp, #-40]
	str	r2, [r3, #8]
	ldr	r3, [fp, #8]
	ldr	r2, [fp, #-24]
	str	r2, [r3, #12]
	ldr	r3, [fp, #8]
	ldr	r2, [fp, #-16]
	str	r2, [r3, #16]
	ldrd	r2, [fp, #-196]
	ldr	r1, [fp, #8]
	strd	r2, [r1, #24]
	ldr	r3, [fp, #4]
	ldr	r3, [r3, #4]
	ldr	r2, [fp, #4]
	ldr	r2, [r2]
	sub	r1, fp, #204
	mov	r0, r2
	blx	r3
	mov	r3, r0
	cmp	r3, #0
	beq	.L83
	ldrd	r0, [fp, #-204]
	ldrd	r2, [fp, #-196]
	cmp	r0, r2
	sbcs	r3, r1, r3
	bcc	.L83
	ldrd	r2, [fp, #-204]
	ldr	r1, [fp, #8]
	strd	r2, [r1, #32]
	ldrd	r0, [fp, #-204]
	ldrd	r2, [fp, #-196]
	subs	r4, r0, r2
	sbc	r5, r1, r3
	ldr	r3, [fp, #8]
	strd	r4, [r3, #40]
	ldr	r3, [fp, #8]
	mov	r2, #1
	str	r2, [r3, #48]
.L83:
	ldrsb	r3, [fp, #-25]
.L84:
	mov	r0, r3
	sub	sp, fp, #12
	@ sp needed
	pop	{r4, r5, fp, pc}
	.size	C2Publisher_Publish, .-C2Publisher_Publish
	.ident	"GCC: (GNU) 13.4.0"
