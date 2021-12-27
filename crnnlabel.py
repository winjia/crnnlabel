#import importlib
#from .cv2 import *
#globals().update(importlib.import_module('cv2.cv2').__dict__)

import cv2
import os
import sys
import time
import lmdb
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DrawLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.__is_rect = False
        self.__is_point = False
        self.__draw_rect_flag = False
        self.__draw_point_flag = False
        self.__left = 0
        self.__top = 0
        self.__right = 0
        self.__bottom = 0
        self.__pt_x = 0
        self.__pt_y = 0
        self.__rectlist = []
        self.__ptlist = []
        self.painter = QPainter()

    def set_rect_flag(self, flag):
        self.__is_rect = flag
        print("set_rect_flag:{},{}".format( self.__is_rect, self.__is_point))

    def set_point_flag(self, flag):
        self.__is_point = flag
        print("set_point_flag:{},{}".format( self.__is_rect, self.__is_point))
    
    def clear_rects_points(self):
        self.__rectlist = []
        self.__ptlist = []


    def mousePressEvent(self,event):
        #print("click:", event.buttons(), Qt.LeftButton)
        #if event.buttons() == Qt.LeftButton:
        if self.__is_rect:
            self.__draw_rect_flag = True
            self.__left = event.x()
            self.__top = event.y()
        #elif event.buttons() == Qt.RightButton:
        if self.__is_point:
            self.__draw_point_flag = True
            self.__pt_x = event.x()
            self.__pt_y = event.y()
            print("point")

    def mouseReleaseEvent(self,event):
        self.__right = event.x()
        self.__bottom = event.y()
        print("rect:{}, point:{}".format( self.__draw_rect_flag, self.__draw_point_flag))
        if self.__draw_rect_flag:
            if abs(self.__left-self.__right) > 10:
                self.repaint()
                self.__draw_rect_flag = False
                self.__rectlist.append((self.__left, self.__top, self.__right, self.__bottom))
            self.__draw_point_flag = False
        if self.__draw_point_flag:
            self.repaint()
            self.__ptlist.append((int((self.__left+self.__right)/2), int((self.__top+self.__bottom)/2)))
        #self.repaint()

    def mouseMoveEvent(self, event):
        self.__right = event.x()
        self.__bottom = event.y()
        if self.__draw_rect_flag:
            self.repaint()


    def paintEvent(self, event):
        super().paintEvent(event)
        self.painter.begin(self)
        #print(self.__left, self.__right)
        if self.__draw_rect_flag:
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            self.painter.setPen(pen)
            #painter.setPen(QColor(255, 0, 0))
            w = self.__right - self.__left + 1
            h = self.__bottom - self.__top + 1
            self.painter.drawRect(self.__left, self.__top, w, h)
        elif self.__draw_point_flag:
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            self.painter.setPen(pen)
            x = self.__pt_x 
            y = self.__pt_y 
            print("point:",x,y)
            self.painter.drawPoint(x, y)
            self.__ptlist.append((x, y))
        #draw 
        for rect in self.__rectlist:
            w = rect[2] - rect[0] + 1
            h = rect[3] - rect[1] + 1
            self.painter.drawRect(rect[0], rect[1], w, h)
        for pt in self.__ptlist:
            self.painter.drawPoint(pt[0], pt[1])
        self.painter.end()

    def show_labeled_rect(self):
        pass

    def get_rect_list(self):
        return self.__rectlist

    def get_point_list(self):
        return self.__ptlist

    def set_rect_list(self, rects):
        self.__rectlist = rects
    
    def redraw_rects(self):
        print("redraw_rects")
        self.painter.begin(self)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        self.painter.setPen(pen)
        for rect in self.__rectlist:
            w = rect[2] - rect[0] + 1
            h = rect[3] - rect[1] + 1
            self.painter.drawRect(rect[0], rect[1], w, h)
        self.painter.end()



