from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import csv
import os
import random as r
import numpy as np
from pyqtgraph.widgets.PlotWidget import PlotWidget

# DATA
class File:
    def __init__(self,file_root,file_name):
        self.root = file_root
        self.name = file_name
        
class Folder:
    def __init__(self,folder_root,folder_name):
        self.root = folder_root
        self.name = folder_name
        self.file_list = []

    def setFileList(self,file_list):
        self.file_list = file_list

class Explorer:
    def __init__(self):
        self.table_path = self.get_resource_path("tables")
        self.explorerBuilding()

    def explorerBuilding(self):
        self.explorer_list = []
        for root,dirs,files in os.walk(self.table_path, topdown=True):
            if root == self.table_path:
                if len(files) != 0 :
                    for filename in files:
                        file = File(self.getFileRoot(root,filename),filename)
                        self.explorer_list.append(file)

                if len(dirs) != 0:
                    for foldername in dirs:
                        folder = Folder(self.table_path,foldername)
                        self.explorer_list.append(folder)
            else :
                if len(files) != 0 :
                    file_list = []
                    for filename in files:
                        file = File(self.getFileRoot(root,filename),filename)
                        file_list.append(file)

                    for explorer_o in self.explorer_list:
                        if explorer_o.name == self.getFolderName(root):
                            if type(explorer_o) == Folder:
                                explorer_o.setFileList(file_list)

    def get_resource_path(self,relative_path):
        try:
            # PyInstaller creates a temp folder and set the path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def getFolderName(self,root):
        for i in range(len(root))[::-1]:
            if root[i] == "\\":
                return(root[i+1:])

    def getFileRoot(self,root,file):
        return(root+'\\' +file)
    
    def getFileList(self):
        file_list = []
        for element in self.explorer_list:
            if type(element) == File:
                file_list.append(element)
            if type(element) == Folder:
                for file in element.file_list:
                    file_list.append(file)
        return(file_list)

class MenuItem(QStandardItem):
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.setText(name)
        self.setEditable(False)
        self.setForeground(QColor('black'))
        fnt = QFont('Open Sans', 15)
        fnt.setBold(True)
        fnt.setWeight(100)
        self.setFont(fnt)

class ExplorerItem(QStandardItem):
    def __init__(self,element):
        super().__init__()
        self.name = element.name
        self.root = element.root
        self.explorer_item_type = type(element)
        self.setText(self.name)
        self.setEditable(False)
        self.setForeground(QColor('black'))
        fnt = QFont('Open Sans', 10)
        fnt.setBold(False)
        fnt.setWeight(100)
        self.setFont(fnt)
        
class Data:
    def __init__(self):
        self.data_root = './DIXO_V8/data/table_data.csv'

