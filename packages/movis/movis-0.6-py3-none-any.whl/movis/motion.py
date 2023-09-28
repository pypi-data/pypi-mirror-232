from __future__ import annotations

import bisect
from typing import Any, Callable, Sequence

import numpy as np

from .enum import AttributeType, Easing

EASING_TO_FUNC = {
    Easing.LINEAR: lambda t: t,
    Easing.EASE_IN: lambda t: t**2,
    Easing.EASE_OUT: lambda t: 1.0 - (1.0 - t) ** 2,
    Easing.EASE_IN_OUT: lambda t: t**2 * (3.0 - 2.0 * t),
    Easing.FLAT: lambda t: 0.0,
    Easing.EASE_IN2: lambda t: t ** 2,
    Easing.EASE_IN3: lambda t: t ** 3,
    Easing.EASE_IN4: lambda t: t ** 4,
    Easing.EASE_IN5: lambda t: t ** 5,
    Easing.EASE_IN6: lambda t: t ** 6,
    Easing.EASE_IN7: lambda t: t ** 7,
    Easing.EASE_IN8: lambda t: t ** 8,
    Easing.EASE_IN9: lambda t: t ** 9,
    Easing.EASE_IN10: lambda t: t ** 10,
    Easing.EASE_IN12: lambda t: t ** 12,
    Easing.EASE_IN14: lambda t: t ** 14,
    Easing.EASE_IN16: lambda t: t ** 16,
    Easing.EASE_IN18: lambda t: t ** 18,
    Easing.EASE_IN20: lambda t: t ** 20,
    Easing.EASE_IN25: lambda t: t ** 25,
    Easing.EASE_IN30: lambda t: t ** 30,
    Easing.EASE_IN35: lambda t: t ** 35,
    Easing.EASE_OUT2: lambda t: 1. - (1 - t) ** 2,
    Easing.EASE_OUT3: lambda t: 1. - (1 - t) ** 3,
    Easing.EASE_OUT4: lambda t: 1. - (1 - t) ** 4,
    Easing.EASE_OUT5: lambda t: 1. - (1 - t) ** 5,
    Easing.EASE_OUT6: lambda t: 1. - (1 - t) ** 6,
    Easing.EASE_OUT7: lambda t: 1. - (1 - t) ** 7,
    Easing.EASE_OUT8: lambda t: 1. - (1 - t) ** 8,
    Easing.EASE_OUT9: lambda t: 1. - (1 - t) ** 9,
    Easing.EASE_OUT10: lambda t: 1. - (1 - t) ** 10,
    Easing.EASE_OUT12: lambda t: 1. - (1 - t) ** 12,
    Easing.EASE_OUT14: lambda t: 1. - (1 - t) ** 14,
    Easing.EASE_OUT16: lambda t: 1. - (1 - t) ** 16,
    Easing.EASE_OUT18: lambda t: 1. - (1 - t) ** 18,
    Easing.EASE_OUT20: lambda t: 1. - (1 - t) ** 20,
    Easing.EASE_OUT25: lambda t: 1. - (1 - t) ** 25,
    Easing.EASE_OUT30: lambda t: 1. - (1 - t) ** 30,
    Easing.EASE_OUT35: lambda t: 1. - (1 - t) ** 35,
    Easing.EASE_IN_OUT2: lambda t: 0.5 * (2 * t) ** 2 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 2,
    Easing.EASE_IN_OUT3: lambda t: 0.5 * (2 * t) ** 3 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 3,
    Easing.EASE_IN_OUT4: lambda t: 0.5 * (2 * t) ** 4 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 4,
    Easing.EASE_IN_OUT5: lambda t: 0.5 * (2 * t) ** 5 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 5,
    Easing.EASE_IN_OUT6: lambda t: 0.5 * (2 * t) ** 6 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 6,
    Easing.EASE_IN_OUT7: lambda t: 0.5 * (2 * t) ** 7 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 7,
    Easing.EASE_IN_OUT8: lambda t: 0.5 * (2 * t) ** 8 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 8,
    Easing.EASE_IN_OUT9: lambda t: 0.5 * (2 * t) ** 9 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 9,
    Easing.EASE_IN_OUT10: lambda t: 0.5 * (2 * t) ** 10 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 10,
    Easing.EASE_IN_OUT12: lambda t: 0.5 * (2 * t) ** 12 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 12,
    Easing.EASE_IN_OUT14: lambda t: 0.5 * (2 * t) ** 14 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 14,
    Easing.EASE_IN_OUT16: lambda t: 0.5 * (2 * t) ** 16 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 16,
    Easing.EASE_IN_OUT18: lambda t: 0.5 * (2 * t) ** 18 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 18,
    Easing.EASE_IN_OUT20: lambda t: 0.5 * (2 * t) ** 20 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 20,
    Easing.EASE_IN_OUT25: lambda t: 0.5 * (2 * t) ** 25 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 25,
    Easing.EASE_IN_OUT30: lambda t: 0.5 * (2 * t) ** 30 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 30,
    Easing.EASE_IN_OUT35: lambda t: 0.5 * (2 * t) ** 35 if t < 0.5 else 1.0 - 0.5 * (1.0 - 2 * (t - 0.5)) ** 35,
}


