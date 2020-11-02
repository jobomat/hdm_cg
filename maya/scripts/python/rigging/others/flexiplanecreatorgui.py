__author__ = 'Aksel'
from qtshim import QtGui, QtCore, Signal


class FlexiCreatorController(QtCore.QObject):
    """
    controllerObject to store signals emitted from Maya
    """
    selectionChanged = Signal(list)


class FlexiCreatorWindow(QtGui.QMainWindow):
    """
    windowClass to store signals emitted to Maya
    """
    # signal that emits text from name box when initiate button is clicked
    createClicked = Signal(str)


# noinspection PyUnresolvedReferences
class FlexiCreatorGui(object):
    """
    GUI that hold widgets for flexiplane creator
    """
    def __init__(self):
        # initial window for GUI
        self.window = FlexiCreatorWindow()

        # main container
        self.container = QtGui.QWidget()
        # initial controller
        self.controller = FlexiCreatorController()

    def create(self, controller, parent=None):
        """
        create GUI for flexiplane module
        :param controller: hold signal emitted from maya
        :param parent:
        :return:
        """
        self.window = FlexiCreatorWindow(parent)
        self.window.setWindowTitle('Flexiplane Creator')
        self.window.setMinimumHeight(128)
        self.window.setFixedWidth(300)
        status_bar = QtGui.QStatusBar()
        # create status bar
        # main container widget
        container_layout = QtGui.QVBoxLayout(self.container)
        self.container.setLayout(container_layout)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setSpacing(0)
        container_layout.setAlignment(QtCore.Qt.AlignTop)


        #name widget
        #
        name_widget = QtGui.QWidget(self.container)
        name_widget.setLayout(QtGui.QVBoxLayout())
        name_widget.layout().setContentsMargins(0, 0, 0, 0)
        name_widget.layout().setSpacing(2)
        name_widget.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                  QtGui.QSizePolicy.Fixed)
        container_layout.addWidget(name_widget)

        name_splitter = Splitter('NAME')
        name_widget.layout().addWidget(name_splitter)

        name_text_layout = QtGui.QHBoxLayout()
        name_text_layout.setContentsMargins(4, 0, 4, 0)
        name_text_layout.setSpacing(2)
        name_widget.layout().addLayout(name_text_layout)

        name_lb = QtGui.QLabel('Prefix:')
        name_le = QtGui.QLineEdit()
        name_text_layout.addWidget(name_lb)
        name_text_layout.addWidget(name_le)

        reg_ex = QtCore.QRegExp("^(?!^_)[a-zA-Z0-9_]+")
        text_validator = QtGui.QRegExpValidator(reg_ex, name_le)
        name_le.setValidator(text_validator)

        container_layout.addSpacerItem(QtGui.QSpacerItem(2, 2, QtGui.QSizePolicy.Expanding))

        #create widget
        #

        create_widget = QtGui.QWidget(self.container)
        create_widget.setLayout(QtGui.QVBoxLayout())
        create_widget.layout().setContentsMargins(0, 0, 0, 0)
        create_widget.layout().setSpacing(0)
        create_widget.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                    QtGui.QSizePolicy.Fixed)
        container_layout.addWidget(create_widget)

        create_splitter = Splitter('CREATE')
        create_widget.layout().addWidget(create_splitter)

        create_bttn_layout = QtGui.QHBoxLayout()
        create_bttn_layout.setContentsMargins(4, 0, 4, 0)
        create_bttn_layout.setSpacing(2)
        create_widget.layout().addLayout(create_bttn_layout)

        create_lb = QtGui.QLabel('e.g.')
        create_bttn = QtGui.QPushButton('create')
        create_bttn.setFixedHeight(20)
        create_bttn.setFixedWidth(55)

        create_bttn_layout.addWidget(create_lb)
        create_bttn_layout.addWidget(create_bttn)

        #credit widget
        #
        credit_widget = QtGui.QWidget()
        credit_widget.setLayout(QtGui.QVBoxLayout())
        credit_widget.layout().setContentsMargins(0, 0, 0, 0)
        credit_widget.layout().setSpacing(2)
        credit_widget.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                    QtGui.QSizePolicy.Fixed)
        container_layout.addWidget(credit_widget)

        credit_splitter = Splitter('AUTHOR')
        credit_widget.layout().addWidget(credit_splitter)

        credit_lb = QtGui.QLabel('--- Aksel Fleuriau-Moscoe ---')
        #credit_widget.layout().addWidget(credit_lb)
        credit_layout = QtGui.QHBoxLayout()
        credit_layout.setContentsMargins(4, 0, 4, 0)
        credit_layout.setSpacing(2)
        credit_widget.layout().addLayout(credit_layout)

        credit_layout.addWidget(credit_lb)

        credit_layout.setAlignment(QtCore.Qt.AlignHCenter)
        credit_widget.layout().addSpacerItem(QtGui.QSpacerItem(5, 5, QtGui.QSizePolicy.Expanding))

        container_layout.addLayout(SplitterLayout())
        end_splitter = Splitter()
        container_layout.addWidget(end_splitter)


        #connect modifiers
        #

        # create widget to hold create widgets group parented to main container
        #create_box = QtGui.QWidget(self.container)
        # create widget to hold name widgets group parented to create box
        #name_box = QtGui.QWidget(create_box)
        # create label parented to name box
        #name_label = QtGui.QLabel('Prefix:', name_box)
        #name_field = QtGui.QLineEdit(name_box)
        #create_button = QtGui.QPushButton('create', create_box)
        #label_box = QtGui.QWidget(self.container)
        #author_label = QtGui.QLabel('--Author: Aksel Fleuriau-Moscoe--', label_box)

        #--------------------------------------------------------------------#

        def _get_flexiplane_settings():
            text = str(name_le.text()).strip()

            return text

        #--------------------------------------------------------------------#
        def _update_example_rename():
            example_text = ''
            placer_text ='_flexiplane...1'

            text = _get_flexiplane_settings()
            if not text:
                create_lb.setText('<font color=#646464>e.g. \'%s\'</font>' % placer_text)
                return

            example_text += '%s_flexiplane...1' % text
            create_lb.setText('<font color=#646464>e.g. \'%s\'</font>' % example_text)

        name_le.textChanged.connect(_update_example_rename)
        _update_example_rename()
        #--------------------------------------------------------------------#
        def on_create_click():
            """
            emits text in name box when create button is clicked
            """
            self.window.createClicked.emit(name_le.text())
        create_bttn.clicked.connect(on_create_click)

        def update_status_bar(new_sel):
            if not new_sel:
                txt = 'Nothing selected.'
            elif len(new_sel) == 1:
                txt = '%s selected.' % new_sel[0]
            else:
                txt = '%s objects selected' % len(new_sel)
            status_bar.showMessage(txt)
        controller.selectionChanged.connect(update_status_bar)

        #container_layout.addWidget(create_box)
        #container_layout.addWidget(label_box)
        #create_layout = QtGui.QVBoxLayout(create_box)
        #create_box.setLayout(create_layout)
        #create_layout.addWidget(name_box)
        #create_layout.addWidget(create_button)
        #name_layout = QtGui.QHBoxLayout(name_box)
        #name_box.setLayout(name_layout)
        #name_layout.addWidget(name_label)
        #name_layout.addWidget(name_field)
        #label_layout = QtGui.QVBoxLayout(label_box)
        #label_box.setLayout(label_layout)
        #label_layout.addWidget(author_label)

        self.window.setCentralWidget(self.container)

        self.window.setStatusBar(status_bar)

        return self.window
