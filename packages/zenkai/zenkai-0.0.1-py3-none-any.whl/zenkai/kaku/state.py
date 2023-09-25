# 1st party
import typing
from abc import abstractproperty
from dataclasses import dataclass
from collections import deque

# local
from .io import IO
from .assess import Assessment, AssessmentDict


class IDable:
    @abstractproperty
    def id(self) -> str:
        pass


class StateKeyError(KeyError):
    """Used to make errors that state returns more explicit"""
    pass


class AssessmentLog(object):
    """Class to log assessments during training. Especially ones that may occur inside the network
    """

    def __init__(self):
        """Instantiate the AssessmentLog
        """

        self._log: typing.Dict[typing.Any, typing.Dict[str, AssessmentDict]] = {}

    def update(self, key, name: str, assessemnt_dict: AssessmentDict, replace: bool=False, to_cpu: bool=True):
        """Update the AssessmentLog with a new AssessmentDict. detach() will automatically be called to prevent storing grads

        Args:
            key : The unique identifier for the layer
            name (str): The name of the layer/operation. Can also include time step info etc
            assessemnt_dict (AssessmentDict): The assessment dict to update with
            replace (bool, optional): Whether to replace the current assessment dict for the key/name. Defaults to False.
            to_cpu (bool): Whether to convert to cpu or not
        """
        assessemnt_dict = assessemnt_dict.detach()
        if to_cpu:
            assessemnt_dict = assessemnt_dict.cpu()

        if key not in self._log:
            self._log[key] = {}
        
        if name not in self._log[key] or replace:
            self._log[key][name] = assessemnt_dict
        else:
            self._log[key][name].union(assessemnt_dict)
    
    def as_assessment_dict(self) -> AssessmentDict:
        """

        Returns:
            AssessmentDict: The assessment log converted to an assessmentdict
        """

        result = AssessmentDict()
        for key, val in self._log.items():

            for key2, val2 in val.items():
                result = result.union(val2.prepend(key2 + "_"))
        return result


