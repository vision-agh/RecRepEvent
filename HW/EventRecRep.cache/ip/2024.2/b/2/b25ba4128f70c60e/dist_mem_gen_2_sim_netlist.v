// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Wed Apr 16 09:26:33 2025
// Host        : Imperator running 64-bit Ubuntu 24.04.2 LTS
// Command     : write_verilog -force -mode funcsim -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
//               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ dist_mem_gen_2_sim_netlist.v
// Design      : dist_mem_gen_2
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xczu7ev-ffvc1156-2-e
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "dist_mem_gen_2,dist_mem_gen_v8_0_15,{}" *) (* downgradeipidentifiedwarnings = "yes" *) (* x_core_info = "dist_mem_gen_v8_0_15,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix
   (a,
    clk,
    spo);
  input [8:0]a;
  input clk;
  output [7:0]spo;

  wire [8:0]a;
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
  (* c_addr_width = "9" *) 
  (* c_default_data = "0" *) 
  (* c_depth = "512" *) 
  (* c_elaboration_dir = "./" *) 
  (* c_has_clk = "1" *) 
  (* c_has_qspo = "0" *) 
  (* c_has_qspo_ce = "0" *) 
  (* c_has_qspo_rst = "0" *) 
  (* c_has_qspo_srst = "0" *) 
  (* c_has_spo = "1" *) 
  (* c_mem_init_file = "dist_mem_gen_2.mif" *) 
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
        .dpra({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
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
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 20896)
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
