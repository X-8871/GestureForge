#ifndef C2_INTEGRATION_STATUS_H
#define C2_INTEGRATION_STATUS_H

#include <stdint.h>

#include "c2_s5_publish.h"

/* 汇总2B、C2稳定读回和单帧显示服务；任一环节失败都不得报告整链PASS。 */
static inline uint32_t C2_IntegrationPass(
    uint32_t chain_pass,
    C2PublishCode publish_rc,
    uint32_t readback_pass,
    int display_rc,
    uint32_t ack_idle)
{
    return (chain_pass != 0u && publish_rc == C2_PUBLISH_OK &&
            readback_pass != 0u && display_rc == 0 && ack_idle != 0u) ? 1u : 0u;
}

#endif