class Motion:
    """Defines a motion of ``Attribute`` instances used for keyframe animations.

    This instance is basically initialized by calling ``enable_motion()`` in ``Attribute`` instances.
    keyframes, values and correspoing motion types can be added using ``append()`` or ``extend()``.
    By using these keyframes, ``Motion`` instance returns the complemented values at the given time.

    Args:
        init_value:
            The initial value to use. It is used when no animation is set,
            or when an animation with zero keyframes is set.
        value_type:
            Specifies the type of value that the ``Attribute`` will handle.

    Examples:
        >>> import movis as mv
        >>> attr = mv.Attribute(1.0, mv.AttributeType.SCALAR)
        >>> attr.enable_motion().append(0.0, 0.0).append(1.0, 1.0)
        >>> len(attr.motion)
        2
        >>> attr.enable_motion().extend([2.0, 3.0], [2.0, 3.0], ['ease_in_out'])
        >>> len(attr.motion)
        4
        >>> attr.motion.clear()
        >>> len(attr.motion)
        0
        >>> assert attr(0.0) == attr.init_value
    """

    def __init__(
        self,
        init_value: float | Sequence[float] | np.ndarray | None = None,
        value_type: AttributeType = AttributeType.SCALAR,
    ):
        self.keyframes: list[float] = []
        self.values: list[np.ndarray] = []
        self.easings: list[Callable[[float], float]] = []
        self.init_value: np.ndarray | None = transform_to_numpy(init_value, value_type) \
            if init_value is not None else None
        self.value_type = value_type

    def __len__(self) -> int:
        return len(self.keyframes)

    def __call__(self, prev_value: np.ndarray, layer_time: float) -> np.ndarray:
        if len(self.keyframes) == 0:
            if self.init_value is not None:
                return self.init_value
            raise ValueError("No keyframes")
        elif len(self.keyframes) == 1:
            return self.values[0]

        if layer_time < self.keyframes[0]:
            return self.values[0]
        elif self.keyframes[-1] <= layer_time:
            return self.values[-1]
        else:
            i = bisect.bisect(self.keyframes, layer_time)
            m, M = self.values[i - 1], self.values[i]
            duration = self.keyframes[i] - self.keyframes[i - 1]
            t = (layer_time - self.keyframes[i - 1]) / duration
            t = self.easings[i - 1](t)
            return m + (M - m) * t

    def append(
        self,
        keyframe: float,
        value: float | Sequence[float] | np.ndarray,
        easing: str | Easing = Easing.LINEAR,
    ) -> "Motion":
        """Append a single keyframe.

        Args:
            keyframe:
                time of the keyframe.
            value:
                value of the keyframe.
            easing:
                motion type of the keyframe. This can be either a string or an ``Easing`` enum.
                The default is ``Easing.LINEAR`` (linear completion).
        """
        i = bisect.bisect(self.keyframes, keyframe)
        if 0 < i and self.keyframes[i - 1] == keyframe:
            raise ValueError(f"Keyframe {keyframe} already exists")
        self.keyframes.insert(i, float(keyframe))
        self.values.insert(i, transform_to_numpy(value, self.value_type))
        easing = Easing.from_string(easing) \
            if isinstance(easing, str) else easing
        self.easings.insert(i, EASING_TO_FUNC[easing])
        return self

    def extend(
        self,
        keyframes: Sequence[float],
        values: Sequence[float | Sequence[float] | np.ndarray],
        easings: Sequence[str | Easing] | None = None,
    ) -> "Motion":
        """Append multiple keyframes.

        Args:
            keyframes:
                times of the keyframes.
            values:
                values of the keyframes. The length of ``values`` must be the same as ``keyframes``.
            easings:
                motion types of the keyframes. This can be either a string or an ``Easing`` enum.
                The length of ``easings`` must be the same as ``len(keyframes)`` or ``len(keyframes) - 1``.
                If ``easings`` is ``None``, ``Easing.LINEAR`` is used for all keyframes.
                If ``len(easings) == len(keyframes) - 1``, ``Motion`` automatically adds ``Easing.LINEAR``
                to the end of ``easings``.

        Examples:
            >>> import movis as mv
            >>> motion = mv.Motion(value_type=mv.AttributeType.SCALAR)
            >>> # add two keyframes and The type of motion for that period is ``Easing.EASE_IN_OUT``
            >>> motion.extend(keyframes=[0.0, 1.0], values=[0.0, 1.0], easings=['ease_in_out'])
            >>> # add other two keyframes and The type of motion for that period is ``Easing.LINEAR``
            >>> motion.extend([2.0, 3.0], [2.0, 3.0])
            >>> len(motion)
            4
        """
        assert len(keyframes) == len(values)
        if isinstance(easings, str) or isinstance(easings, Easing):
            raise ValueError("easings must be a list of strings or Easing enums")
        if easings is not None:
            if len(easings) == len(keyframes) - 1:
                easings = list(easings) + [Easing.LINEAR]
            assert len(keyframes) == len(easings)
        easings = (
            ["linear"] * len(keyframes) if easings is None else easings
        )
        converted_keyframes = [float(k) for k in keyframes]

        # Check if given keyframes already exist
        seen = set(self.keyframes)
        for keyframe in converted_keyframes:
            if keyframe in seen:
                raise ValueError(f"Keyframe {keyframe} already exists")
            seen.add(keyframe)

        updated_keyframes: list[float] = self.keyframes + converted_keyframes
        converted_values = [
            transform_to_numpy(v, self.value_type) for v in values]
        updated_values: list[np.ndarray[Any, np.dtype[np.float64]]] = self.values + converted_values

        def convert(t: str | Easing) -> Callable[[float], float]:
            return EASING_TO_FUNC[Easing.from_string(t)] \
                if isinstance(t, str) else EASING_TO_FUNC[t]

        converted_easings = [convert(t) for t in easings]
        updated_easings: list[Callable[[float], float]] = self.easings + converted_easings

        zipped = sorted(zip(updated_keyframes, updated_values, updated_easings))
        keyframes_sorted, values_sorted, easings_sorted = zip(*zipped)
        self.keyframes = list(keyframes_sorted)
        self.values = list(values_sorted)
        self.easings = list(easings_sorted)
        return self

    def clear(self) -> "Motion":
        self.keyframes = []
        self.values = []
        self.easings = []
        return self