class State(object):
    """Class to store the learning state for one learning iteration
    """

    def __init__(self):
        """initializer
        """
        super().__init__()
        self._data = {}
        self._keep = {}
        self._subs = {}
        self._logs = AssessmentLog()

    def id(self, obj) -> str:
        """Get the key for an object

        Args:
            obj: The object to get the key for

        Returns:
            str: The key
        """
        if isinstance(obj, tuple):
            return tuple(id(el) for el in obj)
        return id(obj)

    def store(self, obj: IDable, key: typing.Hashable, value, keep: bool=False) -> typing.Any:
        """Store data in the state

        Args:
            obj (IDable): the object to store for
            key (typing.Hashable): The key for the value
            value: the value to store

        Returns:
            The value that was stored
        """
        obj_data, keep, _ = self._get_obj(obj)
        
        obj_data[key] = value
        keep[key] = keep
        return value

    def get(self, obj: IDable, key: typing.Hashable, default=None) -> typing.Any:
        """Retrieve the value for a key

        Args:
            obj (IDable): The object to retrieve
            key (typing.Hashable): The key for the object
            default (optional): The default value if the value does not exist. Defaults to None.

        Returns:
            typing.Any: The value stored in the object
        """

        # obj_id = self.id(obj)
        obj_data, _, _ = self._get_obj(obj)
        try:
            if isinstance(key, typing.List):
                result = []
                for key_i in key:
                    result.append(obj_data[key_i])
                return result
            else:
                return obj_data[key]
        except KeyError:
            return default

    def __getitem__(self, index: typing.Tuple[IDable, typing.Hashable]) -> typing.Any:
        """Retrieve an item from the state

        Args:
            index (typing.Tuple[IDable, typing.Hashable]): The object and its key

        Raises:
            StateKeyError: If the key does not exist

        Returns:
            typing.Any: The value stored for the object / key pair
        """
        obj, key = index

        obj_id = self.id(obj)
        
        try:
            if isinstance(key, typing.List):
                result = []
                for key_i in key:
                    result.append(self._data[obj_id][key_i])
                return result
            else:
                return self._data[obj_id][key]
        except KeyError:
            raise StateKeyError(
                f"There is no recorded state for {obj} of type {type(obj)} and key {key}"
            )

    def __setitem__(self, index: typing.Tuple[IDable, typing.Hashable], value):
        """Set the value at the key

        Args:
            index (typing.Tuple[IDable, typing.Hashable]): The obj/key to set the value for
            value: The value to set
        """
        obj, key = index

        obj_data, _, _ = self._get_obj(obj)
        obj_data[key] = value
        return value

    def _get_obj(self, obj, to_add: bool = True):
        id = self.id(obj)

        if to_add and id not in self._data:
            self._data[id] = {}
            self._subs[id] = {}
            self._keep[id] = {}
        else:
            print('Not adding')
        return self._data[id], self._keep[id], self._subs[id]

    def add_sub(self, obj: IDable, key: str, ignore_exists: bool = True) -> "State":
        """Add a 'sub state' specified by key

        Args:
            key (str): The key for the substate
            ignore_exists (bool, optional): Whether to ignore if substate already exists. Defaults to True.

        Raises:
            KeyError: If ignore exists if false and key already exists

        Returns:
            State: The substate created
        """
        _, _, sub_data = self._get_obj(obj)

        if key in sub_data:
            raise StateKeyError(
                f"Subs State {key} is already in State and ignore exists is False."
            )
        result = sub_data[key] = State()
        return result

    def my_sub(self, obj: IDable, key: str, to_add: bool = True) -> "MyState":
        """Retrieve the substate for an object

        Args:
            obj (IDable): The object to retrieve for
            key (str): The key for the sub state
            to_add (bool, optional): Whether to add it if it does not exist. Defaults to True.

        Returns:
            MyState: The resulting substate
        """
        mine = self.mine(obj, to_add)
        return mine.my_sub(key, to_add)

    def sub(self, obj: IDable, key: str, to_add: bool = True) -> "State":
        """Retrieve a sub state

        Args:
            key (str): The name of the sub state
            to_add (bool, optional): Whether to add the state if it does not exist. Defaults to True.

        Raises:
            KeyError: If the sub state does not exist and to_add is false

        Returns:
            State: The substate
        """
        _, _, sub_data = self._get_obj(obj, to_add)
        if to_add and key not in sub_data:
            state = sub_data[key] = State()
            return state
        return sub_data[key]
    
    def keep(self, obj: IDable, key: str, keep: bool=True):
        
        id = self.id(obj)
        self._keep[id][key] = keep

    def clear(self, obj: IDable, clear_keep: bool=False):
        """Remove values in the state for an object

        Args:
            obj (IDable): the object to clear the state for
        """
        # TODO: Add idable for the state
        id = self.id(obj)
            
        if id in self._data:
            self._data[id] = {
                k: v
                for k, v in self._data[id].items() if (not clear_keep and not self._keep[id])
            }
        if id in self._subs:
            if clear_keep:
                self._subs[id].clear()
            else:
                self._subs[id] = {
                    k: v.spawn()
                    for k, v in self._subs[id].items() if (not clear_keep and not self._keep[id])
                }
        if id in self._keep and clear_keep:
            self._keep[id] = {
                k: v
                for k, v in self._keep[id].items() if (not clear_keep and not v)
            }

    def sub_iter(self, obj) -> typing.Iterator[typing.Tuple[str, "State"]]:
        """Iterator over all sub states

        Yields:
            typing.Iterator[typing.Tuple[str, 'State']]: The name and state of all substates
        """
        id = self.id(obj)
        for key, value in self._subs[id].items():
            yield key, value

    def mine(self, obj, to_add: bool = True) -> "MyState":
        """Retrieve the state for a given object

        Args:
            obj: The object to get the state for
            to_add (bool, optional): Whether to add if not currently in the state. Defaults to True.

        Returns:
            MyState: MyState for the object
        """
        return MyState(obj, *self._get_obj(obj, to_add=to_add))

    def __contains__(self, key) -> bool:
        """
        Args:
            key (typing.Tuple[obj, str]): The key to check if the key

        Returns:
            bool: Whether the key is contained
        """
        obj, key = key
        id = self.id(obj)
        return id in self._data and key in self._data[id]
    
    def log_assessment_dict(self, obj: IDable, obj_name: str, assessment_dict: AssessmentDict):
        """Log an assessment

        Args:
            obj: The object to log for
            obj_name: The name of the object to log for (So it is clear who it is coming from)
            assessment_dict (AssessmentDict): the values to log
        """
        key = self.id(obj)
        
        self._logs.update(key, obj_name, assessment_dict)

    def log_assessment(self, obj: typing.Union[typing.Tuple[IDable, IDable], IDable], obj_name: str, log_name: str, assessment: Assessment, update: bool=True):
        """Log an assessment

        Args:
            obj: The object to log for
            obj_name: The name of the object to log for (So it is clear who it is coming from)
            assessment_dict (AssessmentDict): the values to log
        """

        key = self.id(obj)
        self._logs.update(key, obj_name, AssessmentDict(**{log_name: assessment}))

    @property
    def logs(self) -> AssessmentLog:
        return self._logs
    
    def spawn(self, spawn_logs: bool=False) -> 'State':
        """Spawn the state to be used for another time step or another instance of the machine
        All data that is not to be kept will be cleared

        Args:
            spawn_logs (bool, optional): Whether to pass on the logs as well. Defaults to False.

        Returns:
            State: The spawned state
        """

        subs = {}
        data = {}
        keep = {}

        # Loop over all objects
        for k, v in self._data.items():
            # loop over all keys
            for k2, v2 in v.items():
                # add the data if it is supposed to be kept
                if self._keep[k][k2]:
                    if k not in data:
                        data[k] = {}
                        keep[k] = {}
                    data[k][k2] = self._data[k][k2]
                    keep[k][k2] = k
        for k, v in self._subs.items():
            cur_sub = {}
            for k2, v2 in v.items():
                cur_sub[k2] = v2.spawn()
            subs[k] = cur_sub
        
        state = State()
        state._subs = subs
        state._data = {**data}
        state._keep = keep
        if spawn_logs:
            state._logs = self._logs
        return state


