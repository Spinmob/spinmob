if __name__ == '__main__': import spinmob

import pyqtgraph
QPalette = pyqtgraph.QtGui.QPalette
QColor   = pyqtgraph.QtGui.QColor
Qt       = pyqtgraph.QtCore.Qt

qApp = pyqtgraph.QtCore.QCoreApplication.instance()

qApp.setStyle("Fusion")

dark_palette = QPalette()

light_gray = QColor('#303030')
dark_gray  = QColor('#222')
highlight  = QColor('#47A')

dark_palette.setColor(QPalette.Window,          light_gray)
dark_palette.setColor(QPalette.WindowText,      Qt.white)

dark_palette.setColor(QPalette.Base,            dark_gray)
dark_palette.setColor(QPalette.AlternateBase,   light_gray)

dark_palette.setColor(QPalette.ToolTipBase,     Qt.white)
dark_palette.setColor(QPalette.ToolTipText,     Qt.white)

dark_palette.setColor(QPalette.Text,            Qt.white)

dark_palette.setColor(QPalette.Button,          light_gray)
dark_palette.setColor(QPalette.ButtonText,      Qt.white)

dark_palette.setColor(QPalette.BrightText,      Qt.red)

dark_palette.setColor(QPalette.Link,            highlight)
dark_palette.setColor(QPalette.Highlight,       highlight)
dark_palette.setColor(QPalette.HighlightedText, Qt.white)

qApp.setPalette(dark_palette)

# Individual control tweaks
qApp.setStyleSheet(
    """
    :disabled {color: #777777;} 
    QCheckBox::indicator { border: 1px solid white; }
    QCheckBox::indicator:checked  {border: 1px solid white;   background-color: #C77;}
    QCheckBox::indicator:disabled {border: 1px solid #777777;}
    
    QToolTip { color: #ffffff; background-color: #AA4444; border: none;}

    """)

    



if __name__ == '__main__':
    # Standard Fusion theme
    spinmob._qtapp.setStyle('Fusion')

    import mcphysics
    self = mcphysics.instruments.adalm2000()
    #self.button_connect.click()