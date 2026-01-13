"""Common usage basic widgets."""
import math

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui import pick

FONT = "Arial"

BUTTON_STYLE = """
QPushButton
{
    color: #b1b1b1;
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
    border-radius: 4px;
}

QPushButton:hover
{
    background-color: #505050;
    border: 1px solid #ff8d1c;
}

QPushButton:hover[circle=true]
{
    background-color: #505050;
    border: 2px solid #ff8d1c;
}

QPushButton:disabled {
    color: #505050;
    background-color: #303030;
    border: 1px solid #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
}

QPushButton:pressed {
  background-color: #ff8d1c;
  border: 1px solid #ff8d1c;
}
"""



class ClickableFrame(QtWidgets.QFrame):
    """Clickable frame widget."""

    clicked = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        self.clicked.emit()
        return super().mousePressEvent(event)

class StyleFrame(ClickableFrame):
    """Frame with custom styling support."""

    def set_style(self, stylesheet):
        """Set the stylesheet for this frame."""
        self.setStyleSheet(stylesheet)


def lighten_color(color_str, factor=110):
    """
    Lightens the given color.

    Args:
        color_str (str): The color to lighten as a hex string.
        factor (int): The percentage to lighten (100 = no change, >100 = lighter, <100 = darker).

    Returns:
        str: A lighter color as a hex string.
    """
    color = QtGui.QColor(
        color_str)  # Automatically handles both #RRGGBB and "rgb(r,g,b)"
    lighter_color = color.lighter(
        factor)  # Increase brightness by the given factor
    return lighter_color.name()  # Returns as hex string

class TikButton(QtWidgets.QPushButton):
    """Unified button class for the whole app."""

    # Default colors
    DEFAULT_TEXT_COLOR = "#b1b1b1"
    DEFAULT_BACKGROUND_COLOR = "#404040"
    DEFAULT_BORDER_COLOR = "#1e1e1e"

    def __init__(self,
        text="",
        font_size=10,
        text_color=None,
        border_color=None,
        background_color=None,
        parent=None,
        **kwargs,
    ):
        super().__init__(parent=parent)
        self.text_color = text_color or self.DEFAULT_TEXT_COLOR
        self.border_color = border_color or self.DEFAULT_BORDER_COLOR
        self.background_color = background_color or self.DEFAULT_BACKGROUND_COLOR
        self.setText(text)
        self.set_font_size(font_size)
        self.setStyleSheet(BUTTON_STYLE)
        self.set_color(self.text_color, self.background_color, self.border_color)

    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, text_color=None, background_color=None, border_color=None):
        """Set the button colors.

        Args:
            text_color: Color for text (hex string or RGB tuple/list)
            background_color: Color for background (hex string or RGB tuple/list)
            border_color: Color for border (hex string or RGB tuple/list)
        """
        text_color, background_color, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        self.text_color = text_color or self.text_color
        self.background_color = background_color or self.background_color
        self.border_color = border_color or self.border_color

        hover_bg = lighten_color(self.background_color)

        stylesheet = f"""
QPushButton {{
    color: {self.text_color};
    background-color: {self.background_color};
    border-width: 1px;
    border-color: {self.border_color};
    border-style: solid;
    padding: 5px;
    font-size: 12px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background-color: {hover_bg};
    border: 1px solid #ff8d1c;
}}
QPushButton:disabled {{
    color: #505050;
    background-color: #303030;
    border: 1px solid #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12px;
}}
QPushButton:pressed {{
    background-color: #ff8d1c;
    border: 1px solid #ff8d1c;
}}
"""
        self.setStyleSheet(stylesheet)


