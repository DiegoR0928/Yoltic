import sys
from PySide6.QtWidgets import QApplication
import visualizacion, comando, monitoreo

if __name__ == "__main__":
    app = QApplication([])
    ventanaVisualizacion = visualizacion.ventanaVisualizacion()
    ventanaVisualizacion.show()
    ventanaComando = comando.ventanaComando()
    ventanaComando.show()
    ventanaMonitoreo = monitoreo.ventanaMonitoreo()
    ventanaMonitoreo.show()
    sys.exit(app.exec())
