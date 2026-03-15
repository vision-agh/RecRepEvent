`timescale 1ns / 1ps

module gru_layer #(
    parameter int WIDTH         = 224,
    parameter int HEIGHT        = 224,
    parameter int CHANNELS      = 12,
    parameter int INPUT_BIT_X   = 8,
    parameter int INPUT_BIT_Y   = 8,
    parameter int PRECISION     = 8
)(
    input   logic                               clk,
    input   logic                               reset,
    input   logic [INPUT_BIT_X-1:0]             x_coord,
    input   logic [INPUT_BIT_Y-1:0]             y_coord,
    input   logic [PRECISION-1:0]               timestamp,
    input   logic                               is_valid, 

    output  logic [PRECISION * CHANNELS -1:0]   readback_output,
    input   logic [$clog2(WIDTH*HEIGHT)-1 : 0]  readback_addr,
    input   logic                               readback
);

    genvar i;
    
    localparam DELAY_ADD = 2;
    localparam DELAY_MUL = 3;
    
    // Parameters for input and hidden
    localparam ZERO_POINT_INPUT         =   119;
    localparam ZERO_POINT_HIDDEN        =   117;
    
    // Parameters for linear layers
    localparam MULTIPLIER_LINEAR_INPUT  =   7870735;
    localparam ZERO_POINT_LINEAR_INPUT  =   133;
    localparam MULTIPLIER_LINEAR_HIDDEN  =   13271278;
    localparam ZERO_POINT_LINEAR_HIDDEN  =   133;
    
    
    //////////////////////////////////////////////
    //          REPRESENTATION                  //
    //      - resolution WIDTH x HEIGHT         //
    //      - number of CHANNELS x PRECISION    //
    //////////////////////////////////////////////

    logic                               reg_valid;
    logic [PRECISION * CHANNELS -1:0]   h_prev_mem;
    logic [PRECISION * CHANNELS -1:0]   h_new_mem;
    logic [PRECISION-1:0]               h_prev  [CHANNELS-1:0];
    logic [PRECISION-1:0]               h_new [CHANNELS-1:0];

    memory #(
        .AWIDTH     ( $clog2(WIDTH*HEIGHT)  ),
        .DWIDTH     ( PRECISION*CHANNELS    ),
        .RAM_TYPE   ( "block"               ),
        .ZERO_POINT ( {CHANNELS{8'd117}}      )
    ) representation (
    
        // PROCESS ON A
        .clk      ( clk                         ),
        .mem_ena  ( is_valid || reg_valid       ),
        .wea      ( reg_valid                   ),
        .addra    ( x_coord * HEIGHT + y_coord  ),
        .dina     ( h_new_mem                   ),
        .douta    ( h_prev_mem                  ),
        
        // READBACK ON B
        .mem_enb  ( readback                    ),
        .web      ( '0                          ),
        .addrb    ( readback_addr               ),
        .doutb    ( readback_output             )
    );

    //////////////////////////////////////////////
    //      SPLITTING FOR INDIVIDUAL CHANNELS   //
    /////////////////////////////////////////////
    
    always_comb begin
        for (int i = 0; i < CHANNELS; i++) begin
            h_prev[i] = h_prev_mem[i*PRECISION +: PRECISION]; 
        end
    end

    //////////////////////////////////////////////////////////////
    //      INIT LINEAR LAYER WEIGHTS AND BIASES FOR INPUT      //
    /////////////////////////////////////////////////////////////

    logic signed [PRECISION:0] weights_lin_input [3*CHANNELS-1:0][0:0];
    initial begin
        weights_lin_input[0] = {82};     weights_lin_input[1] = {-115};   weights_lin_input[2] = {-73};    weights_lin_input[3] = {-50};
        weights_lin_input[4] = {-85};    weights_lin_input[5] = {68};     weights_lin_input[6] = {-105};   weights_lin_input[7] = {136};
        weights_lin_input[8] = {-61};    weights_lin_input[9] = {87};     weights_lin_input[10] = {5};     weights_lin_input[11] = {-64};
        weights_lin_input[12] = {98};    weights_lin_input[13] = {-112};  weights_lin_input[14] = {-78};   weights_lin_input[15] = {18};
        weights_lin_input[16] = {116};   weights_lin_input[17] = {-63};   weights_lin_input[18] = {-89};   weights_lin_input[19] = {-94};
        weights_lin_input[20] = {-65};   weights_lin_input[21] = {-51};   weights_lin_input[22] = {-34};   weights_lin_input[23] = {-83};
        weights_lin_input[24] = {46};    weights_lin_input[25] = {1};     weights_lin_input[26] = {-96};   weights_lin_input[27] = {-84};
        weights_lin_input[28] = {31};    weights_lin_input[29] = {-2};    weights_lin_input[30] = {104};   weights_lin_input[31] = {-22};
        weights_lin_input[32] = {-119};  weights_lin_input[33] = {-108};  weights_lin_input[34] = {-43};   weights_lin_input[35] = {-32};
    end
       
    logic signed [31:0] bias_lin_input [3*CHANNELS-1:0];
    initial begin
        bias_lin_input = {   -2264,   451,  4349, -6169,  9931,  6154, -9637, -5638,  4650, 10381,  -785,  7112, 10409,  
                        -151, -2732,  2143, 10208, -2451, 3275,  5265,  7406,  -813,  8268,  4836,  6639, -5893, 
                        -7196, 2703,  9437, -3255,  2432,  7772, -3522,  3907, -2375,  1208};
    end
    
    //////////////////////////////////////////////////////////////
    //      INIT LINEAR LAYER WEIGHTS AND BIASES FOR HIDDEN     //
    //////////////////////////////////////////////////////////////
    
    logic signed [PRECISION:0] weights_lin_hidden [3*CHANNELS-1:0][CHANNELS-1:0];
    initial begin
        weights_lin_hidden[0] =   { -35,   35,   28,   86,   47,   58,  113,   40,   19,  -46, 94,   19};
        weights_lin_hidden[1] =   {  82,  123,  -29,   90,  -26,  115,  100,  -46,    5,  -56,  -52,  -26};
        weights_lin_hidden[2] =   {  -1,  -44, -120,  -77,  -11,  -41,   95,  104,   81,   56,   -101,  121};
        weights_lin_hidden[3] =   {-112,  -42,  -90,   46, -106,  -63,  -81,  -78,  -60,  125,  -10,   39};
        weights_lin_hidden[4] =   {-127,  113,  -28, -117,   88,  -34,  116,  -87, -118,  -96, 55,  -14};
        weights_lin_hidden[5] =   {-118,   24,   -8,   46,  -65,  -91,   87,  -61,   90,  103,  -89,  -59};
        weights_lin_hidden[6] =   {  15, -120,   39,  -53,  -57,  -99,   60,  -81, -102,  -34,  -71, -124};
        weights_lin_hidden[7] =   {  51,  -49,   89,   90,  -81,  -74,  -45,   75,   -4,  -46, 79,  121};
        weights_lin_hidden[8] =   {  94,  -98,  -26,  -24,  109,  -66,  -73,    2,  -30,   48, 16,  -76};
        weights_lin_hidden[9] =   {  93,   79,   28, -115,   60,   85,   36,  -49,    9,  -49,  120,  123};
        weights_lin_hidden[10] =  { -15,  -86,   75,   65,   68,  -96,   43,  -54, -112,  -89, 54,   48};
        weights_lin_hidden[11] =  {-112,   72,   98,   97,   72,  -20,   85,  100,   66,  -92,  -45,  101};
        weights_lin_hidden[12] =  {  97,   81,  -53,  -25,  -95,  -73,   98, -105,  -32,   27,  -77,   30};
        weights_lin_hidden[13] =  { -21,   51,  -98,   18, -116,   79,  124,  -46,   19,  -66,  -82,  -65};
        weights_lin_hidden[14] =  { -61,   24,  -15,    9,  -98,  -80, -110,  -92,  107,   47,   -122,  -21};
        weights_lin_hidden[15] =  {  10,   68,  118,   31,   90,  -45,   -4,  -77,   29,  118, 80,  127};
        weights_lin_hidden[16] =  { -57,  -16,   26,  103, -117,  -63,   19,  -74,   48,   -9,  -33,   68};
        weights_lin_hidden[17] =  {  91,  124,   58,   -3,  104,  102,  -64,   58,   15,  -55,  -30,  -30};
        
        weights_lin_hidden[18] =  { -89,  -39,   43,   94,   10, -124,   68,  -39,  114, -123,  -30,   99};
        weights_lin_hidden[19] =  {  55,  -64, -110,   -1,   49, -106, -107,   -2,  -26,   82,   -124,  -20};
        weights_lin_hidden[20] =  { -99,  -19,  -65,   40, -107, -100,  -72, -112,   81,  -18,  -71,   89};
        weights_lin_hidden[21] =  { -29,   66,  -40, -107,   28,   79, -124,   13,   25,   15, -3,  -40};
        weights_lin_hidden[22] =  { -99,   21,  -86, -105,  -41,  -87,   39,   91,   99,  -79, 70,   91};
        weights_lin_hidden[23] =  {   1,   54,   72,   98,   68,   54,  -48,  -71,  -60,  105,  -31,    5};
        weights_lin_hidden[24] =  {-119,   -6,  -36,  -82,   99, -103,  -18,   -9, -115,   77,  -41,   57};
        weights_lin_hidden[25] =  {  71,  112,   32,   96,  118,   25,  -26,  -35,   21,   46,   -120,   96};
        weights_lin_hidden[26] =  {  20, -119,   41,   81,   48,  104,    3, -106,    0,   93,  -61,   54};
        weights_lin_hidden[27] =  {  29,  -21,    1,   54,  -87,   81,   86,   72,  127,   -6,  -90,    6};
        weights_lin_hidden[28] =  { -37,   45,  108,  -70,    5,  124, -102,  -22,  124,   89, 37,  -55};
        weights_lin_hidden[29] =  { -12, -114, -120, -120,  123,  101,   51,  -32,  110,  -34, 89,   -4};
        weights_lin_hidden[30] =  { -60,  -36,  -27, -117,   38,  -39,   59,   81,  -20,   62, 25,   86};
        weights_lin_hidden[31] =  { -82,  -11,  -43,  112, -114,  -72,   14,  113,   86, -119,  -90,  124};
        weights_lin_hidden[32] =  {  19, -109,  -40,   56,  -27,  -98,  -79,  -66,   -5,   50, 61,  -62};
        weights_lin_hidden[33] =  { -21,  -98,   96,  127,  124,   52,  -27,   -3,   46, -111,  8, -104};
        weights_lin_hidden[34] =  {-128,   -4,  -41,  -81,   21,    5,   19,  -71, -125,    3,  -52,  -43};
        weights_lin_hidden[35] =  {  94,   21,   58,  -36, -101,   25,  -84,   16, -100,   96,  -87,  111};
    end
       
    logic signed [31:0] bias_lin_hidden [3*CHANNELS-1:0];
    initial begin
        bias_lin_hidden =     {363, -1638,  6097, -1722, -4904, -5252, -1116, -3823,  5660, 5648, 41, -6219, 
                        -4418,  -332,  -719, -5858, 425, -6233, 3101,  2381,  4789, -4882, -3869,  1805, 
                        230,  2954, 325, 5724, -5773, -2498,  -100,  -306,  1454,  3768,  4747,  4436};
    end

    ////////////////////////////////////////////////////
    //       FORWARD LINEAR LAYER FOR INPUT - 2cc     //
    ////////////////////////////////////////////////////
    
    logic signed [PRECISION:0]  input_signed [0:0];
    assign input_signed[0] = {1'b0, timestamp};
    
    logic [PRECISION-1:0]       lin_input  [(3*CHANNELS)-1:0];
    logic [PRECISION-1:0]       i_r  [CHANNELS-1:0];
    logic [PRECISION-1:0]       i_z  [CHANNELS-1:0];
    logic [PRECISION-1:0]       i_n  [CHANNELS-1:0];

    matrix_multiplication #(
        .INPUT_DIM      ( 1 ),
        .OUTPUT_DIM     ( 3*CHANNELS ),
        .PRECISION      ( PRECISION ),
        .MULTIPLIER     ( MULTIPLIER_LINEAR_INPUT ),
        .ZERO_POINT_IN  ( ZERO_POINT_INPUT ),
        .ZERO_POINT_OUT ( ZERO_POINT_LINEAR_INPUT )
    ) input_linear (
        .clk            ( clk ),
        .reset          ( reset ),
        .feature_matrix ( input_signed ),
        .weight_matrix  ( weights_lin_input ),
        .bias           ( bias_lin_input ),
        .output_matrix  ( lin_input )
    );
    
    always @(posedge clk) begin // 1 cc
        i_r = lin_input[CHANNELS-1:0];
        i_z = lin_input[2*CHANNELS-1:CHANNELS];
        i_n = lin_input[3*CHANNELS-1:2*CHANNELS];
    end

    ////////////////////////////////////////////////////
    //      FORWARD LINEAR LAYER FOR HIDDEN - 2 cc    //
    ////////////////////////////////////////////////////

    logic signed [PRECISION:0]  h_prev_signed [CHANNELS-1:0];
    
    generate
        for (i=0; i<CHANNELS; i++) begin : signed_hidden
            assign h_prev_signed[i] = {1'b0, h_prev[i]};
        end
    endgenerate
    
    logic [PRECISION-1:0]   lin_hidden  [3*CHANNELS-1:0];
   
    logic [PRECISION-1:0]   h_r  [CHANNELS-1:0];
    logic [PRECISION-1:0]   h_z  [CHANNELS-1:0];
    logic [PRECISION-1:0]   h_n  [CHANNELS-1:0];

    matrix_multiplication #(
        .INPUT_DIM  ( CHANNELS ),
        .OUTPUT_DIM ( 3*CHANNELS ),
        .PRECISION  ( PRECISION ),
        .MULTIPLIER ( MULTIPLIER_LINEAR_HIDDEN ),
        .ZERO_POINT_IN  ( ZERO_POINT_HIDDEN ),
        .ZERO_POINT_OUT ( ZERO_POINT_LINEAR_HIDDEN )
        
    ) hidden_linear (
        .clk            ( clk ),
        .reset          ( reset ),
        .feature_matrix ( h_prev_signed ),
        .weight_matrix  ( weights_lin_hidden ),          
        .bias           ( bias_lin_hidden ),                   
        .output_matrix  ( lin_hidden )
    );

    assign h_r = lin_hidden[CHANNELS-1:0];
    assign h_z = lin_hidden[2*CHANNELS-1:CHANNELS];
    assign h_n = lin_hidden[3*CHANNELS-1:2*CHANNELS];


    //////////////////////////////////////
    //      ADDING I_R + H_R - 2 cc     //
    //////////////////////////////////////
    
    logic [PRECISION:0] r_add  [CHANNELS-1:0];
    
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : add_vector_r
            c_addsub_0 add_ir_hr_inst (
                .CLK    ( clk ),
                .A      ( i_r[i] ),
                .B      ( h_r[i] ),
                .S      ( r_add[i] )
            );
        end
    endgenerate
    
    //////////////////////////////////////
    //      ADDING I_Z + H_Z - 2 cc     //
    //////////////////////////////////////
    
    logic [PRECISION:0] z_add  [CHANNELS-1:0];
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : add_vector_z
            c_addsub_0 add_iz_hz_inst (
                .CLK    ( clk ),
                .A      ( i_z[i] ),
                .B      ( h_z[i] ),
                .S      ( z_add[i] )
            );
        end
    endgenerate

    ///////////////////////////////////////////////
    //      GET R VALUE FROM LUT SIGMOID0
    ///////////////////////////////////////////////

    logic [PRECISION-1:0] r  [CHANNELS-1:0];
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : lut_vector_r
            dist_mem_gen_0 lut_sigmoid_r (
                .clk    ( clk ),
                .a      ( r_add[i] ),
                .spo    ( r[i] )
            );
        end
    endgenerate
    
    ///////////////////////////////////////////////
    //      GET Z VALUE FROM LUT SIGMOID1
    ///////////////////////////////////////////////
    
    logic [PRECISION-1:0] z  [CHANNELS-1:0];
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : lut_vector_z
            dist_mem_gen_1 lut_sigmoid_z (
                .clk    ( clk ),
                .a      ( z_add[i] ),
                .spo    ( z[i] )
            );
        end
    endgenerate
    
    
    ///////////////////////////////////////////////
    //  ELEMENT WISE MUL - R (hammard) HN - 1 cc //
    ///////////////////////////////////////////////
    
    logic [PRECISION-1:0] hn_delay  [CHANNELS-1:0];
    
    logic [PRECISION-1:0]       r_hn  [CHANNELS-1:0];
    logic signed [PRECISION:0]  r_signed [CHANNELS-1:0];
    logic signed [PRECISION:0]  h_n_signed [CHANNELS-1:0];
    
    generate
        for (i=0; i<CHANNELS; i++) begin : signed_r
            assign r_signed[i] = {1'b0, r[i]};
        end
    endgenerate
    
    generate
        for (i=0; i<CHANNELS; i++) begin : signed_hn
            assign h_n_signed[i] = {1'b0, hn_delay[i]};
        end
    endgenerate
    
    vector_multiplication #(
        .DIM                ( CHANNELS ),
        .PRECISION          ( PRECISION ),
        .MULTIPLIER         ( 31797212 ),
        .ZERO_POINT_IN_1    ( 0 ),
        .ZERO_POINT_IN_2    ( 133 ),
        .ZERO_POINT_OUT     ( 127 )
    ) vec_mul_r_h_n (
        .clk            ( clk ),
        .reset          ( reset ),
        .vector_1       ( r_signed ),
        .vector_2       ( h_n_signed ),
        .output_vector  ( r_hn )
    );
    
    
    ////////////////////////////////////////////////////
    //      ELEMENT WISE MUL - Z (hammard) H_PREV     //
    ////////////////////////////////////////////////////
    
    logic signed [PRECISION:0] h_prev_delay  [CHANNELS-1:0];
    
    logic [PRECISION-1:0]       z_h  [CHANNELS-1:0];
    logic signed [PRECISION:0]  z_signed [CHANNELS-1:0];
    
    generate
        for (i=0; i<CHANNELS; i++) begin : signed_z
            assign z_signed[i] = {1'b0, z[i]};
        end
    endgenerate
    
    vector_multiplication #(
        .DIM                ( CHANNELS ),
        .PRECISION          ( PRECISION ),
        .MULTIPLIER         ( 27253982 ),
        .ZERO_POINT_IN_1    ( 0 ),
        .ZERO_POINT_IN_2    ( 117 ),
        .ZERO_POINT_OUT     ( 134 )
    ) vec_mul_z_h (
        .clk            ( clk ),
        .reset          ( reset ),
        .vector_1       ( z_signed ),
        .vector_2       ( h_prev_delay ),
        .output_vector  ( z_h )
    );
    
    ////////////////////////////////////
    //  SUBTRACTING Z FROM 1 - 2 cc   //
    ////////////////////////////////////
    
    logic [PRECISION-1:0] z_subb  [CHANNELS-1:0];
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : sub_1_z
            c_addsub_1  sub_1_z_inst (
                .CLK    ( clk ),
                .A      ( 255 ),
                .B      ( z[i] ),
                .S      ( z_subb[i] )
            );
        end
    endgenerate
    
    /////////////////////////////////////////
    //          RESCALE I_N                //
    /////////////////////////////////////////  
    
    logic [PRECISION-1:0]   in_delay  [CHANNELS-1:0];
    logic [PRECISION-1:0]   in_rescale  [CHANNELS-1:0];
    
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : lut_rescale_in
            dist_mem_gen_3 lut_rescale (
                .clk    ( clk ),
                .a      ( in_delay[i] ),
                .spo    ( in_rescale[i] )
            );
        end
    endgenerate
    
    ///////////////////////////////////////////
    //          ADDING I_N TO R_HN           //
    ///////////////////////////////////////////

    logic [PRECISION:0] n_add  [CHANNELS-1:0];
    
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : add_vectors_in_rhn
            c_addsub_0 add_ir_rhn_inst (
                .CLK    ( clk ),
                .A      ( in_rescale[i] ),
                .B      ( r_hn[i] ),
                .S      ( n_add[i] )
            );
        end
    endgenerate

    //////////////////////////////////////////////
    //          GET N VALUE FROM TANH LUT       //
    //////////////////////////////////////////////
    
    logic [PRECISION-1:0] n  [CHANNELS-1:0];
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : lut_vector_n
            dist_mem_gen_2 lut_tanh (
                .clk    ( clk ),
                .a      ( n_add[i] ),
                .spo    ( n[i] )
            );
        end
    endgenerate

    ////////////////////////////////////////////////////
    //      ELEMENT WISE MUL - Z_SUBB (hammard) N     //
    ////////////////////////////////////////////////////
    
    logic [PRECISION-1:0]       z_n  [CHANNELS-1:0];
    logic [PRECISION-1:0]       z_subb_delay  [CHANNELS-1:0];
    logic signed [PRECISION:0]  z_subb_signed [CHANNELS-1:0];
    logic signed [PRECISION:0]  n_signed [CHANNELS-1:0];
    
    generate
        for (i=0; i<CHANNELS; i++) begin : signed_z_subb
            assign z_subb_signed[i] = {1'b0, z_subb_delay[i]};
        end
    endgenerate
    
    generate
        for (i=0; i<CHANNELS; i++) begin : signed_n_signed
            assign n_signed[i] = {1'b0, n[i]};
        end
    endgenerate
    
    vector_multiplication #(
        .DIM                ( CHANNELS ),
        .PRECISION          ( PRECISION ),
        .MULTIPLIER         ( 31427494 ),
        .ZERO_POINT_IN_1    ( 0 ),
        .ZERO_POINT_IN_2    ( 127 ),
        .ZERO_POINT_OUT     ( 115 )
    ) vec_mul_z_n (
        .clk            ( clk ),
        .reset          ( reset ),
        .vector_1       ( z_subb_signed ),
        .vector_2       ( n_signed ),
        .output_vector  ( z_n )
    );

    /////////////////////////////////////////////////
    //     ADDING ZN to ZH - 5 cc????
    ////////////////////////////////////////////////

    logic [PRECISION-1:0] z_h_prev_delay  [CHANNELS-1:0];
    
    logic signed [PRECISION:0]  z_n_signed [CHANNELS-1:0];
    logic signed [PRECISION:0]  z_h_signed [CHANNELS-1:0];
    
    generate
        for (i=0; i<CHANNELS; i++) begin : signed_z_n
            assign z_n_signed[i] = {1'b0, z_n[i]};
        end
    endgenerate
    
    generate
        for (i=0; i<CHANNELS; i++) begin : signed_z_h_prev
            assign z_h_signed[i] = {1'b0, z_h_prev_delay[i]};
        end
    endgenerate
    
    add_vectors_rescale #(
        .DIM                ( CHANNELS ),
        .PRECISION          ( PRECISION ),
        .MULTIPLIER_IN_1    ( 857659136 ),
        .MULTIPLIER_IN_2    ( 33'd2654297599 ),
        .ZERO_POINT_IN_1    ( 115 ),
        .ZERO_POINT_IN_2    ( 134 ),
        .ZERO_POINT_OUT     ( 117 )
        
    ) add_zn_zh (
        .clk                    ( clk ),
        .reset                  ( reset ),
        .input_vector_1         ( z_n_signed ),
        .input_vector_2         ( z_h_signed ),
        .output_vector          ( h_new )
    );
    
    always_comb begin
        for (int i = 0; i < CHANNELS; i++) begin
            h_new_mem[i*PRECISION +: PRECISION] = h_new[i];
        end
    end
    
    //////////////////////////////////////
    //              DELAYS              //
    /////////////////////////////////////
    
    delay_module #(
        .N        ( 1 ),
        .DELAY    ( 16 )
    ) delay_event (
        .clk   ( clk       ),
        .idata ( is_valid  ),
        .odata ( reg_valid )
    );
    
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : delays_h_n
            delay_module #(
                .N        ( 8 ),
                .DELAY    ( 3 )
            ) delay_h_n_module (
                .clk   ( clk ),
                .idata ( h_n[i] ),
                .odata ( hn_delay[i] )
            );
        end
    endgenerate
    

    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : delays_h_prev
            delay_module #(
                .N        ( 9 ),
                .DELAY    ( 5 )
            ) delay_h_prev_module (
                .clk   ( clk ),
                .idata ( h_prev_signed[i] ),
                .odata ( h_prev_delay[i] )
            );
        end
    endgenerate
    
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : delays_in
            delay_module #(
                .N        ( 8 ),
                .DELAY    ( 3  )    //SET DELAY ACCORDING TO LATENCY
            ) delay_in_module (
                .clk   ( clk ),
                .idata ( i_n[i] ),
                .odata ( in_delay[i] )
            );
        end
    endgenerate
    
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : sub_z_delay
            delay_module #(
                .N        ( 8 ),
                .DELAY    ( 2 )    //SET DELAY ACCORDING TO LATENCY
            ) delay_in_module (
                .clk   ( clk ),
                .idata ( z_subb[i] ),
                .odata ( z_subb_delay[i] )
            );
        end
    endgenerate
    
    generate
        for (i = 0; i < CHANNELS; i = i + 1) begin : add_z_h_prev_zn
            delay_module #(
                .N        ( 8 ),
                .DELAY    ( 4 )    //SET DELAY ACCORDING TO LATENCY
            ) delay_in_module (
                .clk   ( clk ),
                .idata ( z_h[i] ),
                .odata ( z_h_prev_delay[i] )
            );
        end
    endgenerate

endmodule