//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

`ifndef LAB1_IMUL_INT_MUL_BASE_V
`define LAB1_IMUL_INT_MUL_BASE_V

`include "vc/trace.v"

`include "vc/arithmetic.v"
`include "vc/regs.v"
`include "vc/muxes.v"

// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// Data path module
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module data_path
(
  //defining all inputs and outputs to system
  input  logic         clk, 
  input  logic         reset,
  input  logic         a_mux_sel,
  input  logic         b_mux_sel,
  input  logic         result_mux_sel,
  input  logic         add_mux_sel,
  input  logic         result_en,
  input  logic  [63:0] req_msg,

  output logic         b_lsb,
  output logic  [31:0] resp_msg
);
  // all local variables/wires
  logic           [31:0] a_mux_out;
  logic           [31:0] b_mux_out;  
  logic           [31:0] a_reg_out;
  logic           [31:0] result_mux_out; 
  logic           [31:0] add_mux_out;
  logic           [31:0] b_reg_out;
  logic           [31:0] result_reg_out;
  logic           [31:0] left_shift_out;
  logic           [31:0] right_shift_out;
  logic           [31:0] adder_out;
  logic           [31:0] req_msg_a =  req_msg[63:32];
  logic           [31:0] req_msg_b =  req_msg[31:0];
// mux for integer a path
//accepts a new value or sends current value through 
//path A
//sends result to register A
  vc_Mux2 #(32) a_mux(
    .in0  ( left_shift_out ),
    .in1  ( req_msg_a ),
    .sel  ( a_mux_sel ),
    .out  ( a_mux_out )
    );
//mux for integer b path
//accepts a new value or sends current value through 
//path B
// sends result to register b
  vc_Mux2 #(32) b_mux(
    .in0  ( right_shift_out ),
    .in1  ( req_msg_b ),
    .sel  ( b_mux_sel ),
    .out  ( b_mux_out)
    );
//mux that determines to keep the value in the datapath or reset to zero
//sends value to result register
  vc_Mux2 #(32) result_mux(
    .in0  ( add_mux_out ), 
    .in1  ( 32'b0 ),
    .sel  ( result_mux_sel ),
    .out  ( result_mux_out )
    );
//mux that determines to take the value from alu or result register
//sends results back through result path
  vc_Mux2 #(32) add_mux(
    .in0  ( adder_out ),
    .in1  ( result_reg_out ),
    .sel  ( add_mux_sel ),
    .out  ( add_mux_out )
    );
// stores the current value in path A
//sends value to left shifter and ALU
  vc_ResetReg #(32) a_reg(
    .clk( clk ),
    .d( a_mux_out ),
    .q( a_reg_out ),
    .reset( reset )
    );
//stores the current vlue in path B
// sends value to right sifter
  vc_ResetReg #(32) b_reg(
    .clk( clk ),
    .d( b_mux_out ),
    .q( b_reg_out ),
    .reset( reset )
    );
//stores the value being manipulated that will eventully be the answer
//sends value to ALU and output
  vc_EnReg #(32) result_reg(
    .clk( clk ),
    .d( result_mux_out ),
    .en( result_en ),
    .q( result_reg_out ),
    .reset( reset )
    );
// shifts the value in path A one to the left
//sends result back through path A
  vc_LeftLogicalShifter #(32) left_shift(
    .in( a_reg_out ),
    .shamt( 1'b1 ),
    .out( left_shift_out )
    );
// shifts the value in path B one to the right
//sends results back through path B
  vc_RightLogicalShifter #(32) right_shift(
    .in( b_reg_out ),
    .shamt( 1'b1 ),
    .out( right_shift_out )
    );
// Adds the current result and the value in path A
  vc_SimpleAdder #(32) adder(
    .in0( a_reg_out ),
    .in1( result_reg_out ),
    .out( adder_out )
    );
//least significant bit used for choosing ALU value or not
  assign b_lsb = b_reg_out[0];
  
//answer at the end of the calulation 
  assign resp_msg = result_reg_out;

