"""Jac's Key Elemental Abstractions"""  # 0 1
from __future__ import annotations
from jaclang import jac_blue_import as __jac_import__  # -1 0
import traceback as __jac_traceback__  # -1 0
from jaclang import handle_jac_error as __jac_error__  # -1 0
from enum import Enum as __jac_Enum__, auto as __jac_auto__  # -1 0
from datetime import datetime  # 0 3

from uuid import UUID, uuid4  # 0 4

from jaclang.jac.constant import EdgeDir  # 0 5

__jac_import__(target='impl.memory_impl', base_path=__file__)  # 0 7
from impl.memory_impl import *  # 0 7

__jac_import__(target='impl.exec_ctx_impl', base_path=__file__)  # 0 8
from impl.exec_ctx_impl import *  # 0 8

__jac_import__(target='impl.element_impl', base_path=__file__)  # 0 9
from impl.element_impl import *  # 0 9

__jac_import__(target='impl.arch_impl', base_path=__file__)  # 0 10
from impl.arch_impl import *  # 0 10

class AccessMode(__jac_Enum__):  # 0 13
    READ_ONLY = __jac_auto__()  # 3 4
    READ_WRITE = __jac_auto__()  # 3 4
    PRIVATE = __jac_auto__()  # 3 4

class Memory:  # 0 15
    def __init__(self,  # 0 0
        index = None,      # 0 0
        save_queue = None,      # 0 0
        *args, **kwargs):      # 0 0
        super().__init__(*args, **kwargs)      # 0 0
        self.index = index      # 0 0
        self.save_queue = save_queue      # 0 0
    def get_obj(self,caller_id: UUID, item_id: UUID, override: bool = False) -> Element:  # 0 19
        try:      # 0 19
            ret = self.index.get(item_id)  # 1 6
            if override or (ret.__is_readable(ret is not None and caller_id)):  # 1 7
                return ret  # 1 8
            
        except Exception as e:      # 0 19
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 19
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 19
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 19
            raise e          # 0 19
    
    def has_obj(self,item_id: UUID) -> bool:  # 0 21
        try:      # 0 21
            return item_id in self.index  # 1 14
        except Exception as e:      # 0 21
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 21
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 21
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 21
            raise e          # 0 21
    
    def save_obj(self,caller_id: UUID, item: Element):  # 0 22
        try:      # 0 22
            if item.is_writable(caller_id):  # 1 19
                self.index[item.id] = item  # 1 20
                if item._persist:  # 1 21
                    self.save_obj_list.add(item)  # 1 22
                
            
            self.mem[item.id] = item  # 1 19
            if item._persist:  # 1 26
                self.save_obj_list.add(item)  # 1 27
            
        except Exception as e:      # 0 22
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 22
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 22
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 22
            raise e          # 0 22
    
    def del_obj(self,caller_id: UUID, item: Element):  # 0 23
        try:      # 0 23
            if item.is_writable(caller_id):  # 1 33
                self.index.pop(item.id)  # 1 34
                if item._persist:  # 1 35
                    self.save_obj_list.remove(item)  # 1 36
                
            
        except Exception as e:      # 0 23
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 23
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 23
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 23
            raise e          # 0 23
    
    def get_object_distribution(self,) -> dict:  # 0 26
        try:      # 0 26
            dist = {}  # 1 42
            for i in self.index.keys():  # 1 43
                t = type(self.index[i])  # 1 44
                if t in dist:  # 1 45
                    dist[t] += 1  # 1 46
                
                else:  # 1 48
                    dist[t] = 1  # 1 49      # 1 43
            return dist  # 1 52
        except Exception as e:      # 0 26
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 26
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 26
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 26
            raise e          # 0 26
    
    def get_mem_size(self,) -> float:  # 0 27
        try:      # 0 27
            return (sys.getsizeof(self.index)) / 1024.0  # 1 56
        except Exception as e:      # 0 27
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 27
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 27
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 27
            raise e          # 0 27
    