def transform_to_numpy(value: int | float | Sequence[float] | np.ndarray, value_type: AttributeType) -> np.ndarray:
    """Transform a scalar, tuple, list or numpy array to a numpy array.

    Args:
        value:
            The value to transform.
        value_type:
            The type of value that the attribute handles.

    Returns:
        A numpy array with the length of 1, 2 or 3.
        This length is determined by the ``value_type``.

    Examples:
        >>> from movis.motion import transform_to_numpy
        >>> transform_to_numpy(1.0, mv.AttributeType.SCALAR)
        array([1.])
        >>> transform_to_numpy([1.0, 2.0], mv.AttributeType.VECTOR2D)
        array([1., 2.])
        >>> transform_to_numpy(1.0, mv.AttributeType.VECTOR3D)
        array([1., 1., 1.])
    """
    if isinstance(value, (int, float)):
        if value_type in (AttributeType.SCALAR, AttributeType.ANGLE):
            return np.array([value], dtype=np.float64)
        elif value_type == AttributeType.VECTOR2D:
            return np.array([value, value], dtype=np.float64)
        elif value_type in (AttributeType.VECTOR3D, AttributeType.COLOR):
            return np.array([value, value, value], dtype=np.float64)
    elif isinstance(value, (Sequence, np.ndarray)):
        if len(value) == 2 and value_type == AttributeType.VECTOR2D or \
                len(value) == 3 and value_type in (AttributeType.VECTOR3D, AttributeType.COLOR) or \
                len(value) == 1 and value_type in (AttributeType.SCALAR, AttributeType.ANGLE):
            return np.array(value, dtype=np.float64)
        else:
            raise ValueError(f"Invalid value type: {value_type}")
    raise ValueError(f"Invalid value type: {value_type}")
