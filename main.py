
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

class FahmiApp(App):

    def build(self):
        Window.clearcolor = (0.06, 0.09, 0.15, 1)

        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        judul = Label(
            text="FAHMI APP",
            font_size=32,
            bold=True
        )

        deskripsi = Label(
            text="Aplikasi Android pertamaku",
            font_size=16
        )

        self.nama = TextInput(
            hint_text="Masukkan nama kamu",
            multiline=False,
            size_hint=(1, 0.2)
        )

        tombol = Button(
            text="MULAI",
            size_hint=(1, 0.2),
            background_color=(0.1, 0.35, 0.9, 1)
        )

        tombol.bind(on_press=self.sapa)

        self.hasil = Label(
            text="Selamat datang!",
            font_size=18
        )

        layout.add_widget(judul)
        layout.add_widget(deskripsi)
        layout.add_widget(self.nama)
        layout.add_widget(tombol)
        layout.add_widget(self.hasil)

        return layout

    def sapa(self, instance):
        nama = self.nama.text.strip()

        if nama:
            self.hasil.text = "Halo, " + nama + "!"

        else:
            self.hasil.text = "Masukkan nama terlebih dahulu!"

if __name__ == "__main__":
    FahmiApp().run()

