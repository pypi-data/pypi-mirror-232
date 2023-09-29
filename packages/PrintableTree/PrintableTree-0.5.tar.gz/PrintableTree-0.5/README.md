# About

It has an implementation of a tree in python and methods that print the tree to an image through OpenCV

# Sobre

É uma implementação de uma árvore em python com métodos que permitem imprimir a árvore através do OpenCV

# Google Colab

Pode ser usado no Google Colab

```bash
    !pip install PrintableTree
```

```python
    from PrintableTree import *

    raiz = No(1, bal=-1)
    raiz.esq = No(2, bal=0)
    raiz.dir = No(3, bal=0)
    tree = PrintableTree(binaryToPrintableTree(raiz), binary=True)
    tree.print()
```
![output1:](images/tree1.png)


```python
    raiz = vectorToPrintableTree([1,2,3,4,5,6,7,8,9,10,11,12])
    tree = PrintableTree(raiz, binary=True)
    tree.print()
```
![output2:](images/tree2.png)