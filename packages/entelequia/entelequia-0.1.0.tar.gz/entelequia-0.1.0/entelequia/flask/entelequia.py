# from __future__ import annotations

# from typing import Any

# from flask import Flask

# from entelequia.system.module import Module
# from entelequia.system.system import GenericSystem
# from entelequia.system.system_interface import GenericSystemInterface


# class Entelequia(Flask):
#     def __init__(self, *args: Any, modules: set[Module], **kwargs: Any):
#         self.modules: dict[str, Module] = {
#             module.interface.accessor: module for module in modules
#         }
#         for accessor, module in self.modules.items():
#             setattr(self, accessor, module.system)
#         super().__init__(*args, **kwargs)

#     def register_module(self, module: Module) -> None:
#         self.modules[module.interface.accessor] = module

#     def implements(self, interface: GenericSystemInterface) -> GenericSystem:
#         return self.__system_named(
#             interface.accessor,
#             not_found=SystemError(
#                 f"No System implements '{interface.accessor}'."
#             ),
#         )

#     def __system_named(
#         self,
#         system_name: str,
#         not_found: Exception = SystemError(
#             "No System called by the requested name."
#         ),
#     ) -> GenericSystem:
#         try:
#             return self.modules[system_name].system
#         except KeyError:
#             raise not_found
