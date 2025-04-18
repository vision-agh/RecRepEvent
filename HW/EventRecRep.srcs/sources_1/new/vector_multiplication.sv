`timescale 1ns / 1ps

module vector_multiplication #(
    parameter int DIM = 4,
    parameter int PRECISION = 8,
    parameter int MULTIPLIER = 0,
    parameter int ZERO_POINT_IN_1 = 0,
    parameter int ZERO_POINT_IN_2 = 0,
    parameter int ZERO_POINT_OUT = 0
)( 
    input  logic                        clk,
    input  logic                        reset,
    input  logic signed [PRECISION:0]   vector_1 [DIM-1:0],
    input  logic signed [PRECISION:0]   vector_2 [DIM-1:0],
    output logic        [PRECISION-1:0] output_vector  [DIM-1:0]
);

    logic signed [31:0]         vector_result  [DIM-1:0];
    logic signed [63:0]         debug_mul  [DIM-1:0];
    
    logic signed [63:0]         product  [DIM-1:0];
    logic signed [PRECISION:0]  temp_sum;
    logic [PRECISION-1:0]       saturated_result;

    genvar m;

    generate
        for (m = 0; m < DIM; m++) begin : raw
            always @(posedge clk) begin
                vector_result[m] = 0;
                vector_result[m] = (vector_1[m] - ZERO_POINT_IN_1) * (vector_2[m] - ZERO_POINT_IN_2);
            end
            always @(posedge clk) begin
                product[m] = (vector_result[m]*MULTIPLIER);
                debug_mul[m] = product[m]>>>32;
                temp_sum = debug_mul[m][PRECISION-1:0] + ZERO_POINT_OUT + product[m][31];

                if (temp_sum > $signed({1'b0, {PRECISION{1'b1}}})) begin
                    saturated_result = {PRECISION{1'b1}};
                end else begin
                    saturated_result = temp_sum[PRECISION-1:0];
                end
            
                output_vector[m] <= saturated_result;

            end
        end
    endgenerate

endmodule