import cv2
import numpy as np
import matplotlib.pyplot as plt

class Null:
    def __str__(self):
        return 'null'
    def __lt__(self,obj):
        return True
    def __gt__(self,obj):
        return True
    def __ge__(self,obj):
        return True
    def __le__(self,obj):
        return True

class PrintableNode:
    filhos = None
    value = None
    x = 0
    y = 0
    modo = None
    detail = None
    is_esq = None
    is_dir = None
    
    #modo=[None, 'max','min']
    def __init__(self,value=None, modo=None):
        self.value = value
        self.filhos = []
        self.modo = modo
        
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        ret = str(self) + "(" 
        for filho in self.filhos:
            ret += repr(filho) + " "
        return ret + ")"
        
    def addFilho(self, value=None, modo=None):
        if type(value) == PrintableNode:
            self.filhos.append(value)
        else:
            self.filhos.append(PrintableNode(value,modo))
        
    def getFilhoByValue(self, value):
        for filho in self.filhos:
            if filho.value == value:
                return filho
        return None
    
    def getFilhoByPos(self,pos):
        return self.filhos[pos]
    
    def getLastFilho(self):
        return self.filhos[-1]
    
    def qtdDescendentes(self):
        qtd = 0
        for filho in self.filhos:
            qtd += filho.qtdDescendentes() +1
        return qtd
    


    



class PrintableTree:
    niveis = []
    margins = []
    size = 30
    binary = False
    
    def __str__(self):
        return str(self.niveis)
    
    def __init__(self, raiz,binary=False):
        self.niveis = []
        self.margins = []
        self.criarNiveis(raiz,0)
        self.binary = binary
        
    def criarNiveis(self,no,nivel):
        if len(self.niveis) == nivel:
            self.niveis.append([])
            self.margins.append(60)
        
        self.niveis[nivel].append(no)
        
        for filho in no.filhos:
            self.criarNiveis(filho, nivel+1)
            
    def nivelMax(self):
        m = 0
        k = 0
        i = 0
        for nivel in self.niveis:
            if len(nivel) > m:
                m = len(nivel)
                k = i
            i += 1
        return [m,k]
    
    def triangle(self, image, coord, size, color, thick):
        if len(coord) == 2 or len(coord) == 3 and coord[2] == 1:
            pt1 = (coord[0],             int(coord[1]-size/2))
            pt2 = (int(coord[0]-size/2), int(coord[1]+size/2))
            pt3 = (int(coord[0]+size/2), int(coord[1]+size/2))
        else:
            pt1 = (coord[0],        int(coord[1]+size/2))
            pt2 = (int(coord[0]-size/2), int(coord[1]-size/2))
            pt3 = (int(coord[0]+size/2), int(coord[1]-size/2))
        triangle_cnt = np.array( [pt1, pt2, pt3] )
        cv2.drawContours(image, [triangle_cnt], 0, color, thick)
        return image

        
        
    def printNodes(self, no, image):
        
        coord = [no.x, no.y]
        line_color = (0,0,0)
        color = (100, 100, 250)
        text_color = (255,255,255)
        
        #desenha filhos com as linhas
        for filho in no.filhos:
            if self.binary == False:
                end = (filho.x, filho.y)
                #linha
                cv2.line(image, tuple(coord), tuple(end), line_color, 2)
                #filho
                image = self.printNodes(filho, image)
            elif (filho.value != None):
                end = (filho.x, filho.y)
                #linha
                cv2.line(image, tuple(coord), tuple(end), line_color, 2)
                #filho
                image = self.printNodes(filho, image)
        
        #desenha no
        margin = 30
        digit_coordinate = [coord[0]-20,coord[1]+10]
        coord_coord = [coord[0]-10,coord[1]+40]
        radius = 30
        thickness = 2
        if no.modo == None:
            image = cv2.circle(image, tuple(coord), radius, color, -1)
            image = cv2.circle(image, tuple(coord), radius+2, (0,0,0), 2)
        elif no.modo == 'min':
            image = self.triangle(image, tuple(coord + [0]), radius*2, color, -1)
            image = self.triangle(image, tuple(coord + [0]), radius*2+2, (0,0,0), 2)
            digit_coordinate[1] -= 15
        elif no.modo == 'max':
            image = self.triangle(image, tuple(coord + [1]), radius*2, color, -1)
            image = self.triangle(image, tuple(coord + [1]), radius*2+2, (0,0,0), 2)
            digit_coordinate[1] += 13
        
        image = cv2.putText(image, str(no.value), tuple(digit_coordinate), cv2.FONT_HERSHEY_SIMPLEX, .8, text_color, 2)
        #mostrar coordenadas
        #image = cv2.putText(image, str(coord), coord_coord, cv2.FONT_HERSHEY_SIMPLEX, .4, line_color, 1)
        
        
        if no.detail:
            detail_coord = [coord[0]-10,coord[1]-40]
            image = cv2.putText(image, no.detail, tuple(detail_coord), cv2.FONT_HERSHEY_SIMPLEX, .7, line_color, 2)
            
        
        return image
    
    
                    
    
    #define a posicao do nivel
    def __definePos(self,nivel):
        radius = 30
        for no in self.niveis[nivel]:
            qtdF = len(no.filhos)
            if qtdF > 0:
                margin = self.margins[nivel+1]
                
                
                
                if (qtdF == 1):
                    if (self.binary):
                        x_ini = int(no.x - (margin*2)/2)
                        #caso so possua filho direito
                        if no.filhos[0].is_dir:
                            x_ini += int((margin*2)/(2-1))   
                    else:
                        x_ini = no.x
                    step = 0
                else:
                    x_ini = int(no.x - (margin*qtdF)/2)
                    step = int((margin*qtdF)/(qtdF-1))
                
                
                x = x_ini
                for filho in no.filhos:
                    filho.x = x
                    filho.y = no.y + 80
                    x += step
        
    #define todos os niveis
    def definePos(self,ini=0):
        for nivel in range(ini-1,len(self.niveis)):
            self.__definePos(nivel)
                    
        
    def print(self):
        height, width = 600, 1500
        image = np.ones((height,width,3), np.uint8)
        image *= 255

        self.niveis[0][0].x = int(width/2)
        self.niveis[0][0].y = 50
        
    
        self.margins[-1] = 40
        for nivel in range(len(self.niveis)-2,0,-1):
            self.margins[nivel] = self.margins[nivel+1] * 2
        
        
        self.definePos()
        
        image = self.printNodes(self.niveis[0][0], image)

        # Displaying the image
        plt.figure(figsize = (17,12))
        plt.axis('off')
        plt.imshow(image)


