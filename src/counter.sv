`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2026/09/03 12:13:57
// Design Name: 
// Module Name: counter
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


module counter#(

    parameter  int WIDTH=3,
    parameter  int MAX_COUNT=5,
    parameter  bit WRAP_ON_OVERFLOW=1'b1
     )

(
    input logic clk,
    input logic en,
    input logic rst,
    output logic [WIDTH-1:0] count
    );
    
    always_ff @(posedge clk)
    begin
            if(rst) begin
            count<=1'b0;
          end  else if(en)begin
                   if(count<MAX_COUNT) begin        
                    count<=count+1'b1;
                end
                  else  if(WRAP_ON_OVERFLOW==1) begin
                        count<='0;
                    end else begin
                     count<=MAX_COUNT;
                     end
                     end
                     end
                    
    
endmodule