class MyState(object):
    """Convenience class to make it easy to access state values for an object

    Usage:
    x = object()
    my_state = State().mine(x)
    my_state.t = 1
    """

    def __init__(self, obj, data: typing.Dict, keep: typing.Dict, subs: typing.Dict):
        """initializer

        Args:
            data (typing.Dict): The data for the object
            subs (typing.Dict): The sub states for the object
        """
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_keep", keep)
        object.__setattr__(self, "_subs", subs)

    @property
    def subs(self) -> typing.Dict[str, State]:
        """Retrieve the sub states for the state

        Returns:
            typing.Dict[str, State]: The sub states
        """
        return {**self._subs}

    def add_sub(self, key: str, state: State = None) -> "State":
        """Add a substate to the state

        Args:
            key (str): Name of the sub state
            state (State): The substate to add

        Raises:
            KeyError: The key already exists in the sub states
        """
        if key in self._subs:
            raise KeyError(f"State by name of {key} already exists in subs")
        state = state or State()
        self._subs[key] = state
        return state

    def my_sub(self, key: str, to_add: bool = True) -> "MyState":
        """Get the sub state for a key

        Args:
            key (str): The name for the sub state
            to_add (bool, optional): Whether to add the sub state. Defaults to True.

        Returns:
            MyState: The substate
        """
        if to_add and key not in self._subs:
            self._subs[key] = State()
        return self._subs[key].mine(self._obj)

    def get(self, key: str, default=None, keep: bool=False) -> typing.Any:
        """Get the value at a key

        Args:
            key (str): The key to retrieve for
            default (optional): The default value if the key does not have a value. Defaults to None.

        Returns:
            typing.Any: The value at the key or the default
        """
        if keep:
            return self._keep.get(key, default)
        return self._data.get(key, default)

    def store(self, key: str, value, keep: bool=False) -> typing.Any:
        """Get the value at a key

        Args:
            key (str): The key to retrieve for
            default (optional): The default value if the key does not have a value. Defaults to None.

        Returns:
            typing.Any: The value at the key or the default
        """
        if keep:
            self._keep[key] = value
        else:
            self._data[key] = value

    def __getitem__(self, key: str) -> typing.Any:
        """Get the value at a key

        Args:
            key (str): _description_

        Returns:
            typing.Any: The value at the key
        """
        return self._data[key]

    def __setitem__(self, key: str, value):
        """Set the value at the key

        Args:
            key (str): The key to set the value to
            value: The value to set
        """
        self._data[key] = value

    def __getattr__(self, key):
        """Get the value at a key

        Args:
            key (str): _description_

        Returns:
            typing.Any: The value at the key
        """
        return self._data[key]

    def __setattr__(self, key: str, value: typing.Any) -> typing.Any:
        """Set the value at the key

        Args:
            key (str): The key to set the value to
            value: The value to set
        """
        self._data[key] = value
        return value

    def __contains__(self, key: str) -> bool:
        return key in self._data



class EmissionStack(object):
    """Class to use for recording the state of emissions"""

    def __init__(self, *emissions: IO):
        """Convenience wrapper for deque to simplify recording emissions for the step method

        usage:
        def forward(self, x) -> IO:
            ...
            emissions = EmissionStack()
            x = emissions(layer(x))
            state[self, 'emissions'] = emissions
            ...

        def step(self, ...):
            ...
            layer.step(conn, state, from_=state[self, 'emissions'].pop())

        """
        self._stack = deque(emissions)

    def __call__(self, io: IO) -> IO:
        """Add an element to the stack

        Args:
            io (IO): Element to add

        Returns:
            IO: the element that was added
        """

        self._stack.append(io)
        return io

    def __len__(self) -> int:
        return len(self._stack)

    def stack_on(self, io: IO):
        """Restack the stack by placing it on another vlaue

        Args:
            io (IO): the io to stack the current stack onto
        """

        self._stack.insert(0, io)

    def pop(self) -> typing.Union[IO, None]:
        """Pop off the last element in the stack. Returns None if empty

        Raises:
            IndexError: If there are no elements left in the stack

        Returns:
            IO: the last element
        """

        try:
            return self._stack.pop()
        except IndexError:
            return None
            # raise IndexError("No more elements left in the EmissionStack to pop")

    def __iter__(self):
        """
        LIFO Iteration over the stack
        """

        for io in reversed(self._stack):
            yield io
    
    def __getitem__(self, key) -> IO:
        return self._stack[key]
