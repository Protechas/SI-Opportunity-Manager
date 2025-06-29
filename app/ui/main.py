import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QPushButton, QLabel, QStackedWidget, QSystemTrayIcon,
                           QMenu, QStyle, QHBoxLayout, QFrame, QSlider, QDialog, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QPoint, QTimer, QSettings
from PyQt5.QtGui import (QIcon, QPixmap, QImage, QTransform, QPainter, QColor, QLinearGradient,
                      QPaintEvent, QMouseEvent, QResizeEvent, QMoveEvent, QCloseEvent)
from app.ui.qt_types import (
    AlignCenter, FramelessWindowHint, WindowStaysOnTopHint, Tool, NoDropShadowWindowHint,
    WA_TranslucentBackground, WA_ShowWithoutActivating, WA_AlwaysShowToolTips,
    Horizontal, Vertical, SmoothTransformation, KeepAspectRatio, IgnoreAspectRatio,
    NoPen, WindowMinimized, AA_EnableHighDpiScaling, AA_UseHighDpiPixmaps,
    AA_UseStyleSheetPropagationInWidgetStyles, AA_DontCreateNativeWidgetSiblings
)
from app.ui.dashboard import DashboardWidget
from app.ui.opportunity_form import OpportunityForm
from app.ui.auth import AuthWidget
from app.ui.account_creation import AccountCreationWidget
from app.ui.settings import SettingsWidget
from app.ui.management_portal import ManagementPortal
from app.ui.profile import ProfileWidget
from app.database.connection import SessionLocal
from app.models.models import Opportunity, Notification, User
from datetime import datetime, timedelta, timezone
from win10toast import ToastNotifier
from sqlalchemy import and_, or_
import traceback
from typing import Optional, Dict, List, Union, cast, Any, Protocol, TypeVar, TYPE_CHECKING
import asyncio
import websockets
import json

T = TypeVar('T')

if TYPE_CHECKING:
    from PyQt5.QtCore import QObject
    from PyQt5.QtWidgets import QWidget as QWidgetType

class DatabaseSession(Protocol):
    def query(self, model: type[T]) -> 'Query[T]': ...
    def add(self, obj: Any) -> None: ...
    def commit(self) -> None: ...
    def close(self) -> None: ...

class Query(Protocol[T]):
    def filter(self, *criterion: Any) -> 'Query[T]': ...
    def first(self) -> Optional[T]: ...
    def all(self) -> list[T]: ...

class NotificationBadge(QLabel):
    """A badge showing the number of unread notifications"""
    def __init__(self, parent: Optional['QWidgetType'] = None) -> None:
        super().__init__(parent)
        self.setAlignment(AlignCenter)
        self.setAttribute(WA_TranslucentBackground)
        
        # Slightly larger size for better visibility
        self.setFixedSize(22, 22)
        
        # Modern style with gradient background and refined typography
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FF4B4B,
                    stop:1 #FF6B6B);
                color: white;
                border-radius: 11px;
                padding: 0px;
                font-size: 11px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        print("DEBUG: NotificationBadge created with size:", self.size())

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the notification badge with custom styling"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw red circle background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(0, 0, self.width(), self.height())
        
        # Draw notification count text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.rect(), AlignCenter, self.text())