class ExecutionContext:  # 0 30
    def __init__(self,  # 0 0
        master = None,      # 0 0
        memory = None,      # 0 0
        *args, **kwargs):      # 0 0
        super().__init__(*args, **kwargs)      # 0 0
        self.master = uuid4() if master is None else master      # 0 0
        self.memory = Memory() if memory is None else memory      # 0 0
    def reset(self,):  # 0 34
        try:      # 0 34
            self.__init__()  # 2 13
        except Exception as e:      # 0 34
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 34
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 34
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 34
            raise e          # 0 34
    
    def get_root(self,) -> Node:  # 0 35
        try:      # 0 35
            if type(self.master) == UUID:  # 2 6
                self.master = Master()  # 2 7
            
            return self.master.root_node  # 2 9
        except Exception as e:      # 0 35
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 35
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 35
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 35
            raise e          # 0 35
    

exec_ctx = ExecutionContext()  # 0 38

class ElementMetaData:  # 0 40
    def __init__(self,  # 0 0
        jid = None,      # 0 0
        timestamp = None,      # 0 0
        persist = None,      # 0 0
        access_mode = None,      # 0 0
        rw_access = None,      # 0 0
        ro_access = None,      # 0 0
        owner_id = None,      # 0 0
        mem = None,      # 0 0
        *args, **kwargs):      # 0 0
        super().__init__(*args, **kwargs)      # 0 0
        self.jid = uuid4() if jid is None else jid      # 0 0
        self.timestamp = datetime.now() if timestamp is None else timestamp      # 0 0
        self.persist = False if persist is None else persist      # 0 0
        self.access_mode = AccessMode.PRIVATE if access_mode is None else access_mode      # 0 0
        self.rw_access = set() if rw_access is None else rw_access      # 0 0
        self.ro_access = set() if ro_access is None else ro_access      # 0 0
        self.owner_id = exec_ctx.master if owner_id is None else owner_id      # 0 0
        self.mem = exec_ctx.memory if mem is None else mem      # 0 0

class Element:  # 0 51
    def __init__(self,  # 0 0
        _jinfo = None,      # 0 0
        exec_ctx: ExecutionContext = None,      # 0 0
        *args, **kwargs):      # 0 0
        self._jinfo = ElementMetaData() if _jinfo is None else _jinfo      # 0 0
        self.__jinfo = ExecutionContext(exec_ctx)  # 3 11
    
    def _jac_make_public_ro(self,):  # 0 55
        try:      # 0 55
            self.__jinfo.access_mode = AccessMode.READ_ONLY  # 3 15
        except Exception as e:      # 0 55
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 55
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 55
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 55
            raise e          # 0 55
    
    def _jac_make_public_rw(self,):  # 0 56
        try:      # 0 56
            self.__jinfo.access_mode = AccessMode.READ_WRITE  # 3 19
        except Exception as e:      # 0 56
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 56
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 56
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 56
            raise e          # 0 56
    
    def _jac_make_private(self,):  # 0 57
        try:      # 0 57
            self.__jinfo.access_mode = AccessMode.PRIVATE  # 3 23
        except Exception as e:      # 0 57
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 57
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 57
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 57
            raise e          # 0 57
    
    def _jac_is_public_ro(self,) -> bool:  # 0 58
        try:      # 0 58
            return self.__jinfo.access_mode == AccessMode.READ_ONLY  # 3 27
        except Exception as e:      # 0 58
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 58
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 58
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 58
            raise e          # 0 58
    
    def _jac_is_public_rw(self,) -> bool:  # 0 59
        try:      # 0 59
            return self.__jinfo.access_mode == AccessMode.READ_WRITE  # 3 31
        except Exception as e:      # 0 59
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 59
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 59
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 59
            raise e          # 0 59
    
    def _jac_is_private(self,) -> bool:  # 0 60
        try:      # 0 60
            return self.__jinfo.access_mode == AccessMode.PRIVATE  # 3 35
        except Exception as e:      # 0 60
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 60
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 60
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 60
            raise e          # 0 60
    
    def _jac_is_readable(self,caller_id: UUID) -> bool:  # 0 61
        try:      # 0 61
            return (caller_id == self.owner_id or self.is_public_read() or caller_id in self.ro_access or caller_id in self.rw_access)  # 3 40
        except Exception as e:      # 0 61
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 61
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 61
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 61
            raise e          # 0 61
    
    def _jac_is_writable(self,caller_id: UUID) -> bool:  # 0 62
        try:      # 0 62
            return (caller_id == self.owner_id or self.is_public_write() or caller_id in self.rw_access)  # 3 50
        except Exception as e:      # 0 62
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 62
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 62
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 62
            raise e          # 0 62
    
    def _jac_give_access(self,caller_id: UUID, read_write: bool = False):  # 0 63
        try:      # 0 63
            if read_write:  # 3 59
                self.rw_access.add(caller_id)  # 3 60
            
            else:  # 3 62
                self.ro_access.add(caller_id)  # 3 63
            
        except Exception as e:      # 0 63
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 63
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 63
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 63
            raise e          # 0 63
    
    def _jac_revoke_access(self,caller_id: UUID):  # 0 64
        try:      # 0 64
            self.ro_access.discard(caller_id)  # 3 69
            self.rw_access.discard(caller_id)  # 3 69
        except Exception as e:      # 0 64
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 64
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 64
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 64
            raise e          # 0 64
    

