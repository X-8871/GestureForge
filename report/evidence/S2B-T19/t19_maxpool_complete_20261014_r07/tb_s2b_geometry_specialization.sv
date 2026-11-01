// 新旧真实引擎逐周期差分；状态仅用于定位abort刺激，所有公开输出均比较。
module tb_s2b_geometry_specialization;
logic clk = 0; logic reset = 1;
integer cycles=0; integer pool_cases=0; integer upsample_cases=0;
integer p_abort_coverage=0; integer u_abort_coverage=0;
function automatic logic [7:0] memory_byte(input logic [31:0] address, input integer raw);
logic [7:0] value; begin value = raw != 0 ? 8'h80 : 8'((address ^ (address >> 8) ^ 32'ha5) & 32'hff);
if (raw == 0 && value == 8'h80) value = 8'h81; return value; end endfunction
logic  p_abort_in;
logic  p_start_valid_in;
logic  p_start_ready_old;
logic  p_start_ready_new;
logic [31:0] p_layer_index_in;
logic [31:0] p_input_base_address_in;
logic [31:0] p_input_length_bytes_in;
logic [31:0] p_input_channels_in;
logic [31:0] p_input_height_in;
logic [31:0] p_input_width_in;
logic [31:0] p_output_base_address_in;
logic [31:0] p_output_length_bytes_in;
logic [31:0] p_output_channels_in;
logic [31:0] p_output_height_in;
logic [31:0] p_output_width_in;
logic [31:0] p_kernel_height_in;
logic [31:0] p_kernel_width_in;
logic [31:0] p_stride_y_in;
logic [31:0] p_stride_x_in;
logic [31:0] p_darknet_padding_parameter_in;
logic [31:0] p_output_channel_in;
logic [31:0] p_output_y_in;
logic [31:0] p_output_x_in;
logic  p_backend_cancel_old;
logic  p_backend_cancel_new;
logic  p_backend_req_valid_old;
logic  p_backend_req_valid_new;
logic  p_backend_req_ready_in;
logic  p_backend_req_write_old;
logic  p_backend_req_write_new;
logic [31:0] p_backend_req_addr_old;
logic [31:0] p_backend_req_addr_new;
logic [31:0] p_backend_req_wdata_old;
logic [31:0] p_backend_req_wdata_new;
logic [3:0] p_backend_req_rstrb_old;
logic [3:0] p_backend_req_rstrb_new;
logic [3:0] p_backend_req_wstrb_old;
logic [3:0] p_backend_req_wstrb_new;
logic  p_backend_rsp_valid_in;
logic [31:0] p_backend_rsp_rdata_in;
logic [2:0] p_backend_rsp_error_in;
logic  p_result_valid_old;
logic  p_result_valid_new;
logic  p_result_ready_in;
logic [127:0] p_result_tap_addresses_old;
logic [127:0] p_result_tap_addresses_new;
logic [31:0] p_result_output_address_old;
logic [31:0] p_result_output_address_new;
logic [7:0] p_result_value_old;
logic [7:0] p_result_value_new;
logic [2:0] p_result_error_code_old;
logic [2:0] p_result_error_code_new;
s2a_maxpool_engine p_old (.clk(clk),
.hard_reset(reset),
.abort(p_abort_in),
.start_valid(p_start_valid_in),
.start_ready(p_start_ready_old),
.layer_index(p_layer_index_in),
.input_base_address(p_input_base_address_in),
.input_length_bytes(p_input_length_bytes_in),
.input_channels(p_input_channels_in),
.input_height(p_input_height_in),
.input_width(p_input_width_in),
.output_base_address(p_output_base_address_in),
.output_length_bytes(p_output_length_bytes_in),
.output_channels(p_output_channels_in),
.output_height(p_output_height_in),
.output_width(p_output_width_in),
.kernel_height(p_kernel_height_in),
.kernel_width(p_kernel_width_in),
.stride_y(p_stride_y_in),
.stride_x(p_stride_x_in),
.darknet_padding_parameter(p_darknet_padding_parameter_in),
.output_channel(p_output_channel_in),
.output_y(p_output_y_in),
.output_x(p_output_x_in),
.backend_cancel(p_backend_cancel_old),
.backend_req_valid(p_backend_req_valid_old),
.backend_req_ready(p_backend_req_ready_in),
.backend_req_write(p_backend_req_write_old),
.backend_req_addr(p_backend_req_addr_old),
.backend_req_wdata(p_backend_req_wdata_old),
.backend_req_rstrb(p_backend_req_rstrb_old),
.backend_req_wstrb(p_backend_req_wstrb_old),
.backend_rsp_valid(p_backend_rsp_valid_in),
.backend_rsp_rdata(p_backend_rsp_rdata_in),
.backend_rsp_error(p_backend_rsp_error_in),
.result_valid(p_result_valid_old),
.result_ready(p_result_ready_in),
.result_tap_addresses(p_result_tap_addresses_old),
.result_output_address(p_result_output_address_old),
.result_value(p_result_value_old),
.result_error_code(p_result_error_code_old));
s2b_maxpool_engine p_new (.clk(clk),
.hard_reset(reset),
.abort(p_abort_in),
.start_valid(p_start_valid_in),
.start_ready(p_start_ready_new),
.layer_index(p_layer_index_in),
.input_base_address(p_input_base_address_in),
.input_length_bytes(p_input_length_bytes_in),
.input_channels(p_input_channels_in),
.input_height(p_input_height_in),
.input_width(p_input_width_in),
.output_base_address(p_output_base_address_in),
.output_length_bytes(p_output_length_bytes_in),
.output_channels(p_output_channels_in),
.output_height(p_output_height_in),
.output_width(p_output_width_in),
.kernel_height(p_kernel_height_in),
.kernel_width(p_kernel_width_in),
.stride_y(p_stride_y_in),
.stride_x(p_stride_x_in),
.darknet_padding_parameter(p_darknet_padding_parameter_in),
.output_channel(p_output_channel_in),
.output_y(p_output_y_in),
.output_x(p_output_x_in),
.backend_cancel(p_backend_cancel_new),
.backend_req_valid(p_backend_req_valid_new),
.backend_req_ready(p_backend_req_ready_in),
.backend_req_write(p_backend_req_write_new),
.backend_req_addr(p_backend_req_addr_new),
.backend_req_wdata(p_backend_req_wdata_new),
.backend_req_rstrb(p_backend_req_rstrb_new),
.backend_req_wstrb(p_backend_req_wstrb_new),
.backend_rsp_valid(p_backend_rsp_valid_in),
.backend_rsp_rdata(p_backend_rsp_rdata_in),
.backend_rsp_error(p_backend_rsp_error_in),
.result_valid(p_result_valid_new),
.result_ready(p_result_ready_in),
.result_tap_addresses(p_result_tap_addresses_new),
.result_output_address(p_result_output_address_new),
.result_value(p_result_value_new),
.result_error_code(p_result_error_code_new));
task automatic p_clear; begin p_abort_in=0; p_start_valid_in=0; p_layer_index_in=0; p_input_base_address_in=0; p_input_length_bytes_in=0; p_input_channels_in=0; p_input_height_in=0; p_input_width_in=0; p_output_base_address_in=0; p_output_length_bytes_in=0; p_output_channels_in=0; p_output_height_in=0; p_output_width_in=0; p_kernel_height_in=0; p_kernel_width_in=0; p_stride_y_in=0; p_stride_x_in=0; p_darknet_padding_parameter_in=0; p_output_channel_in=0; p_output_y_in=0; p_output_x_in=0; p_backend_req_ready_in=0; p_backend_rsp_valid_in=0; p_backend_rsp_rdata_in=0; p_backend_rsp_error_in=0; p_result_ready_in=0; end endtask
integer p_pending=0; integer p_delay=0; integer p_requests=0; integer p_raw=0; integer p_response_error=0; integer p_error_target=0; integer p_stall=1; logic [31:0] p_response_data=0; logic [2:0] p_pending_error=0;

task automatic p_service;
logic accepting; logic responding; logic [31:0] address;
begin
  p_backend_req_ready_in = (p_stall == 0 || (cycles % 5) != 0);
  p_backend_rsp_valid_in = p_pending != 0 && p_delay == 0;
  p_backend_rsp_rdata_in = p_response_data;
  p_backend_rsp_error_in = p_pending_error;
  #1;
  accepting = p_backend_req_valid_old && p_backend_req_ready_in;
  responding = p_backend_rsp_valid_in;
  address = p_backend_req_addr_old;
  if (p_abort_in) begin accepting=0; responding=0; end
  tick;
  if (p_abort_in) begin p_pending=0; p_delay=0; end
  else begin
    if (responding) p_pending=0;
    else if (p_pending != 0 && p_delay > 0) p_delay=p_delay-1;
    if (accepting) begin
      if (p_pending != 0) $fatal(1,"重复memory请求");
      p_requests=p_requests+1;
      p_pending=1;
      p_delay=p_stall == 0 ? 0 : cycles % 4;
      p_pending_error=p_requests == p_error_target ? 3'(p_response_error) : 3'd0;
      for(integer lane=0;lane<4;lane=lane+1)
        p_response_data[lane*8+:8]=memory_byte(address+32'(lane),p_raw);
    end
  end
end endtask


task automatic p_vectors;
integer file_handle; integer scanned; integer expected_error; integer abort_state; integer elapsed; integer injected;
logic [31:0] source_address; logic [31:0] expected_output_address; logic signed [7:0] expected_value; logic signed [7:0] candidate;
begin
  file_handle=$fopen("pool_vectors.dat","r");
  if(file_handle==0) $fatal(1,"向量文件缺失");
  while(!$feof(file_handle)) begin
    scanned=$fscanf(file_handle,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",p_layer_index_in,p_input_base_address_in,p_input_length_bytes_in,p_input_channels_in,p_input_height_in,p_input_width_in,p_output_base_address_in,p_output_length_bytes_in,p_output_channels_in,p_output_height_in,p_output_width_in,p_kernel_height_in,p_kernel_width_in,p_stride_y_in,p_stride_x_in,p_darknet_padding_parameter_in,p_output_channel_in,p_output_y_in,p_output_x_in,expected_error,p_raw,p_response_error,p_error_target,abort_state,p_stall);
    if(scanned==25) begin
      p_pending=0; p_requests=0; p_backend_rsp_valid_in=0; p_backend_rsp_error_in=0;
      p_start_valid_in=1; p_result_ready_in=0; p_abort_in=(abort_state==0); injected=0;
      tick;
      p_start_valid_in=0;
      if(abort_state==0) begin
        if(p_result_valid_old || p_backend_req_valid_old || p_start_ready_old) $fatal(1,"IDLE abort未阻止启动");
        p_abort_coverage=p_abort_coverage | 1;
        p_abort_in=0; tick;
      end else begin
        elapsed=0;
        while(!p_result_valid_old && elapsed<200) begin
          if(abort_state!=6 && abort_state==integer'(p_old.state)) begin
            p_abort_in=1; injected=1;
            p_abort_coverage=p_abort_coverage | (1<<abort_state);
          end
          p_service;
          elapsed=elapsed+1;
          if(injected!=0) begin
            if(p_result_valid_old || p_backend_req_valid_old || !p_backend_cancel_old) $fatal(1,"活动状态abort未取消");
            p_abort_in=0; tick;
            break;
          end
        end
        if(injected==0) begin
          if(!p_result_valid_old) $fatal(1,"结果超时");
          if(p_result_error_code_old !== 3'(expected_error)) $fatal(1,"错误优先/响应错误码不符 case=%0d expected=%0d actual=%0d",pool_cases,expected_error,p_result_error_code_old);
          
if (p_result_valid_old && expected_error == 0) begin
  expected_output_address=((p_output_channel_in*p_output_height_in+p_output_y_in)*p_output_width_in)+p_output_x_in+p_output_base_address_in;
  expected_value=-8'sd127;
  for(integer tap=0;tap<4;tap=tap+1) begin
    source_address=((p_output_channel_in * p_input_height_in + p_output_y_in*2 + 32'(tap/2))*p_input_width_in)+p_output_x_in*2+32'(tap%2)+p_input_base_address_in;
    if (p_result_tap_addresses_old[tap*32+:32] !== source_address) $fatal(1,"池化tap地址错误");
    candidate=$signed(memory_byte(source_address,p_raw));
    if (candidate>expected_value) expected_value=candidate;
  end
  if (p_result_output_address_old !== expected_output_address || p_result_value_old !== expected_value) $fatal(1,"池化独立地址/数值错误");
end

          if(expected_error==0 && p_requests!=5) $fatal(1,"合法请求数不符");
          if(expected_error!=0 && p_response_error==0 && p_raw==0 && p_requests!=0) $fatal(1,"拒绝参数产生请求");
          if(abort_state==6) begin
            p_abort_in=1; tick;
            if(!p_result_valid_old) $fatal(1,"RESULT abort丢失结果");
            p_abort_coverage=p_abort_coverage | (1<<abort_state);
            p_abort_in=0;
          end
          repeat(3) p_service;
          p_result_ready_in=1; tick;
          p_result_ready_in=0;
        end
      end
      p_backend_rsp_valid_in=0; p_backend_req_ready_in=0; p_abort_in=0;
      tick;
      if(!p_start_ready_old) $fatal(1,"未回到IDLE");
      pool_cases=pool_cases+1;
    end else if(scanned!=-1) $fatal(1,"向量字段数量不符");
  end
  $fclose(file_handle);
end endtask

logic  u_abort_in;
logic  u_start_valid_in;
logic  u_start_ready_old;
logic  u_start_ready_new;
logic [31:0] u_input_base_address_in;
logic [31:0] u_input_length_bytes_in;
logic [31:0] u_output_base_address_in;
logic [31:0] u_output_length_bytes_in;
logic [31:0] u_input_channels_in;
logic [31:0] u_input_height_in;
logic [31:0] u_input_width_in;
logic [31:0] u_stride_in;
logic [31:0] u_output_channel_in;
logic [31:0] u_output_y_in;
logic [31:0] u_output_x_in;
logic  u_backend_cancel_old;
logic  u_backend_cancel_new;
logic  u_backend_req_valid_old;
logic  u_backend_req_valid_new;
logic  u_backend_req_ready_in;
logic  u_backend_req_write_old;
logic  u_backend_req_write_new;
logic [31:0] u_backend_req_addr_old;
logic [31:0] u_backend_req_addr_new;
logic [31:0] u_backend_req_wdata_old;
logic [31:0] u_backend_req_wdata_new;
logic [3:0] u_backend_req_rstrb_old;
logic [3:0] u_backend_req_rstrb_new;
logic [3:0] u_backend_req_wstrb_old;
logic [3:0] u_backend_req_wstrb_new;
logic  u_backend_rsp_valid_in;
logic [31:0] u_backend_rsp_rdata_in;
logic [2:0] u_backend_rsp_error_in;
logic  u_result_valid_old;
logic  u_result_valid_new;
logic  u_result_ready_in;
logic [31:0] u_result_source_address_old;
logic [31:0] u_result_source_address_new;
logic [31:0] u_result_output_address_old;
logic [31:0] u_result_output_address_new;
logic [7:0] u_result_value_old;
logic [7:0] u_result_value_new;
logic [2:0] u_result_error_code_old;
logic [2:0] u_result_error_code_new;
s2a_upsample_engine u_old (.clk(clk),
.hard_reset(reset),
.abort(u_abort_in),
.start_valid(u_start_valid_in),
.start_ready(u_start_ready_old),
.input_base_address(u_input_base_address_in),
.input_length_bytes(u_input_length_bytes_in),
.output_base_address(u_output_base_address_in),
.output_length_bytes(u_output_length_bytes_in),
.input_channels(u_input_channels_in),
.input_height(u_input_height_in),
.input_width(u_input_width_in),
.stride(u_stride_in),
.output_channel(u_output_channel_in),
.output_y(u_output_y_in),
.output_x(u_output_x_in),
.backend_cancel(u_backend_cancel_old),
.backend_req_valid(u_backend_req_valid_old),
.backend_req_ready(u_backend_req_ready_in),
.backend_req_write(u_backend_req_write_old),
.backend_req_addr(u_backend_req_addr_old),
.backend_req_wdata(u_backend_req_wdata_old),
.backend_req_rstrb(u_backend_req_rstrb_old),
.backend_req_wstrb(u_backend_req_wstrb_old),
.backend_rsp_valid(u_backend_rsp_valid_in),
.backend_rsp_rdata(u_backend_rsp_rdata_in),
.backend_rsp_error(u_backend_rsp_error_in),
.result_valid(u_result_valid_old),
.result_ready(u_result_ready_in),
.result_source_address(u_result_source_address_old),
.result_output_address(u_result_output_address_old),
.result_value(u_result_value_old),
.result_error_code(u_result_error_code_old));
s2b_upsample_engine u_new (.clk(clk),
.hard_reset(reset),
.abort(u_abort_in),
.start_valid(u_start_valid_in),
.start_ready(u_start_ready_new),
.input_base_address(u_input_base_address_in),
.input_length_bytes(u_input_length_bytes_in),
.output_base_address(u_output_base_address_in),
.output_length_bytes(u_output_length_bytes_in),
.input_channels(u_input_channels_in),
.input_height(u_input_height_in),
.input_width(u_input_width_in),
.stride(u_stride_in),
.output_channel(u_output_channel_in),
.output_y(u_output_y_in),
.output_x(u_output_x_in),
.backend_cancel(u_backend_cancel_new),
.backend_req_valid(u_backend_req_valid_new),
.backend_req_ready(u_backend_req_ready_in),
.backend_req_write(u_backend_req_write_new),
.backend_req_addr(u_backend_req_addr_new),
.backend_req_wdata(u_backend_req_wdata_new),
.backend_req_rstrb(u_backend_req_rstrb_new),
.backend_req_wstrb(u_backend_req_wstrb_new),
.backend_rsp_valid(u_backend_rsp_valid_in),
.backend_rsp_rdata(u_backend_rsp_rdata_in),
.backend_rsp_error(u_backend_rsp_error_in),
.result_valid(u_result_valid_new),
.result_ready(u_result_ready_in),
.result_source_address(u_result_source_address_new),
.result_output_address(u_result_output_address_new),
.result_value(u_result_value_new),
.result_error_code(u_result_error_code_new));
task automatic u_clear; begin u_abort_in=0; u_start_valid_in=0; u_input_base_address_in=0; u_input_length_bytes_in=0; u_output_base_address_in=0; u_output_length_bytes_in=0; u_input_channels_in=0; u_input_height_in=0; u_input_width_in=0; u_stride_in=0; u_output_channel_in=0; u_output_y_in=0; u_output_x_in=0; u_backend_req_ready_in=0; u_backend_rsp_valid_in=0; u_backend_rsp_rdata_in=0; u_backend_rsp_error_in=0; u_result_ready_in=0; end endtask
integer u_pending=0; integer u_delay=0; integer u_requests=0; integer u_raw=0; integer u_response_error=0; integer u_error_target=0; integer u_stall=1; logic [31:0] u_response_data=0; logic [2:0] u_pending_error=0;

task automatic u_service;
logic accepting; logic responding; logic [31:0] address;
begin
  u_backend_req_ready_in = (u_stall == 0 || (cycles % 5) != 0);
  u_backend_rsp_valid_in = u_pending != 0 && u_delay == 0;
  u_backend_rsp_rdata_in = u_response_data;
  u_backend_rsp_error_in = u_pending_error;
  #1;
  accepting = u_backend_req_valid_old && u_backend_req_ready_in;
  responding = u_backend_rsp_valid_in;
  address = u_backend_req_addr_old;
  if (u_abort_in) begin accepting=0; responding=0; end
  tick;
  if (u_abort_in) begin u_pending=0; u_delay=0; end
  else begin
    if (responding) u_pending=0;
    else if (u_pending != 0 && u_delay > 0) u_delay=u_delay-1;
    if (accepting) begin
      if (u_pending != 0) $fatal(1,"重复memory请求");
      u_requests=u_requests+1;
      u_pending=1;
      u_delay=u_stall == 0 ? 0 : cycles % 4;
      u_pending_error=u_requests == u_error_target ? 3'(u_response_error) : 3'd0;
      for(integer lane=0;lane<4;lane=lane+1)
        u_response_data[lane*8+:8]=memory_byte(address+32'(lane),u_raw);
    end
  end
end endtask


task automatic u_vectors;
integer file_handle; integer scanned; integer expected_error; integer abort_state; integer elapsed; integer injected;
logic [31:0] source_address; logic [31:0] expected_output_address; logic signed [7:0] expected_value; 
begin
  file_handle=$fopen("upsample_vectors.dat","r");
  if(file_handle==0) $fatal(1,"向量文件缺失");
  while(!$feof(file_handle)) begin
    scanned=$fscanf(file_handle,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",u_input_base_address_in,u_input_length_bytes_in,u_output_base_address_in,u_output_length_bytes_in,u_input_channels_in,u_input_height_in,u_input_width_in,u_stride_in,u_output_channel_in,u_output_y_in,u_output_x_in,expected_error,u_raw,u_response_error,u_error_target,abort_state,u_stall);
    if(scanned==17) begin
      u_pending=0; u_requests=0; u_backend_rsp_valid_in=0; u_backend_rsp_error_in=0;
      u_start_valid_in=1; u_result_ready_in=0; u_abort_in=(abort_state==0); injected=0;
      tick;
      u_start_valid_in=0;
      if(abort_state==0) begin
        if(u_result_valid_old || u_backend_req_valid_old || u_start_ready_old) $fatal(1,"IDLE abort未阻止启动");
        u_abort_coverage=u_abort_coverage | 1;
        u_abort_in=0; tick;
      end else begin
        elapsed=0;
        while(!u_result_valid_old && elapsed<200) begin
          if(abort_state!=5 && abort_state==integer'(u_old.state)) begin
            u_abort_in=1; injected=1;
            u_abort_coverage=u_abort_coverage | (1<<abort_state);
          end
          u_service;
          elapsed=elapsed+1;
          if(injected!=0) begin
            if(u_result_valid_old || u_backend_req_valid_old || !u_backend_cancel_old) $fatal(1,"活动状态abort未取消");
            u_abort_in=0; tick;
            break;
          end
        end
        if(injected==0) begin
          if(!u_result_valid_old) $fatal(1,"结果超时");
          if(u_result_error_code_old !== 3'(expected_error)) $fatal(1,"错误优先/响应错误码不符 case=%0d expected=%0d actual=%0d",upsample_cases,expected_error,u_result_error_code_old);
          
if (u_result_valid_old && expected_error == 0) begin
  expected_output_address=((u_output_channel_in*32'd26+u_output_y_in)*32'd26)+u_output_x_in+u_output_base_address_in;
  source_address=((u_output_channel_in*32'd13+(u_output_y_in>>1))*32'd13)+(u_output_x_in>>1)+u_input_base_address_in;
  expected_value=$signed(memory_byte(source_address,u_raw));
  if (u_result_source_address_old !== source_address || u_result_output_address_old !== expected_output_address || u_result_value_old !== expected_value) $fatal(1,"上采样独立地址/数值错误");
end

          if(expected_error==0 && u_requests!=2) $fatal(1,"合法请求数不符");
          if(expected_error!=0 && u_response_error==0 && u_raw==0 && u_requests!=0) $fatal(1,"拒绝参数产生请求");
          if(abort_state==5) begin
            u_abort_in=1; tick;
            if(!u_result_valid_old) $fatal(1,"RESULT abort丢失结果");
            u_abort_coverage=u_abort_coverage | (1<<abort_state);
            u_abort_in=0;
          end
          repeat(3) u_service;
          u_result_ready_in=1; tick;
          u_result_ready_in=0;
        end
      end
      u_backend_rsp_valid_in=0; u_backend_req_ready_in=0; u_abort_in=0;
      tick;
      if(!u_start_ready_old) $fatal(1,"未回到IDLE");
      upsample_cases=upsample_cases+1;
    end else if(scanned!=-1) $fatal(1,"向量字段数量不符");
  end
  $fclose(file_handle);
end endtask

task automatic p_compare; begin if({p_start_ready_old,p_backend_cancel_old,p_backend_req_valid_old,p_backend_req_write_old,p_backend_req_addr_old,p_backend_req_wdata_old,p_backend_req_rstrb_old,p_backend_req_wstrb_old,p_result_valid_old,p_result_tap_addresses_old,p_result_output_address_old,p_result_value_old,p_result_error_code_old} !== {p_start_ready_new,p_backend_cancel_new,p_backend_req_valid_new,p_backend_req_write_new,p_backend_req_addr_new,p_backend_req_wdata_new,p_backend_req_rstrb_new,p_backend_req_wstrb_new,p_result_valid_new,p_result_tap_addresses_new,p_result_output_address_new,p_result_value_new,p_result_error_code_new}) $fatal(1,"pool公开端口逐周期不等价 cycles=%0d cases=%0d",cycles,pool_cases); end endtask
task automatic u_compare; begin if({u_start_ready_old,u_backend_cancel_old,u_backend_req_valid_old,u_backend_req_write_old,u_backend_req_addr_old,u_backend_req_wdata_old,u_backend_req_rstrb_old,u_backend_req_wstrb_old,u_result_valid_old,u_result_source_address_old,u_result_output_address_old,u_result_value_old,u_result_error_code_old} !== {u_start_ready_new,u_backend_cancel_new,u_backend_req_valid_new,u_backend_req_write_new,u_backend_req_addr_new,u_backend_req_wdata_new,u_backend_req_rstrb_new,u_backend_req_wstrb_new,u_result_valid_new,u_result_source_address_new,u_result_output_address_new,u_result_value_new,u_result_error_code_new}) $fatal(1,"upsample公开端口逐周期不等价 cycles=%0d cases=%0d",cycles,upsample_cases); end endtask
task automatic tick; begin clk=0; #2; p_compare; u_compare; clk=1; #2; p_compare; u_compare; clk=0; #1; cycles=cycles+1; end endtask
integer p_reset_coverage=0; task automatic p_resets; integer elapsed; begin for(integer target=0;target<7;target++) begin p_clear; p_layer_index_in=32'h9; p_input_base_address_in=32'h14f3800; p_input_length_bytes_in=32'h152000; p_input_channels_in=32'h80; p_input_height_in=32'h68; p_input_width_in=32'h68; p_output_base_address_in=32'h1645800; p_output_length_bytes_in=32'h54800; p_output_channels_in=32'h80; p_output_height_in=32'h34; p_output_width_in=32'h34; p_kernel_height_in=32'h2; p_kernel_width_in=32'h2; p_stride_y_in=32'h2; p_stride_x_in=32'h2; p_darknet_padding_parameter_in=32'h1; p_output_channel_in=32'h0; p_output_y_in=32'h0; p_output_x_in=32'h0;
p_pending=0; p_requests=0; p_raw=0; p_response_error=0; p_error_target=0; p_stall=1;
if(target!=0) begin p_start_valid_in=1; tick; p_start_valid_in=0; elapsed=0; while(integer'(p_old.state)!=target && elapsed<200) begin p_service; elapsed++; end if(elapsed>=200) $fatal(1,"reset状态不可达"); end
reset=1; p_start_valid_in=1; p_result_ready_in=1; p_backend_rsp_valid_in=1; p_abort_in=1; tick;
if(p_start_ready_old || p_backend_req_valid_old || p_result_valid_old || !p_backend_cancel_old || p_result_value_old!=0 || p_result_error_code_old!=0 || p_result_output_address_old!=0) $fatal(1,"hard_reset优先或输出清零错误");
p_reset_coverage|=1<<target; p_clear; p_pending=0; reset=0; tick; if(!p_start_ready_old) $fatal(1,"reset恢复失败"); end end endtask
integer u_reset_coverage=0; task automatic u_resets; integer elapsed; begin for(integer target=0;target<6;target++) begin u_clear; u_input_base_address_in=32'h1a51e00; u_input_length_bytes_in=32'h5480; u_output_base_address_in=32'h1a57280; u_output_length_bytes_in=32'h15200; u_input_channels_in=32'h80; u_input_height_in=32'hd; u_input_width_in=32'hd; u_stride_in=32'h2; u_output_channel_in=32'h0; u_output_y_in=32'h0; u_output_x_in=32'h0;
u_pending=0; u_requests=0; u_raw=0; u_response_error=0; u_error_target=0; u_stall=1;
if(target!=0) begin u_start_valid_in=1; tick; u_start_valid_in=0; elapsed=0; while(integer'(u_old.state)!=target && elapsed<200) begin u_service; elapsed++; end if(elapsed>=200) $fatal(1,"reset状态不可达"); end
reset=1; u_start_valid_in=1; u_result_ready_in=1; u_backend_rsp_valid_in=1; u_abort_in=1; tick;
if(u_start_ready_old || u_backend_req_valid_old || u_result_valid_old || !u_backend_cancel_old || u_result_value_old!=0 || u_result_error_code_old!=0 || u_result_output_address_old!=0) $fatal(1,"hard_reset优先或输出清零错误");
u_reset_coverage|=1<<target; u_clear; u_pending=0; reset=0; tick; if(!u_start_ready_old) $fatal(1,"reset恢复失败"); end end endtask
initial begin p_clear; u_clear; repeat(2) tick; reset=0; tick; p_vectors; u_vectors; p_resets; u_resets; if(p_reset_coverage!=127 || u_reset_coverage!=63) $fatal(1,"reset覆盖不足"); $display("RESET_COVERAGE pool=%0d upsample=%0d",p_reset_coverage,u_reset_coverage);
if(p_abort_coverage!=127 || u_abort_coverage!=63) $fatal(1,"abort状态覆盖不足");
$display("PASS GEOMETRY_SPECIALIZATION pool=%0d upsample=%0d cycles=%0d pool_abort=%0d upsample_abort=%0d",pool_cases,upsample_cases,cycles,p_abort_coverage,u_abort_coverage); $finish; end
endmodule
