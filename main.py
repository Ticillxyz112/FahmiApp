
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen

from scanner_engine import scan_market


BG = (0.04, 0.06, 0.11, 1)
BLUE = (0.08, 0.22, 0.48, 1)
GREEN = (0.08, 0.48, 0.27, 1)


def make_label(text, size=16, height=dp(45)):
    return Label(
        text=text,
        font_size=size,
        size_hint_y=None,
        height=height,
        halign="center",
        valign="middle"
    )


def make_button(text, callback, color=BLUE):
    button = Button(
        text=text,
        size_hint_y=None,
        height=dp(55),
        background_normal="",
        background_color=color,
        font_size=16
    )
    button.bind(on_press=callback)
    return button


class DashboardScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        layout.add_widget(
            make_label("FAHMI TRADING APP", 25, dp(75))
        )

        layout.add_widget(
            make_label(
                "Automated Crypto Market Scanner",
                14
            )
        )

        layout.add_widget(
            make_button(
                "MULTI-COIN SCANNER",
                self.open_scanner
            )
        )

        layout.add_widget(
            make_button(
                "SMART SCANNER TOP 5",
                self.open_scanner,
                GREEN
            )
        )

        layout.add_widget(
            make_button(
                "BACKTESTING",
                self.open_backtest
            )
        )

        layout.add_widget(
            make_button(
                "PENGATURAN TELEGRAM",
                self.open_telegram
            )
        )

        layout.add_widget(
            make_label(
                "FahmiApp | Trading Dashboard",
                12
            )
        )

        self.add_widget(layout)

    def open_scanner(self, instance):
        self.manager.current = "scanner"

    def open_backtest(self, instance):
        self.manager.current = "backtest"

    def open_telegram(self, instance):
        self.manager.current = "telegram"


class ScannerScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.running = False

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        layout.add_widget(
            make_label("MULTI-COIN SCANNER", 22, dp(60))
        )

        self.status = make_label(
            "Scanner belum dijalankan",
            14
        )

        layout.add_widget(self.status)

        layout.add_widget(
            make_button(
                "MULAI SCAN MARKET",
                self.start_scan,
                GREEN
            )
        )

        scroll = ScrollView()

        self.output = Label(
            text="Hasil analisis akan muncul di sini.",
            size_hint_y=None,
            halign="left",
            valign="top",
            font_size=dp(14)
        )

        self.output.bind(
            width=lambda obj, width:
            setattr(obj, "text_size", (width - dp(10), None))
        )

        self.output.bind(
            texture_size=lambda obj, size:
            setattr(obj, "height", size[1] + dp(30))
        )

        scroll.add_widget(self.output)
        layout.add_widget(scroll)

        layout.add_widget(
            make_button(
                "KEMBALI KE DASHBOARD",
                self.go_home
            )
        )

        self.add_widget(layout)

    def start_scan(self, instance):

        if self.running:
            return

        self.running = True

        self.status.text = "Mengambil data Binance..."
        self.output.text = (
            "Mohon tunggu.\n"
            "Scanner sedang menganalisis 22 koin."
        )

        threading.Thread(
            target=self.scan_worker,
            daemon=True
        ).start()

    def scan_worker(self):

        try:
            result = scan_market()

            Clock.schedule_once(
                lambda dt: self.show_results(result),
                0
            )

        except Exception as error:

            Clock.schedule_once(
                lambda dt, message=str(error): self.show_error(message),
                0
            )

    def show_results(self, data):

        self.running = False

        results = data["results"]
        errors = data["errors"]
        top5 = data["top5"]

        text = "TOP 5 CRYPTO SIGNALS\n"
        text += "=" * 30 + "\n\n"

        if not results:
            text += "Tidak ada data koin yang berhasil diperoleh.\n"
        else:
            for index, coin in enumerate(top5, 1):

                text += (
                    f"{index}. {coin['coin']}\n"
                    f"Price: {coin['price']:.8g}\n"
                    f"Score: {coin['score']}/100\n"
                    f"RSI: {coin['rsi']:.2f}\n"
                    f"Volume: {coin['volume']:.2f}x\n"
                    f"Entry: {coin['entry']:.8g}\n"
                    f"Stop Loss: {coin['sl']:.8g}\n"
                    f"TP1: {coin['tp1']:.8g}\n"
                    f"TP2: {coin['tp2']:.8g}\n"
                    f"TP3: {coin['tp3']:.8g}\n"
                    f"Breakout: {coin['breakout']}\n"
                    + "-" * 30 + "\n"
                )

        text += "\nSEMUA HASIL SCAN\n\n"

        for coin in results:
            text += (
                f"{coin['coin']} | "
                f"Score: {coin['score']}\n"
            )

        text += f"\nBerhasil: {len(results)} koin"
        text += f"\nGagal: {len(errors)} koin"

        if errors:
            text += "\n\nDAFTAR ERROR\n"

            for item in errors:
                text += (
                    f"{item['coin']}: "
                    f"{item['error'][:100]}\n"
                )

        self.output.text = text

        self.status.text = (
            f"Scan selesai | "
            f"{len(results)} koin berhasil"
        )

    def show_error(self, error):

        self.running = False
        self.status.text = "Scanner mengalami error"
        self.output.text = error

    def go_home(self, instance):
        self.manager.current = "dashboard"


class BacktestScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        layout.add_widget(
            make_label("BACKTESTING", 24)
        )

        layout.add_widget(
            make_label(
                "Modul backtesting akan diintegrasikan "
                "setelah dashboard scanner diuji.",
                15,
                dp(100)
            )
        )

        layout.add_widget(
            make_button(
                "KEMBALI",
                self.go_home
            )
        )

        self.add_widget(layout)

    def go_home(self, instance):
        self.manager.current = "dashboard"


class TelegramScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        layout.add_widget(
            make_label("TELEGRAM SETTINGS", 23)
        )

        layout.add_widget(
            make_label(
                "Integrasi Telegram akan diaktifkan "
                "setelah token diamankan.",
                15,
                dp(100)
            )
        )

        layout.add_widget(
            make_button(
                "KEMBALI",
                self.go_home
            )
        )

        self.add_widget(layout)

    def go_home(self, instance):
        self.manager.current = "dashboard"


class FahmiApp(App):

    def build(self):

        Window.clearcolor = BG

        manager = ScreenManager()

        manager.add_widget(
            DashboardScreen(name="dashboard")
        )

        manager.add_widget(
            ScannerScreen(name="scanner")
        )

        manager.add_widget(
            BacktestScreen(name="backtest")
        )

        manager.add_widget(
            TelegramScreen(name="telegram")
        )

        return manager


if __name__ == "__main__":
    FahmiApp().run()