endmodule

// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// Control module
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module control
(
// module input and output data
  input  logic         clk,
  input  logic         reset,
  input  logic         b_lsb,
  input  logic         req_val,
  input  logic         resp_rdy,
  output logic         result_en,
  output logic         a_mux_sel,
  output logic         b_mux_sel,
  output logic         result_mux_sel,
  output logic         add_mux_sel,
  output logic         req_rdy,
  output logic         resp_val
);
// all local variables/wires
  logic   [5:0] counter = 0;
  localparam STATE_IDLE = 2'b0;
  localparam STATE_CALC = 2'b01;
  localparam STATE_DONE = 2'b10;
  logic [1:0] state_reg;
  logic [1:0] Snext;

// defines all controls by the FSM
  task cs
  (
    input logic cs_result_en,
    input logic cs_a_mux_sel,
    input logic cs_b_mux_sel,
    input logic cs_result_mux_sel,
    input logic cs_add_mux_sel,
    input logic cs_req_rdy,
    input logic cs_resp_val
  );
// assigns current data to outputs
  begin
    result_en      = cs_result_en;
    a_mux_sel      = cs_a_mux_sel;
    b_mux_sel      = cs_b_mux_sel;
    result_mux_sel = cs_result_mux_sel;
    add_mux_sel    = cs_add_mux_sel;
    req_rdy        = cs_req_rdy;
    resp_val       = cs_resp_val;
  end
  endtask
  
// defines the value of the counter for shifting operations
//for each state in the FSM
  always@(posedge clk)
  begin
    if (reset) begin
      state_reg <= STATE_IDLE;
      counter <= 0;
    end
    if (state_reg == STATE_CALC)begin
      counter <= counter + 1;
    end
    if (state_reg == STATE_IDLE)begin
      counter <= 0;
    end
      state_reg <= Snext;
  end
  
//defines the outputs for each state
  always_comb begin
    cs(0,1'dx,1'dx,1'dx,1'dx,0,0);
    case ( state_reg )
      STATE_IDLE: begin 
                  cs(1,1,1,1,1'dx,1,0);
                  if (req_val)begin
                    Snext = STATE_CALC;
                  end
                  else begin
                    Snext = STATE_IDLE;
                  end         
      end
      STATE_CALC: begin if ( counter < 32 && b_lsb == 1 ) begin
                    cs(1,0,0,0,0,0,0);
                    Snext = STATE_CALC;
                    end
                  else if ( counter < 32 && b_lsb == 0 )begin
                    cs(1,0,0,0,1,0,0);
                    Snext = STATE_CALC;
                    end
                  else if (counter == 32)begin
                    Snext = STATE_DONE;
                  end 
      end                       
      STATE_DONE: begin 
                  cs(0,1'dx,1'dx,1'dx,1'dx,0,1);
                  if (resp_rdy)begin
                    Snext = STATE_IDLE;
                  end 
                  
      end
      default cs(1'dx,1'dx,1'dx,1'dx,1'dx,1'dx,1'dx) ;
 endcase
 end
endmodule
//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

module lab1_imul_IntMulBaseVRTL
(
  input  logic        clk,
  input  logic        reset,

  input  logic        req_val,
  output logic        req_rdy,
  input  logic [63:0] req_msg,

  output logic        resp_val,
  input  logic        resp_rdy,
  output logic [31:0] resp_msg
);

  logic                b_lsb;
  logic                result_en;
  logic                a_mux_sel;
  logic                b_mux_sel;
  logic                result_mux_sel;
  logic                add_mux_sel;
// includes control module 
  control ctrl(
    .*
    );
// includes data_path module    
  data_path path(
    .*
    );
  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x", req_msg );
    vc_trace.append_val_rdy_str( trace_str, req_val, req_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    // Add additional line tracing using the helper tasks for
    // internal state including the current FSM state.
    // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", resp_msg );
    vc_trace.append_val_rdy_str( trace_str, resp_val, resp_rdy, str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* LAB1_IMUL_INT_MUL_BASE_V */
