from PySide6.QtWidgets import (
    QWidget, QLabel, QApplication, QPushButton, 
    QVBoxLayout, QComboBox, QMainWindow, QRubberBand,
    QTextEdit)
from PySide6.QtCore import Qt, QRect, Signal, QSize
from PySide6.QtGui import QPalette, QColor
from PIL import ImageGrab
from main import perform_ocr, translate_text, map_to_tesseract_lang_code

def capture_screen(qrect):
    # Implement screen capture
    MAC_CAPTURE_OFFSET = 60
    if qrect is None:
        image = ImageGrab.grab()
    else:
        x, y, width, height = qrect.getRect()
        # convert to PIL tuple
        bbox = (x, y + MAC_CAPTURE_OFFSET, x + width, y + height + MAC_CAPTURE_OFFSET)
        image = ImageGrab.grab(bbox=bbox)
    
    # Save the image to a temporary file for debugging
    image.save("temp.png")

    return image



    
class ScreenOverlay(QWidget):

    areaSelected = Signal(QRect)

    def __init__(self):
        super(ScreenOverlay, self).__init__()

        # Make the window cover the entire screen
        self.setGeometry(QApplication.instance().primaryScreen().geometry())

        # Make the window transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.5) 

        # Make the window transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize the rubber band
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)

        # Initialize the rubber band color
        palette = QPalette()
        palette.setColor(QPalette.Highlight, QColor(Qt.red))
        self.rubber_band.setPalette(palette)

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubber_band.setGeometry(QRect(self.origin, QSize()))
        self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.rubber_band.isVisible():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.rubber_band.hide()
        selected_region = self.rubber_band.geometry()
        self.areaSelected.emit(selected_region)
        self.close()

class OCRTranslationWindow(QMainWindow):
    def __init__(self, source_lang, target_lang):
        super(OCRTranslationWindow, self).__init__()
        self.source_lang = source_lang
        self.target_lang = target_lang

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.ocr_result = QTextEdit("OCR Result will be shown here.")
        self.translation_result = QTextEdit("Translation will be shown here.")

        self.select_area_button = QPushButton("Select Area")
        self.select_area_button.clicked.connect(self.on_select_area_button_clicked)

        self.capture_button = QPushButton("Capture")
        self.capture_button.clicked.connect(self.on_capture_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.ocr_result)
        layout.addWidget(self.translation_result)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.select_area_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Make a placeholder for the selected region for repeated screen capture
        self.selected_region = None

        # TODO: Mark the selected region with a rectangle


    def on_capture_button_clicked(self):
        # if no selected region, capture the entire screen
        # print(f"Selected region: {self.selected_region}") 
        # Convert the human-readable language to its respective tesseract code (you need to implement this mapping)
        tesseract_lang_code = map_to_tesseract_lang_code(self.source_lang)

        if self.selected_region is None:
            image = capture_screen(None)
        else:
            image = capture_screen(self.selected_region)
        # perform OCR
        ocr_result = perform_ocr(image, tesseract_lang_code)
        # perform translation
        translation_result = translate_text(ocr_result, 
                                            source_lang=self.source_lang, 
                                            target_lang=self.target_lang)
        # display results
        self.ocr_result.setText(ocr_result)
        self.translation_result.setText(translation_result)

    def capture_selected_area(self, selected_region):
        self.selected_region = selected_region

    def on_select_area_button_clicked(self):
        # Create a transparent widget and covers the entire screen
        # select an area and return the coordinates
        # mark the selected area with a red rectangle
        self.overlay = ScreenOverlay()
        self.overlay.areaSelected.connect(self.capture_selected_area)
        self.overlay.show()




class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("OCR Translator")
        self.setMinimumSize(400, 200)
        
        layout = QVBoxLayout()

        label1 = QLabel('Select source language:')
        layout.addWidget(label1)
        
        combo1 = QComboBox()
        combo1.addItem("Japanese")
        combo1.addItem("English")
        combo1.addItem("Chinese")
        combo1.addItem("Russian")
        combo1.addItem("German")
        layout.addWidget(combo1)

        label2 = QLabel('Select target language:')
        layout.addWidget(label2)

        combo2 = QComboBox()
        combo2.addItem("Chinese")
        combo2.addItem("English")
        combo2.addItem("Japanese")
        combo2.addItem("Russian")
        combo2.addItem("German")
        layout.addWidget(combo2)

        self.source_language_combo = combo1
        self.target_language_combo = combo2

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.on_start_button_clicked)
        layout.addWidget(self.start_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_start_button_clicked(self):
        source_lang = self.source_language_combo.currentText()
        target_lang = self.target_language_combo.currentText()
        self.ocr_translation_window = OCRTranslationWindow(source_lang, target_lang)
        self.ocr_translation_window.show()