class Object(Element):  # 0 67
    _jac_ds_entry_funcs: list[dict] = []  # 0 68
    _jac_ds_exit_funcs: list[dict] = []  # 0 68
    
    def __init__(self,  # 0 0
        *args, **kwargs):      # 0 0
        super().__init__(*args, **kwargs)      # 0 0
    @classmethod  # 0 71
    def _jac_on_entry(cls: type, triggers: list[type]):  # 0 71
        try:      # 0 71
            def decorator(func: callable) -> callable:  # 3 75
                try:      # 3 75
                    cls._jac_ds_entry_funcs.append({'func': func, 'types': triggers})  # 3 76
                    def wrapper(*args: list, **kwargs: dict) -> callable:  # 3 77
                        try:      # 3 77
                            return func(*args, **kwargs)  # 3 78
                        except Exception as e:      # 3 77
                            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 3 77
                            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 3 77
                            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 3 77
                            raise e          # 3 77
                    return wrapper  # 3 80
                except Exception as e:      # 3 75
                    tb = __jac_traceback__.extract_tb(e.__traceback__)          # 3 75
                    __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 3 75
                    e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 3 75
                    raise e          # 3 75
            return decorator  # 3 82
        except Exception as e:      # 0 71
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 71
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 71
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 71
            raise e          # 0 71
    
    @classmethod  # 0 72
    def _jac_on_exit(cls: type, triggers: list[type]):  # 0 72
        try:      # 0 72
            def decorator(func: callable) -> callable:  # 3 87
                try:      # 3 87
                    cls._jac_ds_exit_funcs.append({'func': func, 'types': triggers})  # 3 88
                    def wrapper(*args: list, **kwargs: dict) -> callable:  # 3 89
                        try:      # 3 89
                            return func(*args, **kwargs)  # 3 90
                        except Exception as e:      # 3 89
                            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 3 89
                            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 3 89
                            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 3 89
                            raise e          # 3 89
                    return wrapper  # 3 92
                except Exception as e:      # 3 87
                    tb = __jac_traceback__.extract_tb(e.__traceback__)          # 3 87
                    __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 3 87
                    e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 3 87
                    raise e          # 3 87
            return decorator  # 3 94
        except Exception as e:      # 0 72
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 72
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 72
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 72
            raise e          # 0 72
    

class Node(Object):  # 0 75
    def __init__(self,  # 0 0
        _jac_edges_ = None,      # 0 0
        *args, **kwargs):      # 0 0
        super().__init__(*args, **kwargs)      # 0 0
        self._jac_edges_ = {EdgeDir.OUT: [], EdgeDir.IN: []} if _jac_edges_ is None else _jac_edges_      # 0 0
    def __call__(self,walk: Walker):  # 0 79
        try:      # 0 79
            if not isinstance(walk, Walker):  # 4 6
                raise TypeError(("Argument must be a Walker instance"))  # 4 7
            
            walk(self)  # 4 6
        except Exception as e:      # 0 79
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 79
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 79
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 79
            raise e          # 0 79
    
    def _jac_connect_node_(self,nd: Node, edg: Edge) -> Node:  # 0 80
        try:      # 0 80
            edg._jac_attach_(self, nd)  # 4 14
            return self  # 4 15
        except Exception as e:      # 0 80
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 80
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 80
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 80
            raise e          # 0 80
    
    def _jac_edges_to_nodes_(self,dir: EdgeDir) -> list[Node]:  # 0 81
        try:      # 0 81
            ret_nodes = []  # 4 20
            if dir in [EdgeDir.OUT, EdgeDir.ANY]:  # 4 21
                for i in self._jac_edges_[EdgeDir.OUT]:  # 4 22
                    ret_nodes.append(i._jac_target_)  # 4 23      # 4 22
            
            elif dir in [EdgeDir.IN, EdgeDir.ANY]:  # 4 25
                for i in self._jac_edges_[EdgeDir.IN]:  # 4 26
                    ret_nodes.append(i._jac_source_)  # 4 27      # 4 26
            
            return ret_nodes  # 4 31
        except Exception as e:      # 0 81
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 81
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 81
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 81
            raise e          # 0 81
    

