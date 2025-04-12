from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QIcon

class ventanaMonitoreo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventana con un Label")
        self.setGeometry(50,50,200,200)    
        self.setWindowIcon(QIcon('../logo.png'))

        # Crear un QLabel
        label = QLabel("¡Hola, este es un Label!", self)
        
        # Ajustar el tamaño del label para que se vea correctamente
        label.setGeometry(50, 50, 300, 50)