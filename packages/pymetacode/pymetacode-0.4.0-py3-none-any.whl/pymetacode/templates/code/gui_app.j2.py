import sys

from PySide6.QtWidgets import QApplication
{%- if gui.splash %}
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen
{%- endif %}

from {{ package.name }}.gui.mainwindow import MainWindow


{% if gui.splash -%}
def splash_screen():
    pixmap = QPixmap(
        os.path.join(os.path.dirname(__file__), "data", "splash.svg")
    )
    splash = QSplashScreen(pixmap)
    splash.show()
    return splash


{% endif -%}
def main():
    app = QApplication(sys.argv)
    {% if gui.splash -%}
    splash = splash_screen()

    {% endif -%}
    window = MainWindow()
    window.show()
    {% if gui.splash -%}

    alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
    splash.showMessage("Loaded main window", alignment=alignment)
    splash.finish(window)

    {% endif -%}
    app.exec()


if __name__ == "__main__":
    main()