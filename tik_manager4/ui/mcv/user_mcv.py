"""Custom widgets for setting / displaying users"""

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.dialog.user_dialog import LoginDialog
from tik_manager4.ui.widgets.common import TikButton, ResolvedText


class TikUserWidget(QtWidgets.QWidget):
    """Widget for displaying user information"""

    def __init__(self, user_obj, parent=None):
        super().__init__(parent)
        self.user_obj = user_obj

        # --- Layout Setup ---
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # --- UI Elements ---
        _user_lbl = QtWidgets.QLabel(parent=self)
        _user_lbl.setMaximumHeight(30)
        _user_lbl.setText("User: ")
        self.main_layout.addWidget(_user_lbl)

        self.user_name_lbl = ResolvedText(self.user_obj.get())
        self.user_name_lbl.setMaximumHeight(30)
        self.main_layout.addWidget(self.user_name_lbl)

        self.set_user_btn = TikButton(parent=self)
        self.set_user_btn.setMaximumHeight(30)
        self.set_user_btn.setText("Login")
        self.set_user_btn.setToolTip("Opens up User Login Dialog")
        self.main_layout.addWidget(self.set_user_btn)

        # SIGNALS
        self.set_user_btn.clicked.connect(lambda: self.on_set_user())

    def refresh(self):
        """Refresh the user name"""
        self.user_name_lbl.setText(self.user_obj.get())

    @QtCore.Slot()
    def on_set_user(self):
        """Set the user to display"""
        # We pass 'self' as the parent to ensure the dialog
        # is correctly parented to this widget or its top-level window.
        dialog = LoginDialog(self.user_obj, parent=self)
        state = dialog.exec_()

        # In standard Qt dialogs, Accepted is usually 1
        if state == 1:
            self.refresh()