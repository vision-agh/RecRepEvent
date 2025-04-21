`timescale 1ns / 1ps


module kamil_ut;
    logic                               clk = '0;
    logic                               rst = '0;
    logic [8-1:0]                       x = 0;
    logic [8-1:0]                       y = 0;
    logic [8-1:0]                       t = 129;
    logic [31:0]                        cnt = 0;
    logic                               is_valid = '0;

    logic [8 * 12 -1:0]                 r_output = '0;
    logic [$clog2(128*128)-1 : 0]       addr = '0;
    logic                               read = '0;
    
    logic [8-1:0] t_in = 0;
    logic [8-1:0] x_in = 0;
    logic [8-1:0] y_in = 0;
    
    
    always begin
        clk = 0;
        forever #5 clk = ~clk; 
    end

    always @(posedge clk) begin
        cnt <= cnt + 1;
        is_valid <= 1'b0;
        
        if (cnt == 20) begin
            t_in <= 129;
            x_in <= 0;
            y_in <= 0;
            is_valid <= 1'b1;
        end
        
        if (cnt == 22) begin
            t_in <= 130;
            x_in <= 1;
            y_in <= 1;
            is_valid <= 1'b1;
        end
        
        if (cnt == 24) begin
            t_in <= 131;
            x_in <= 2;
            y_in <= 2;
            is_valid <= 1'b1;
        end
        
        
    end

    top uut (
        .clk(clk),
        .reset(rst),
        .x_coord(x_in),
        .y_coord(y_in),
        .timestamp(t_in),
        .is_valid(is_valid),
        .readback_output(r_output),
        .readback_addr(addr),
        .readback(read)
    );

endmodule
