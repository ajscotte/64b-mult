#=========================================================================
# IntMulFL_test
#=========================================================================

import pytest
import random
import math

random.seed(0xdeadbeef)

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

from lab1_imul.IntMulFL   import IntMulFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, imul, src_msgs, sink_msgs,
                src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src  = TestSource ( Bits(64), src_msgs,  src_delay  )
    s.imul = imul
    s.sink = TestSink   ( Bits(32), sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.imul.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.imul = TranslationTool( s.imul )

    # Connect

    s.connect( s.src.out,  s.imul.req  )
    s.connect( s.imul.resp, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.imul.line_trace()  + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def req( a, b ):
  msg = Bits( 64 )
  msg[32:64] = Bits( 32, a, trunc=True )
  msg[ 0:32] = Bits( 32, b, trunc=True )
  return msg

def resp( a ):
  return Bits( 32, a, trunc=True )

#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------

small_pos_pos_msgs = [
  req(  2,  3 ), resp(   6 ),
  req(  4,  5 ), resp(  20 ),
  req(  3,  4 ), resp(  12 ),
  req( 10, 13 ), resp( 130 ),
  req(  8,  7 ), resp(  56 ),
]

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional lists of request/response messages to create
# additional directed and random test cases.
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

zero_one_neg_one_msgs = [
  req(  0,   1 ), resp(   0 ),
  req(  0,   0 ), resp(   0 ),
  req(  0,  -1 ), resp(   0 ),
  req(  1,   1 ), resp(   1 ),
  req(  1,   0 ), resp(   0 ),
  req(  1,  -1 ), resp(  -1 ),
  req( -1,  -1 ), resp(   1 ),
  req( -1,   0 ), resp(   0 ),
]

#----------------------------------------------------------------------
# Test Case: Small negative numbers x small positive numbers
#----------------------------------------------------------------------

small_neg_pos_msgs = [
  req(  -2,  3 ), resp(   -6 ),
  req(  -4,  5 ), resp(  -20 ),
  req(  -3,  4 ), resp(  -12 ),
  req( -10, 13 ), resp( -130 ),
  req(  -8,  7 ), resp(  -56 ),
]

#----------------------------------------------------------------------
# Test Case: Small positive numbers x small negative numbers
#----------------------------------------------------------------------

small_pos_neg_msgs = [
  req(  2,  -3 ), resp(   -6 ),
  req(  4,  -5 ), resp(  -20 ),
  req(  3,  -4 ), resp(  -12 ),
  req( 10, -13 ), resp( -130 ),
  req(  8,  -7 ), resp(  -56 ),
]

#----------------------------------------------------------------------
# Test Case: Small negative numbers x small negative numbers
#----------------------------------------------------------------------

small_neg_neg_msgs = [
  req(  -2,  -3 ), resp(   6 ),
  req(  -4,  -5 ), resp(  20 ),
  req(  -3,  -4 ), resp(  12 ),
  req( -10, -13 ), resp( 130 ),
  req(  -8,  -7 ), resp(  56 ),
]

#----------------------------------------------------------------------
# Test Case: Large positive numbers x large positive numbers
#----------------------------------------------------------------------

large_pos_pos_msgs = [
  req(    50,  112 ), resp(   5600 ),
  req(   145,  342 ), resp(  49590 ),
  req(  1234,  123 ), resp(  151782 ),
  req(    34, 4568 ), resp( 155312 ),
  req(  10342,  13 ), resp(  134446 ),
  req(  2147483647,  1 ), resp(  2147483647 ),
  req( 1, 2147483647 ), resp(  2147483647 ),
  req(  10000, 100000 ), resp(  1000000000 ),
]

#----------------------------------------------------------------------
# Test Case: Large positive numbers x large negative numbers
#----------------------------------------------------------------------

large_pos_neg_msgs = [
  req(    50,  -112 ), resp(   -5600 ),
  req(   145,  -342 ), resp(  -49590 ),
  req(  1234,  -123 ), resp(  -151782 ),
  req(    34, -4568 ), resp( -155312 ),
  req(  10342,  -13 ), resp(  -134446 ),
  req(  -2147483647,  1 ), resp(  -2147483647 ),
  req(  1, -2147483647 ), resp(  -2147483647 ),
  req(  10000, -100000 ), resp(  -1000000000 ),
]

#----------------------------------------------------------------------
# Test Case: Large positive numbers x large negative numbers
#----------------------------------------------------------------------

large_neg_pos_msgs = [
  req(    -50,  112 ), resp(   -5600 ),
  req(   -145,  342 ), resp(  -49590 ),
  req(  -1234,  123 ), resp(  -151782 ),
  req(    -34, 4568 ), resp( -155312 ),
  req(  -10342,  13 ), resp(  -134446 ),
  req(  -10000, 100000 ), resp(  -1000000000 ),
  
  
]

#----------------------------------------------------------------------
# Test Case: Large negative numbers x large negative numbers
#----------------------------------------------------------------------

large_neg_neg_msgs = [
  req(    -50,  -112 ), resp(   5600 ),
  req(   -145,  -342 ), resp(  49590 ),
  req(  -1234,  -123 ), resp(  151782 ),
  req(    -34, -4568 ), resp( 155312 ),
  req(  -10342,  -13 ), resp(  134446 ),
  req(  -10000, -100000 ), resp(  1000000000 ),
]
#----------------------------------------------------------------------
# Test Case: low order bits
#----------------------------------------------------------------------
low_order_bits = [
  req(    131072,  64 ), resp(   8388608 ),
  req(   64,  131072 ), resp(  8388608 ),
  req(  1,  536870912 ), resp(  536870912 ),
  req(536870912, 1 ), resp(  536870912 ),
]
#----------------------------------------------------------------------
# Test Case: middle order bits
#----------------------------------------------------------------------
middle_order_bits = [
  req(    67,  7687 ), resp(   515029 ),
  req( 7687, 67 ), resp(   515029 ),
  req(  5,  16515079 ), resp( 82575395  ),
  req(  16515079, 5 ), resp( 82575395  ),
]
#----------------------------------------------------------------------
# Test Case: sparse zeros
#----------------------------------------------------------------------
sparse_zeros = [
  req(    76,  33825 ), resp(   2570700 ),
  req( 33825, 76 ), resp(   2570700 ),
  req(  1296,  67860 ), resp(  87946560 ),
  req( 67860, 1296 ), resp(  87946560 ),
]
#----------------------------------------------------------------------
# Test Case: Dense ones
#----------------------------------------------------------------------
dense_ones = [
  req(    2031,  128635 ), resp(  261257685  ),
  req( 128635, 2031 ), resp(  261257685  ),
  req(  94,  24573 ), resp(  2309862 ),
  req( 24573, 94 ), resp(  2309862 ),
]
#----------------------------------------------------------------------
# Test Case: random small
#----------------------------------------------------------------------
random_small_test = []
for i in xrange(50):
  a = random.randint(0,100)
  b = random.randint(0,100)
  random_small_test.extend([req( a, b ), resp(  a*b )])
#----------------------------------------------------------------------
# Test Case: random large
#----------------------------------------------------------------------
random_large_test = []
for i in xrange(50):
  a = random.randint(0,46340)
  b = random.randint(-45000,46340)
  random_large_test.extend([req( a, b ), resp(  a*b )])
#----------------------------------------------------------------------
# Test Case: random lo mask
#----------------------------------------------------------------------
random_lo_mask_test = []
for i in xrange(50):
  e = random.randint(20, 30)
  a = random.randint(1, 9)
  b = 1073741824 + math.pow(2, e)
  random_lo_mask_test.extend([req( a, b ), resp(  a*b )])
#----------------------------------------------------------------------
# Test Case: random lo hi mask
#----------------------------------------------------------------------
random_lohi_mask_test = []
for i in xrange(50):
  e = random.randint(10, 15)
  f = random.randint(10, 15)
  a = random.randint(1, 200)
  b = 0 + math.pow(2, e) + math.pow(2,f)
  random_lohi_mask_test.extend([req( a, b ), resp(  a*b )])
#----------------------------------------------------------------------
# Test Case: random hi mask
#----------------------------------------------------------------------
random_hi_mask_test = []
for i in xrange(50):
  a = random.randint(1, 15)
  b = random.randint(1,15)
  random_hi_mask_test.extend([req( a, b ), resp(  a*b )])
 #----------------------------------------------------------------------
# Test Case: random sparse
#---------------------------------------------------------------------- 
random_sparse_test = []
for i in xrange(50):
  acc = 0 
  for c in range(6):
    power = random.randint(0, 25)
    acc = acc + math.pow(2, power)
  c = random.randint(0, 300)
  random_sparse_test.extend([req( c, acc ), resp(  c*acc )])
#----------------------------------------------------------------------
# Test Case: Random dense
#----------------------------------------------------------------------
random_dense_test = []
for i in xrange(50):
  acc = 0 
  for c in range(20):
    power = random.randint(0, 25)
    acc = acc + math.pow(2, power)
  c = random.randint(0, 300)
  random_dense_test.extend([req( acc, c ), resp(  c*acc )])

test_case_table = mk_test_case_table([
  (                      "msgs                 src_delay sink_delay"),
  [ "small_pos_pos",     small_pos_pos_msgs,   0,        0          ],
  [ "zero_one_neg_one_msgs",     zero_one_neg_one_msgs,   20,        40          ],
  [ "small_neg_pos_msgs",     small_neg_pos_msgs,   40,        20          ],
  [ "small_pos_neg_msgs",     small_pos_neg_msgs,   0,        0          ],
  [ "small_neg_neg_msgs",     small_neg_neg_msgs,   15,        30          ],
  [ "large_pos_pos_msgs",     large_pos_pos_msgs,   50,        50          ],
  [ "large_pos_neg_msgs",     large_pos_neg_msgs,   100,        0          ],
  [ "large_neg_pos_msgs",     large_neg_pos_msgs,   0,        100          ],
  [ "large_neg_neg_msgs",     large_neg_neg_msgs,   50,        20          ], 
  [ "low_order_bits",         low_order_bits,       20,        40          ], 
  [ "middle_order_bits",      middle_order_bits,    20,        40          ], 
  [ "sparse_zeros",           sparse_zeros,         20,        40          ], 
  [ "dense_ones",             dense_ones,           20,        40          ], 
  [ "random_small",           random_small_test,    0,        0          ], 
  [ "random_large_test",      random_large_test,    20,        40          ], 
  [ "random_lohi_mask_test",  random_lohi_mask_test,   20,        40          ], 
  [ "random_hi_mask_test",    random_hi_mask_test,   20,        40          ], 
  [ "dense_sparse_test",      random_sparse_test,  20,        40          ], 
  [ "dense_dense_test",       random_dense_test,   20,        40          ], 

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to leverage the additional lists
  # of request/response messages defined above, but also to test
  # different source/sink random delays.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( IntMulFL(),
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

