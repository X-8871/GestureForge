// tb_s4d_axis8_to_axis64.sv —— 自检 TB：16 字节（0x00..0x0F）应打包成 2 个 64 bit beat
//   beat0 = 0x0706050403020100, tkeep=0xFF, tlast=0
//   beat1 = 0x0F0E0D0C0B0A0908, tkeep=0xFF, tlast=1
// 另测：帧尾不足 8 字节（3 字节 0xA1,0xA2,0xA3）应得 1 个 beat：tdata[23:0]=0xA3A2A1, tkeep=0x07, tlast=1
`timescale 1ns / 1ps

module tb_s4d_axis8_to_axis64;
    logic clk = 1'b0;
    logic rstn = 1'b0;

    logic [7:0]  s_tdata  = 8'h00;
    logic        s_tvalid = 1'b0;
    logic        s_tready;
    logic        s_tlast  = 1'b0;
    logic        s_tuser  = 1'b0;

    logic [63:0] m_tdata;
    logic [7:0]  m_tkeep;
    logic        m_tvalid;
    logic        m_tready = 1'b1;
    logic        m_tlast;

    s4d_axis8_to_axis64 dut (
        .clk(clk), .rstn(rstn),
        .s_tdata(s_tdata), .s_tvalid(s_tvalid), .s_tready(s_tready), .s_tlast(s_tlast), .s_tuser(s_tuser),
        .m_tdata(m_tdata), .m_tkeep(m_tkeep), .m_tvalid(m_tvalid), .m_tready(m_tready), .m_tlast(m_tlast)
    );

    always #5 clk = ~clk;

    integer errors = 0;
    integer beats  = 0;
    logic [63:0] exp_data [0:3];
    logic [7:0]  exp_keep [0:3];
    logic        exp_last [0:3];

    // 收集输出 beat
    always @(posedge clk) begin
        if (rstn && m_tvalid && m_tready) begin
            if (beats < 4) begin
                if (m_tdata !== exp_data[beats]) begin
                    $display("FAIL beat%0d data got=%016h exp=%016h", beats, m_tdata, exp_data[beats]);
                    errors = errors + 1;
                end
                if (m_tkeep !== exp_keep[beats]) begin
                    $display("FAIL beat%0d keep got=%02h exp=%02h", beats, m_tkeep, exp_keep[beats]);
                    errors = errors + 1;
                end
                if (m_tlast !== exp_last[beats]) begin
                    $display("FAIL beat%0d last got=%0b exp=%0b", beats, m_tlast, exp_last[beats]);
                    errors = errors + 1;
                end
            end
            beats = beats + 1;
        end
    end

    task automatic push_byte(input logic [7:0] b, input logic last);
        begin
            @(negedge clk);
            while (!s_tready) @(negedge clk);   // 等能收
            s_tdata  = b;
            s_tlast  = last;
            s_tvalid = 1'b1;
            @(posedge clk);                     // 本拍被接收（s_tready 在拍间稳定）
            @(negedge clk);
            s_tvalid = 1'b0;
            s_tlast  = 1'b0;
        end
    endtask

    integer i;
    initial begin
        exp_data[0] = 64'h0706050403020100; exp_keep[0] = 8'hFF; exp_last[0] = 1'b0;
        exp_data[1] = 64'h0F0E0D0C0B0A0908; exp_keep[1] = 8'hFF; exp_last[1] = 1'b1;
        exp_data[2] = 64'h0000000000A3A2A1; exp_keep[2] = 8'h07; exp_last[2] = 1'b1;
        exp_data[3] = 64'h0;

        repeat (4) @(posedge clk);
        rstn = 1'b1;
        @(posedge clk);

        for (i = 0; i < 16; i = i + 1) begin
            push_byte(i[7:0], (i == 15));
        end
        repeat (6) @(posedge clk);

        push_byte(8'hA1, 1'b0);
        push_byte(8'hA2, 1'b0);
        push_byte(8'hA3, 1'b1);
        repeat (8) @(posedge clk);

        if (beats !== 3) begin
            $display("FAIL beat_count got=%0d exp=3", beats);
            errors = errors + 1;
        end
        if (errors == 0) $display("PACKER_TB_RESULT=PASS beats=%0d", beats);
        else             $display("PACKER_TB_RESULT=FAIL errors=%0d", errors);
        $finish;
    end

    initial begin
        #20000;
        $display("PACKER_TB_RESULT=FAIL timeout beats=%0d", beats);
        $finish;
    end
endmodule