class DragHandle(QWidget):
    def __init__(self, parent: Optional['QWidgetType'] = None, orientation: Qt.Orientation = Qt.Horizontal) -> None:
        super().__init__(parent)
        self._orientation = orientation
        self.setFixedSize(8, 30 if orientation == Qt.Horizontal else 8)
        self.setCursor(Qt.SizeHorCursor if orientation == Qt.Horizontal else Qt.SizeVerCursor)
        
        # Style with a semi-transparent background
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(43, 43, 43, 0.95);
                border-radius: 5px;
            }
            QWidget:hover {
                background-color: rgba(60, 60, 60, 0.95);
            }
        """)
        
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw handle dots
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(200, 200, 200))
        
        if self._orientation == Qt.Horizontal:
            # Draw three horizontal dots
            for i in range(3):
                painter.drawEllipse(2, 8 + i * 7, 4, 4)
        else:
            # Draw three vertical dots
            for i in range(3):
                painter.drawEllipse(8 + i * 7, 2, 4, 4)

class PeekButton(QPushButton):
    def __init__(self, parent: Optional['QWidgetType'] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setCursor(Qt.PointingHandCursor)
        self._expanded = False
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.setText("◀")  # Left arrow for collapsed state

    def toggle_state(self, is_expanded: bool) -> None:
        """Toggle the peek button state"""
        self._expanded = is_expanded
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the peek button with custom styling"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw arrow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(200, 200, 200))
        
        if self._expanded:
            points = [QPoint(4, 12), QPoint(12, 12), QPoint(8, 4)]
        else:
            points = [QPoint(4, 4), QPoint(12, 4), QPoint(8, 12)]
            
        painter.drawPolygon(*points)

class FloatingToolbar(QWidget):
    def __init__(self, parent: Optional['QWidgetType'] = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.NoDropShadowWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        
        # Enable mouse tracking for the toolbar itself
        self.setMouseTracking(True)
        
        # Load background image
        self.bg_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    'resources', 'icons', 'Brushed_Bar_horizontal.png')
        self.background_image = QPixmap(self.bg_image_path)
        
        self.is_vertical = True  # Always start in vertical mode
        self.settings = QSettings('SI Opportunity Manager', 'Toolbar')
        self.initUI()
        self.is_pinned = False
        self.drag_position = None
        self.notification_count = 0
        self.last_checked_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        self.viewed_opportunities = set()
        self.viewed_notifications = set()
        self.toaster = ToastNotifier()
        
        # Load last position or set default
        self.load_position()
        
        # Add color animation properties
        self.current_hue = 0.0
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_icon_colors)
        
        # Store original colors for non-animating buttons
        self.static_colors = {
            "new": "#00FF00",  # Keep green
            "close": "#FF0000"  # Keep red
        }
        
        # Initialize with default theme
        self.current_theme = "Rainbow Animation"
        self.color_timer.start(50)  # Start with rainbow animation by default

    def initUI(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create container frame
        self.container = QFrame()
        self.container.setObjectName("toolbar_container")
        self.container.setStyleSheet("""
            QFrame#toolbar_container {
                border: none;
                min-width: 36px;
                max-width: 36px;
                min-height: 460px;
                padding: 0px;
                margin: 0px;
                background-color: transparent;
            }
        """)
        
        # Container layout
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        
        # Create buttons
        icons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'resources', 'icons')
        
        buttons_data = [
            ("new", "new-svgrepo-com.svg", "#00FF00", "Create New Ticket"),  # Green
            ("dashboard", "dashboard-gauge-measure-svgrepo-com.svg", "#FFFFFF", "View Dashboard"),  # White
            ("management", "manager-avatar-svgrepo-com.svg", "#FFFFFF", "Management Portal"),
            ("profile", "profile-default-svgrepo-com.svg", "#FFFFFF", "User Profile"),
            ("pin", "Anchor for Pin toggle.svg", "#FFFFFF", "Pin Toolbar"),
            ("layout", "Veritical to Horizontal.svg", "#FFFFFF", "Toggle Layout"),
            ("opacity", "eye-svgrepo-com.svg", "#FFFFFF", "Adjust Opacity"),
            ("close", "exit-sign-svgrepo-com.svg", "#FF0000", "Exit Application")  # Red
        ]

        self.buttons = {}
        for btn_id, icon_file, icon_color, tooltip in buttons_data:
            print(f"\nDEBUG: Processing button {btn_id}")
            # Skip management button if user is not admin/manager
            if btn_id == "management":
                parent = self.parent()
                print(f"DEBUG: Management button check - Parent: {parent}, Current user: {parent.current_user if parent else None}")
                if not parent or not parent.current_user:
                    print("DEBUG: Skipping management button - No parent or current user")
                    continue
                print(f"DEBUG: User role: {parent.current_user.role}")
                if parent.current_user.role.lower() not in ["admin", "manager"]:
                    print(f"DEBUG: Skipping management button - User role not admin/manager")
                    continue
                print("DEBUG: Adding management button")
                
            btn = QPushButton()
            btn.setFixedSize(36, 36)
            btn.setMouseTracking(True)
            btn.setAttribute(Qt.WA_AlwaysShowToolTips)
            btn.setToolTip(tooltip)
            
            # Set button style with updated tooltip styling
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(43, 43, 43, 0.25);
                    border: none;
                    padding: 0px;
                    margin: 0px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: rgba(60, 60, 60, 0.35);
                }
                QPushButton:pressed {
                    background-color: rgba(30, 30, 30, 0.45);
                }
            """)
            
            # Set global tooltip style
            self.setStyleSheet("""
                QToolTip {
                    background-color: rgba(43, 43, 43, 0.95);
                    color: white;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 4px;
                    font-size: 12px;
                    margin: 0px;
                }
            """)
            
            # Load and set SVG icon
            icon_path = os.path.join(icons_path, icon_file)
            if os.path.exists(icon_path):
                print(f"DEBUG: Loading icon from {icon_path}")
                icon_pixmap = QPixmap(icon_path)
                
                # Convert icon to specified color
                temp_image = icon_pixmap.toImage()
                for x in range(temp_image.width()):
                    for y in range(temp_image.height()):
                        color = temp_image.pixelColor(x, y)
                        if color.alpha() > 0:
                            new_color = QColor(icon_color)
                            new_color.setAlpha(color.alpha())
                            temp_image.setPixelColor(x, y, new_color)
                icon_pixmap = QPixmap.fromImage(temp_image)
                
                # Scale icon to proper size (24x24)
                scaled_pixmap = icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                btn.setIcon(QIcon(scaled_pixmap))
                btn.setIconSize(QSize(24, 24))
            else:
                print(f"DEBUG: Icon file not found: {icon_path}")
            
            # Connect button signals
            if btn_id == "new":
                btn.clicked.connect(lambda: self.parent().show_opportunity_form() if self.parent() and self.parent().current_user else None)
            elif btn_id == "dashboard":
                btn.clicked.connect(lambda: self.parent().show_dashboard() if self.parent() and self.parent().current_user else None)
                # Create and configure notification badge
                self.dashboard_badge = NotificationBadge(btn)
                # Position the badge in the top-right corner with adjusted position
                self.dashboard_badge.move(15, -5)
                self.dashboard_badge.hide()
                self.dashboard_badge.raise_()
                print("DEBUG: Dashboard badge initialized at position:", self.dashboard_badge.pos())
            elif btn_id == "management":
                btn.clicked.connect(lambda: self.parent().show_management_portal() if self.parent() and self.parent().current_user else None)
            elif btn_id == "profile":
                btn.clicked.connect(lambda: self.parent().show_profile() if self.parent() and self.parent().current_user else None)
            elif btn_id == "pin":
                btn.clicked.connect(self.toggle_pin)
                self.pin_button = btn
            elif btn_id == "layout":
                btn.clicked.connect(self.toggle_layout)
                self.layout_button = btn
            elif btn_id == "opacity":
                btn.clicked.connect(self.show_opacity_slider)
            elif btn_id == "close":
                btn.clicked.connect(QApplication.quit)
            
            self.buttons[btn_id] = btn
            print(f"DEBUG: Added button {btn_id} to buttons dictionary")
            self.container_layout.addWidget(btn, 0, Qt.AlignCenter)
        
        # Add container to main layout
        self.main_layout.addWidget(self.container, 0, Qt.AlignCenter)
        
        # Set fixed width for toolbar
        self.setFixedWidth(36)
        self.setMinimumHeight(460)

    def paintEvent(self, event):
        """Custom paint event to draw the metallic background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background image if it exists
        if hasattr(self, 'background_image') and not self.background_image.isNull():
            # Scale and transform the background image based on orientation
            if self.is_vertical:
                transformed_image = self.background_image.transformed(QTransform().rotate(90))
                scaled_image = transformed_image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            else:
                scaled_image = self.background_image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(self.rect(), scaled_image)
        else:
            # Fallback to gradient if image is not available
            gradient = QLinearGradient(0, 0, self.width(), 0)
            gradient.setColorAt(0, QColor(30, 30, 30))
            gradient.setColorAt(0.5, QColor(45, 45, 45))
            gradient.setColorAt(1, QColor(30, 30, 30))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(self.rect(), 2, 2)
            
            # Add subtle highlight at the top
            highlight = QLinearGradient(0, 0, 0, 10)
            highlight.setColorAt(0, QColor(255, 255, 255, 20))
            highlight.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setBrush(highlight)
            painter.drawRect(0, 0, self.width(), 10)
            
            # Add subtle shadow at the bottom
            shadow = QLinearGradient(0, self.height() - 10, 0, self.height())
            shadow.setColorAt(0, QColor(0, 0, 0, 0))
            shadow.setColorAt(1, QColor(0, 0, 0, 40))
            painter.setBrush(shadow)
            painter.drawRect(0, self.height() - 10, self.width(), 10)

    def load_position(self):
        """Load the last saved position or set default position"""
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Set size for vertical layout
        self.setFixedWidth(36)
        self.setMinimumHeight(460)
        self.resize(36, 460)
        
        # Position at right-center by default
        self.move(
            screen.width() - self.width() - 10,
            (screen.height() - self.height()) // 2
        )
        
        # Load saved position if available
        saved_pos = self.settings.value('toolbar_position', None)
        if saved_pos and isinstance(saved_pos, list) and len(saved_pos) == 2:
            try:
                x, y = int(saved_pos[0]), int(saved_pos[1])
                if self.is_position_valid(QPoint(x, y)):
                    self.move(x, y)
            except (ValueError, TypeError):
                pass

    def is_position_valid(self, pos):
        """Check if the given position is valid (visible on any screen)"""
        for screen in QApplication.screens():
            if screen.availableGeometry().contains(pos):
                return True
        return False

    def save_position(self):
        """Save the current position"""
        pos = self.pos()
        self.settings.setValue('toolbar_position', [int(pos.x()), int(pos.y())])
        self.settings.sync()  # Ensure settings are saved immediately

    def toggle_peek(self):
        """Toggle between peeked and expanded states in vertical mode"""
        if not self.is_vertical:
            return
            
        self.is_peeked = not self.is_peeked
        
        if self.is_peeked:
            # Collapse to peek state
            self.container.hide()
            self.handle.hide()
            self.setFixedWidth(30)
            self.peek_button.move(0, self.height() // 2 - 15)
            self.peek_button.toggle_state(False)
            self.peek_button.raise_()  # Ensure peek button stays on top
        else:
            # Expand to full state
            self.setFixedWidth(90)  # Match container width
            self.container.show()
            self.handle.show()
            self.peek_button.move(60, self.height() // 2 - 15)  # Adjusted position
            self.peek_button.toggle_state(True)
            self.peek_button.raise_()  # Ensure peek button stays on top

    def toggle_layout(self):
        """Toggle between vertical and horizontal layout"""
        self.is_vertical = not self.is_vertical
        
        # Reset peek state when switching layouts
        self.is_peeked = False
        
        # Get the layout button's icon
        if hasattr(self, 'layout_button'):
            icon = self.layout_button.icon()
            if not icon.isNull():
                pixmap = icon.pixmap(24, 24)
                
        if self.is_vertical:
            # Rotate the layout icon 90 degrees for vertical mode
            if hasattr(self, 'layout_button'):
                transform = QTransform().rotate(90)
                rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
                self.layout_button.setIcon(QIcon(rotated_pixmap))
            
            # Set vertical layout dimensions
            self.setFixedWidth(36)
            self.setMinimumHeight(460)
            self.container.setStyleSheet("""
                QFrame#toolbar_container {
                    border: none;
                    min-width: 36px;
                    max-width: 36px;
                    min-height: 460px;
                    padding: 0px;
                    margin: 0px;
                    background-color: transparent;
                }
            """)
            
            # Create new vertical layout with no spacing
            new_layout = QVBoxLayout()
            new_layout.setContentsMargins(0, 0, 0, 0)
            new_layout.setSpacing(0)
            
            # Update button sizes for vertical layout
            for btn in self.buttons.values():
                btn.setFixedSize(36, 36)
                btn.setIconSize(QSize(24, 24))
                
                # Update button style with increased transparency
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(43, 43, 43, 0.25);
                        border: none;
                        padding: 0px;
                        margin: 0px;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: rgba(60, 60, 60, 0.35);
                    }
                    QPushButton:pressed {
                        background-color: rgba(30, 30, 30, 0.45);
                    }
                """)
        else:
            # Reset layout icon rotation for horizontal mode
            if hasattr(self, 'layout_button'):
                self.layout_button.setIcon(QIcon(pixmap))
            
            # Set horizontal layout dimensions
            self.setFixedHeight(56)  # Reduced height to better fit background
            self.setMinimumWidth(650)  # Adjusted minimum width
            self.container.setStyleSheet("""
                QFrame#toolbar_container {
                    border: none;
                    min-height: 56px;
                    max-height: 56px;
                    min-width: 650px;
                    padding: 0px;
                    margin: 0px;
                    background-color: transparent;
                }
            """)
            
            # Create new horizontal layout with adjusted margins
            new_layout = QHBoxLayout()
            new_layout.setContentsMargins(80, 2, 80, 2)  # Reduced margins
            new_layout.setSpacing(8)  # Increased spacing between buttons
            
            # Update button sizes for horizontal layout
            for btn in self.buttons.values():
                btn.setFixedSize(48, 48)  # Smaller buttons
                btn.setIconSize(QSize(28, 28))  # Slightly smaller icons
                
                # Update button style with increased transparency
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(43, 43, 43, 0.25);
                        border: none;
                        padding: 4px;
                        margin: 0px;
                        border-radius: 12px;
                    }
                    QPushButton:hover {
                        background-color: rgba(60, 60, 60, 0.35);
                    }
                    QPushButton:pressed {
                        background-color: rgba(30, 30, 30, 0.45);
                    }
                """)
        
        # Re-add buttons in the correct order
        button_order = ['new', 'dashboard', 'management', 'profile', 'pin', 'layout', 'opacity', 'close']
        print("\nDEBUG: Enforcing button order")
        print(f"DEBUG: Available buttons: {list(self.buttons.keys())}")
        
        # Check if management button should be included
        parent = self.parent()
        if parent and parent.current_user and parent.current_user.role.lower() in ["admin", "manager"]:
            print("DEBUG: User has admin/manager role, management button should be present")
        else:
            print("DEBUG: User does not have admin/manager role, management button should not be present")
            if "management" in button_order:
                button_order.remove("management")
        
        # Add buttons in order
        for btn_id in button_order:
            if btn_id in self.buttons:
                print(f"DEBUG: Adding button {btn_id} to layout")
                new_layout.addWidget(self.buttons[btn_id], 0, Qt.AlignCenter)
            else:
                print(f"DEBUG: Button {btn_id} not found in buttons dictionary")
        
        # Set the new layout
        QWidget().setLayout(self.container.layout())
        self.container.setLayout(new_layout)
        
        # Update window size and position
        self.load_position()
        
        # Force a repaint
        self.update()

    def update_window_flags(self):
        """Update window flags based on pin state"""
        try:
            # Store current position and visibility
            pos = self.pos()
            was_visible = self.isVisible()
            
            # Hide window before changing flags
            self.hide()
            
            # Set base flags
            flags = Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
            
            # Add WindowStaysOnTopHint if pinned
            if self.is_pinned:
                flags |= Qt.WindowStaysOnTopHint
            
            # Apply new flags
            self.setWindowFlags(flags)
            
            # Restore visibility and position
            if was_visible:
                self.show()
                self.raise_()
                self.move(pos)
                
        except Exception as e:
            print(f"Error updating window flags: {str(e)}")
            # Ensure window is shown even if there's an error
            self.show()
            self.raise_()
            
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        # Ensure minimum size based on orientation
        if self.is_vertical:
            if self.width() != 76:  # Fixed width for vertical layout
                self.setFixedWidth(76)
            if self.height() < 500:  # Minimum height for vertical layout
                self.setMinimumHeight(500)
        else:
            if self.width() < 800:  # Minimum width for horizontal layout
                self.setMinimumWidth(800)
            if self.height() != 80:  # Fixed height for horizontal layout
                self.setFixedHeight(80)

    def moveEvent(self, event):
        """Handle move events to keep window within available screen space and save position"""
        super().moveEvent(event)
        
        # Get the screen containing the center of the window
        center = self.geometry().center()
        screen = QApplication.screenAt(center)
        
        if screen:
            # Get available geometry for the current screen
            available_geometry = screen.availableGeometry()
            current_pos = self.pos()
            new_pos = current_pos
            
            # Keep window within screen bounds
            if current_pos.x() < available_geometry.left():
                new_pos.setX(available_geometry.left())
            elif current_pos.x() + self.width() > available_geometry.right():
                new_pos.setX(available_geometry.right() - self.width())
                
            if current_pos.y() < available_geometry.top():
                new_pos.setY(available_geometry.top())
            elif current_pos.y() + self.height() > available_geometry.bottom():
                new_pos.setY(available_geometry.bottom() - self.height())
                
            # Only move if position changed and not dragging
            if new_pos != current_pos and self.drag_position is None:
                self.move(new_pos)
            
            # Save position after manual move (when not dragging)
            if self.drag_position is None:
                self.save_position()

    def check_updates(self):
        """Check for new opportunities and notifications"""
        if not self.parent() or not self.parent().current_user:
            return
            
        current_time = datetime.now(timezone.utc)
        print(f"\nDEBUG: Checking updates at {current_time}")
        print(f"DEBUG: Last check time was {self.last_checked_time}")
        
        db = SessionLocal()
        try:
            # Check new opportunities (notify about all new tickets)
            new_opportunities = db.query(Opportunity).filter(
                Opportunity.status.ilike("New"),  # Case-insensitive status check
                Opportunity.creator_id != str(self.parent().current_user.id)  # Don't notify for own tickets
            ).all()
            
            # Count unviewed opportunities (only those that haven't been viewed)
            unviewed_opportunities = [opp for opp in new_opportunities if opp.id not in self.viewed_opportunities]
            print(f"DEBUG: Found {len(unviewed_opportunities)} unviewed opportunities")
            
            # Check new notifications (these are already filtered by user_id)
            new_notifications = db.query(Notification).filter(
                Notification.user_id == str(self.parent().current_user.id),
                Notification.read == False
            ).all()
            
            print(f"DEBUG: Found {len(new_notifications)} new notifications")
            
            # Update total notification count (unviewed opportunities + unread notifications)
            total_count = len(unviewed_opportunities) + len(new_notifications)
            print(f"DEBUG: Total notification count: {total_count}")
            
            # Only update notification count if it's different
            if total_count != self.notification_count:
                self.notification_count = total_count
                self.update_notification_badge()
            
            # Show aggregate notification for new opportunities only if there are new ones since last check
            if len(unviewed_opportunities) > 0 and current_time > self.last_checked_time:
                self.show_windows_notification(
                    "New Opportunities",
                    f"There are {len(unviewed_opportunities)} new opportunities in the dashboard"
                )
            
            # Show aggregate notification for new notifications only if there are new ones since last check
            if len(new_notifications) > 0 and current_time > self.last_checked_time:
                self.show_windows_notification(
                    "New Notifications",
                    f"You have {len(new_notifications)} new notifications"
                )
                # Add all new notifications to viewed set
                for notif in new_notifications:
                    self.viewed_notifications.add(notif.id)
            
            # Update last check time only for future notifications
            self.last_checked_time = current_time
            
        except Exception as e:
            print(f"Error checking updates: {str(e)}")
        finally:
            db.close()

    def show_windows_notification(self, title, message):
        """Show Windows notification"""
        try:
            # Ensure the toaster is initialized
            if not hasattr(self, 'toaster'):
                self.toaster = ToastNotifier()
            
            # Show the notification in a non-blocking way
            self.toaster.show_toast(
                title,
                message,
                duration=5,
                threaded=True,
                icon_path=None  # Let Windows use the app's default icon
            )
            print(f"DEBUG: Showing notification - Title: {title}, Message: {message}")
        except Exception as e:
            print(f"Error showing notification: {str(e)}")

    def update_notification_badge(self):
        """Update the notification badge on the dashboard button"""
        try:
            print(f"DEBUG: Updating notification badge. Count: {self.notification_count}")
            if self.notification_count > 0:
                # Set the text and ensure it's visible
                self.dashboard_badge.setText(str(self.notification_count))
                self.dashboard_badge.show()
                
                # Position in top-right corner of the button
                button_rect = self.buttons["dashboard"].geometry()
                self.dashboard_badge.move(button_rect.right() - 15, button_rect.top() - 5)
                self.dashboard_badge.raise_()
                print("DEBUG: Showing notification badge")
            else:
                self.dashboard_badge.hide()
                print("DEBUG: Hiding notification badge")
        except Exception as e:
            print(f"Error updating notification badge: {str(e)}")
        
    def toggle_pin(self):
        """Toggle pin state and update window flags"""
        # Update pin state
        self.is_pinned = not self.is_pinned
        
        # Update pin button appearance with blue highlight when pinned
        if hasattr(self, 'pin_button'):
            if self.is_pinned:
                self.pin_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(25, 118, 210, 0.6);
                        color: white;
                        border: none;
                        padding: 4px;
                        border-radius: 12px;
                        font-size: 10px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: rgba(30, 136, 229, 0.7);
                    }
                    QPushButton:pressed {
                        background-color: rgba(21, 101, 192, 0.8);
                    }
                """)
            else:
                # Reset to default dark style when unpinned
                self.pin_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(43, 43, 43, 0.25);
                        color: white;
                        border: none;
                        padding: 4px;
                        border-radius: 12px;
                        font-size: 10px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: rgba(60, 60, 60, 0.35);
                    }
                    QPushButton:pressed {
                        background-color: rgba(30, 30, 30, 0.45);
                    }
                """)
        
        # Update window flags and ensure visibility
        self.update_window_flags()
        QApplication.processEvents()  # Process pending events
        self.show()
        self.raise_()
        
    def show_opacity_slider(self):
        """Show a popup with opacity slider control"""
        popup = QDialog(self)
        popup.setWindowTitle("Adjust Opacity")
        popup.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        
        # Create layout
        layout = QVBoxLayout(popup)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Add title label
        title = QLabel("Adjust Toolbar Opacity")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Create slider
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(20)
        slider.setMaximum(100)
        slider.setValue(int(self.windowOpacity() * 100))
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #3d3d3d;
                height: 8px;
                background: #2b2b2b;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #1976D2;
                border: none;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #1E88E5;
            }
        """)
        
        # Create value label
        value_label = QLabel(f"{slider.value()}%")
        value_label.setStyleSheet("color: white; font-size: 12px;")
        value_label.setAlignment(Qt.AlignCenter)
        
        # Update opacity when slider moves
        def update_opacity(value):
            self.setWindowOpacity(value / 100)
            value_label.setText(f"{value}%")
        
        slider.valueChanged.connect(update_opacity)
        
        # Add widgets to layout
        layout.addWidget(slider)
        layout.addWidget(value_label)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        close_btn.clicked.connect(popup.close)
        layout.addWidget(close_btn)
        
        # Style popup
        popup.setStyleSheet("""
            QDialog {
                background-color: rgba(43, 43, 43, 0.98);
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3d3d3d;
                height: 8px;
                background: #2b2b2b;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #1976D2;
                border: none;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #1E88E5;
            }
        """)
        
        # Set size and position
        popup.setFixedSize(300, 150)
        popup.move(
            self.mapToGlobal(QPoint(0, 0)).x() + (self.width() - popup.width()) // 2,
            self.mapToGlobal(QPoint(0, self.height())).y()
        )
        
        popup.exec_()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_pinned:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_position is not None and not self.is_pinned:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def update_icon_colors(self):
        """Update the colors of the icons in a rainbow pattern"""
        try:
            self.current_hue = (self.current_hue + 0.005) % 1.0  # Slowly increment hue
            
            # Convert HSV to RGB (hue cycles, full saturation and value)
            color = QColor.fromHsvF(self.current_hue, 0.7, 1.0)
            
            # Update each button's icon color
            for btn_id, btn in self.buttons.items():
                # Skip buttons with static colors
                if btn_id in self.static_colors:
                    continue
                    
                # Get the current icon
                icon = btn.icon()
                if not icon.isNull():
                    pixmap = icon.pixmap(24, 24)
                    if not pixmap.isNull():
                        # Convert to image for color manipulation
                        image = pixmap.toImage()
                        
                        # Apply new color while preserving alpha
                        for x in range(image.width()):
                            for y in range(image.height()):
                                pixel_color = image.pixelColor(x, y)
                                if pixel_color.alpha() > 0:
                                    new_color = QColor(color)
                                    new_color.setAlpha(pixel_color.alpha())
                                    image.setPixelColor(x, y, new_color)
                        
                        # Convert back to pixmap and update button
                        colored_pixmap = QPixmap.fromImage(image)
                        if not colored_pixmap.isNull():
                            btn.setIcon(QIcon(colored_pixmap))
            
            return 0  # Return success to Windows message handler
            
        except Exception as e:
            print(f"Error updating icon colors: {str(e)}\nTraceback: {traceback.format_exc()}")
            return 0  # Return success even on error to prevent Windows message handler issues

    def closeEvent(self, event):
        """Stop the color timer when closing"""
        self.color_timer.stop()
        super().closeEvent(event)

    def apply_static_theme(self):
        """Apply a static color theme to all icons"""
        theme_colors = {
            "White Icons": "#FFFFFF",
            "Blue Theme": "#2196F3",
            "Green Theme": "#4CAF50",
            "Purple Theme": "#9C27B0"
        }
        
        print(f"Applying static theme: {self.current_theme}")
        if self.current_theme in theme_colors:
            color = QColor(theme_colors[self.current_theme])
            print(f"Using color: {color.name()}")
            
            # Update each button's icon color
            for btn_id, btn in self.buttons.items():
                # Skip buttons with static colors
                if btn_id in self.static_colors:
                    print(f"Skipping static color button: {btn_id}")
                    continue
                    
                # Get the current icon
                icon = btn.icon()
                if not icon.isNull():
                    print(f"Updating icon for button: {btn_id}")
                    pixmap = icon.pixmap(24, 24)
                    
                    # Convert to image for color manipulation
                    image = pixmap.toImage()
                    
                    # Apply new color while preserving alpha
                    for x in range(image.width()):
                        for y in range(image.height()):
                            pixel_color = image.pixelColor(x, y)
                            if pixel_color.alpha() > 0:
                                new_color = QColor(color)
                                new_color.setAlpha(pixel_color.alpha())
                                image.setPixelColor(x, y, new_color)
                    
                    # Convert back to pixmap and update button
                    colored_pixmap = QPixmap.fromImage(image)
                    btn.setIcon(QIcon(colored_pixmap))
        else:
            print(f"Warning: Unknown theme color: {self.current_theme}")

    def update_theme(self, new_theme):
        """Update the toolbar's theme"""
        print(f"Updating theme to: {new_theme}")
        self.current_theme = new_theme
        
        # Stop color timer if it's running
        if self.color_timer.isActive():
            self.color_timer.stop()
        
        # Start or stop color timer based on theme
        if new_theme == "Rainbow Animation":
            self.color_timer.start(50)  # Update every 50ms for smooth animation
        else:
            self.apply_static_theme()

    def clear_notifications(self):
        """Clear all notifications and reset the badge"""
        db = SessionLocal()
        try:
            # Mark all notifications as read
            notifications = db.query(Notification).filter(
                Notification.user_id == str(self.parent().current_user.id),
                Notification.read == False
            ).all()
            
            for notification in notifications:
                notification.read = True
            
            db.commit()
            
            # Reset notification count and hide badge
            self.notification_count = 0
            if hasattr(self, 'dashboard_badge'):
                self.dashboard_badge.hide()
            
            # Clear viewed sets
            self.viewed_opportunities.clear()
            self.viewed_notifications.clear()
            
        except Exception as e:
            print(f"Error clearing notifications: {str(e)}")
        finally:
            db.close()

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set fixed size
        self.setFixedSize(300, 300)
            
        # Set window flags to ensure it stays on top and is frameless
        self.setWindowFlags(
            Qt.Window |  # Make it an independent window
            Qt.FramelessWindowHint |  # No window frame
            Qt.WindowStaysOnTopHint |  # Stay on top
            Qt.Tool  # Don't show in taskbar
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add logo
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'resources', 'SI Opportunity Manager LOGO.png.png')
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_pixmap = logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)
        
        # Add loading label
        self.loading_label = QLabel("Loading...")
        self.loading_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_label)
        
        # Add stretch to center vertically
        layout.addStretch()
        
        # Set widget style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 15px;
            }
        """)
        
        # Center on screen
        self.center_on_screen()
        
    def center_on_screen(self):
        # Get the screen geometry
        screen = QApplication.primaryScreen().availableGeometry()
        # Calculate center position
        center_x = (screen.width() - self.width()) // 2
        center_y = (screen.height() - self.height()) // 2
        # Move to center
        self.move(screen.left() + center_x, screen.top() + center_y)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.drawRoundedRect(self.rect(), 15, 15)  # Added rounded corners

class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QMainWindow] = None) -> None:
        super().__init__(parent)
        
        # Initialize asyncio loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Create timer for asyncio events
        self.asyncio_timer = QTimer(self)
        self.asyncio_timer.timeout.connect(self._process_asyncio_events)
        self.asyncio_timer.start(10)  # Process every 10ms
        
        # Initialize other attributes
        self.current_user = None
        self.opportunity_form = None
        self.management_portal = None
        self.profile = None
        self.websocket = None
        self.websocket_task = None
        self.notification_queue = asyncio.Queue()
        
        # Initialize UI
        self.initUI()
        
        # Hide the main window - only auth widget should be visible
        self.hide()
        
        # Show auth widget
        self.auth.show()
        
    def _process_asyncio_events(self):
        """Process pending asyncio events"""
        try:
            # Only process events if the loop is running and not closed
            if self.loop and not self.loop.is_closed():
                # Process pending callbacks without blocking
                self.loop._ready.clear() if hasattr(self.loop, '_ready') else None
        except Exception as e:
            print(f"Error processing asyncio events: {e}")
            
    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Stop asyncio timer first
            if hasattr(self, 'asyncio_timer'):
                self.asyncio_timer.stop()
            
            # Clean up asyncio loop safely
            if hasattr(self, 'loop') and self.loop and not self.loop.is_closed():
                try:
                    # Cancel any pending tasks
                    pending = asyncio.all_tasks(self.loop)
                    for task in pending:
                        task.cancel()
                    
                    # Try to clean up gracefully
                    if pending:
                        self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception as loop_error:
                    print(f"Error cleaning up asyncio loop: {loop_error}")
                finally:
                    try:
                        self.loop.close()
                    except Exception as close_error:
                        print(f"Error closing loop: {close_error}")
            
            # Hide all windows
            for attr_name in ['toolbar', 'dashboard', 'opportunity_form', 'settings', 'auth', 'account_creation', 'management_portal']:
                if hasattr(self, attr_name):
                    widget = getattr(self, attr_name)
                    if widget and hasattr(widget, 'hide'):
                        try:
                            widget.hide()
                        except Exception as hide_error:
                            print(f"Error hiding {attr_name}: {hide_error}")
                
            # Accept the close event
            event.accept()
        except Exception as e:
            print(f"Error during close: {str(e)}")
            event.accept()

    async def init_websocket(self):
        """Initialize WebSocket connection"""
        if not self.current_user:
            return
            
        try:
            self.websocket = await websockets.connect(
                f"ws://localhost:8000/ws/notifications/{self.current_user.id}"
            )
            self.websocket_task = asyncio.create_task(self.handle_notifications())
        except Exception as e:
            print(f"Error initializing WebSocket: {e}")
            
    def start_websocket(self):
        """Start WebSocket connection in the event loop"""
        if self.current_user and self.loop and not self.loop.is_closed():
            try:
                asyncio.run_coroutine_threadsafe(self.init_websocket(), self.loop)
            except RuntimeError as e:
                print(f"WebSocket initialization skipped due to event loop issue: {e}")
                # Continue without WebSocket - the app will still function

    def on_authentication(self, user):
        """Handle successful authentication"""
        print(f"DEBUG: User authenticated - Role: {user.role}")
        self.current_user = user
        
        # Hide auth widget immediately
        self.auth.hide()
        
        # Create toolbar
        self.toolbar = FloatingToolbar(self)
        self.toolbar.show()
        
        # Start WebSocket connection
        self.start_websocket()
        
        # Recreate dashboard with current user
        if hasattr(self, 'dashboard'):
            self.dashboard.deleteLater()
        self.dashboard = DashboardWidget(current_user=user)
        
        # Create management portal if user is admin/manager
        if user.role.lower() in ["admin", "manager"]:
            print("DEBUG: Creating management portal for admin/manager")
            self.management_portal = ManagementPortal(user, self)
            self.management_portal.refresh_needed.connect(self.on_management_refresh)
        
        # Initialize notification system
        db = SessionLocal()
        try:
            # Get last login time or use a default (24 hours ago)
            last_login = db.query(User.last_login).filter(User.id == user.id).scalar()
            if last_login:
                self.toolbar.last_checked_time = last_login
            else:
                # For new users or first login, check last 24 hours
                self.toolbar.last_checked_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            # Update last login time
            user_obj = db.query(User).filter(User.id == user.id).first()
            if user_obj:
                user_obj.last_login = datetime.now(timezone.utc)
                db.commit()
            
            # Start notification check timer
            self.toolbar.check_updates()
            
        except Exception as e:
            print(f"Error initializing notifications: {e}")
        finally:
            db.close()

    def on_account_created(self, user):
        self.account_creation.hide()
        self.auth.show()

    def on_new_opportunity(self, opportunity):
        """Handle newly created opportunity"""
        if hasattr(self, 'toolbar'):
            # Update notification count
            self.toolbar.notification_count += 1
            self.toolbar.update_notification_badge()
            # Show notification
            self.toolbar.show_windows_notification(
                "New SI Opportunity",
                f"Ticket: {opportunity.title}\nVehicle: {opportunity.display_title}\nDescription: {opportunity.description[:100]}..."
            )

    def show_profile(self):
        """Show the user profile window"""
        if not self.profile:
            self.profile = ProfileWidget(self.current_user)
            self.profile.profile_updated.connect(self.on_profile_updated)
        self.profile.show()
        self.profile.activateWindow()

    def on_profile_updated(self):
        """Handle profile updates"""
        print("Profile update received")
        db = SessionLocal()
        try:
            # Refresh current user data
            print(f"Refreshing user data for ID: {self.current_user.id}")
            self.current_user = db.query(User).filter(User.id == self.current_user.id).first()
            print(f"User data refreshed, theme: {self.current_user.icon_theme}")
            
            # Update toolbar theme if it exists
            if hasattr(self, 'toolbar'):
                print("Updating toolbar theme")
                self.toolbar.update_theme(self.current_user.icon_theme)
            else:
                print("Warning: Toolbar not found")
            
            # Update other windows that might need refreshing
            if hasattr(self, 'dashboard'):
                print("Refreshing dashboard")
                self.dashboard.load_opportunities()
            if hasattr(self, 'management_portal') and self.management_portal is not None:
                try:
                    print("Refreshing management portal")
                    self.management_portal.load_data()
                except Exception as e:
                    print(f"Error updating management portal: {str(e)}\nTraceback: {traceback.format_exc()}")
        except Exception as e:
            print(f"Error in profile update: {str(e)}\nTraceback: {traceback.format_exc()}")
        finally:
            db.close()
            print("Profile update completed")

    def show_opportunity_form(self):
        # Create form if it doesn't exist
        if not self.opportunity_form:
            self.opportunity_form = OpportunityForm(str(self.current_user.id))
            # Connect the opportunity created signal to the toolbar
            self.opportunity_form.opportunity_created.connect(self.on_new_opportunity)
        self.opportunity_form.show()
        self.opportunity_form.raise_()
        self.opportunity_form.activateWindow()
        
    def show_dashboard(self):
        """Show and refresh dashboard"""
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please log in first")
            return
            
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()
        self.dashboard.load_opportunities()
        if hasattr(self, 'toolbar'):
            self.toolbar.clear_notifications()
        
    def show_account_creation(self):
        self.account_creation.show()
        self.account_creation.raise_()
        self.account_creation.activateWindow()
        
    def show_management_portal(self):
        """Show management portal for admins and managers"""
        if not self.current_user or self.current_user.role not in ["admin", "manager"]:
            QMessageBox.warning(self, "Access Denied", "You don't have permission to access the management portal.")
            return
            
        if not self.management_portal:
            self.management_portal = ManagementPortal(self.current_user, self)
            self.management_portal.refresh_needed.connect(self.on_management_refresh)
            
        self.management_portal.show()
        self.management_portal.raise_()
        self.management_portal.activateWindow()
        self.management_portal.load_data()
        
    def on_management_refresh(self):
        """Handle refresh requests from management portal"""
        if hasattr(self, 'dashboard'):
            self.dashboard.load_opportunities()
            
    def initUI(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add logo at the top
        logo_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'SI Opportunity Manager LOGO.png.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Initialize windows (hidden initially)
        self.auth = AuthWidget()
        self.auth.authenticated.connect(self.on_authentication)
        self.auth.create_account_requested.connect(self.show_account_creation)
        
        self.account_creation = AccountCreationWidget()
        self.account_creation.account_created.connect(self.on_account_created)
        
        # Initialize dashboard with None user (will be set after authentication)
        self.dashboard = DashboardWidget()
        self.opportunity_form = None
        self.settings = SettingsWidget()
        self.profile = None
        self.management_portal = None
        
        # Show auth widget first
        self.auth.show()

def main():
    # Enable High DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Enable additional attributes after QApplication creation
    QApplication.setAttribute(Qt.AA_UseStyleSheetPropagationInWidgetStyles)
    QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    
    # Set application-wide stylesheet with tooltip style
    app.setStyleSheet("""
        QToolTip { 
            background-color: rgba(43, 43, 43, 0.95);
            color: white;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 4px;
            font-size: 12px;
            margin: 0px;
        }
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            color: #ffffff;
            font-size: 12px;
        }
    """)
    
    # Create main window but don't show it (only auth widget should be visible)
    window = MainWindow()
    # Don't show the main window - only the auth widget will be shown
    
    # Start the event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 