# from copy import deepcopy
#
# import torch
# from nobuco.util import collect_recursively, set_torch_tensor_id, get_torch_tensor_identifier
#
# from nobuco.trace.trace import Tracer


# class TracingTensor(torch.Tensor):
#     def __init__(self, tensor, metadata=None):
#         super.__init__()
#         self._t = tensor
#         self._metadata = metadata
#
#     def __repr__(self):
#         return f'Metadata:\n{self._metadata}\n\ndata:\n{self._t}'
#
#     @classmethod
#     def __torch_function__(cls, func, types, args=(), kwargs=None):
#         if kwargs is None:
#             kwargs = {}
#
#         # print('!!!1', dir(func))
#         # print('!!!2', func.__qualname__)
#
#         if hasattr(func, '__objclass__'):
#             op_cls_name = func.__objclass__.__name__
#         elif hasattr(func, '__module__'):
#             op_cls_name = func.__module__
#         else:
#             raise Exception()
#         print('!!!', op_cls_name, func.__qualname__)
#
#         args, kwargs = unwrap_torch_tensors_recursively((args, kwargs))
#         outputs = Tracer.tracing_tensor_op(super(), func, types, op_cls_name, None, *args, **kwargs)
#         outputs = wrap_torch_tensors_recursively(outputs)
#         return outputs
#
#
# def wrap_torch_tensors_recursively(obj, annotate=True):
#     collected = collect_recursively(obj, torch.Tensor)
#
#     def replace_func(obj):
#         if obj.is_leaf:
#             wrapped = obj.as_subclass(TracingTensor)
#             if annotate:
#                 set_torch_tensor_id(wrapped, get_torch_tensor_identifier(obj))
#             return wrapped
#         else:
#             return obj
#
#     replace_dict = {id(c): replace_func(c) for c in collected}
#     return deepcopy(obj, memo=replace_dict)
#
#
# def unwrap_torch_tensors_recursively(obj, annotate=True):
#     collected = collect_recursively(obj, TracingTensor)
#
#     def replace_func(obj):
#         # if obj.is_leaf:
#             wrapped = obj.as_subclass(torch.Tensor)
#             if annotate:
#                 set_torch_tensor_id(wrapped, get_torch_tensor_identifier(obj))
#             return wrapped
#         # else:
#         #     return obj
#
#     replace_dict = {id(c): replace_func(c) for c in collected}
#     return deepcopy(obj, memo=replace_dict)