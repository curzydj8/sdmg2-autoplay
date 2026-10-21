"""测试C++逻辑模块"""
import ctypes
import os

lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'libgamelogic.so'))

lib.flow_create.restype = ctypes.c_void_p
lib.flow_destroy.argtypes = [ctypes.c_void_p]
lib.flow_check_topup.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.flow_check_topup.restype = ctypes.c_int
lib.flow_should_start.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.flow_should_start.restype = ctypes.c_int
lib.flow_get_target.argtypes = [ctypes.c_void_p]
lib.flow_get_target.restype = ctypes.c_int

flow = lib.flow_create()

# 测试
assert lib.flow_check_topup(flow, 0) == 1
assert lib.flow_check_topup(flow, 10) == 1
assert lib.flow_check_topup(flow, 11) == 0
print("✅ check_topup 通过")

assert lib.flow_should_start(flow, 10) == 1
assert lib.flow_should_start(flow, 9) == 0
print("✅ should_start 通过")

assert lib.flow_get_target(flow) == 10
print("✅ get_target 通过")

lib.flow_destroy(flow)
print("\nC++逻辑模块测试全过！")
