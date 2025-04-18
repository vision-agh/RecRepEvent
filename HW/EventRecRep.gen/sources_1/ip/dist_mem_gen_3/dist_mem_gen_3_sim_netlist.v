// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Apr 18 21:12:15 2025
// Host        : Imperator running 64-bit Ubuntu 24.04.2 LTS
// Command     : write_verilog -force -mode funcsim
//               /home/imperator/Code/RecRepEvent/HW/EventRecRep.gen/sources_1/ip/dist_mem_gen_3/dist_mem_gen_3_sim_netlist.v
// Design      : dist_mem_gen_3
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xczu7ev-ffvc1156-2-e
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "dist_mem_gen_3,dist_mem_gen_v8_0_15,{}" *) (* downgradeipidentifiedwarnings = "yes" *) (* x_core_info = "dist_mem_gen_v8_0_15,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module dist_mem_gen_3
   (a,
    clk,
    spo);
  input [7:0]a;
  input clk;
  output [7:0]spo;

  wire [7:0]a;
  wire clk;
  wire [7:0]spo;
  wire [7:0]NLW_U0_dpo_UNCONNECTED;
  wire [7:0]NLW_U0_qdpo_UNCONNECTED;
  wire [7:0]NLW_U0_qspo_UNCONNECTED;

  (* C_FAMILY = "zynquplus" *) 
  (* C_HAS_D = "0" *) 
  (* C_HAS_DPO = "0" *) 
  (* C_HAS_DPRA = "0" *) 
  (* C_HAS_I_CE = "0" *) 
  (* C_HAS_QDPO = "0" *) 
  (* C_HAS_QDPO_CE = "0" *) 
  (* C_HAS_QDPO_CLK = "0" *) 
  (* C_HAS_QDPO_RST = "0" *) 
  (* C_HAS_QDPO_SRST = "0" *) 
  (* C_HAS_WE = "0" *) 
  (* C_MEM_TYPE = "0" *) 
  (* C_PIPELINE_STAGES = "0" *) 
  (* C_QCE_JOINED = "0" *) 
  (* C_QUALIFY_WE = "0" *) 
  (* C_REG_DPRA_INPUT = "0" *) 
  (* c_addr_width = "8" *) 
  (* c_default_data = "0" *) 
  (* c_depth = "256" *) 
  (* c_elaboration_dir = "./" *) 
  (* c_has_clk = "1" *) 
  (* c_has_qspo = "0" *) 
  (* c_has_qspo_ce = "0" *) 
  (* c_has_qspo_rst = "0" *) 
  (* c_has_qspo_srst = "0" *) 
  (* c_has_spo = "1" *) 
  (* c_mem_init_file = "dist_mem_gen_3.mif" *) 
  (* c_parser_type = "1" *) 
  (* c_read_mif = "1" *) 
  (* c_reg_a_d_inputs = "1" *) 
  (* c_sync_enable = "1" *) 
  (* c_width = "8" *) 
  (* is_du_within_envelope = "true" *) 
  dist_mem_gen_3_dist_mem_gen_v8_0_15 U0
       (.a(a),
        .clk(clk),
        .d({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .dpo(NLW_U0_dpo_UNCONNECTED[7:0]),
        .dpra({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .i_ce(1'b1),
        .qdpo(NLW_U0_qdpo_UNCONNECTED[7:0]),
        .qdpo_ce(1'b1),
        .qdpo_clk(1'b0),
        .qdpo_rst(1'b0),
        .qdpo_srst(1'b0),
        .qspo(NLW_U0_qspo_UNCONNECTED[7:0]),
        .qspo_ce(1'b1),
        .qspo_rst(1'b0),
        .qspo_srst(1'b0),
        .spo(spo),
        .we(1'b0));
endmodule
`pragma protect begin_protected
`pragma protect version = 1
`pragma protect encrypt_agent = "XILINX"
`pragma protect encrypt_agent_info = "Xilinx Encryption Tool 2024.2"
`pragma protect key_keyowner="Synopsys", key_keyname="SNPS-VCS-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
QNtvE2CtVtCLMRpkLokNuGcllLrkXv1+lIa0yP+/1RuZi9oRL2LImNinlDdnYjplAMhYGl9XEctd
Vgvu47P/zXualZ0bLjhzg/aX77+nnnsogQe5QvbfAjNzC3kVXEI0ayxzBG4YOTRrN1s80vc8cnmF
luLtHMoVFTLV/Qa2ImY=

`pragma protect key_keyowner="Aldec", key_keyname="ALDEC15_001", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
EsS/DTw31dJ3RxUR5I9m01nWTF9kOWw8OcKsdprEfjEtZHh8rL+clyuQ4Lub9TZ7hvhtvdAM/yG2
lHSWYAypt558DVmIWXAhMktEhUX1YZsVivVh2JCr5Zwpv2M2Zgpbj/u5CVPA/hOLi6zvyslFmuPT
3xQPUx1QbvKJFKaAEIM90X8jh7Ib4ReOb/HDKfMoZpehJ5DROEpNQIMJc3A4xj1YwMvpm1sbGrQ9
BccqTOlUp26MHJqGfaW8k2zVxZWE6EBhTUryObnY6BMG0+oaqvkvNPmIC6DTQ67YDUMEXnF+a9tK
dg2+K6uDt3ntGg0h1nCEXfZlWGaD012YfXAM6A==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VELOCE-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
kvhusES6uczMSZDYIHCLM9JA6G0Ue0G1DJVuqxCaLmNC4FL9fKAJMgGDE9v7dXmHVzr0haCW3l6u
fhPWIv8RS4pQCBUcJ5SbLScY+RrgDxYCV6FAJc1MTcJeCsJL8Set1C2a1I9UMp9tKlbjsU4y7Fzw
zPrhH61jVSiSUHNOKA0=

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VERIF-SIM-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
inENfe4FJDUWkXD2uskdmhcUKJs5FlDsfQejbIY+Kj3b3+VupqpRsdsVCOZR1iuI1YeUk/pEmpFO
UVwlLds+Gv462s6vzEryKKTUt5LwBWICjIOS1oipeNyRytMUgOzfB1ebbqE/qtSguwFkpuh+PM0R
G4XIc/yb+4ekv06FdCTwRsr1PPQhBN3dvlbmthDh+DlNg+451903inyVrElARA1sfsDyxLE5NXc6
aAGx9EnIlCMIyA3b+EHfUR2fpIJRv2WI8pXHp3BMkDFpFleQncgMRZawXlA8LyRTlEkQY9bWZloL
7c/PR9IocOI7Hgze6It+qoa1TMD4JYI1l4aiag==

`pragma protect key_keyowner="Real Intent", key_keyname="RI-RSA-KEY-1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
fAUq8XfjyOSmYpeEsqFovnm9wo6MN+HSQMUxVb+8Tk7JxMZRzjIUavsTcxzCBGwV0cn9mhAROckY
ZL/S5ZCe9dNczc2GPLM/tKq0J00RTrg1/CnF83vDPBsTqPnubB8Ezocd9Y4mc7fpAqIK37xNhKWw
ZtaqQR5unbDfx1VXgu38tZOtw5xBdYDxXwTpiYO1CpppjaKYlkNgjn14fXojbu1WgOi5te1YIyMq
6VdV+a4vHs8ld5/Bzj1aYQpksd9HSmjhlvRbudp+Wzyeg/JQ/n/rVuL17spv9fRhRYzsYUmVpwVP
XHq7AEGPUxUsCR/hAlOZl74Y6CHWvMLJ1K3BJg==

`pragma protect key_keyowner="Xilinx", key_keyname="xilinxt_2023_11", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
viS1PaTaQyAmM0YlLlhPnaKoLyjFUdvV9D3cAsx0LAJDMTKtprr3n6TaJCVxoagTVaFkhc+XNiEY
3MerOEmTEA8PDu+i838+6oE2kSm2AaB5Ay8C2jAKzSTy+G+c1GMbYEnjHq5MNg4E2Jm1PtfCE0SP
QGvgfwSsSN87MBSHyAJsvK4mamZrAuhZWmEqZhT1QZb9hlijud9Tb/RRYib+D2mMfCdXddMWNqaP
NdLMgVMC4ANzo+0rYHrh4UTOeR7KaJJKQy/Mi4p71lRnZoN40Ii89TuZ3bJ7/8T+K5nbcuKUwuyJ
XJ0J8KclRbK50ihLP0KpXo2pm5KlA5/teSmkuQ==

`pragma protect key_keyowner="Metrics Technologies Inc.", key_keyname="DSim", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
E8Onz0icX0rH7d0giRecpH5/0LgSB945u0ZnuCpRBtsZWEDByWN4u/K25fQewqo49MlWTepnY6ih
PjoebsOpWNJfQPSgg1L0bPoxnmCScTQ3hQ5ihl7i5h3/1No6o6xyodzFdjfqaRjKZ1DO+MIkhv3p
Wud7PyjZ4Ms0FokgGRpYVWxKLCxoXBRSPbQIkSpW+K3g2YqKIKHjJgVcppXw0sCHzYPC/bkyQmjZ
8k8SsdLV0mSwakgdCD3RujY1sYU6IkirOvpJKHMqG/1D2ArNZwAHXLiJkN/DXZOTzXYo4fKSsO8t
aDIi9/VhLVFit4O+eoScusBihpNtrS8HEIm58w==

`pragma protect key_keyowner="Atrenta", key_keyname="ATR-SG-RSA-1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=384)
`pragma protect key_block
ucQchZNK5CXwhtcYBqqQo6DsBOn9eqPg9ol14ONJC8GgTGsYkXtBkLlTv9aOasMyBGKN6enj6sP+
s7C6NxtZw3YAebGfUqSi+R6H+puN46oekTmqVotJkXK/WUX7xc0M0TOcPeYC4XQrd9sz+skEsLch
WsFM9dm84HZ+mMle+By4OEV4LNHaptuAVTu3rrWiJBWidv754MkRpqk8volWGFKpMNLErMvOqMxG
F9s6Y8D2qI/Pj2ETd4xhrNxZ0rhgvZTwTnC+XVhYW76Sok0WNEyVVoIGWQpv3gKNjFII+klapSH7
MN6zCshLHtEpCoorA2TnPgEvygMo5sSLKaxQ5iReBX8bWyzYNdjmt/5qugSuwuMrQzq5lBIWyWRh
zgdZI0LLSMDwhJEpZn9+bRPoTPsjLDeIj0Z6rzMR4MT+giSf9DYoa+zPlnEeffzfWtay5W6s6cDb
xpf3cEtSFsYrgff3SGvHmmFRMQ8z641lLCvKuBP04YULFfd+A48W1oW3

`pragma protect key_keyowner="Cadence Design Systems.", key_keyname="CDS_RSA_KEY_VER_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
CAJIQgg4LFZ+P0oHwSwu+iEMgGfaKcnQZQrsU3X2LtjDX7mkLYSyP1DUS22lEdlVm1PDDG0M+DN6
j3z4HYyqTBYo06Nu2v5gQs2KNzvE2EmfRlSmtFj784qfv/hbCjRwM1BgSi9pEpRb1fsUXbi2TgrD
QdHcVyRTJGmyva1IFxM6fw0kV59++vjpI8Sv/3nYnkTu4fTFTyXJbpbxlavxYFh7EiLpwnsd3254
xio+kbN3pFIrRdBfD0hk41SQW4Wv69/PSD7vVZ1FlVdcf4z/a7YBNFxpE22bZrKmmfaZOy2H7HSC
PwSIe+298Q8AGwn8ua/D0TLVLS62+/vv8+vpaQ==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 11088)
`pragma protect data_block
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
`pragma protect end_protected
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;
    parameter GRES_WIDTH = 10000;
    parameter GRES_START = 10000;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    wire GRESTORE;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;
    reg GRESTORE_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;
    assign (strong1, weak0) GRESTORE = GRESTORE_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

    initial begin 
	GRESTORE_int = 1'b0;
	#(GRES_START);
	GRESTORE_int = 1'b1;
	#(GRES_WIDTH);
	GRESTORE_int = 1'b0;
    end

endmodule
`endif