def ptrBinaryToPrintableTree(no, pNo=None):
    
    if (pNo == None):
        pNo = PrintableNode(no.ptr.value)
        pNo.detail = str(no.ptr.bal)
    else:
        pai = pNo
        pNo = PrintableNode(no.ptr.value)
        pai.addFilho(pNo)
        pai.getLastFilho().detail = str(no.ptr.bal)
    
    if no.ptr.esq.ptr.value != None:
        ptrBinaryToPrintableTree(no.ptr.esq, pNo)
        
    if no.ptr.dir.ptr.value != None:
        ptrBinaryToPrintableTree(no.ptr.dir, pNo)
        
    return pNo
            
def binaryToPrintableTree(no, pNo=None, dir=None, esq=None):
    
    if (pNo == None):
        pNo = PrintableNode(no.value)
        if hasattr(no,"bal"):
            pNo.detail = str(no.bal)
    else:
        pai = pNo
        pNo = PrintableNode(no.value)
        pNo.is_esq = esq
        pNo.is_dir = dir
        pai.addFilho(pNo)
        if hasattr(no,"bal"):
            pai.getLastFilho().detail = str(no.bal)
    
    if no.esq != None:
        binaryToPrintableTree(no.esq, pNo, esq=True)
        
    if no.dir != None:
        binaryToPrintableTree(no.dir, pNo, dir=True)
        
    return pNo
            
    


def addDescendents(vec, i, pai = None):
    no = PrintableNode(vec[i])
    
    if pai != None:
        pai.addFilho(no)
    
    fEsq = i*2+1
    fDir = i*2+2
    
    if len(vec) > fEsq:
        addDescendents(vec, fEsq, no)
        
    if len(vec) > fDir:
        addDescendents(vec, fDir, no)
    
    if pai == None:
        return no

def vectorToPrintableTree(vec):
    return addDescendents(vec, 0)
	
class No:
    esq = None
    dir = None
    value = None
    bal = ""
    def __init__(self,value, bal=""):
        self.value = value
        self.bal = bal
    

class No:
    esq = None
    dir = None
    value = None
    def __init__(self,value):
        self.value = value
        
