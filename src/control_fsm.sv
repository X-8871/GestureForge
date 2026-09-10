`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2026/09/04 09:40:42
// Design Name: 
// Module Name: control_fsm
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module control_fsm #(
parameter int PROCESS_CYCLES=3
)

(
    input clk,
    input rst,
    input start,
    output logic done,
    output logic busy
    );
    
    typedef enum logic [1:0]
    {
    IDLE,
    PROCESS,
    DONE
    }state_t;
    
    state_t state;
    state_t next_state;
    
    localparam int COUNT_WIDTH =
        (PROCESS_CYCLES <= 1) ? 1 : $clog2(PROCESS_CYCLES);
    
    logic [COUNT_WIDTH-1:0] count;
    
    always_ff @(posedge clk) begin
        if(rst) 
            state<=IDLE;
        else
            state<=next_state;
        end
    always_ff @(posedge clk) begin 
        if(rst) begin
            count<='0;
            end else if(state==PROCESS)begin 
                        if(count==PROCESS_CYCLES-1)begin
                        count<='0;
                        end else begin
                        count<=count+1'b1;
                        end 
                        end
                        else begin
                            count<='0;
                            end
                            end
                                 
                 
            
           
    always_comb begin
    next_state=state;
    
    case(state)
        IDLE:   begin
            if(start)
            next_state=PROCESS;
            end
            
        PROCESS:begin
            if(count==PROCESS_CYCLES-1)
                next_state=DONE;
                end
        DONE:begin
            next_state=IDLE;
            end
            
        default :begin
            next_state= IDLE;
             end
        endcase     
     end
     
     assign done=(state==DONE);
     assign busy=(state==PROCESS);      
endmodule
