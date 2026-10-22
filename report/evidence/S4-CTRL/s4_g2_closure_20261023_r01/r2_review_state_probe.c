#include "s4_inject_frame.h"
#include <stdio.h>
#include <string.h>
static int bc,fail_at,fl,iv;
static void f(void*c,uint64_t a,uint64_t n){(void)c;(void)a;(void)n;fl++;}
static void i(void*c,uint64_t a,uint64_t n){(void)c;(void)a;(void)n;iv++;}
static int b(void*c){(void)c;bc++;return bc!=fail_at;}
int main(void){s4_inject_ring r={0};s4_inject_region g={"local",0x10000000,2048};s4_inject_cache_ops o={f,i,b};s4_inject_validation_report q;char nm[]="local";int bad=0;
if(s4_inject_ring_init(&r,1,1,&g,1,&o,0,&q)!=S4_INJECT_OK)return 2;
memset(nm,'x',sizeof(nm));o.flush=0;o.invalidate=0;o.barrier=0;
r.slots[0].state=S4_SLOT_LOADING;r.slots[0].desc.length_bytes=48;strcpy(r.slots[0].desc.region_name,"local");r.slots[0].written_bytes=48;r.slots[0].addr_start=g.base_addr;r.slots[0].addr_end=g.base_addr+48;
fail_at=1;bad+=s4_inject_ring_advance(&r,0,S4_EV_WRITE_COMPLETE,&q)!=S4_INJECT_OK;
bad+=s4_inject_ring_advance(&r,0,S4_EV_FLUSH,&q)!=S4_INJECT_ERR_CACHE_BARRIER;
bad+=s4_inject_ring_advance(&r,0,S4_EV_PUBLISH,&q)!=S4_INJECT_ERR_EVENT_ORDER;
fail_at=0;bad+=s4_inject_ring_advance(&r,0,S4_EV_FLUSH,&q)!=S4_INJECT_OK;
bad+=s4_inject_ring_advance(&r,0,S4_EV_PUBLISH,&q)!=S4_INJECT_OK;
fail_at=bc+1;bad+=s4_inject_ring_advance(&r,0,S4_EV_INVALIDATE,&q)!=S4_INJECT_ERR_CACHE_BARRIER;
bad+=s4_inject_ring_advance(&r,0,S4_EV_CONSUMER_START,&q)!=S4_INJECT_ERR_EVENT_ORDER;
fail_at=0;bad+=s4_inject_ring_advance(&r,0,S4_EV_INVALIDATE,&q)!=S4_INJECT_OK;
bad+=s4_inject_ring_timeout(&r,0,&q)!=S4_INJECT_ERR_CONSUMER_TIMEOUT;
bad+=s4_inject_ring_abort(&r,0,&q)!=S4_INJECT_ERR_EVENT_ORDER;
bad+=s4_inject_ring_confirm_consumer_stopped(&r,0,&q)!=S4_INJECT_OK;
bad+=s4_inject_ring_abort(&r,0,&q)!=S4_INJECT_OK;
printf("checks=12 failures=%d flush=%d invalidate=%d barrier=%d\n",bad,fl,iv,bc);return bad?1:0;}