# renvoi la donné de data_table situé à la colomne data_column et à la ligne 
    def getData(self,data_row,data_column):
        with open(self.data_root,'r',encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            selector = list(reader)
            for i in range(0,reader.line_num -1):
                if selector[i]['TABLE_NAME'] == data_row:
                    return(selector[i][data_column])

class Table:
    def __init__(self,root,name):
        super().__init__()
        self.root = root
        self.name = name
        self.tab = self.getTableTab()
        self.l1 = ''
        self.l2 = ''
        self.nb_word = 0
        if len(self.getTableTab()) != 0:
            self.getTableData()

    def getTableData(self):
        with open(self.root,'r',encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            selector = list(reader)
            self.nb_word = len(selector)-1
            self.l1 = selector[0][0]
            self.l2 = selector[0][1]

    def getTableTab(self):
        tab = []
        with open(self.root,'r',encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                tab.append(row)
            return(tab)

    def saveTableTab(self,tabWidget):
        tab_to_save = []
        row = []
        for i in range(tabWidget.rowCount()):
            for j in range(2):
                row.append(tabWidget.item(i,j).text())
            tab_to_save.append(row)
            row = []
        if self.tab != tab_to_save:
            with open(self.root,'w',newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(tab_to_save)
             
class Test:
    def __init__(self,table,langue_from,langue_to,proposals,random,personal):
        super().__init__()
        self.table = table
        self.proposals = proposals
        self.random = random
        self.personal = personal
        self.current_word_index = 0
        self.table_index_list = list(np.arange(0,self.table.nb_word,1))
        self.picked_index_list = r.sample(self.table_index_list,len(self.table_index_list))

        if self.random == True:
            self.setRandomLangue(langue_from,langue_to)
        else : 
            self.langue_from = langue_from
            self.langue_to = langue_to
        if self.personal == True:
            self.cnt = 0
        else : self.cnt = 0

        self.current_word = ''
        self.current_correc = ''
        self.err_tab = []
        self.end = False

    def setRandomLangue(self,langue_from,langue_to):
        langue_list = [langue_from,langue_to]
        self.langue_from = r.choice(langue_list)
        langue_list.remove(self.langue_from)
        self.langue_to = r.choice(langue_list)

    def setProposalList(self):
        self.word_proposal_list = []
        my_table_index_list = self.table_index_list.copy()
        ordered_list = [] # Contient les index de : [true_resp,fals_resp,fals_resp]
        random_list = [] # Liste des indexes mélangé
        ordered_list.append(self.current_word_index)
        my_table_index_list.remove(self.current_word_index)
        ordered_list.extend(r.sample(my_table_index_list,2))
        random_list = r.sample(ordered_list,3)
        for word_proposal_index in random_list:
            self.word_proposal_list.append(self.getWord(word_proposal_index,self.langue_to))

    def pickWord(self):
        if self.random == True:
            self.setRandomLangue(self.langue_from,self.langue_to)
        self.current_word_index = self.picked_index_list[self.cnt]
        self.current_word = self.getWord(self.current_word_index,self.langue_from)
        self.current_correc = self.getWord(self.current_word_index,self.langue_to)
        if self.proposals == True:
            self.setProposalList()
        self.cnt += 1
        if self.cnt >= self.table.nb_word:
            self.end = True
        #print('self.word / correc',self.current_word_index,self.current_word,self.current_correc)
        #print('self.cnt,self.end',self.cnt,self.end)
        return(self.current_word,self.current_correc)

    def getWord(self,i,langue):
        with open(self.table.root,'r',encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            selector = list(reader)
            word = selector[i][langue]
        return(word)

    def setErrTab(self,my_resp):
        err = [self.current_word,my_resp,self.current_correc]
        self.err_tab.append(err)

    def getProgress(self):
        return(f'{self.cnt}/{self.table.nb_word}')

class TabWidget(QTableWidget):
    def __init__(self,tab,enable_header,hHeader_list):
        super().__init__()
        self.setRowCount(len(tab))
        if len(tab) != 0:
            self.setColumnCount(len(tab[0]))
        hHeader = self.horizontalHeader()
        vHeader = self.horizontalHeader()
        if enable_header == False:
            hHeader.setVisible(False)
            vHeader.setVisible(False)
        else : 
            hHeader.setVisible(True)
            vHeader.setVisible(True)
            self.setHorizontalHeaderLabels(hHeader_list)
        hHeader.setResizeMode(QHeaderView.Stretch)
        self.setStyleSheet("font-size: 30px")

        if len(tab) != 0:
            for i in range(len(tab)):
                for j in range(len(tab[0])):
                    self.setItem(i,j,QTableWidgetItem(tab[i][j]))
                self.setRowHeight(i,50)
        
class MyTable():
    def __init__(self,file_list,file_list_selected):
        super().__init__()
        self.root = './DIXO_V8/myquizz/myquizz.csv'
        self.name = 'myquizz.csv'
        self.my_table_list = []

        for file_selected in file_list_selected:
            for file in file_list:
                if file_selected == file.name:
                    table = Table(file.root,file.name)
                    tab = table.tab
                    self.my_table_list.extend(tab[1:])
        self.saveMyTable()

    def saveMyTable(self):
        with open(self.root,'w',newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(self.my_table_list)
        self.my_table_list = []

#WINDOWS
class Menu(QWidget):
    menu_signal = pyqtSignal(QStandardItem)
    def __init__(self):
        super().__init__()
        self.data = Data()
        self.e = Explorer()
        self.UIComponents()
        self.modelBuilding()

    def UIComponents(self):
        self.model = QStandardItemModel()
        self.rootNode = self.model.invisibleRootItem()
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.menulayout = QVBoxLayout()

    def modelBuilding(self):
        self.explorerItem = MenuItem('EXPLORER')
        self.rootNode.appendRow(self.explorerItem)
        self.personalQuizzItem = MenuItem('Personal Quizz')
        self.rootNode.appendRow(self.personalQuizzItem)

        for element in self.e.explorer_list:
            if type(element) == Folder:
                folderItem = ExplorerItem(element)
                folderItem.setCheckable(False)
                self.explorerItem.appendRow(folderItem)
                for file in element.file_list:
                    fileItem = ExplorerItem(file)
                    folderItem.appendRow(fileItem)
            if type(element) == File:
                fileItem = ExplorerItem(element)
                self.explorerItem.appendRow(fileItem)

        self.tree.setModel(self.model)
        self.menulayout.addWidget(self.tree)
        self.setLayout(self.menulayout)
        self.tree.clicked.connect(self.signal) 

    def signal(self,index):
        it = self.model.itemFromIndex(index)
        self.menu_signal.emit(it)

class StartFrame(QWidget):
    def __init__(self):
        super().__init__()

        self.mainLay = QVBoxLayout()
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = "./dixo_img.png"
        abs_file_path = os.path.join(script_dir, rel_path)

        self.img = QPixmap(abs_file_path) 
        self.dixoImg = QLabel() 
        self.dixoImg.setPixmap(self.img) 
        self.dixoImg.setAlignment(Qt.AlignCenter)
        self.mainLay.addWidget(self.dixoImg)
        self.setLayout(self.mainLay)

class InitTestFrame(QWidget):
    start_quizz_signal = pyqtSignal(Table,str,str,bool,bool,bool)
    def __init__(self):
        super().__init__()
        self.proposal_btn_stylesheet = 'QRadioButton{font: 15pt Helvetica MS;} QRadioButton::indicator { width: 20px; height: 20px;};'

    def setData(self,table_root,table_name):
        self.table_root = table_root
        self.table_name = table_name
        self.table = Table(self.table_root,self.table_name)
        self.tab_to_save = []
        self.langue_from = ''
        self.langue_to = ''
        self.nb_word = 0
        self.UIComponents()

    def UIComponents(self):
        self.mainLay = QGridLayout()
        self.setLayout(self.mainLay)
        self.mainLay.setSpacing(20)

        self.titleLabel = QLabel(self.table.name)
        self.titleLabel.setAlignment(Qt.AlignTop)
        self.titleLabel.setAlignment(Qt.AlignHCenter)
        self.titleLabel.setStyleSheet("font-size: 50px")

        self.saveBtn = QPushButton('SAVE')
        self.saveBtn.clicked.connect(self.saveTableEdit)

        self.addRowBtn = QPushButton("+")
        self.addRowBtn.clicked.connect(self.addTableRow)
        self.removeRowBtn = QPushButton("-")
        self.removeRowBtn.clicked.connect(self.removeTableRow)

        self.tabWidget = TabWidget(self.table.tab,False,[])

        self.bottomBox = QGroupBox()
        self.bottomBox.setMinimumHeight(150)

        self.bottomLay = QGridLayout()
        self.bottomBox.setLayout(self.bottomLay)

        self.langueBtnList = [QRadioButton(self.table.l1),QRadioButton(self.table.l2),QRadioButton('random')]
        self.languebtnGroup,self.languebtnGroupeLay = self.getBtnGroupeLay(self.langueBtnList)

        self.testTypeBtnList = [QRadioButton('write your response'),QRadioButton('with 3 proposals')]
        self.testTypeBtnGroup,self.testTypebtnGroupeLay = self.getBtnGroupeLay(self.testTypeBtnList)

        self.bottomLay.addWidget(QLabel('Select language'),0,0)
        self.bottomLay.addLayout(self.languebtnGroupeLay,0,1)
        self.bottomLay.addWidget(QLabel('Select Test type'),1,0)
        self.bottomLay.addLayout(self.testTypebtnGroupeLay,1,1)
        
        #self.bottomLay.addLayout(self.languebtnGroupeLay,1,1)

        self.startBtn = QPushButton("START QUIZZ")
        self.startBtn.clicked.connect(self.startQuizzSignal)

        self.mainLay.addWidget(self.titleLabel,0,0,1,2)
        self.mainLay.addWidget(self.saveBtn,1,0,1,2)
        self.mainLay.addWidget(self.addRowBtn,2,0)
        self.mainLay.addWidget(self.removeRowBtn,2,1)
        self.mainLay.addWidget(self.tabWidget,3,0,1,2)
        self.mainLay.addWidget(self.bottomBox,4,0,1,2)
        self.mainLay.addWidget(self.startBtn,5,0,1,2)
        
    def getBtnGroupeLay(self,btn_list):
        btnGroupeLay = QHBoxLayout()
        btnGroupe = QButtonGroup()
        i = 0
        for btn in btn_list:
            btn.setCheckable(True)
            btn.setStyleSheet(self.proposal_btn_stylesheet)
            btnGroupe.addButton(btn,i)
            btnGroupeLay.addWidget(btn)
            i += 1
        return(btnGroupe,btnGroupeLay)

    def saveTableEdit(self):
        self.table.saveTableTab(self.tabWidget)
        del self.table
        self.table = Table(self.table_root,self.table_name)

    def addTableRow(self):
        rowPosition = self.tabWidget.rowCount()
        self.tabWidget.insertRow(rowPosition)

    def removeTableRow(self):
        rowPosition = self.tabWidget.rowCount()-1
        self.tabWidget.removeRow(rowPosition)

    def startQuizzSignal(self):
        random = False
        proposals = False
        if self.languebtnGroup.checkedButton().text() == self.table.l1:
            self.langue_from = self.table.l1
            self.langue_to = self.table.l2
        if self.languebtnGroup.checkedButton().text() == self.table.l2:
            self.langue_from = self.table.l2
            self.langue_to = self.table.l1
        if self.languebtnGroup.checkedButton().text() == 'random':
            random = True
            self.langue_from = self.table.l1
            self.langue_to = self.table.l2

        if self.testTypeBtnGroup.checkedButton().text() == 'with 3 proposals':
            proposals = True

        self.start_quizz_signal.emit(self.table,self.langue_from,self.langue_to,proposals,random,False)

class TestFrame(QWidget):
    show_correc_signal = pyqtSignal(Test)
    def __init__(self):
        super().__init__()
        self.proposal_btn_stylesheet = 'QRadioButton{font: 20pt Helvetica MS;} QRadioButton::indicator { width: 20px; height: 20px;};'

    def setData(self,table,langue_from,langue_to,proposals,random,personal):
        self.test = Test(table,langue_from,langue_to,proposals,random,personal)
        self.word,self.correc = self.test.pickWord()   
        self.UIComponents()
        
    def UIComponents(self):
        self.mainLay = QVBoxLayout()
        self.setLayout(self.mainLay)
        self.mainLay.setSpacing(100)

        self.titleLabel = QLabel(self.test.table.name)
        self.titleLabel.setStyleSheet("QLabel {font-size: 50px;}")
        self.titleLabel.setAlignment(Qt.AlignHCenter)
        #self.titleLabel.setStyleSheet("font-size: 50px")

        self.wordLabel = QLabel(self.word)
        self.wordLabel.setStyleSheet("QLabel {font-size: 35px;}")
        self.wordLabel.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        #self.wordLabel.setStyleSheet("font-size: 30px")

        self.mainLay.addWidget(self.titleLabel)
        self.mainLay.addWidget(self.wordLabel)

        if self.test.proposals == False:
            self.wordEdit = QLineEdit()
            self.mainLay.addWidget(self.wordEdit)
            #self.wordEdit.setTextMargins(10,10,10,10)
            #self.wordEdit.setMaximumWidth(400)
            self.wordEdit.setAlignment(Qt.AlignHCenter)
            self.wordEdit.setStyleSheet("font-size: 25px")

        if self.test.proposals == True:
            prop_btn_list = [QRadioButton(self.test.word_proposal_list[0]),QRadioButton(self.test.word_proposal_list[1]),QRadioButton(self.test.word_proposal_list[2])]
            self.propBtnGroup,self.propBtnLay = self.getBtnGroupeLay(prop_btn_list)
            self.propBtnLay.setAlignment(Qt.AlignCenter)
            self.mainLay.addLayout(self.propBtnLay)

        self.correcLabel = QLabel('')
        self.correcLabel.setStyleSheet("QLabel {font-size: 35px;color: red;}")
        self.correcLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.progressLabel = QLabel(self.test.getProgress())
        self.progressLabel.setAlignment(Qt.AlignCenter)
        #self.scoreLabel = QLabel('SCORE')

        self.show_correctionBtn = QPushButton('Show Correction')
        self.show_correctionBtn.setStyleSheet("QLabel {font-size: 35px;}")
        self.mainLay.addWidget(self.show_correctionBtn)
        self.show_correctionBtn.clicked.connect(self.showCorrecEvent)

        self.mainLay.addWidget(self.correcLabel)
        self.mainLay.addWidget(self.progressLabel)
        self.mainLay.addWidget(self.show_correctionBtn)

    def getBtnGroupeLay(self,btn_list):
        btnGroupeLay = QHBoxLayout()
        btnGroupe = QButtonGroup()
        i = 0
        for btn in btn_list:
            btn.setCheckable(True)
            btn.setStyleSheet(self.proposal_btn_stylesheet)
            btnGroupe.addButton(btn,i)
            btnGroupeLay.addWidget(btn)
            i += 1
        return(btnGroupe,btnGroupeLay)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return :
            self.nextWordEvent()

    def nextWordEvent(self):
        my_resp = self.getResponse()
        if my_resp == self.correc:
            self.correcLabel.clear()
            if self.test.end == False:
                self.word,self.correc = self.test.pickWord()
                self.wordLabel.setText(self.word)
                if self.test.proposals == True:
                    self.setResponseWidget()
                else : self.wordEdit.clear()
                self.progressLabel.setText(self.test.getProgress())
            else:
                self.wordLabel.setText('End of Quizz')
                if self.test.proposals == True:
                    self.hideResponseWidget()
                else : self.wordEdit.setVisible(False)                         
        else :
            self.test.setErrTab(my_resp)
            self.correcLabel.setText(self.correc)
            if self.test.proposals == False:
                self.wordEdit.clear()

    def getResponse(self):
        if self.test.proposals == False:
            my_resp = self.wordEdit.text()
        if self.test.proposals == True:
            my_resp = self.propBtnGroup.checkedButton().text()
        return(my_resp)

    def setResponseWidget(self):
        for i in range(3):
            self.propBtnLay.itemAt(i).widget().setText(self.test.word_proposal_list[i])

    def hideResponseWidget(self):
        for i in range(3):
            self.propBtnLay.itemAt(i).widget().setVisible(False)

    def showCorrecEvent(self):
        self.show_correc_signal.emit(self.test)

class CorrecFrame(QWidget):
    def __init__(self):
        super().__init__()

    def setData(self,test):
        self.test = test
        self.UIComponents()
    
    def UIComponents(self):
        self.mainLay = QVBoxLayout()
        self.titleLabel = QLabel(self.test.table.name)
        self.titleLabel.setAlignment(Qt.AlignTop)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("font-size: 50px")

        self.tabWidget = TabWidget(self.test.err_tab,True,['Word','Response','Correction'])

        self.mainLay.addWidget(self.titleLabel)
        self.mainLay.addWidget(self.tabWidget)

        self.setLayout(self.mainLay)

class MyQuizzFrame(QWidget):
    startMyQuizzSignal = pyqtSignal(MyTable)
    def __init__(self):
        super().__init__()
        self.e = Explorer()
        self.file_list = self.e.getFileList()
        self.file_list_selected = []
        self.UIComponents()

    def UIComponents(self):
        self.mainLay = QFormLayout()
        self.setLayout(self.mainLay)

        self.titleLabel = QLabel('Personal Quizz')
        self.titleLabel.setAlignment(Qt.AlignTop)
        self.titleLabel.setAlignment(Qt.AlignHCenter)
        self.titleLabel.setStyleSheet("font-size: 50px")
        self.mainLay.addRow(self.titleLabel)

        self.selectLabel = QLabel('Select Table')
        self.selectLabel.setAlignment(Qt.AlignTop)

        self.btnBox = QVBoxLayout()
        self.allBtn = QCheckBox('All')
        self.btnBox.addWidget(self.allBtn)
        for i in range(len(self.file_list)):
            self.btnBox.addWidget(QCheckBox(self.file_list[i].name))
            
        self.nbLabel = QLabel('Nb of word')

        self.nbWordEdit = QLineEdit()
        self.nbWordEdit.setAlignment(Qt.AlignCenter)
        #self.nbWordEdit.setMaximumWidth(400)

        self.nbEdit = QLineEdit()
        self.nbEdit.setTextMargins(5,5,5,5)
        self.nbEdit.setMaximumWidth(50)
        self.nbEdit.setAlignment(Qt.AlignHCenter)
        self.nbEdit.setStyleSheet("font-size: 10px")

        self.next_btn = QPushButton('verify')
        self.next_btn.clicked.connect(self.verify)

        self.groupBox = QGroupBox()
        self.groupBox.setAlignment(Qt.AlignTop)
        self.groupBox.setAlignment(Qt.AlignHCenter)
        self.mainLay.addRow(self.groupBox)

        self.gridLay = QGridLayout()
        self.groupBox.setLayout(self.gridLay)
        self.gridLay.addWidget(self.selectLabel,0,0)
        self.gridLay.addLayout(self.btnBox,0,1)
        self.gridLay.addWidget(self.nbLabel,1,0)
        self.gridLay.addWidget(self.nbWordEdit,1,1)

        self.mainLay.addRow(self.next_btn)
        
    def verify(self):
        for i in range(len(self.file_list)+1):
            if self.btnBox.itemAt(i).widget().isChecked() == True:
                if self.btnBox.itemAt(i).widget().text() == 'All':
                    for j in range(len(self.file_list)+1)[1:]:
                        self.file_list_selected.append(self.btnBox.itemAt(j).widget().text())
                    break
                else :
                    self.file_list_selected.append(self.btnBox.itemAt(i).widget().text())
        myTable = MyTable(self.file_list,self.file_list_selected)
        self.file_list_selected = []
        self.startMyQuizzSignal(myTable)

#MAIN
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DIXO')
        #self.setStyleSheet("background-color: #636262;")
        self.UIComponents()
        
    def UIComponents(self):
        self.menu = Menu()
        self.menu.setContentsMargins(0,0,0,0)

        self.stackWidget = QStackedWidget()
        self.startFrame = StartFrame()
        self.myQuizzFrame = MyQuizzFrame()
        self.initTestFrame = InitTestFrame()
        self.testFrame = TestFrame()        
        self.correcFrame = CorrecFrame()
        self.stackWidget.addWidget(self.startFrame)
        self.stackWidget.addWidget(self.myQuizzFrame)
        self.stackWidget.addWidget(self.initTestFrame)
        self.stackWidget.addWidget(self.testFrame)
        self.stackWidget.addWidget(self.correcFrame)

        self.backLay = QHBoxLayout()
        self.backLay.addWidget(self.menu)
        self.backLay.addWidget(self.stackWidget)
        self.backLay.setStretch(1,5)
        self.backLay.setSpacing(0)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(self.backLay)

        self.menu.menu_signal.connect(self.menuEvent)

    def menuEvent(self,item):
        if type(item) == MenuItem:
            if item.name == 'EXPLORER':
                self.stackWidget.setCurrentIndex(0)
            if item.name == 'Personal Quizz':
                self.stackWidget.setCurrentIndex(1)

        if type(item) == ExplorerItem:
            if item.explorer_item_type == Folder:
                self.stackWidget.setCurrentIndex(0)
            if item.explorer_item_type == File:
                self.initTestFrame.setParent(None)
                self.testFrame.setParent(None)
                self.correcFrame.setParent(None)
                self.initTestFrame = InitTestFrame()
                self.initTestFrame.setData(item.root,item.name)
                self.initTestFrame.start_quizz_signal.connect(self.initTestEvent)
                self.stackWidget.insertWidget(2,self.initTestFrame)
                self.stackWidget.setCurrentIndex(2)

    def initTestEvent(self,table,lang_from,lang_to,proposals,random,personal):
        #self.testFrame.setParent(None)
        self.testFrame = TestFrame()
        self.testFrame.setData(table,lang_from,lang_to,proposals,random,personal)
        self.testFrame.show_correc_signal.connect(self.testEvent)
        self.stackWidget.insertWidget(3,self.testFrame)
        self.stackWidget.setCurrentIndex(3)

    def testEvent(self,test):
        #self.correcFrame.setParent(None)
        self.correcFrame = CorrecFrame()
        self.correcFrame.setData(test)
        self.stackWidget.insertWidget(4,self.correcFrame)
        self.stackWidget.setCurrentIndex(4)

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