class Edge(Object):  # 0 84
    def __init__(self,  # 0 0
        _jac_source_ = None,      # 0 0
        _jac_target_ = None,      # 0 0
        _jac_dir_ = None,      # 0 0
        *args, **kwargs):      # 0 0
        super().__init__(*args, **kwargs)      # 0 0
        self._jac_source_ = _jac_source_      # 0 0
        self._jac_target_ = _jac_target_      # 0 0
        self._jac_dir_ = _jac_dir_      # 0 0
    def __call__(self,walk: Walker):  # 0 89
        try:      # 0 89
            if not isinstance(walk, Walker):  # 4 36
                raise TypeError(("Argument must be a Walker instance"))  # 4 37
            
            walk(self._jac_target_)  # 4 36
        except Exception as e:      # 0 89
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 89
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 89
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 89
            raise e          # 0 89
    
    def _jac_apply_dir_(self,dir: EdgeDir) -> Edge:  # 0 90
        try:      # 0 90
            self._jac_dir_ = dir  # 4 44
            return self  # 4 45
        except Exception as e:      # 0 90
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 90
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 90
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 90
            raise e          # 0 90
    
    def _jac_attach_(self,src: Node, trg: Node) -> Edge:  # 0 91
        try:      # 0 91
            if self._jac_dir_ == EdgeDir.IN:  # 4 50
                self._jac_source_ = trg  # 4 51
                self._jac_target_ = src  # 4 51
                src._jac_edges_[EdgeDir.IN].append(self)  # 4 51
                trg._jac_edges_[EdgeDir.OUT].append(self)  # 4 51
            
            else:  # 4 55
                self._jac_source_ = src  # 4 56
                self._jac_target_ = trg  # 4 56
                src._jac_edges_[EdgeDir.OUT].append(self)  # 4 56
                trg._jac_edges_[EdgeDir.IN].append(self)  # 4 56
            
            return self  # 4 62
        except Exception as e:      # 0 91
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 91
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 91
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 91
            raise e          # 0 91
    