class TikIconButton(TikButton):
    """Button specific for fixed sized icons."""

    def __init__(self, icon_name=None, circle=True, size=22, icon_size=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = int(size * 0.5)
        self.circle = circle
        self.set_size(size)
        self._icon_size = icon_size

        if icon_name:
            self.set_icon(icon_name)

    def set_icon(self, icon_name):
        self.setIcon(pick.icon(icon_name))
        #double the size of the icon
        if self._icon_size:
            self.setIconSize(QtCore.QSize(self._icon_size, self._icon_size))

    def set_size(self, size):
        self.setFixedSize(size, size)
        self.radius = int(size * 0.5)
        border_radius = f"{self.radius}px" if self.circle else "4px"

        hover_bg = lighten_color(self.background_color)

        stylesheet = f"""
QPushButton {{
    color: {self.text_color};
    background-color: {self.background_color};
    border-width: 1px;
    border-color: {self.border_color};
    border-style: solid;
    padding: 5px;
    font-size: 12px;
    border-radius: {border_radius};
}}
QPushButton:hover {{
    background-color: {hover_bg};
    border: 1px solid #ff8d1c;
}}
QPushButton:disabled {{
    color: #505050;
    background-color: #303030;
    border: 1px solid #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12px;
    border-radius: {border_radius};
}}
QPushButton:pressed {{
    background-color: #ff8d1c;
    border: 1px solid #ff8d1c;
}}
"""
        self.setStyleSheet(stylesheet)

    @staticmethod
    def square_to_circle_multiplier(side_length):
        diagonal = math.sqrt(2) * side_length
        radius = diagonal * 0.5
        multiplier = radius / side_length
        return multiplier


class TikButtonBox(QtWidgets.QDialogButtonBox):
    """Unified button box class for the whole app."""

    def __init__(self, *args, font_size=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_size = font_size
        for button in self.buttons():
            self.modifyButton(button)

    def set_font_size(self, font_size):
        self.font_size = font_size
        for button in self.buttons():
            self.modifyButton(button)

    def event(self, event):
        if event.type() == QtCore.QEvent.ChildAdded:
            child = event.child()
            self.modifyButton(child)
        return super().event(event)

    def modifyButton(self, button):
        button.setFont(QtGui.QFont(FONT, self.font_size))
        button.setMinimumWidth(100)
        button.setStyleSheet(BUTTON_STYLE)


class TikMessageBox(QtWidgets.QMessageBox):
    """Message box with custom font."""

    def __init__(self, *args, font_size=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_font_size(font_size)

    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size))


class TikLabel(QtWidgets.QLabel):
    """Unified label class for the whole app."""

    # Default colors
    DEFAULT_TEXT_COLOR = "#b1b1b1"
    DEFAULT_BORDER_COLOR = "#1e1e1e"

    def __init__(self, text="", font_size=10, bold=False, color=(255, 255, 255), parent=None, **kwargs):
        super().__init__(parent=parent)
        self.text_color = self.DEFAULT_TEXT_COLOR
        self.border_color = self.DEFAULT_BORDER_COLOR
        self.color = color
        self.set_font_size(font_size, bold=bold)
        self.set_color(text_color=self.color, border_color=self.color)

    def set_font_size(self, font_size, bold=False):
        if bold:
            self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))
        else:
            self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, text_color=None, background_color=None, border_color=None):
        """Set the label colors.

        Args:
            text_color: Color for text (hex string or RGB tuple/list)
            background_color: Unused, kept for API compatibility
            border_color: Color for border (hex string or RGB tuple/list)
        """
        text_color, _, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        text_color = text_color or self.text_color
        border_color = border_color or self.border_color

        color_style = f"""
QLabel {{
    color: {text_color};
    border-color: {border_color};
}}"""

        self.setStyleSheet(color_style)

    def set_text(self, text):
        self.setText(text)


class TikLabelButton(TikButton):
    """Customize the button to be used next to the header."""

    style_sheet = """
    QPushButton
    {{
        color: {0};
        background-color: #404040;
        border-width: 1px;
        border-color: {0};
        border-style: solid;
        padding: 5px;
        font-size: 12x;
        border-radius: 0px;
    }}"""

    def __init__(self, *args, color=(255, 255, 255), **kwargs):
        super().__init__(*args, **kwargs)
        self.normal_text = kwargs.get("text", ">")
        self.clicked_text = "˅"
        self.setText(self.normal_text)
        # make the button checkable
        self.setCheckable(True)
        self.setProperty("label", True)
        self.set_color(text_color=color, border_color=color)
        self.toggled.connect(self.set_state_text)

    # override the checked state
    def set_state_text(self, checked):
        if checked:
            self.setText(self.clicked_text)
        else:
            self.setText(self.normal_text)


class HeaderLabel(TikLabel):
    """Label with bold font and indent."""

    style_sheet = """
QLabel
{
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
    border-radius: 14px;
}
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setProperty("header", True)
        self.setIndent(10)
        self.setFixedHeight(30)
        self.setFrameShape(QtWidgets.QFrame.Box)
        # center text
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.color = (255, 0, 255)
        self.setStyleSheet(self.style_sheet)

    def set_font_size(self, font_size, bold=True):
        super().set_font_size(font_size, bold)


class ResolvedText(TikLabel):
    """Label for resolved paths, names etc."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make is selectable
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        # make is wrap
        self.setWordWrap(True)

    def set_font_size(self, font_size, bold=True):
        super().set_font_size(font_size, bold)


class VerticalSeparator(QtWidgets.QLabel):
    """Simple vertical separator."""

    def __init__(self, color=(100, 100, 100), height=25, width=20):
        super().__init__()
        self._pixmap = QtGui.QPixmap(2, 100)
        self.set_color(color)
        self.setPixmap(self._pixmap)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setAlignment(QtCore.Qt.AlignCenter)

    def set_color(self, color):
        self._pixmap.fill(QtGui.QColor(*color))


class HorizontalSeparator(QtWidgets.QLabel):
    """Simple horizontal separator."""

    def __init__(self, color=(100, 100, 100), height=1, width=None):
        super().__init__()
        self.set_color(color)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)

    def set_color(self, color):
        if isinstance(color, (tuple, list)):
            color = f"rgb({color[0]}, {color[1]}, {color[2]});"
        self.setStyleSheet(f"background-color: {color};")
