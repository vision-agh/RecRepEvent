`timescale 1ns / 1ps

module add_vectors_rescale #(
    parameter int DIM = 4,
    parameter int PRECISION = 8,
    parameter longint MULTIPLIER_IN_1 = 0,
    parameter longint MULTIPLIER_IN_2 = 0,
    parameter int ZERO_POINT_IN_1 = 0,
    parameter int ZERO_POINT_IN_2 = 0,
    parameter int ZERO_POINT_OUT = 0
)( 
    input  logic                         clk,
    input  logic                         reset,
    input  logic signed [PRECISION:0]   input_vector_1 [DIM-1:0],
    input  logic signed [PRECISION:0]   input_vector_2 [DIM-1:0],
    output logic        [PRECISION-1:0] output_vector   [DIM-1:0]
);

    logic signed [63:0] product          [DIM-1:0];
    logic signed [63:0] debug_mul        [DIM-1:0];
    logic signed [PRECISION:0] temp_sum  [DIM-1:0];
    logic        [PRECISION-1:0] saturated_result [DIM-1:0];

    genvar m;
    generate
        for (m = 0; m < DIM; m++) begin : raw
            always_ff @(posedge clk) begin
                // Fixed-point multiply and accumulate
                product[m] <= 
                    $signed(input_vector_1[m] - ZERO_POINT_IN_1) * $signed(MULTIPLIER_IN_1) +
                    $signed(input_vector_2[m] - ZERO_POINT_IN_2) * $signed(MULTIPLIER_IN_2);

                // Shift down by 32 (simulate fixed-point result)
                debug_mul[m] <= product[m] >>> 32;

                // Add output zero point + rounding (bit 31 of lower 32 bits)
                temp_sum[m] <= debug_mul[m][PRECISION-1:0] + ZERO_POINT_OUT + product[m][31];

                // Saturate to [0, 2^PRECISION - 1]
                if (temp_sum[m] > $signed({1'b0, {PRECISION{1'b1}}})) begin
                    saturated_result[m] <= {PRECISION{1'b1}};
                end else begin
                    saturated_result[m] <= temp_sum[m][PRECISION-1:0];
                end

                // Output assignment
                output_vector[m] <= saturated_result[m];
            end
        end
    endgenerate

endmodule