class Walker(Object):  # 0 94
    def __init__(self,  # 0 0
        _jac_path_ = None,      # 0 0
        _jac_next_ = None,      # 0 0
        _jac_ignores_ = None,      # 0 0
        _jac_disengaged_ = None,      # 0 0
        *args, **kwargs):      # 0 0
        super().__init__(*args, **kwargs)      # 0 0
        self._jac_path_ = [] if _jac_path_ is None else _jac_path_      # 0 0
        self._jac_next_ = [] if _jac_next_ is None else _jac_next_      # 0 0
        self._jac_ignores_ = [] if _jac_ignores_ is None else _jac_ignores_      # 0 0
        self._jac_disengaged_ = False if _jac_disengaged_ is None else _jac_disengaged_      # 0 0
    def __call__(self,nd: Node):  # 0 100
        try:      # 0 100
            self._jac_path_ = []  # 4 67
            self._jac_next_ = [nd]  # 4 67
            walker_type = self.__class__.__name__  # 4 67
            while len(self._jac_next_):  # 4 70
                nd = self._jac_next_.pop(0)  # 4 71
                node_type = nd.__class__.__name__  # 4 71
                for i in nd._jac_ds_entry_funcs:  # 4 74
                    if i['func'].__qualname__.split(".")[0] == node_type and type(self) in i['types']:  # 4 75
                        i['func'](nd, self)  # 4 77
                    
                    if self._jac_disengaged_:  # 4 79
                        return  # 4 79      # 4 74
                for i in self._jac_ds_entry_funcs:  # 4 81
                    if i['func'].__qualname__.split(".")[0] == walker_type and (type(nd) in i['types'] or nd in i['types']):  # 4 82
                        i['func'](self, nd)  # 4 84
                    
                    if self._jac_disengaged_:  # 4 86
                        return  # 4 86      # 4 81
                for i in self._jac_ds_exit_funcs:  # 4 88
                    if i['func'].__qualname__.split(".")[0] == walker_type and (type(nd) in i['types'] or nd in i['types']):  # 4 89
                        i['func'](self, nd)  # 4 91
                    
                    if self._jac_disengaged_:  # 4 93
                        return  # 4 93      # 4 88
                for i in nd._jac_ds_exit_funcs:  # 4 95
                    if i['func'].__qualname__.split(".")[0] == node_type and type(self) in i['types']:  # 4 96
                        i['func'](nd, self)  # 4 98
                    
                    if self._jac_disengaged_:  # 4 100
                        return  # 4 100      # 4 95
                self._jac_path_.append(nd)  # 4 71      # 4 70
            self._jac_ignores_ = []  # 4 67
        except Exception as e:      # 0 100
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 100
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 100
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 100
            raise e          # 0 100
    
    def _jac_visit_(self,nds: list[Node]|list[Edge]|Node|Edge):  # 0 101
        try:      # 0 101
            if isinstance(nds, list):  # 4 109
                for i in nds:  # 4 110
                    if (i not in self._jac_ignores_):  # 4 111
                        self._jac_next_.append(i)  # 4 111      # 4 110
            
            elif nds not in self._jac_ignores_:  # 4 113
                self._jac_next_.append(nds)  # 4 113
            
            return len(nds) if isinstance(nds, list) else 1  # 4 114
        except Exception as e:      # 0 101
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 101
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 101
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 101
            raise e          # 0 101
    
    def _jac_ignore_(self,nds: list[Node]|list[Edge]|Node|Edge):  # 0 102
        try:      # 0 102
            if isinstance(nds, list):  # 4 119
                for i in nds:  # 4 120
                    self._jac_ignores_.append(i)  # 4 121      # 4 120
            
            else:  # 4 123
                self._jac_ignores_.append(nds)  # 4 123
            
        except Exception as e:      # 0 102
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 102
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 102
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 102
            raise e          # 0 102
    
    def _jac_disengage_(self,):  # 0 103
        try:      # 0 103
            self._jac_next_ = []  # 4 127
            self._jac_disengaged_ = True  # 4 127
        except Exception as e:      # 0 103
            tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 103
            __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 103
            e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 103
            raise e          # 0 103
    

class Master(Element):  # 0 106
    def __init__(self,  # 0 0
        root_node = None,      # 0 0
        *args, **kwargs):      # 0 0
        super().__init__(*args, **kwargs)      # 0 0
        self.root_node = Node() if root_node is None else root_node      # 0 0

def make_architype(base_class: type) -> type:  # 0 110
    try:      # 0 110
        def class_decorator(cls: type) -> type:  # 3 98
            try:      # 3 98
                if not issubclass(cls, base_class):  # 3 100
                    cls = type(cls.__name__, (cls, base_class), {})  # 3 102
                
                return cls  # 3 110
            except Exception as e:      # 3 98
                tb = __jac_traceback__.extract_tb(e.__traceback__)          # 3 98
                __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 3 98
                e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 3 98
                raise e          # 3 98
        return class_decorator  # 3 112
    except Exception as e:      # 0 110
        tb = __jac_traceback__.extract_tb(e.__traceback__)          # 0 110
        __jac_tmp__ = __jac_error__(_jac_pycodestring_, e, tb)          # 0 110
        e.args = (f'{e.args[0]}\n' + __jac_tmp__,) + e.args[1:] if 'Jac error originates from...' not in str(e) else e.args          # 0 110
        raise e          # 0 110

r""" JAC DEBUG INFO
/home/ninja/jaclang/jaclang/core/primitives.jac
/home/ninja/jaclang/jaclang/core/impl/memory_impl.jac
/home/ninja/jaclang/jaclang/core/impl/exec_ctx_impl.jac
/home/ninja/jaclang/jaclang/core/impl/element_impl.jac
/home/ninja/jaclang/jaclang/core/impl/arch_impl.jac
JAC DEBUG INFO """