from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QApplication, QMainWindow
import sys
from lib.UiNewFundIndice import Ui_MainWindow
from lib.LoginUi import Ui_Dialog_password
import logging
from lib.utils import logger

from PySide2.QtWidgets import QDialog        
from lib.utils import logger
from PySide2.QtCore import QThread, QObject, QMutex, QRunnable, Slot
from lib.tt import get_new_fund_index
from PySide2.QtWidgets import QTableWidgetItem

import os, sys
import PySide2

dirname = os.path.dirname(sys.executable)

plugin_path = os.path.join(dirname, 'Library', 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

class UpdateFund(QRunnable):
    #countChanged = Signal(int)

    def __init__(self, start, days, column, tableWidget):
        """更新基金数据

        """
        super().__init__()
        self.start = start
        self.days = days
        self.column = column
        self.tableWidget = tableWidget
        
    #@Slot() #一定要加上
    def run(self):

        result = get_new_fund_index(self.start, self.days)

        for i,k in enumerate(result):
            try:
                #寻找已有值
                flag = QtCore.Qt.MatchExactly
                k_Item = self.tableWidget.findItems(k, flag)[0]
            except IndexError:
                #找不到则末尾插入一行
                self.tableWidget.insertRow(0)
                #self.tableWidget.setItem(self.tableWidget.rowCount(),0, QTableWidgetItem(k))
                self.tableWidget.setItem(0,0, QTableWidgetItem(k))
                #self.tableWidget.setItem(self.tableWidget.rowCount(),column, QTableWidgetItem(str(result[k])))
                self.tableWidget.setItem(0,self.column, QTableWidgetItem(str(result[k])))
            else:
                #如果已有，更改值即可
                self.tableWidget.setItem(k_Item.row(),self.column, QTableWidgetItem(str(result[k])))


class UiMainWindow(Ui_MainWindow):
    def __init__(self, mainWindow):
        super().__init__()

        # 运行子程序的pool，必须在__init__阶段初始化，在sync时会进入子进程造成阻塞
        self.pool = QtCore.QThreadPool()
        self.pool.setMaxThreadCount(1)
        #装载UI界面      
        self.setupUi(mainWindow)
        #绑定事件
        self.pushButton_run.clicked.connect(self.sync)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['关键词','当月视角','-1月视角', '-2月视角', '-3月视角'])

    def sync(self):
        #基金关键词，通过jieba分词过滤后获得，可以每年更新一次
        
        from datetime import datetime, timedelta
        today = datetime.now()
        for col,past in enumerate([0, 30, 60, 90]):
            start = datetime.now() - timedelta(days=past)
            self.pool.start(UpdateFund(start,90, col+1, self.tableWidget))

def to_login(next_window):
    def _verify():

        import hashlib
        from datetime import datetime
        day = datetime.today().strftime('%Y%m')
        #signature = hashlib.sha256('jiedanjishiben'+day).hexdigest()[:6]
        signature = day
        password = loginUi.lineEdit_password.text()

        if password == signature:
            loginDialog.close()
            next_window.show()
            return True
        else:
            from PySide2.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("cookie.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            msg.setWindowIcon(icon)
            msg.setText("请重新输入")
            msg.setInformativeText("或者添加公众号获取密码")
            msg.setWindowTitle("密码错误")
            msg.setDetailedText("公众号: \n结丹记事本儿")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
            return retval
            #msg.buttonClicked.connect(msgbtn)    

    
    loginUi = Ui_Dialog_password()
    loginDialog = QDialog()
    loginUi.setupUi(loginDialog)
    loginUi.pushButton_login.clicked.connect(_verify)
    loginDialog.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    uiMainWindow = UiMainWindow(mainWindow)

    to_login(next_window = mainWindow)

    sys.exit(app.exec_())