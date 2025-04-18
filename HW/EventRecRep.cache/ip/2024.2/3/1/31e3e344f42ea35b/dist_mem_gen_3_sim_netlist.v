// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Apr 18 21:12:15 2025
// Host        : Imperator running 64-bit Ubuntu 24.04.2 LTS
// Command     : write_verilog -force -mode funcsim -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
//               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ dist_mem_gen_3_sim_netlist.v
// Design      : dist_mem_gen_3
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xczu7ev-ffvc1156-2-e
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "dist_mem_gen_3,dist_mem_gen_v8_0_15,{}" *) (* downgradeipidentifiedwarnings = "yes" *) (* x_core_info = "dist_mem_gen_v8_0_15,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix
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
  decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_dist_mem_gen_v8_0_15 U0
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
