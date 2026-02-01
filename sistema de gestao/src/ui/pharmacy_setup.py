from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QTabWidget, QFormLayout, QMessageBox,
    QScrollArea, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit
)
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QSize
import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

# Add src to path
src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_root not in sys.path:
    sys.path.insert(0, src_root)

from database.db_manager import PharmacyDatabaseManager


class PharmacySetupWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gestor de Farmácia - Cadastro de Farmácia')
        self.setGeometry(100, 100, 900, 800)
        self.setMinimumSize(800, 700)
        
        self.db_manager = PharmacyDatabaseManager()
        
        # Temporary storage for uploads
        self.logo_path = None
        self.pharmacy_photo_path = None
        self.owner_id = None
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Create the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel('Cadastro de Farmácia')
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        main_layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Owner Information
        self.owner_tab = self.create_owner_tab()
        self.tabs.addTab(self.owner_tab, 'Informações do Proprietário')
        
        # Tab 2: Pharmacy Information
        self.pharmacy_tab = self.create_pharmacy_tab()
        self.tabs.addTab(self.pharmacy_tab, 'Informações da Farmácia')
        
        # Tab 3: Media Upload
        self.media_tab = self.create_media_tab()
        self.tabs.addTab(self.media_tab, 'Logotipo e Fotos')
        
        main_layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton('Registrar Farmácia')
        self.save_btn.setMinimumWidth(150)
        self.save_btn.clicked.connect(self.save_pharmacy)
        
        self.clear_btn = QPushButton('Limpar')
        self.clear_btn.setMinimumWidth(150)
        self.clear_btn.clicked.connect(self.clear_form)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_owner_tab(self):
        """Create owner information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form_layout = QFormLayout(content)
        
        # Owner fields
        self.owner_name = QLineEdit()
        self.owner_email = QLineEdit()
        self.owner_phone = QLineEdit()
        self.owner_cpf = QLineEdit()
        self.owner_password = QLineEdit()
        self.owner_password.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow('Nome Completo:', self.owner_name)
        form_layout.addRow('Email:', self.owner_email)
        form_layout.addRow('Telefone:', self.owner_phone)
        form_layout.addRow('CPF:', self.owner_cpf)
        form_layout.addRow('Senha:', self.owner_password)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_pharmacy_tab(self):
        """Create pharmacy information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form_layout = QFormLayout(content)
        
        # Pharmacy fields
        self.pharmacy_name = QLineEdit()
        self.pharmacy_cnpj = QLineEdit()
        self.pharmacy_address = QLineEdit()
        self.pharmacy_city = QLineEdit()
        
        self.pharmacy_state = QComboBox()
        self.pharmacy_state.addItems([
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
            'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ])
        
        self.pharmacy_zip = QLineEdit()
        self.pharmacy_phone = QLineEdit()
        self.pharmacy_email = QLineEdit()
        
        self.pharmacy_latitude = QDoubleSpinBox()
        self.pharmacy_latitude.setRange(-90, 90)
        self.pharmacy_latitude.setDecimals(6)
        
        self.pharmacy_longitude = QDoubleSpinBox()
        self.pharmacy_longitude.setRange(-180, 180)
        self.pharmacy_longitude.setDecimals(6)
        
        self.pharmacy_description = QTextEdit()
        self.pharmacy_description.setMaximumHeight(100)
        
        form_layout.addRow('Nome da Farmácia:', self.pharmacy_name)
        form_layout.addRow('CNPJ:', self.pharmacy_cnpj)
        form_layout.addRow('Endereço:', self.pharmacy_address)
        form_layout.addRow('Cidade:', self.pharmacy_city)
        form_layout.addRow('Estado:', self.pharmacy_state)
        form_layout.addRow('CEP:', self.pharmacy_zip)
        form_layout.addRow('Telefone:', self.pharmacy_phone)
        form_layout.addRow('Email:', self.pharmacy_email)
        form_layout.addRow('Latitude:', self.pharmacy_latitude)
        form_layout.addRow('Longitude:', self.pharmacy_longitude)
        form_layout.addRow('Descrição:', self.pharmacy_description)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_media_tab(self):
        """Create media upload tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Logo section
        logo_label = QLabel('Logotipo da Farmácia')
        logo_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        layout.addWidget(logo_label)
        
        self.logo_display = QLabel()
        self.logo_display.setMinimumSize(200, 200)
        self.logo_display.setStyleSheet('border: 1px dashed #ccc; background: #f9f9f9;')
        self.logo_display.setAlignment(Qt.AlignCenter)
        self.logo_display.setText('Nenhuma imagem selecionada')
        layout.addWidget(self.logo_display)
        
        logo_btn = QPushButton('Selecionar Logotipo')
        logo_btn.clicked.connect(self.select_logo)
        layout.addWidget(logo_btn)
        
        # Pharmacy photo section
        photo_label = QLabel('Foto da Farmácia')
        photo_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        layout.addWidget(photo_label)
        
        self.photo_display = QLabel()
        self.photo_display.setMinimumSize(200, 200)
        self.photo_display.setStyleSheet('border: 1px dashed #ccc; background: #f9f9f9;')
        self.photo_display.setAlignment(Qt.AlignCenter)
        self.photo_display.setText('Nenhuma imagem selecionada')
        layout.addWidget(self.photo_display)
        
        photo_btn = QPushButton('Selecionar Foto da Farmácia')
        photo_btn.clicked.connect(self.select_pharmacy_photo)
        layout.addWidget(photo_btn)
        
        layout.addStretch()
        return widget
    
    def select_logo(self):
        """Select logo file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Selecionar Logotipo',
            '',
            'Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)'
        )
        
        if file_path:
            self.logo_path = file_path
            self.display_image(self.logo_display, file_path)
    
    def select_pharmacy_photo(self):
        """Select pharmacy photo file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Selecionar Foto da Farmácia',
            '',
            'Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)'
        )
        
        if file_path:
            self.pharmacy_photo_path = file_path
            self.display_image(self.photo_display, file_path)
    
    def display_image(self, label: QLabel, file_path: str):
        """Display image in label"""
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
    
    def copy_image_to_assets(self, source_path: str, image_type: str) -> str:
        """Copy image to assets folder and return the new path"""
        if not source_path or not os.path.exists(source_path):
            return None
        
        assets_dir = os.path.join(
            os.path.dirname(__file__),
            '../../assets/uploads'
        )
        os.makedirs(assets_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(source_path)[1]
        new_filename = f'{image_type}_{timestamp}{ext}'
        new_path = os.path.join(assets_dir, new_filename)
        
        try:
            shutil.copy2(source_path, new_path)
            return new_path
        except Exception as e:
            raise Exception(f'Erro ao copiar imagem: {str(e)}')
    
    def validate_owner_form(self) -> bool:
        """Validate owner information"""
        if not self.owner_name.text().strip():
            QMessageBox.warning(self, 'Validação', 'Nome do proprietário é obrigatório')
            return False
        
        if not self.owner_email.text().strip():
            QMessageBox.warning(self, 'Validação', 'Email é obrigatório')
            return False
        
        if not self.owner_phone.text().strip():
            QMessageBox.warning(self, 'Validação', 'Telefone é obrigatório')
            return False
        
        if not self.owner_cpf.text().strip():
            QMessageBox.warning(self, 'Validação', 'CPF é obrigatório')
            return False
        
        if not self.owner_password.text().strip():
            QMessageBox.warning(self, 'Validação', 'Senha é obrigatória')
            return False
        
        return True
    
    def validate_pharmacy_form(self) -> bool:
        """Validate pharmacy information"""
        if not self.pharmacy_name.text().strip():
            QMessageBox.warning(self, 'Validação', 'Nome da farmácia é obrigatório')
            return False
        
        if not self.pharmacy_cnpj.text().strip():
            QMessageBox.warning(self, 'Validação', 'CNPJ é obrigatório')
            return False
        
        if not self.pharmacy_address.text().strip():
            QMessageBox.warning(self, 'Validação', 'Endereço é obrigatório')
            return False
        
        if not self.pharmacy_city.text().strip():
            QMessageBox.warning(self, 'Validação', 'Cidade é obrigatória')
            return False
        
        if not self.pharmacy_phone.text().strip():
            QMessageBox.warning(self, 'Validação', 'Telefone é obrigatório')
            return False
        
        if not self.pharmacy_email.text().strip():
            QMessageBox.warning(self, 'Validação', 'Email é obrigatório')
            return False
        
        return True
    
    def save_pharmacy(self):
        """Save pharmacy and owner information"""
        try:
            # Validate forms
            if not self.validate_owner_form():
                self.tabs.setCurrentIndex(0)
                return
            
            if not self.validate_pharmacy_form():
                self.tabs.setCurrentIndex(1)
                return
            
            # Create owner
            self.owner_id = self.db_manager.create_owner(
                full_name=self.owner_name.text().strip(),
                email=self.owner_email.text().strip(),
                phone=self.owner_phone.text().strip(),
                cpf=self.owner_cpf.text().strip(),
                password=self.owner_password.text().strip()
            )
            
            # Copy images to assets
            logo_final_path = None
            photo_final_path = None
            
            if self.logo_path:
                logo_final_path = self.copy_image_to_assets(self.logo_path, 'logo')
            
            if self.pharmacy_photo_path:
                photo_final_path = self.copy_image_to_assets(self.pharmacy_photo_path, 'pharmacy')
            
            # Create pharmacy
            pharmacy_id = self.db_manager.create_pharmacy(
                owner_id=self.owner_id,
                name=self.pharmacy_name.text().strip(),
                cnpj=self.pharmacy_cnpj.text().strip(),
                address=self.pharmacy_address.text().strip(),
                city=self.pharmacy_city.text().strip(),
                state=self.pharmacy_state.currentText(),
                zip_code=self.pharmacy_zip.text().strip(),
                phone=self.pharmacy_phone.text().strip(),
                email=self.pharmacy_email.text().strip(),
                latitude=self.pharmacy_latitude.value() if self.pharmacy_latitude.value() != 0 else None,
                longitude=self.pharmacy_longitude.value() if self.pharmacy_longitude.value() != 0 else None,
                logo_path=logo_final_path,
                pharmacy_photo_path=photo_final_path,
                description=self.pharmacy_description.toPlainText().strip() or None
            )
            
            QMessageBox.information(
                self,
                'Sucesso',
                f'Farmácia registrada com sucesso!\n\nID da Farmácia: {pharmacy_id}\nProprietário: {self.owner_name.text()}'
            )
            
            self.clear_form()
            
        except ValueError as e:
            QMessageBox.critical(self, 'Erro de Validação', str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao registrar farmácia: {str(e)}')
    
    def clear_form(self):
        """Clear all form fields"""
        self.owner_name.clear()
        self.owner_email.clear()
        self.owner_phone.clear()
        self.owner_cpf.clear()
        self.owner_password.clear()
        
        self.pharmacy_name.clear()
        self.pharmacy_cnpj.clear()
        self.pharmacy_address.clear()
        self.pharmacy_city.clear()
        self.pharmacy_state.setCurrentIndex(0)
        self.pharmacy_zip.clear()
        self.pharmacy_phone.clear()
        self.pharmacy_email.clear()
        self.pharmacy_latitude.setValue(0)
        self.pharmacy_longitude.setValue(0)
        self.pharmacy_description.clear()
        
        self.logo_path = None
        self.pharmacy_photo_path = None
        self.logo_display.setText('Nenhuma imagem selecionada')
        self.photo_display.setText('Nenhuma imagem selecionada')
        self.logo_display.setPixmap(QPixmap())
        self.photo_display.setPixmap(QPixmap())
        
        self.tabs.setCurrentIndex(0)
    
    def apply_styles(self):
        """Apply stylesheet to the application"""
        stylesheet = """
        QMainWindow {
            background-color: #FAFAFA;
        }
        
        QLabel {
            color: #263238;
            font-family: 'Segoe UI';
        }
        
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            border: 1px solid #B0BEC5;
            border-radius: 4px;
            padding: 6px;
            background-color: #FFFFFF;
            color: #263238;
            font-family: 'Segoe UI';
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #009688;
            background-color: #FFFFFF;
        }
        
        QPushButton {
            background-color: #009688;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            font-family: 'Segoe UI';
        }
        
        QPushButton:hover {
            background-color: #00796B;
        }
        
        QPushButton:pressed {
            background-color: #004D40;
        }
        
        QTabWidget::pane {
            border: 1px solid #B0BEC5;
        }
        
        QTabBar::tab {
            background-color: #ECEFF1;
            color: #263238;
            padding: 8px 20px;
            border: 1px solid #B0BEC5;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #009688;
            color: #FFFFFF;
        }
        """
        self.setStyleSheet(stylesheet)


def main():
    import sys
    app = __import__('PyQt5.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    window = PharmacySetupWizard()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