#------------------------------------------------------------------------------#

class Splitter(QtGui.QWidget):
    def __init__(self, text=None, shadow=True, color=(150, 150, 150)):
        QtGui.QWidget.__init__(self)

        self.setMinimumHeight(2)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(QtCore.Qt.AlignVCenter)

        first_line = QtGui.QFrame()
        first_line.setFrameStyle(QtGui.QFrame.HLine)
        self.layout().addWidget(first_line)

        main_color = 'rgba( %s, %s, %s, 255)' % color
        shadow_color = 'rgba( 45, 45, 45, 255)'

        bottom_border = ''
        if shadow:
            bottom_border = 'border-bottom:1px solid %s' % shadow_color

        style_sheet = "border:0px solid rgba(0,0,0,0);\
                       background-color: %s;\
                       max-height:1px;\
                       %s;" % (main_color, bottom_border)

        first_line.setStyleSheet(style_sheet)

        if text is None:
            return
        first_line.setMaximumWidth(5)

        font = QtGui.QFont()
        font.setBold(True)

        text_width = QtGui.QFontMetrics(font)
        width = text_width.width(text) + 6

        label = QtGui.QLabel()
        label.setText(text)
        label.setFont(font)
        label.setMaximumWidth(width)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.layout().addWidget(label)

        second_line = QtGui.QFrame()
        second_line.setFrameStyle(QtGui.QFrame.HLine)
        second_line.setStyleSheet(style_sheet)
        self.layout().addWidget(second_line)


class SplitterLayout(QtGui.QHBoxLayout):
    def __init__(self):
        QtGui.QHBoxLayout.__init__(self)
        self.setContentsMargins(40, 2, 40, 2)

        splitter = Splitter(shadow=False, color=(60, 60, 60))
        splitter.setFixedHeight(1)

        self.addWidget(splitter)


def _py_test():
    import random

    controller = FlexiCreatorController()

    def next_sel():
        return random.choice([
            [],
            ['single'],
            ['single', 'double']
        ])

    def on_create(prefix):
        print 'Creating %s Flexiplane' % prefix
        controller.selectionChanged.emit(next_sel())

    app = QtGui.QApplication([])
    win = FlexiCreatorGui().create(controller)
    win.createClicked.connect(on_create)
    win.show()
    app.exec_()

if __name__ == '__main__':
    _py_test()