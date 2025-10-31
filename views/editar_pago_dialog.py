# views/editar_pago_dialog.py
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDoubleSpinBox, QLineEdit, QComboBox,
    QTextEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt


class EditarPagoDialog(QDialog):
    """Diálogo para editar un pago existente."""
    def __init__(self, pago, parent=None):
        super().__init__(parent)
        self.pago = pago
        self.setWindowTitle("Editar Pago")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0, 1000000)
        self.spin_monto.setPrefix("$ ")
        self.spin_monto.setValue(float(self.pago[3]))

        self.txt_mes = QLineEdit(self.pago[5])
        self.cmb_metodo = QComboBox()
        self.cmb_metodo.addItems(["efectivo", "transferencia", "débito", "crédito", "mercadopago", "otro"])
        metodo_actual = self.pago[6].lower() if self.pago[6] else "efectivo"
        idx = self.cmb_metodo.findText(metodo_actual, Qt.MatchFixedString)
        if idx >= 0: self.cmb_metodo.setCurrentIndex(idx)

        self.txt_obs = QTextEdit(self.pago[7] if self.pago[7] else "")
        self.txt_obs.setMaximumHeight(100)

        layout.addRow("Monto:", self.spin_monto)
        layout.addRow("Mes:", self.txt_mes)
        layout.addRow("Método:", self.cmb_metodo)
        layout.addRow("Observaciones:", self.txt_obs)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def obtener_datos(self):
        return (
            self.spin_monto.value(),
            self.txt_mes.text(),
            self.cmb_metodo.currentText(),
            self.txt_obs.toPlainText()
        )
