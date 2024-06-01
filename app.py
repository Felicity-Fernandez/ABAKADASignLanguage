from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.camera import Camera
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from PIL import Image as PILImage
from kivy.metrics import dp
import re
from Syllabify import syllabify 


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Make button background transparent
        self.color = (0, 0, 0, 1)  # Set the font color to black

        with self.canvas.before:
            Color(198 / 255, 205 / 255, 255 / 255, 1)  # RGBA values for #C6CDFF
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        
        # Add padding to the bottom of the layout
        self.layout = BoxLayout(orientation='vertical', padding=[0, 0, 0, 50])
        
        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add logo image
        logo = Image(source='logo.png', size_hint=(None, None))
        logo.size = (Window.width * 0.5, Window.width * 0.5)  # Adjust the size as needed
        logo.pos_hint = {'center_x': 0.5, 'top': 1}  # Center the logo horizontally and keep it at the top
        self.layout.add_widget(logo)

        # Create a GridLayout for buttons
        button_layout = GridLayout(cols=2, spacing=20, size_hint=(None, None))
        button_layout.bind(minimum_height=button_layout.setter('height'))

        # Add buttons to the GridLayout
        button1 = RoundedButton(text="PAGPAPANTIG", font_size=20, size_hint=(None, None), size=(250, 30))
        button2 = RoundedButton(text="BALIK TANAW", font_size=20, size_hint=(None, None), size=(250, 30))
        button3 = RoundedButton(text="PINASOK NA SALITA", font_size=20, size_hint=(None, None), size=(250, 30))
        button4 = RoundedButton(text="HATIIN SA MGA PANTIG", font_size=20, size_hint=(None, None), size=(250, 30))

        # Bind buttons to transition to Screens
        button3.bind(on_release=lambda x: setattr(self.manager, 'current', 'pinasok_na_salita'))
        button2.bind(on_release=lambda x: setattr(self.manager, 'current', 'second'))  # Go to the next page when button2 is clicked

        button_layout.add_widget(button1)
        button_layout.add_widget(button2)
        button_layout.add_widget(button3)
        button_layout.add_widget(button4)

        # Add button layout
        self.layout.add_widget(button_layout)

        # Center the GridLayout horizontally
        button_layout.size = (500, 200)  # Adjust size as needed
        button_layout.pos_hint = {'center_x': 0.50}  # Center horizontally

        self.add_widget(self.layout)

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg3.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        self.add_widget(back_button)

        # Add label with centered text
        label = Label(text="BALIK TANAW SA ALPABETONG\nPILIPINO", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.9}, halign='center')
        self.add_widget(label)

        # Add buttons
        button1 = RoundedButton(text="ABAKADA", font_size=20, size_hint=(None, None), size=(250, 30), pos_hint={'center_x': 0.5, 'center_y': 0.6})
        button2 = RoundedButton(text="ALPABETONG PILIPINO", font_size=20, size_hint=(None, None), size=(250, 30), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        button_layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(None, None), size=(250, 150), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        button_layout.add_widget(button1)
        button_layout.add_widget(button2)
        self.add_widget(button_layout)

        # Bind button1 to transition to AbakadaScreen
        button1.bind(on_release=lambda x: setattr(self.manager, 'current', 'abakada'))
        button2.bind(on_release=lambda x: setattr(self.manager, 'current', 'alpabetong_pilipino'))


    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

class AbakadaScreen(Screen):
    def __init__(self, **kwargs):
        super(AbakadaScreen, self).__init__(**kwargs)

        # Load the TensorFlow model
        self.model = tf.keras.models.load_model('my_model.h5')

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg3.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add help button
        help_button = Button(size_hint=(None, None), size=(60, 60), background_normal='help.png', pos=(Window.width - 70, Window.height - 85))
        self.add_widget(help_button)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'second'))
        self.add_widget(back_button)

        # Add label with centered text
        label = Label(text="ABAKADA", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.9}, halign='center')
        self.add_widget(label)

        # Add mock camera image (replace with actual camera implementation if available)
        self.camera_image = Image(source='logo2.png', size_hint=(0.4, 0.4), pos_hint={'center_x': 0.3, 'center_y': 0.5})
        self.add_widget(self.camera_image)

        # Add label for predictions
        self.prediction_label = Label(text="Predicted: ", font_name="transportm.ttf", font_size=20, size_hint=(None, None), size=(200, 100), pos_hint={'center_x': 0.7, 'center_y': 0.5})
        self.add_widget(self.prediction_label)

        # Add ScrollView for alphabet images
        scroll_view = ScrollView(size_hint=(None, None), size=(Window.width * 0.7, Window.height * 0.2), pos_hint={'center_x': 0.55, 'center_y': 0.15})
        scroll_layout = GridLayout(cols=6, spacing=5, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Path to the folder containing the alphabet images
        alphabet_folder = 'D:/E kix/AnYe portfolio/codes/hotdog/htest'

        # Add alphabet images to the ScrollView
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            image_path = os.path.join(alphabet_folder, f'{letter}.jpg')
            letter_image = Image(source=image_path, size_hint=(None, None), size=(50, 50))
            label = Label(text=letter, size_hint=(None, None), size=(50, 20), halign='center', valign='middle')  # Add label with image name
            letter_box = BoxLayout(orientation='vertical', size_hint_y=None, height=70)
            letter_box.add_widget(letter_image)
            letter_box.add_widget(label)
            scroll_layout.add_widget(letter_box)

        scroll_view.add_widget(scroll_layout)
        self.add_widget(scroll_view)

        # Schedule the prediction updates
        Clock.schedule_interval(self.update_prediction, 1.0 / 30.0)  # Update at 30 FPS

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def update_prediction(self, dt):
        # Placeholder for capturing frame from the camera (or load an image from file for this example)
        # Replace with actual camera frame capture logic
        img_path = 'D:\E kix\AnYe portfolio\codes\hotdog\htest\X.jpg'
        input_image = PILImage.open(img_path).resize((150, 150))
        input_image = img_to_array(input_image)
        input_image = np.expand_dims(input_image, axis=0)
        input_image = input_image / 255.0  # Normalize

        # Get prediction
        prediction = self.model.predict(input_image)
        predicted_letter = chr(np.argmax(prediction) + 65)  # Convert prediction index to corresponding letter
        self.prediction_label.text = f"Predicted: {predicted_letter}"

class AlpabetongPilipinoScreen(Screen):
    def __init__(self, **kwargs):
        super(AlpabetongPilipinoScreen, self).__init__(**kwargs)

        # Load the TensorFlow model
        self.model = tf.keras.models.load_model('my_model.h5')

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg3.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add help button
        help_button = Button(size_hint=(None, None), size=(60, 60), background_normal='help.png', pos=(Window.width - 70, Window.height - 85))
        self.add_widget(help_button)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'second'))
        self.add_widget(back_button)

        # Add label with centered text
        label = Label(text="ALPABETONG PILIPINO", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.9}, halign='center')
        self.add_widget(label)

        # Add mock camera image (replace with actual camera implementation if available)
        self.camera_image = Image(source='logo2.png', size_hint=(0.4, 0.4), pos_hint={'center_x': 0.3, 'center_y': 0.5})
        self.add_widget(self.camera_image)

        # Add label for predictions
        self.prediction_label = Label(text="Predicted: ", font_name="transportm.ttf", font_size=20, size_hint=(None, None), size=(200, 100), pos_hint={'center_x': 0.7, 'center_y': 0.5})
        self.add_widget(self.prediction_label)

        # Add ScrollView for alphabet images
        scroll_view = ScrollView(size_hint=(None, None), size=(Window.width * 0.7, Window.height * 0.2), pos_hint={'center_x': 0.55, 'center_y': 0.15})
        scroll_layout = GridLayout(cols=6, spacing=5, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Path to the folder containing the alphabet images
        alphabet_folder = 'D:/E kix/AnYe portfolio/codes/hotdog/htest'

        # Add alphabet images to the ScrollView
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            image_path = os.path.join(alphabet_folder, f'{letter}.jpg')
            letter_image = Image(source=image_path, size_hint=(None, None), size=(50, 50))
            label = Label(text=letter, size_hint=(None, None), size=(50, 20), halign='center', valign='middle')  # Add label with image name
            letter_box = BoxLayout(orientation='vertical', size_hint_y=None, height=70)
            letter_box.add_widget(letter_image)
            letter_box.add_widget(label)
            scroll_layout.add_widget(letter_box)

        scroll_view.add_widget(scroll_layout)
        self.add_widget(scroll_view)

        # Schedule the prediction updates
        Clock.schedule_interval(self.update_prediction, 1.0 / 30.0)  # Update at 30 FPS

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def update_prediction(self, dt):
        # Placeholder for capturing frame from the camera (or load an image from file for this example)
        # Replace with actual camera frame capture logic
        img_path = 'D:\E kix\AnYe portfolio\codes\hotdog\htest\X.jpg'
        input_image = PILImage.open(img_path).resize((150, 150))
        input_image = img_to_array(input_image)
        input_image = np.expand_dims(input_image, axis=0)
        input_image = input_image / 255.0  # Normalize

        # Get prediction
        prediction = self.model.predict(input_image)
        predicted_letter = chr(np.argmax(prediction) + 65)  # Convert prediction index to corresponding letter
        self.prediction_label.text = f"Predicted: {predicted_letter}"


class RowWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(RowWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(30)  # Set a fixed height for each row

        # Add Line at the bottom of each row
        with self.canvas.after:
            Color(0, 0, 0, 1)  # Set color for the line (black)
            self.line = Line(points=[self.x, self.y, self.x + self.width, self.y], width=1)

        # Bind the Line's points to the size and position of the RowWidget
        self.bind(size=self._update_line, pos=self._update_line)

    def _update_line(self, *args):
        # Update the Line's points to match the width of the RowWidget
        self.line.points = [self.x, self.y, self.x + self.width, self.y]
        
class PinasokNaSalitaScreen(Screen):
    def __init__(self, **kwargs):
        super(PinasokNaSalitaScreen, self).__init__(**kwargs)
        self.recorded_words = []

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg3.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        self.add_widget(back_button)

        # Add label with centered text
        label = Label(text="MGA PINASOK NA SALITA", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.9}, halign='center')
        self.add_widget(label)

        # Create a ScrollView
        self.scroll_view = ScrollView(size_hint=(None, None), size=(Window.width * 0.8, Window.height * 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.4}, bar_color=[0, 0, 0, 1])

        # Create a layout for recorded words and their syllabification
        self.container_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        with self.container_layout.canvas.before:
            Color(198 / 255, 205 / 255, 255 / 255, 1)  # RGBA values for the desired background color
            self.rect = Rectangle(pos=self.container_layout.pos, size=self.container_layout.size)
        self.container_layout.bind(pos=self._update_rect, size=self._update_rect)
        self.container_layout.bind(minimum_height=self.container_layout.setter('height'))  # Allow the layout to expand in height based on content

        # Add the container layout to the ScrollView
        self.scroll_view.add_widget(self.container_layout)

        # Add the ScrollView to the screen
        self.add_widget(self.scroll_view)

    def update_recorded_words(self, new_words):
        self.recorded_words = new_words
        self.container_layout.clear_widgets()

        for recorded_word in self.recorded_words:
            syllabified_word = '-'.join(syllabify(recorded_word))  # Syllabify the recorded word
            recorded_word_label = Label(text=recorded_word, font_size=16, size_hint_y=None, height=dp(30), halign='left', color=[0, 0, 0, 1])
            syllabified_word_label = Label(text=syllabified_word, font_size=16, size_hint_y=None, height=dp(30), halign='right', color=[0, 0, 0, 1])
            
            # Create a custom widget for each row
            row_widget = RowWidget()
            row_widget.add_widget(recorded_word_label)
            row_widget.add_widget(syllabified_word_label)
            self.container_layout.add_widget(row_widget)

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class SignLanguageApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SecondScreen(name='second'))
        sm.add_widget(AbakadaScreen(name='abakada'))  # Add the AbakadaScreen
        sm.add_widget(AlpabetongPilipinoScreen(name='alpabetong_pilipino')) 
        sm.add_widget(PinasokNaSalitaScreen(name='pinasok_na_salita')) 
        return sm

# Run the Kivy application
if __name__ == '__main__':
    from kivy.app import App

    class TestApp(App):
        def build(self):
            screen = PinasokNaSalitaScreen()
            screen.update_recorded_words([
                "KARAPATAN", "BAHAY", "BATUTA", "KABANATA", "ANO",
                "BAKIT", "SAAN", "HOTDOG", "ASO", "BULAKLAK",
                "KAMAY", "MANGGA", "MABAIT", "PAYONG", "PAG-IBIG",
                "NAKAKAINIS", "YELO", "KUMUSTA", "MAINIT", "MUSIKA", "PAG-IIGIB"
            ])
            return screen

    TestApp().run()