#class CrnnPlate(QTabWidget):
class CrnnPlate(QWidget):
    def __init__(self, handler):
        super(CrnnPlate, self).__init__()
        self.__tabhander = handler
        self.__imgpath = None
        self.__imglist = []
        self.__namelist = []
        self.__imgidx = 0
        self.__imgnum = 0
        self.__labeldata = {}
        self.__env = None
        self.__lmdb_handle = None 

    def __del__(self):
        print("_del_")
        #self.__env.close()

    def layout(self):
        layout=QFormLayout()
        layout.addRow('姓名',QLineEdit())
        layout.addRow('地址',QLineEdit())
        #设置选项卡的小标题与布局方式
        self.__tabhander.setLayout(layout)

    def layout2(self):
        hlayout = QHBoxLayout()
        vlayout1 = QVBoxLayout()
        vlayout2 = QVBoxLayout()
        self.__openbtn = QPushButton("打开目录", self)
        self.__prevbtn = QPushButton("上一张")
        self.__nextbtn = QPushButton("下一张")
        self.__rect_btn = QPushButton("删除")
        self.__label_text = QLineEdit()
        self.__name_text = QLineEdit()
        self.__name_text.setReadOnly(True)
        self.__list_text = QLineEdit()
        self.__list_text.setReadOnly(True)
        vlayout1.addWidget(self.__openbtn)
        vlayout1.addWidget(self.__prevbtn)
        vlayout1.addWidget(self.__nextbtn)
        vlayout1.addWidget(self.__rect_btn)
        #
        #self.__showimagelabel = QLabel(self)
        self.__showimagelabel = DrawLabel()
        #self.__showimagelabel.move(100,100)
        #width, height
        self.__showimagelabel.setFixedSize(600, 300)
        #self.__showimagelabel.setScaledContents(True)
        self.__showimagelabel.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        vlayout2.addWidget(self.__showimagelabel)
        vlayout2.addWidget(self.__label_text)
        vlayout2.addWidget(self.__name_text)
        vlayout2.addWidget(self.__list_text)
        #
        #hlayout.addWidget(self.__showimagelabel)
        #
        left = QWidget()
        right = QWidget()
        left.setLayout(vlayout1)
        right.setLayout(vlayout2)
        hlayout.addWidget(left)
        hlayout.addWidget(right)
        self.__tabhander.setLayout(hlayout)
        #添加事件
        self.__openbtn.clicked.connect(lambda: self.open_dir())
        self.__prevbtn.clicked.connect(lambda: self.prev_image())
        self.__nextbtn.clicked.connect(lambda: self.next_image())
        self.__rect_btn.clicked.connect(lambda: self.delete_file())
    
    def delete_file(self):
        name = self.__namelist[self.__imgidx]
        fpath = self.__imgpath + "/" + name
        if os.path.exists(fpath):
            os.remove(fpath)
        fpath = self.__imgpath + "/" + name.replace(".jpg", ".txt")
        if os.path.exists(fpath):
            os.remove(fpath)

    def rect_flag(self):
        self.__showimagelabel.set_rect_flag(True)
        self.__showimagelabel.set_point_flag(False)

    def keypoint_flag(self):
        self.__showimagelabel.set_rect_flag(False)
        self.__showimagelabel.set_point_flag(True)

    #打开目录
    def open_dir(self):
        dirpath = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
        if dirpath is None:
            QMessageBox.information(self, "提示", "文件为空,请重新操作!")
        else:
            self.__imgpath = dirpath
        self.__imgpath = "textrcg/error_imgs"
        self.get_imagelist()
        self.__imgnum = len(self.__imglist)
        self.show_image()
        #self.load_label_data()
        #self.show_first_image()


    #显示图片
    def show_image(self):
        #pix = QPixmap(self.__imglist[self.__imgidx])
        pix,text,path = self.resize_image()
        if pix is None:
            return
        #print(path, text)
        self.__showimagelabel.setPixmap(QPixmap.fromImage(pix))
        #QMessageBox.information(self, "afa", "aff")
        self.__showimagelabel.repaint()
        #self.__label_text.setText("                               ")
        #self.__label_text.setText("==================================")
        #self.__label_text.clear()
        #print("after clear:", self.__label_text.text())
        self.__label_text.setText(text)
        #self.__label_text.setFocus()
        #self.__label_text.selectAll()
        #self.__name_text.clear()
        self.__name_text.setText(path)
        #QApplication.processEvents()
        #self.__label_text.update()
        self.__list_text.setText("{}/{}".format(self.__imgnum, self.__imgidx+1))

    #获取图片列表
    def get_imagelist(self):
        if self.__imgpath is None:
            return []
        files = os.listdir(self.__imgpath)
        for f in files:
            if len(f)<=4:
                continue
            if f.endswith("jpg") or f.endswith("jpeg"):
                self.__imglist.append(self.__imgpath+"/"+f)
                self.__namelist.append(f)
    
    #初始化加载标签数据
    def load_label_data(self):
        self.__env = lmdb.open(self.__imgpath+"/data")
        with self.__env.begin() as txn:
            cursor = txn.cursor()
            for key, value in cursor:
                self.__labeldata[str(key, encoding="utf-8")] = json.loads(str(value, encoding="utf-8"))
        self.__env.close()

    def show_first_image(self):
        if self.__namelist[self.__imgidx] in self.__labeldata:
            self.__showimagelabel.set_rect_list(self.__labeldata[self.__namelist[self.__imgidx]])
            self.show_image()

            
    def save_label_data(self, value):
        self.__env = lmdb.open(self.__imgpath+"/data")
        self.__lmdb_handle = self.__env.begin(write=True)
        #imgname = self.__imglist[self.__imgidx]
        imgname = self.__namelist[self.__imgidx]
        #value = self.__showimagelabel.get_rect_list()
        self.__labeldata[self.__namelist[self.__imgidx]] = value
        print("all:", self.__labeldata)
        value = json.dumps(value)
        self.__lmdb_handle.put(key=imgname.encode(), value=value.encode())
        self.__lmdb_handle.commit()
        print("save:", self.__imgidx, imgname, value)
        self.__env.close()
        
    def _save_label_text(self):
        text = self.__label_text.text()
        path = self.__imglist[self.__imgidx]
        fname = path.replace(".jpg", ".txt")
        with open(fname, "w") as pfile:
            pfile.write(text)


    #下一张
    def next_image(self):
        #save current
        #rects = self.__showimagelabel.get_rect_list()
        #print("next image:", rects)
        name = self.__namelist[self.__imgidx]
        #
        self._save_label_text()
        self.__imgidx += 1
        #self.__label_text.clear()
        self.show_image()

    def prev_image(self):
        self._save_label_text()
        self.__imgidx -= 1
        #print("prev:", self.__imgidx)
        if self.__imgidx < 0:
            self.__imgidx = 0
        self.show_image()

    def resize_image(self):
        #print("resize_image:", self.__imgidx)
        if self.__imgidx > self.__imgnum-1:
            QMessageBox.information(self, "提示", "最后一张")
            self.__imgidx = self.__imgnum - 1
            #print("if:", self.__imgidx)
        path = self.__imglist[self.__imgidx]
        if os.path.exists(path) == False:
            QMessageBox.information(self, "提示", "文件不存在!")
            return None, None, None
        img = cv2.imread(path)
        h,w = img.shape[:2]
        if w > 600:
            nw = 600
            nh = 32
        else:
            nw = int(2*w)
            if nw > 600:
                nw = 600
            nh = int(nw*1.0*h/w)
        #print("h,w:", h,w)
        #print("nh,nw:", nh,nw)
        resizeimg = cv2.resize(img, (nw, nh))
        rgbimg = cv2.cvtColor(resizeimg, cv2.COLOR_BGR2RGB)
        qtimg = QImage(rgbimg.data, nw, nh, 3*nw, QImage.Format_RGB888)
        fname = path.replace(".jpg", ".txt")
        text = ""
        with open(fname, "r") as pfile:
            text = pfile.readline().strip()
        return qtimg, text, path



if __name__=="__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    demo = CrnnPlate(w)
    demo.layout2()
    w.show()
    sys.exit(app.exec_())
