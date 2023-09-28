"""
in-dev bps beta
"""

class ChecksumMismatch(Exception): pass 
class ContinuityError(Exception): pass

#FOR DEV
import time

__version__ = "0.6"
from zlib import crc32 as crc 
import re
"""
def build   | build a BPS with : source, target | optional : metadata
def apply   | apply a BPS with : source         | optional : metadata, validate
"""

def encode(number : int) -> bytes:
    """enocdes numerical information with variable width encoding

    Args:
        number (int): the number to encode

    Returns:
        bytes: the encoded number
    """
    encoded = bytes()
    while True:
        x = number & 0x7f
        number >>= 7
        if number:
            encoded += x.to_bytes(1, "big")
            number -= 1
        else: return encoded + (0x80 | x).to_bytes(1, "big")
                    
class bps:
    def __iter__(self): return iter(self.actions)
    def __getitem__(self, index): return self.actions[index]
    def __setitem__(self, index, value): self.actions[index] = value
    
    class action:
        def __init__(self, parent, operation : int, length : int, offset : int): 
            self.parent, self.operation, self.length, self.offset = parent, operation, length, offset
            self.end = offset + length
            
        def modify(self, operation : int = None, offset : int = None, length : int = None, payload : bytes = None, relative : int = None, name : str = None): 
            raise NotImplementedError("action modification is currently unimplemented")
            
    class source_read(action):
        def __init__(self, parent, length : int, offset : int, name : str):
            super().__init__(parent, 0, length, offset)
            
            self.name = name
    class target_read(action):
        def __init__(self, parent, length : int, offset : int, name : str, payload : bytes):
            super().__init__(parent, 1, length, offset)
            self.name, self.payload = name, payload
            
    class relative_action(action):
        def __init__(self, parent, length : int, offset : int, name : str, relative : int, action : int):
            super().__init__(parent, action, length, offset)
            self.name, self.relative, self.source = name, relative, action & 1
            
    def __init__(self, patch : bytes, checks : bool = True, metadata : bool = True): 
        if not isinstance(patch, bytes): raise TypeError("Original patch file must be bytes")
        if not isinstance(checks, bool): raise TypeError("Checksum validation flag must be boolean")
        if not isinstance(metadata, bool): raise TypeError("Metadata flag must be boolean")
        if len(patch) < 19: raise ValueError("BPS is corrupt, invalid filesize")
        
        self.source_checksum, self.target_checksum, self.patch_checksum = [patch[i:i+4 if i+4 else None][::-1].hex() for i in range(-12, 0, 4)]
        if checks and crc(patch[:-4]) != int(self.patch_checksum, 16): raise ChecksumMismatch("BPS file is corrupt!")
        patch = patch[4:-12]
        
        def decode():
            nonlocal patch
            decoded, shift = 0, 1 
            while True:
                x = patch[0]
                patch = patch[1:]
                decoded += (x & 0x7f) * shift
                if x & 0x80: return decoded 
                shift <<= 7
                decoded += shift
        try:        
            self.source_size, self.target_size, self.metadata_size = decode(), decode(), decode()
        except IndexError:
            raise ValueError("BPS has invalid sizes")
        
        if metadata and self.metadata_size:
            self.metadata = patch[:self.metadata_size]
            patch = patch[self.metadata_size:]        
        else:
            self.metadata = bytes() 
            self.metadata_size = 0             
            
        self.actions = []
        offset = 0
        try:
            while patch:
                length = decode() 
                action  = length & 3
                length = (length >> 2) + 1 
                
                def add_source_read(): 
                    nonlocal length, action, offset, patch
                    self.actions.append(self.source_read(self, length, offset, f"Unnamed source read at {hex(offset)[2:].upper()} with length {hex(length)[2:].upper()}"))
                
                def add_target_read(): 
                    nonlocal length, action, offset, patch
                    payload = patch[:length]
                    patch = patch[length:]
                    self.actions.append(self.target_read(self, length, offset, f"Unnamed target read at {hex(offset)[2:].upper()} with length {hex(length)[2:].upper()}", payload))
                
                def add_relative_copy(): 
                    nonlocal length, action, offset, patch
                    relative = decode() 
                    relative = (-1 if relative & 1 else 1) * (relative >> 1)
                    self.actions.append(self.relative_action(self, length, offset, f"Unnamed {'target' if action & 1 else 'source'} copy at {hex(offset)[2:].upper()} with length {hex(length)[2:].upper()} and relative offset of {('-' if relative < 0 else '') + hex(relative)[2 + (relative < 0):].upper()}", relative, action))
                
                (add_source_read, add_target_read, add_relative_copy, add_relative_copy)[action]()
                offset += length
        except KeyboardInterrupt:
            pass 
        except:
            raise ValueError("BPS file is corrupt!")
        if sum(tuple(action.length for action in self.actions)) != self.target_size:
            raise ContinuityError("BPS file is corrupt!")
        
    def to_bytes(self, metadata : bool = False)->bytes:
        """process bps object into encoded file

        Args:
            metadata (bool, optional): metadata inclusion flag. Defaults to False.
            checks (bool, optional): validate checksums. Defaults to True.

        Returns:
            bytes: encoded bps file
        """
        if not isinstance(metadata, bool): raise TypeError("metadata flag must be boolean")
        
        contents = bytes() 
        for action in self: 
            contents += encode(((action.length - 1) << 2) + action.operation)
            if action.operation & 2: contents += encode(abs(action.relative * 2) + (action.relative < 0))
            elif action.operation & 1: contents += action.payload
        contents = b"BPS1"+ encode(self.source_size) + encode(self.target_size) + (encode(self.metadata_size if metadata else 0)) + (self.metadata if metadata and self.metadata_size else bytes()) + contents + int(self.source_checksum, 16).to_bytes(4, "little") + int(self.target_checksum, 16).to_bytes(4, "little")
        return contents + crc(contents).to_bytes(4, "little")
    
    def range(self,start : int = 0, end : int = None, exclude_source_read : bool = False) -> bytes: 
        """
        Retrieves all existing actions within a specified range of offsets
        """

        if end is None: end = 0xFFFFFF
        if not isinstance(start, int): raise TypeError("`start` must be of type `int`")
        if not isinstance(end, int): raise TypeError("`end` must be of type `int`")
        if start < 0: start = self.actions[-1].end+start 
        if end < 0: end = self.actions[-1].end+end
        if start > end : return [ins for ins in self.actions if (ins.end > start) and ((ins.operation) if exclude_source_read else True)]+[ins for ins in self.actions if (ins.end < end) and ((ins.operation) if exclude_source_read else True)]
        else: return [ins for ins in self.actions if ins.end > start and ins.offset < end] 
    
    def create(self, operation : int, offset : int, length : int, relative : int = None, payload : bytes = None, override : bool = False):
        """_summary_

        Args:
            action (int): _description_
            offset (int): _description_
            length (int): _description_
            relative (int, optional): _description_. Defaults to None.
            payload (bytes, optional): _description_. Defaults to None.

        Raises:
            TypeError: _description_
        """
        if not isinstance(operation, int): raise TypeError
        if not isinstance(length, int): raise TypeError
        if not isinstance(offset, int): raise TypeError
        if not isinstance(relative, int) if not relative is None else False: raise TypeError
        if not isinstance(payload, bytes) if not relative is None else False: raise TypeError
        if not isinstance(override, bool): raise TypeError
        
        if payload:
            if len(payload) != length: raise ValueError("payload is not of specified length")
    
        action = abs(action & 3)
        clashes = self.range(offset, offset + length, True)
        if len(clashes):
            if not override: raise ContinuityError("Cannot write new data, existing non-source_read actions are present at this range")
            source_relative = target_relative = 0
        
            if clashes[0].offset < offset: 
                if clashes[0].operation & 2:
                    clashes[1].relative += offset - clashes[0].offset
                else:
                    clashes[0].payload = clashes[0].payload[:offset - clashes[0].offset]
                clashes[0].length = offset - clashes.offset[0] 
            else: 
                del clashes[0]
                clashes.insert(0, None)
                
            if clashes[-1].end > offset + length: 
                if clashes[-1].operation & 2:
                    clashes[-1].relative += clashes[-1].end - (offset + length)
                else:
                    clashes[-1].payload = clashes[-1].payload[clashes[-1].end - (offset + length):]
                clashes[-1].length = clashes[-1].end - (offset + length) 
            else:
                del clashes[-1]
                clashes.append(None)
                
            for act in clashes[1:-1]:
                if act.operation & 2:
                    if act.operaion & 1:
                        target_relative += act.relative 
                    else:
                        source_relative += act.relative
                del act
            if source_relative:
                for act in self.range(offset + length, None, True):
                    if act.operation == 2:
                        act.relative += source_relative
                        break 
            if target_relative:
                for act in self.range(offset + length, None, True):
                    if act.operation == 3:
                        act.relative += target_relative
                        break 
        if operation & 2:
            action = self.relative_action(self, length, offset, "None", relative, operation & 1)
        elif operation & 1:
            action = self.target_read(self, length, offset, "Name", payload)
        else:
            action = self.source_read(self, length, offset, "None")
                
        self.actions.insert(self.range(offset - 1, offset, False), action)
    
    def delete(self, actions : target_read | relative_action | tuple | list | str | int, _instream : list = []) -> dict:
        """delete action(s) from a bps

        Args:
            action (target_read | relative_action | tuple | list | str | int): offset or name of action, or action itself, or array of actions to be deleted
            _instream (list, optional): incoming structs if deletion is iterative. Defaults to [].
        Returns:
            dict: struct of action contents
        """
        stores = []
        if not actions.operation: raise ContinuityError("cannot delete source_read action")
        if isinstance(actions, (tuple, list)):
            if not all(isinstance(a, self.action, str , int) for a in actions): raise ValueError("actions parameter containts non-patch results")
            for act in actions: stores.append(self.delete(act))
            
        if isinstance(actions, str): 
            for act in [act for act in self.actions if act.name == actions]: self.delete(act)
        
        if isinstance(actions, int):
            actions = self.get(actions)
        
        if isinstance(actions, (self.action, self.relative_action, self.target_read)):
            store = {"operation" : actions.operation, "offset" : actions.offset, "length" : actions.length, "name" : actions.name}
            if actions.operation & 2: 
                store["relative"] = actions.relative
                modify = [act for act in self.range(actions.offset, actions.offset + actions.length, True) if act.operation == actions.operation]
                if len(modify): modify[0].relative += store["relative"]
            else: store["payload"] = actions.payload
            
            del actions
            return stores if stores else store
            
                    
