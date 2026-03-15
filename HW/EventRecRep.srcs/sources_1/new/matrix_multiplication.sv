`timescale 1ns / 1ps

(* use_dsp48 = "no" *)

module matrix_multiplication #(
    parameter int INPUT_DIM = 4,
    parameter int INPUT_PRECISION = 8,    
    parameter int OUTPUT_DIM = 8,
    parameter int PRECISION = 8,
    parameter int MULTIPLIER = 0,
    parameter int ZERO_POINT_IN = 0,
    parameter int ZERO_POINT_OUT = 0
)( 
    input  logic                        clk,
    input  logic                        reset,
    input  logic signed [INPUT_PRECISION:0]   feature_matrix [INPUT_DIM-1:0],
    input  logic signed [PRECISION:0]   weight_matrix  [OUTPUT_DIM-1:0][INPUT_DIM-1:0],
    input  logic signed [31:0]          bias           [OUTPUT_DIM-1:0],
    output logic        [PRECISION-1:0] output_matrix  [OUTPUT_DIM-1:0]
);

    logic signed [31:0]         matrix_result  [OUTPUT_DIM-1:0];
    logic signed [63:0]         debug_bias  [OUTPUT_DIM-1:0];
    logic signed [63:0]         debug_mul  [OUTPUT_DIM-1:0];
    
    logic signed [63:0]         product  [OUTPUT_DIM-1:0];
    logic signed [INPUT_PRECISION:0]  temp_diff;
    logic signed [PRECISION:0]  temp_sum;
    logic [PRECISION-1:0]       saturated_result;

    genvar m;

    generate
        for (m = 0; m < OUTPUT_DIM; m++) begin : raw
            always @(posedge clk) begin
                matrix_result[m] = 0;
                for (int j=0; j< INPUT_DIM; j=j+1) begin: cols
                    temp_diff = feature_matrix[j] - ZERO_POINT_IN;
                    matrix_result[m] = matrix_result[m] + ( ( temp_diff ) * weight_matrix[m][j]);
                end
                debug_bias[m] <= (matrix_result[m]+bias[m]);
            end
            always @(posedge clk) begin
                product[m] = (debug_bias[m]*MULTIPLIER);
                debug_mul[m] = product[m]>>>32;
                temp_sum = debug_mul[m][PRECISION-1:0] + ZERO_POINT_OUT + product[m][31];

                if (temp_sum > $signed({1'b0, {PRECISION{1'b1}}})) begin
                    saturated_result = {PRECISION{1'b1}};
                end else begin
                    saturated_result = temp_sum[PRECISION-1:0];
                end
            
                output_matrix[m] <= temp_sum;

            end
        end
    endgenerate

endmodule