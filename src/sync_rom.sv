`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2026/09/07 10:33:17
// Design Name: 
// Module Name: sync_rom
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


module sync_rom #(
parameter int ADDR_WIDTH=2,
parameter int DATA_WIDTH=8,
parameter int DEPTH=1<<ADDR_WIDTH
)

(
input logic rst,
input logic clk,
input logic rd_en,
input logic [ADDR_WIDTH-1:0] rd_addr,
output logic [DATA_WIDTH-1:0] rd_data,
output logic rd_valid

    );
    logic [DATA_WIDTH-1:0] rom [0:DEPTH-1];
    
    initial begin
        rom [0]=8'h11;
        rom [1]=8'h22;
        rom [2]=8'h33;
        rom [3]=8'h44;
    end
     
    always_ff @(posedge clk) begin
        if(rst) begin
            rd_data<='0;
            rd_valid<=1'b0;
            end else if(rd_en)begin
                rd_valid<=1'b1;
                rd_data<=rom[rd_addr];
                end else rd_valid<=1'b0;
                
   
    end
        
    
endmodule