def apply(source : bytes, patch : bps, checks : bool = True, metadata : bool | bytes = False) -> tuple | bytes: 
    """apply a bps object to the required source file.

    Args:
        source (bytes): source file required by the patch
        patch (bps): patch object to be used on the source
        checks (bool, optional): perform checksum validation. Defaults to True.
        metadata (bool, optional): include metadata in output. Defaults to False.

    Raises:
        ChecksumMismatch: on source mismatch
        ChecksumMismatch: on target mismatch

    Returns:
        tuple | bytes: patched file, or combination of patched file with metadata
    """
    
    if isinstance(metadata, bytes):
        applied_metadata = bytes 
        metadata = True
    else: 
        applied_metadata = patch.metadata
    
    if not isinstance(source, bytes): raise TypeError("Source file must be array of bytes")
    if not isinstance(patch, bps): raise TypeError("Patch must be normalized bps object")
    if not isinstance(checks, bool): raise TypeError("checksum validation flag must be boolean")
    if not isinstance(metadata, bool): raise TypeError("metadata inclusion flag must be boolean or bytes")       
    
    # this is merely to catch user errors, in truth a patch MAY function with a different size (we can add a check?)
    if len(source) != patch.source_size: raise ValueError("Wrong source file for this patch")
    
    target, source_relative_offset, target_relative_offset = bytes(), 0, 0
    if checks and crc(source) != int(patch.source_checksum, 16): raise ChecksumMismatch("Source File is not suited to this Patch!")
    for action in patch:
        if action.operation == 0:
            target += source[action.offset : action.end]
        if action.operation == 1:
            target += action.payload 
        if action.operation == 2:
            source_relative_offset += action.relative 
            target += source[source_relative_offset : source_relative_offset + action.length] 
            source_relative_offset += action.length
        if action.operation == 3:
            target_relative_offset += action.relative 
            if target_relative_offset + action.length < len(target):
                target += target[target_relative_offset: target_relative_offset + action.length]
            else:
                loop = target[target_relative_offset:]
                target += b"".join([loop for x in range(action.length // len(loop))]) + loop[:action.length % len(loop)]
            target_relative_offset += action.length
    if len(target) != patch.target_size: raise ValueError("Wrong source file for this patch")
    if checks and crc(target) != int(patch.target_checksum, 16): raise ChecksumMismatch("Source File is not suited to this Patch!")
    return (target, applied_metadata) if patch.metadata_size and metadata else (target)


def build(source : bytes, target : bytes, checks : bool = True, metadata : bool = False)->bytes:
    raise NotImplementedError("patchlib.bps.build has been inevitably postponed")