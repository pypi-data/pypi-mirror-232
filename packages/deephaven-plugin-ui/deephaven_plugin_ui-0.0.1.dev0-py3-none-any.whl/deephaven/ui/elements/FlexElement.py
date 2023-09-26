"""
Python implementation for the Adobe React Spectrum Flex component.
https://react-spectrum.adobe.com/react-spectrum/Flex.html
"""

from typing import Literal, Optional, Union
from .Element import Element
from .._internal import RenderContext


class FlexElement(Element):
    def __init__(
        self,
        *children,
        direction: Optional[Literal["row", "column", "row-reverse", "column-reverse"]],
        wrap: Optional[Literal["wrap", "nowrap", "wrap-reverse"]],
        justify_content: Optional[
            Literal[
                "start",
                "end",
                "center",
                "left",
                "right",
                "space-between",
                "space-around",
                "space-evenly",
                "stretch",
                "baseline",
                "first baseline",
                "last baseline",
                "safe center",
                "unsafe center",
            ]
        ],
        align_content: Optional[
            Literal[
                "start",
                "end",
                "center",
                "space-between",
                "space-around",
                "space-evenly",
                "stretch",
                "baseline",
                "first baseline",
                "last baseline",
                "safe center",
                "unsafe center",
            ]
        ],
        align_items: Optional[
            Literal[
                "start",
                "end",
                "center",
                "stretch",
                "self-start",
                "self-end",
                "baseline" "first baseline",
                "last baseline",
                "safe center",
                "unsafe center",
            ]
        ],
        gap: Optional[Union[str, int, float]],
        column_gap: Optional[Union[str, int, float]],
        row_gap: Optional[Union[str, int, float]],
        **props
    ):
        self._children = children
        self._props = {
            "direction": direction,
            "wrap": wrap,
            "justifyContent": justify_content,
            "alignContent": align_content,
            "alignItems": align_items,
            "gap": gap,
            "columnGap": column_gap,
            "rowGap": row_gap,
            **props,
        }

    def render(self, context: RenderContext):
        return self._children

    @property
    def props(self):
        return self._props
