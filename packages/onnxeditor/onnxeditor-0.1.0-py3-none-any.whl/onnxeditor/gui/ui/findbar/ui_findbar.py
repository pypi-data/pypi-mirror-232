# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'findbar.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_FindBar(object):
    def setupUi(self, FindBar):
        if not FindBar.objectName():
            FindBar.setObjectName(u"FindBar")
        FindBar.resize(400, 300)
        self.verticalLayout = QVBoxLayout(FindBar)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(FindBar)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.find_mod = QComboBox(FindBar)
        self.find_mod.addItem("")
        self.find_mod.addItem("")
        self.find_mod.addItem("")
        self.find_mod.addItem("")
        self.find_mod.setObjectName(u"find_mod")

        self.horizontalLayout.addWidget(self.find_mod)

        self.le_name = QLineEdit(FindBar)
        self.le_name.setObjectName(u"le_name")

        self.horizontalLayout.addWidget(self.le_name)

        self.btn_find = QPushButton(FindBar)
        self.btn_find.setObjectName(u"btn_find")

        self.horizontalLayout.addWidget(self.btn_find)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.filter_node = QCheckBox(FindBar)
        self.filter_node.setObjectName(u"filter_node")

        self.horizontalLayout_2.addWidget(self.filter_node)

        self.filter_io = QCheckBox(FindBar)
        self.filter_io.setObjectName(u"filter_io")

        self.horizontalLayout_2.addWidget(self.filter_io)

        self.filter_var = QCheckBox(FindBar)
        self.filter_var.setObjectName(u"filter_var")

        self.horizontalLayout_2.addWidget(self.filter_var)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.ret_list = QListWidget(FindBar)
        self.ret_list.setObjectName(u"ret_list")

        self.verticalLayout.addWidget(self.ret_list)


        self.retranslateUi(FindBar)

        QMetaObject.connectSlotsByName(FindBar)
    # setupUi

    def retranslateUi(self, FindBar):
        FindBar.setWindowTitle(QCoreApplication.translate("FindBar", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("FindBar", u"Name", None))
        self.find_mod.setItemText(0, QCoreApplication.translate("FindBar", u"Has", None))
        self.find_mod.setItemText(1, QCoreApplication.translate("FindBar", u"StartWith", None))
        self.find_mod.setItemText(2, QCoreApplication.translate("FindBar", u"EndsWith", None))
        self.find_mod.setItemText(3, QCoreApplication.translate("FindBar", u"Regex", None))

        self.btn_find.setText(QCoreApplication.translate("FindBar", u"Find", None))
        self.filter_node.setText(QCoreApplication.translate("FindBar", u"Node", None))
        self.filter_io.setText(QCoreApplication.translate("FindBar", u"GraphIO", None))
        self.filter_var.setText(QCoreApplication.translate("FindBar", u"Variable", None))
    # retranslateUi

