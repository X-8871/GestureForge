module tb_s2a_t63_descriptor_rom_dynamic;
  import s2a_network_descriptor_pkg::*;

  localparam integer LAYER_RECORD_BITS = 2608;
  localparam integer CHANNEL_RECORD_BITS = 232;

  logic [LAYER_RECORD_BITS-1:0] expected_layer [0:37];
  logic [CHANNEL_RECORD_BITS-1:0] expected_channel [0:3163];
  integer op_count [0:4];
  integer layer_index;
  integer channel_index;
  integer file_handle;
  string layer_fixture_path;
  string channel_fixture_path;

  function automatic logic [LAYER_RECORD_BITS-1:0] actual_layer(input integer idx);
    actual_layer = {
      S2A_LAYER_INDEX[idx],
      S2A_CFG_SECTION[idx],
      S2A_OP[idx],
      S2A_INPUT_COUNT[idx],
      S2A_INPUT_KIND[idx][0],
      S2A_INPUT_SOURCE_INDEX[idx][0],
      S2A_INPUT_ADDRESS[idx][0],
      S2A_INPUT_LENGTH_BYTES[idx][0],
      S2A_INPUT_N[idx][0],
      S2A_INPUT_C[idx][0],
      S2A_INPUT_H[idx][0],
      S2A_INPUT_W[idx][0],
      S2A_INPUT_SCALE_BITS[idx][0],
      S2A_INPUT_ROUTE_CHANNEL_START[idx][0],
      S2A_INPUT_ROUTE_CHANNEL_END[idx][0],
      S2A_INPUT_KIND[idx][1],
      S2A_INPUT_SOURCE_INDEX[idx][1],
      S2A_INPUT_ADDRESS[idx][1],
      S2A_INPUT_LENGTH_BYTES[idx][1],
      S2A_INPUT_N[idx][1],
      S2A_INPUT_C[idx][1],
      S2A_INPUT_H[idx][1],
      S2A_INPUT_W[idx][1],
      S2A_INPUT_SCALE_BITS[idx][1],
      S2A_INPUT_ROUTE_CHANNEL_START[idx][1],
      S2A_INPUT_ROUTE_CHANNEL_END[idx][1],
      S2A_OUTPUT_TENSOR_INDEX[idx],
      S2A_OUTPUT_ALLOCATION_KIND[idx],
      S2A_OUTPUT_ALIAS_LAYER_INDEX[idx],
      S2A_OUTPUT_MEMORY_WRITE_REQUIRED[idx],
      S2A_OUTPUT_ADDRESS[idx],
      S2A_OUTPUT_LENGTH_BYTES[idx],
      S2A_OUTPUT_N[idx],
      S2A_OUTPUT_C[idx],
      S2A_OUTPUT_H[idx],
      S2A_OUTPUT_W[idx],
      S2A_OUTPUT_SCALE_BITS[idx],
      S2A_KERNEL_H[idx],
      S2A_KERNEL_W[idx],
      S2A_STRIDE_H[idx],
      S2A_STRIDE_W[idx],
      S2A_PADDING_LEFT[idx],
      S2A_PADDING_RIGHT[idx],
      S2A_PADDING_TOP[idx],
      S2A_PADDING_BOTTOM[idx],
      S2A_GROUP_COUNT[idx],
      S2A_ROUTE_GROUP_ID[idx],
      S2A_PADDING_VALUE_INT8[idx],
      S2A_ACTIVATION[idx],
      S2A_ACCUMULATOR_BITS[idx],
      S2A_WEIGHT_LAYER_INDEX[idx],
      S2A_GF8_RECORD_OFFSET[idx],
      S2A_GF8_WEIGHT_SCALE_OFFSET[idx],
      S2A_GF8_BIAS_OFFSET[idx],
      S2A_GF8_WEIGHT_OFFSET[idx],
      S2A_GF8_WEIGHT_BYTES[idx],
      S2A_GF8_PACKAGE_BASE[idx],
      S2A_GF8_PACKAGE_LENGTH[idx],
      S2A_GF8_WEIGHT_ADDRESS[idx],
      S2A_GF8_BIAS_ADDRESS[idx],
      S2A_GF8_BIAS_BYTES[idx],
      S2A_T23_MQ_BASE[idx],
      S2A_T23_MQ_CHANNEL_COUNT[idx],
      S2A_MAXPOOL_DARKNET_PADDING[idx],
      S2A_MAXPOOL_ACTUAL_PAD_LEFT[idx],
      S2A_MAXPOOL_ACTUAL_PAD_RIGHT[idx],
      S2A_MAXPOOL_ACTUAL_PAD_TOP[idx],
      S2A_MAXPOOL_ACTUAL_PAD_BOTTOM[idx],
      S2A_MAXPOOL_WINDOW_ORIGIN_Y[idx],
      S2A_MAXPOOL_WINDOW_ORIGIN_X[idx],
      S2A_MAXPOOL_FORMULA[idx],
      S2A_UPSAMPLE_SCALE_BITS[idx],
      S2A_UPSAMPLE_STRIDE[idx],
      S2A_UPSAMPLE_METHOD[idx],
      S2A_ROUTE_REQUANTIZATION[idx],
      S2A_ROUTE_SLICE_ORDER[idx],
      S2A_YOLO_CLASSES[idx],
      S2A_YOLO_SCALE_X_Y_BITS[idx],
      S2A_YOLO_NEW_COORDS[idx],
      S2A_YOLO_HEAD_LOGIT_SCALE_BITS[idx],
      S2A_ROUTE_CHANNEL_START[idx][0],
      S2A_ROUTE_CHANNEL_START[idx][1],
      S2A_ROUTE_CHANNEL_END[idx][0],
      S2A_ROUTE_CHANNEL_END[idx][1],
      S2A_ROUTE_SOURCE_MULTIPLIER_Q31[idx][0],
      S2A_ROUTE_SOURCE_MULTIPLIER_Q31[idx][1],
      S2A_YOLO_ANCHOR_W[idx][0],
      S2A_YOLO_ANCHOR_W[idx][1],
      S2A_YOLO_ANCHOR_W[idx][2],
      S2A_YOLO_ANCHOR_W[idx][3],
      S2A_YOLO_ANCHOR_W[idx][4],
      S2A_YOLO_ANCHOR_W[idx][5],
      S2A_YOLO_ANCHOR_H[idx][0],
      S2A_YOLO_ANCHOR_H[idx][1],
      S2A_YOLO_ANCHOR_H[idx][2],
      S2A_YOLO_ANCHOR_H[idx][3],
      S2A_YOLO_ANCHOR_H[idx][4],
      S2A_YOLO_ANCHOR_H[idx][5],
      S2A_YOLO_MASK[idx][0],
      S2A_YOLO_MASK[idx][1],
      S2A_YOLO_MASK[idx][2],
      S2A_CONV_CANDIDATE_SHA256[idx],
      S2A_ROUTE_CONTRACT_SHA256[idx],
      S2A_MAXPOOL_FORMULA_SHA256[idx]
    };
  endfunction

  function automatic logic [CHANNEL_RECORD_BITS-1:0] actual_channel(input integer idx);
    actual_channel = {
      S2A_CONV_CHANNEL_LAYER_INDEX[idx],
      S2A_CONV_CHANNEL_INDEX[idx],
      S2A_CONV_WEIGHT_SCALE_BITS[idx],
      S2A_CONV_FUSED_BIAS_FLOAT32_BITS[idx],
      S2A_CONV_BIAS_ACCUMULATOR_INT32[idx],
      S2A_T23_MQ_ROM[idx]
    };
  endfunction

  task automatic check_global_constants;
    begin
      if (S2A_LAYER_COUNT !== 38 || S2A_CONV_CHANNEL_COUNT !== 3164 || S2A_MAX_INPUTS !== 2)
        $fatal(1, "T63 global ROM count constants mismatch");
      if (S2A_SERIAL_DISPATCH !== 1'b1 || S2A_TIMEOUT_SCOPE_GLOBAL !== 1'b1 ||
          S2A_PER_LAYER_TIMEOUT_RESTART !== 1'b0 || S2A_PS_VISIBLE_CSR_CHANGED !== 1'b0 ||
          S2A_MEMORY_OUTSTANDING_LIMIT !== 8'd1)
        $fatal(1, "T63 frozen G0/T22 protocol constants mismatch");
      if (S2A_G0_SPEC_SHA256 !== 256'h7C2C8684CE0B6377F5742964464B914A23410BD3F6E4F198075E6C97B371F230 ||
          S2A_MANIFEST_SHA256 !== 256'h9DD2477BC6F12B556DED8BED71E5ACD9EFB22F6E314564973A3BBBDA8279453A ||
          S2A_T22_SHA256 !== 256'h611D47CC85BD254474C5412FCAB2F8ACCE3A263138787588F2A6445EAC61D9A8 ||
          S2A_T23_SHA256 !== 256'h396DC66AA3CCC41050CC8183BFF16B86143A6F5553CF38FED16B0BA8B4EB4AE1)
        $fatal(1, "T63 frozen source SHA constants mismatch");
      if (S2A_OP_CONV !== 3'd0 || S2A_OP_MAXPOOL !== 3'd1 || S2A_OP_ROUTE !== 3'd2 ||
          S2A_OP_UPSAMPLE !== 3'd3 || S2A_OP_YOLO !== 3'd4)
        $fatal(1, "T63 operator enum constants mismatch");
      if (S2A_INPUT_NETWORK !== 2'd0 || S2A_INPUT_LAYER_OUTPUT !== 2'd1 ||
          S2A_OUTPUT_OWNED !== 1'b0 || S2A_OUTPUT_HEAD_ALIAS !== 1'b1)
        $fatal(1, "T63 input/output enum constants mismatch");
      if (S2A_ACT_NONE !== 2'd0 || S2A_ACT_LINEAR !== 2'd1 || S2A_ACT_LEAKY !== 2'd2)
        $fatal(1, "T63 activation enum constants mismatch");
      if (S2A_ROUTE_REQUANT_NONE !== 2'd0 || S2A_ROUTE_REQUANT_TO_OUTPUT_SCALE !== 2'd1 ||
          S2A_ROUTE_ORDER_NONE !== 2'd0 || S2A_ROUTE_ORDER_SLICE_THEN_CFG_CONCAT !== 2'd1 ||
          S2A_ROUTE_Q31_FRACTIONAL_BITS !== 31)
        $fatal(1, "T63 route enum/formula constants mismatch");
      if (S2A_MAXPOOL_FORMULA_NONE !== 2'd0 || S2A_MAXPOOL_FORMULA_DARKNET !== 2'd1 ||
          S2A_UPSAMPLE_NONE !== 2'd0 || S2A_UPSAMPLE_NEAREST_REPEAT !== 2'd1)
        $fatal(1, "T63 maxpool/upsample enum constants mismatch");
    end
  endtask

  task automatic check_yolo_alias(input integer idx, input integer source_layer);
    integer anchor_index;
    begin
      if (S2A_OP[idx] !== S2A_OP_YOLO ||
          S2A_OUTPUT_ALLOCATION_KIND[idx] !== S2A_OUTPUT_HEAD_ALIAS ||
          S2A_OUTPUT_ALIAS_LAYER_INDEX[idx] !== source_layer[5:0] ||
          S2A_OUTPUT_TENSOR_INDEX[idx] !== source_layer[5:0] ||
          S2A_OUTPUT_MEMORY_WRITE_REQUIRED[idx] !== 1'b0 ||
          S2A_INPUT_COUNT[idx] !== 2'd1 ||
          S2A_INPUT_KIND[idx][0] !== S2A_INPUT_LAYER_OUTPUT ||
          S2A_INPUT_SOURCE_INDEX[idx][0] !== source_layer[5:0] ||
          S2A_OUTPUT_ADDRESS[idx] !== S2A_INPUT_ADDRESS[idx][0] ||
          S2A_OUTPUT_LENGTH_BYTES[idx] !== S2A_INPUT_LENGTH_BYTES[idx][0] ||
          S2A_OUTPUT_N[idx] !== S2A_INPUT_N[idx][0] ||
          S2A_OUTPUT_C[idx] !== S2A_INPUT_C[idx][0] ||
          S2A_OUTPUT_H[idx] !== S2A_INPUT_H[idx][0] ||
          S2A_OUTPUT_W[idx] !== S2A_INPUT_W[idx][0] ||
          S2A_OUTPUT_SCALE_BITS[idx] !== S2A_INPUT_SCALE_BITS[idx][0])
        $fatal(1, "T63 YOLO alias semantics mismatch at layer %0d", idx);
      if (S2A_YOLO_CLASSES[idx] !== 16'd5 ||
          S2A_YOLO_MASK[idx][0] !== (idx == 30 ? 16'd3 : 16'd1) ||
          S2A_YOLO_MASK[idx][1] !== (idx == 30 ? 16'd4 : 16'd2) ||
          S2A_YOLO_MASK[idx][2] !== (idx == 30 ? 16'd5 : 16'd3))
        $fatal(1, "T63 YOLO mask/classes mismatch at layer %0d", idx);
      for (anchor_index = 0; anchor_index < 6; anchor_index = anchor_index + 1) begin
        case (anchor_index)
          0: if (S2A_YOLO_ANCHOR_W[idx][anchor_index] !== 16'd10 || S2A_YOLO_ANCHOR_H[idx][anchor_index] !== 16'd14) $fatal(1, "T63 anchor 0 mismatch");
          1: if (S2A_YOLO_ANCHOR_W[idx][anchor_index] !== 16'd23 || S2A_YOLO_ANCHOR_H[idx][anchor_index] !== 16'd27) $fatal(1, "T63 anchor 1 mismatch");
          2: if (S2A_YOLO_ANCHOR_W[idx][anchor_index] !== 16'd37 || S2A_YOLO_ANCHOR_H[idx][anchor_index] !== 16'd58) $fatal(1, "T63 anchor 2 mismatch");
          3: if (S2A_YOLO_ANCHOR_W[idx][anchor_index] !== 16'd81 || S2A_YOLO_ANCHOR_H[idx][anchor_index] !== 16'd82) $fatal(1, "T63 anchor 3 mismatch");
          4: if (S2A_YOLO_ANCHOR_W[idx][anchor_index] !== 16'd135 || S2A_YOLO_ANCHOR_H[idx][anchor_index] !== 16'd169) $fatal(1, "T63 anchor 4 mismatch");
          5: if (S2A_YOLO_ANCHOR_W[idx][anchor_index] !== 16'd344 || S2A_YOLO_ANCHOR_H[idx][anchor_index] !== 16'd319) $fatal(1, "T63 anchor 5 mismatch");
          default: $fatal(1, "T63 invalid anchor index");
        endcase
      end
    end
  endtask

  initial begin : run_dynamic_rom_check
    check_global_constants();
    if (!$value$plusargs("LAYER_FIXTURE=%s", layer_fixture_path))
      $fatal(1, "missing LAYER_FIXTURE plusarg");
    if (!$value$plusargs("CHANNEL_FIXTURE=%s", channel_fixture_path))
      $fatal(1, "missing CHANNEL_FIXTURE plusarg");
    file_handle = $fopen(layer_fixture_path, "r");
    if (file_handle == 0)
      $fatal(1, "cannot open layer expected fixture");
    $fclose(file_handle);
    file_handle = $fopen(channel_fixture_path, "r");
    if (file_handle == 0)
      $fatal(1, "cannot open channel expected fixture");
    $fclose(file_handle);
    $readmemh(layer_fixture_path, expected_layer);
    $readmemh(channel_fixture_path, expected_channel);

    for (layer_index = 0; layer_index < 5; layer_index = layer_index + 1)
      op_count[layer_index] = 0;
    for (layer_index = 0; layer_index < 38; layer_index = layer_index + 1) begin
      if (S2A_OP[layer_index] > S2A_OP_YOLO)
        $fatal(1, "T63 invalid operator code at layer %0d", layer_index);
      op_count[S2A_OP[layer_index]] = op_count[S2A_OP[layer_index]] + 1;
      if (actual_layer(layer_index) !== expected_layer[layer_index]) begin
        $display("T63 descriptor mismatch layer=%0d actual=%h expected=%h",
                 layer_index, actual_layer(layer_index), expected_layer[layer_index]);
        $fatal(1, "T63 descriptor ROM fixture mismatch");
      end
    end
    if (op_count[0] != 21 || op_count[1] != 3 || op_count[2] != 11 ||
        op_count[3] != 1 || op_count[4] != 2)
      $fatal(1, "T63 operator distribution mismatch: %0d,%0d,%0d,%0d,%0d",
             op_count[0], op_count[1], op_count[2], op_count[3], op_count[4]);

    for (channel_index = 0; channel_index < 3164; channel_index = channel_index + 1) begin
      if (actual_channel(channel_index) !== expected_channel[channel_index]) begin
        $display("T63 channel mismatch index=%0d actual=%h expected=%h",
                 channel_index, actual_channel(channel_index), expected_channel[channel_index]);
        $fatal(1, "T63 T23 M/Q/channel fixture mismatch");
      end
    end

    check_yolo_alias(30, 29);
    check_yolo_alias(37, 36);
    $display("PASS S2A-T63 dynamic descriptor ROM layers=38 fields_per_layer=104 channels=3164 fields_per_channel=6 op=21,3,11,1,2 yolo_alias=2");
    $finish;
  end
endmodule
