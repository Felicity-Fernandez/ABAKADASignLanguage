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
from kivy.uix.camera import Camera
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
import cv2
from kivy.graphics.texture import Texture


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
            self.bg = Rectangle(source='bg5.png', pos=self.pos, size=self.size)
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
        button1.bind(on_release=lambda x: setattr(self.manager, 'current', 'pagpapantig')) 
        button2.bind(on_release=lambda x: setattr(self.manager, 'current', 'second'))  # Go to the next page when button2 is clicked
        button3.bind(on_release=lambda x: setattr(self.manager, 'current', 'pinasok_na_salita'))
        button4.bind(on_release=lambda x: setattr(self.manager, 'current', 'hatiin_sa_mga_pantig'))

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
            self.bg = Rectangle(source='bg4.png', pos=self.pos, size=self.size)
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
        self.frame_counter = 0  # Counter to track the number of frames processed
        # Load the TensorFlow model
        self.model = tf.keras.models.load_model('best_model.h5')
        self.hand_cascade = cv2.CascadeClassifier('aGest.xml')
        # Check if the model is loaded correctly
        print(self.model.summary())

        # Test the model with a known image
        test_image = cv2.imread('D:/E kix/AnYe portfolio/codes/hotdog/htest/C.jpg')
        test_image = cv2.resize(test_image, (150, 150))
        test_image = img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis=0)
        test_image = test_image / 255.0  # Normalize

        # Get prediction for the test image
        test_prediction = self.model.predict(test_image)
        test_predicted_index = np.argmax(test_prediction)
        print(f"Test prediction: {test_prediction}")
        print(f"Test predicted letter: {chr(test_predicted_index + 65)}")
        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg4.png', pos=self.pos, size=self.size)
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

        # Attempt to initialize camera
        try:
            self.camera = Camera(play=True, resolution=(640, 480), size_hint=(0.4, 0.4), pos_hint={'center_x': 0.3, 'center_y': 0.5})
            self.add_widget(self.camera)
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            self.camera = None
            error_label = Label(text="Failed to initialize camera", font_name="transportm.ttf", font_size=20, size_hint=(None, None), size=(300, 100), pos_hint={'center_x': 0.3, 'center_y': 0.5})
            self.add_widget(error_label)

        # Add label for predictions
        self.prediction_label = Label(text="", font_name="transportm.ttf", font_size=20, size_hint=(None, None), size=(200, 100), pos_hint={'center_x': 0.7, 'center_y': 0.5})
        self.add_widget(self.prediction_label)

        # Add ScrollView for alphabet images
        scroll_view = ScrollView(size_hint=(None, None), size=(Window.width * 0.7, Window.height * 0.2), pos_hint={'center_x': 0.55, 'center_y': 0.15})
        scroll_layout = GridLayout(cols=6, spacing=5, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Path to the folder containing the alphabet images
        alphabet_folder = 'D:/E kix/AnYe portfolio/codes/hotdog/htest'

        # Create a list of letters
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # Insert NTILDE after 'N'
        letters.insert(letters.index('N') + 1, 'NTILDE')

        # Add alphabet images to the ScrollView
        for letter in letters:
            image_path = os.path.join(alphabet_folder, f'{letter}.jpg')
            letter_image = Image(source=image_path, size_hint=(None, None), size=(50, 50))
            label = Label(text=letter, size_hint=(None, None), size=(50, 20), halign='center', valign='middle')  # Add label with image name
            letter_box = BoxLayout(orientation='vertical', size_hint_y=None, height=70)
            letter_box.add_widget(letter_image)
            letter_box.add_widget(label)
            scroll_layout.add_widget(letter_box)

        scroll_view.add_widget(scroll_layout)
        self.add_widget(scroll_view)

        # Initialize update_event to None
        self.update_event = None

    def on_enter(self):
        # Schedule the prediction updates when the screen is active
        self.update_event = Clock.schedule_interval(self.update_prediction, 1.0 / 30.0)  # Update at 30 FPS

    def on_leave(self):
        # Stop the prediction updates when the screen is not active
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def update_prediction(self, dt):
        # Capture frame from the camera
        camera_texture = self.camera.texture
        if camera_texture and camera_texture.size[0] > 0 and camera_texture.size[1] > 0:
            camera_pixels = camera_texture.pixels
            width, height = camera_texture.size
            input_image = np.frombuffer(camera_pixels, np.uint8).reshape(height, width, 4)
            input_image = input_image[:, :, :3]  # Remove alpha channel

            # Convert to grayscale for hand detection
            gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

            # Detect hands using Haar cascade
            hands = self.hand_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(hands) == 0:
                print("No hand detected!")  # Debugging
                self.prediction_label.text = "No hand present"
                return

            # For simplicity, assume only one hand is detected
            x, y, w, h = hands[0]

            # Crop and resize the detected hand region
            hand_region = input_image[y:y+h, x:x+w]
            hand_region = cv2.resize(hand_region, (150, 150))
            hand_region = img_to_array(hand_region)
            hand_region = np.expand_dims(hand_region, axis=0)
            hand_region = hand_region / 255.0  # Normalize

            # Get prediction
            prediction = self.model.predict(hand_region)
            predicted_index = np.argmax(prediction)  # Get the index of the highest probability
            max_confidence = np.max(prediction)  # Get the highest confidence level
            if max_confidence < 0.2:  # Set a threshold for confidence level
                print("Low confidence prediction!")  # Debugging
                self.prediction_label.text = "No significant prediction"
            else:
                predicted_letter = chr(predicted_index + 65)  # Convert prediction index to corresponding letter
                print(f"Prediction probabilities: {prediction}")
                print(f"Predicted letter: {predicted_letter}")  # Debugging
                self.prediction_label.text = f"{predicted_letter}"
        else:
            print("No hand detected!")  # Debugging
            self.prediction_label.text = "No hand present"

class AlpabetongPilipinoScreen(Screen):
    def __init__(self, **kwargs):
        super(AlpabetongPilipinoScreen, self).__init__(**kwargs)

        # Load the TensorFlow model
        self.model = tf.keras.models.load_model('my_model.h5')

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg4.png', pos=self.pos, size=self.size)
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
            self.bg = Rectangle(source='bg4.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        self.add_widget(back_button)

        # Add label with centered text
        label = Label(text="MGA PINASOK NA SALITA", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.9}, halign='center')
        self.add_widget(label)

        # Create a ScrollView
        self.scroll_view = ScrollView(size_hint=(None, None), size=(Window.width * 0.8, Window.height * 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.4}, bar_color=[88/255, 101/255, 242/255, 1])

        # Create a layout for recorded words and their syllabification
        self.container_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        with self.container_layout.canvas.before:
            Color(49 / 255, 51 / 255, 56 / 255, 1)  # RGBA values for the desired background color
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
            recorded_word_label = Label(text=recorded_word, font_size=16, size_hint_y=None, height=dp(30), halign='left')
            syllabified_word_label = Label(text=syllabified_word, font_size=16, size_hint_y=None, height=dp(30), halign='right')
            
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

class LinedLabel(BoxLayout):
    def __init__(self, text='', font_name=None, font_size=None, **kwargs):
        super(LinedLabel, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.label = Label(text=text, font_name=font_name, font_size=font_size)
        self.add_widget(self.label)

        with self.canvas.before:
            Color(1, 1, 1, 1)  # Black color
            self.line = Line()

        self.bind(size=self._update_line)
        self.bind(pos=self._update_line)

    def _update_line(self, *args):
        # Adjust the y-coordinate to move the line higher by 10 pixels
        y_coordinate = self.y + self.height - 65
        self.line.points = [self.x, y_coordinate, self.x + self.width, y_coordinate]
        
class HatiinSaMgaPantigScreen(Screen):
    def __init__(self, **kwargs):
        super(HatiinSaMgaPantigScreen, self).__init__(**kwargs)

        # Ensure keyboard inputs are handled
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

        # Load the TensorFlow model
        self.model = tf.keras.models.load_model('my_model.h5')

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg4.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add help button
        help_button = Button(size_hint=(None, None), size=(60, 60), background_normal='help.png', pos=(Window.width - 70, Window.height - 85))
        help_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'help'))
        self.add_widget(help_button)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        self.add_widget(back_button)

        # Add label with centered text
        label = Label(text="HATIIN SA MGA PANTIG", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.9}, halign='center')
        self.add_widget(label)

        # Add mock camera image (replace with actual camera implementation if available)
        self.camera_image = Image(source='logo2.png', size_hint=(0.4, 0.4), pos_hint={'center_x': 0.3, 'center_y': 0.5})
        self.add_widget(self.camera_image)

        # Add input line for displaying the predicted word or letter
        self.input_label = LinedLabel(text=" ", font_name="transportm.ttf", font_size=20, size_hint=(None, None), size=(300, 100), pos_hint={'center_x': 0.7, 'center_y': 0.5})
        self.add_widget(self.input_label)
        
        # Add label for syllabification
        self.syllabified_label = Label(text=" ", font_name="transportm.ttf", font_size=20, size_hint=(None, None), size=(300, 100), pos_hint={'center_x': 0.7, 'center_y': 0.45})
        self.add_widget(self.syllabified_label)

        # Add ScrollView for default words
        scroll_view = ScrollView(size_hint=(None, None), size=(Window.width * 0.6, Window.height * 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.15})
        scroll_layout = GridLayout(cols=3, spacing=5, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Default words
        default_words = [
            "aso", "araw", "anak", "aral", "ama", "asawa", "bala", "bata", "bahay", "baga", 
            "babae", "baboy", "bago", "baka", "binti", "bigas", "buko", "bulaklak", "bundok", 
            "dahon", "daga", "damit", "dalaga", "daliri", "dilaw", "duyan", "gabi", "ginto", 
            "gulay", "guro", "hangin", "ilaw", "ilog", "ina", "isda", "itim", "kamay", "kanin", 
            "kama", "kanta", "katotohanan", "kape", "kotse", "lamesa", "langit", "laro", "lapis", 
            "langka", "laban", "likod", "lupa", "lolo", "lola", "lungkot", "mahal", "malakas", 
            "malusog", "mangga", "mano", "mata", "matamis", "mainit", "maitim", "mabait", "mabuti", 
            "mangkok", "mesa", "musika", "nagtatanong", "nanay", "niyog", "nobela", "otso", "oras", 
            "puno", "pera", "puso", "pula", "puno", "pagkain", "papel", "payong", "paa", "pag-ibig", 
            "pag-aalaga", "pakikipagkaibigan", "pagkakaibigan", "pagkakaintindihan", "pagkakaiba", 
            "pagkakaintindi", "pagkakamali", "pag-asa", "pagsasama", "pagtutulungan", "pag-usapan", 
            "pagtatapos", "pagtuturo", "walis", "yelo", "paglalakbay"
        ]

        # Add default words to the ScrollView
        for word in default_words:
            word_button = RoundedButton(text=word.upper(), font_size=12, size_hint=(None, None), size=(150, 30))
            word_button.bind(on_release=lambda btn: self.display_default_word(btn.text))
            scroll_layout.add_widget(word_button)

        scroll_view.add_widget(scroll_layout)
        self.add_widget(scroll_view)

        # Schedule the prediction updates
        """Clock.schedule_interval(self.update_prediction, 1.0 / 30.0)  # Update at 30 FPS"""

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def display_default_word(self, word):
        self.input_label.label.text = f"{word}"
        self.syllabified_label.text = f"{'-'.join(syllabify(word))}"

        # Update recorded words in PinasokNaSalitaScreen
        pinasok_na_salita_screen = self.manager.get_screen('pinasok_na_salita')
        pinasok_na_salita_screen.update_recorded_words(pinasok_na_salita_screen.recorded_words + [word])

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        # Handle key inputs
        if keycode[1] == 'q':
            self._next_hand_spelling()
        elif keycode[1] == 'backspace':
            self._remove_previous_letter()
        elif keycode[1] == 'enter':
            self._finish_inputting_hand_spells()
        elif keycode[1] == 'r':
            self._remove_input()
        return True

    def _next_hand_spelling(self):
        # Add another predicted letter next to the current predicted letters
        img_path = 'D:\E kix\AnYe portfolio\codes\hotdog\htest\A.jpg'
        input_image = PILImage.open(img_path).resize((150, 150))
        input_image = img_to_array(input_image)
        input_image = np.expand_dims(input_image, axis=0)
        input_image = input_image / 255.0  # Normalize

        # Get prediction
        prediction = self.model.predict(input_image)
        predicted_letter = chr(np.argmax(prediction) + 65)  # Convert prediction index to corresponding letter

        # Display the predicted letter in the syllabified label
        self.input_label.label.text += predicted_letter

    def _remove_previous_letter(self):
        # Remove the previous letter in the syllabified label
        self.input_label.label.text = self.input_label.label.text[:-1]

    def _finish_inputting_hand_spells(self):
        # Finish inputting hand spells
        # Get the entered word from the input label
        entered_word = self.input_label.label.text.strip()

        # Store the entered word in PinasokNaSalitaScreen
        pinasok_na_salita_screen = self.manager.get_screen('pinasok_na_salita')
        pinasok_na_salita_screen.update_recorded_words([entered_word])

        # Clear the input label for the next input
        self.input_label.label.text = ""

    def _remove_input(self):
        # Remove all input in the syllabified label
        self.input_label.label.text = ""

    """def update_prediction(self, dt):
        # Placeholder for capturing frame from the camera (or load an image from file for this example)
        # Replace with actual camera frame capture logic
        img_path = 'D:\E kix\AnYe portfolio\codes\hotdog\htest\A.jpg'
        input_image = PILImage.open(img_path).resize((150, 150))
        input_image = img_to_array(input_image)
        input_image = np.expand_dims(input_image, axis=0)
        input_image = input_image / 255.0  # Normalize

        # Get prediction
        prediction = self.model.predict(input_image)
        predicted_letter = chr(np.argmax(prediction) + 65)  # Convert prediction index to corresponding letter

        self.input_label.text = f"Predicted: {predicted_letter}"

        # Update the recorded words in PinasokNaSalitaScreen
        pinasok_na_salita_screen = self.manager.get_screen('pinasok_na_salita')
        pinasok_na_salita_screen.update_recorded_words(pinasok_na_salita_screen.recorded_words + [predicted_letter])
"""
class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super(HelpScreen, self).__init__(**kwargs)

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg4.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'hatiin_sa_mga_pantig'))
        self.add_widget(back_button)

        # Create a FloatLayout to hold background and container
        layout = FloatLayout()

        # Background color for container
        with layout.canvas.before:
            Color(49 / 255, 51 / 255, 56 / 255, 1)
            self.rect = Rectangle(pos=(Window.width * 0.1, Window.height * 0.1), size=(Window.width * 0.8, Window.height * 0.75))

        # Add "Help" icon
        help_icon = Image(source='help.png', size_hint=(None, None), size=(35, 35), pos_hint={'center_x': 0.5, 'top': 0.815})
        layout.add_widget(help_icon)

        # Add label with centered text
        help_label = Label(text="HELP", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.805}, halign='center')
        layout.add_widget(help_label)

        # Create GridLayout for help content
        help_content_layout = GridLayout(cols=2, spacing=5, size_hint=(None, None), size=(Window.width * 0.6, Window.height * 0.5), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        help_content_layout.bind(minimum_height=help_content_layout.setter('height'))

        # Add labels for help content
        help_content = [
            ("LETTER Q KEY", "NEXT HAND SPELLING"),
            ("BACKSPACE KEY", "REMOVE PREVIOUS LETTER"),
            ("ENTER KEY", "FINISH INPUTTING HAND SPELLS"),
            ("LETTER R KEY", "REMOVE INPUT")
        ]

        for left_text, right_text in help_content:
            left_label = Label(text=left_text, font_size=16, size_hint=(None, None), size=(Window.width * 0.3, 50), halign='left', text_size=(Window.width * 0.25, None))
            right_label = Label(text=right_text, font_size=16, size_hint=(None, None), size=(Window.width * 0.3, 50), halign='left', text_size=(Window.width * 0.25, None))
            help_content_layout.add_widget(left_label)
            help_content_layout.add_widget(right_label)

        # Add help content layout to the main layout
        layout.add_widget(help_content_layout)

        # Add the layout to the screen
        self.add_widget(layout)

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class PagpapantigScreen(Screen):
    def __init__(self, **kwargs):
        super(PagpapantigScreen, self).__init__(**kwargs)

        # Ensure keyboard inputs are handled
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

        # Load the TensorFlow model
        self.model = tf.keras.models.load_model('my_model.h5')

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg4.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add help button
        help_button = Button(size_hint=(None, None), size=(60, 60), background_normal='help.png', pos=(Window.width - 70, Window.height - 85))
        help_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'help2'))
        self.add_widget(help_button)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        self.add_widget(back_button)

        # Add label with centered text
        label = Label(text="PAGPAPANTIG", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.9}, halign='center')
        self.add_widget(label)

        # Add mock camera image (replace with actual camera implementation if available)
        self.camera_image = Image(source='logo2.png', size_hint=(0.4, 0.4), pos_hint={'center_x': 0.3, 'center_y': 0.5})
        self.add_widget(self.camera_image)

        # Add input line for displaying the predicted word or letter
        self.syllabified_label = LinedLabel(text=" ", font_name="transportm.ttf", font_size=20, size_hint=(None, None), size=(300, 100), pos_hint={'center_x': 0.7, 'center_y': 0.5})
        self.add_widget(self.syllabified_label)
        
        # Add label for default words
        self.input_label = Label(text=" ", font_name="transportm.ttf", font_size=20, size_hint=(None, None), size=(300, 100), pos_hint={'center_x': 0.7, 'center_y': 0.45})
        self.add_widget(self.input_label)

        # Add ScrollView for default words
        scroll_view = ScrollView(size_hint=(None, None), size=(Window.width * 0.6, Window.height * 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.15})
        scroll_layout = GridLayout(cols=3, spacing=5, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Default words
        default_words = [
            "aso", "araw", "anak", "aral", "ama", "asawa", "bala", "bata", "bahay", "baga", 
            "babae", "baboy", "bago", "baka", "binti", "bigas", "buko", "bulaklak", "bundok", 
            "dahon", "daga", "damit", "dalaga", "daliri", "dilaw", "duyan", "gabi", "ginto", 
            "gulay", "guro", "hangin", "ilaw", "ilog", "ina", "isda", "itim", "kamay", "kanin", 
            "kama", "kanta", "katotohanan", "kape", "kotse", "lamesa", "langit", "laro", "lapis", 
            "langka", "laban", "likod", "lupa", "lolo", "lola", "lungkot", "mahal", "malakas", 
            "malusog", "mangga", "mano", "mata", "matamis", "mainit", "maitim", "mabait", "mabuti", 
            "mangkok", "mesa", "musika", "nagtatanong", "nanay", "niyog", "nobela", "otso", "oras", 
            "puno", "pera", "puso", "pula", "puno", "pagkain", "papel", "payong", "paa", "pag-ibig", 
            "pag-aalaga", "pakikipagkaibigan", "pagkakaibigan", "pagkakaintindihan", "pagkakaiba", 
            "pagkakaintindi", "pagkakamali", "pag-asa", "pagsasama", "pagtutulungan", "pag-usapan", 
            "pagtatapos", "pagtuturo", "walis", "yelo", "paglalakbay"
        ]

        # Add default words to the ScrollView
        for word in default_words:
            word_button = RoundedButton(text=word.upper(), font_size=12, size_hint=(None, None), size=(150, 30))
            word_button.bind(on_release=lambda btn: self.display_default_word(btn.text))
            scroll_layout.add_widget(word_button)

        scroll_view.add_widget(scroll_layout)
        self.add_widget(scroll_view)

        # Schedule the prediction updates
        """Clock.schedule_interval(self.update_prediction, 1.0 / 30.0)  # Update at 30 FPS"""

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def display_default_word(self, word):
        self.input_label.text = f"{word}"

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        # Handle key inputs
        if keycode[1] == 'q':
            self._next_hand_spelling()
        elif keycode[1] == 'backspace':
            self._remove_previous_letter()
        elif keycode[1] == 'enter':
            self._finish_inputting_hand_spells()
        elif keycode[1] == 'r':
            self._remove_input()
        elif keycode[1] == 'w':
            self._add_dash()
        return True

    def _next_hand_spelling(self):
        # Add another predicted letter next to the current predicted letters
        img_path = 'D:\E kix\AnYe portfolio\codes\hotdog\htest\A.jpg'
        input_image = PILImage.open(img_path).resize((150, 150))
        input_image = img_to_array(input_image)
        input_image = np.expand_dims(input_image, axis=0)
        input_image = input_image / 255.0  # Normalize

        # Get prediction
        prediction = self.model.predict(input_image)
        predicted_letter = chr(np.argmax(prediction) + 65)  # Convert prediction index to corresponding letter

        # Display the predicted letter in the syllabified label
        self.syllabified_label.label.text += predicted_letter

    def _remove_previous_letter(self):
        # Remove the previous letter in the syllabified label
        if self.syllabified_label.label.text:
            # Clear the outline completely
            self.input_label.canvas.before.clear()
            self.syllabified_label.label.text = self.syllabified_label.label.text[:-1]

    def _finish_inputting_hand_spells(self):
        # Finish inputting hand spells and check correctness
        user_input = self.syllabified_label.label.text.strip().lower()
        correct_syllabification = '-'.join(syllabify(self.input_label.text)).lower()
        # Check if the entered text matches the correct syllabification
        is_correct = user_input == correct_syllabification

        # Update the outline color based on correctness
        self._update_input_label_outline(is_correct)

    def _remove_input(self):
        # Remove all input in the syllabified label
        self.syllabified_label.label.text = ""
        # Clear the outline completely
        self.input_label.canvas.before.clear()

    def _add_dash(self):
        # Add a dash to the syllabified label
        self.syllabified_label.label.text += "-"

    def _update_input_label_outline(self, is_correct):
        # Clear previous outline
        self.input_label.canvas.before.clear()
        with self.input_label.canvas.before:
            if is_correct:
                Color(0, 1, 0, 1)  # Green color
            else:
                Color(1, 0, 0, 1)  # Red color
            Line(rectangle=(self.input_label.x, self.input_label.y, self.input_label.width, self.input_label.height), width=2)

    """def update_prediction(self, dt):
        # Placeholder for capturing frame from the camera (or load an image from file for this example)
        # Replace with actual camera frame capture logic
        img_path = 'D:\E kix\AnYe portfolio\codes\hotdog\htest\A.jpg'
        input_image = PILImage.open(img_path).resize((150, 150))
        input_image = img_to_array(input_image)
        input_image = np.expand_dims(input_image, axis=0)
        input_image = input_image / 255.0  # Normalize

        # Get prediction
        prediction = self.model.predict(input_image)
        predicted_letter = chr(np.argmax(prediction) + 65)  # Convert prediction index to corresponding letter

        # Display the predicted letter in the syllabified label
        self.syllabified_label.text = predicted_letter
    """
class HelpScreen2(Screen):
    def __init__(self, **kwargs):
        super(HelpScreen2, self).__init__(**kwargs)

        # Background image
        with self.canvas.before:
            self.bg = Rectangle(source='bg4.png', pos=self.pos, size=self.size)
            self.bind(size=self._update_bg, pos=self._update_bg)

        # Add back button
        back_button = Button(size_hint=(None, None), size=(60, 60), background_normal='back.png', pos=(10, Window.height - 85))
        back_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'hatiin_sa_mga_pantig'))
        self.add_widget(back_button)

        # Create a FloatLayout to hold background and container
        layout = FloatLayout()

        # Background color for container
        with layout.canvas.before:
            Color(49 / 255, 51 / 255, 56 / 255, 1)
            self.rect = Rectangle(pos=(Window.width * 0.1, Window.height * 0.1), size=(Window.width * 0.8, Window.height * 0.75))

        # Add "Help" icon
        help_icon = Image(source='help.png', size_hint=(None, None), size=(35, 35), pos_hint={'center_x': 0.5, 'top': 0.815})
        layout.add_widget(help_icon)

        # Add label with centered text
        help_label = Label(text="HELP", font_name="transportm.ttf", font_size=30, size_hint=(None, None), size=(Window.width, 100), pos_hint={'center_x': 0.5, 'top': 0.805}, halign='center')
        layout.add_widget(help_label)

        # Create GridLayout for help content
        help_content_layout = GridLayout(cols=2, spacing=5, size_hint=(None, None), size=(Window.width * 0.6, Window.height * 0.5), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        help_content_layout.bind(minimum_height=help_content_layout.setter('height'))

        # Add labels for help content
        help_content = [
            ("LETTER Q KEY", "NEXT HAND SPELLING"),
            ("BACKSPACE KEY", "REMOVE PREVIOUS LETTER"),
            ("ENTER KEY", "FINISH INPUTTING HAND SPELLS"),
            ("LETTER R KEY", "REMOVE INPUT"),
            ("LETTER W KEY", "ADD '-' INPUT")
        ]

        for left_text, right_text in help_content:
            left_label = Label(text=left_text, font_size=16, size_hint=(None, None), size=(Window.width * 0.3, 50), halign='left', text_size=(Window.width * 0.25, None))
            right_label = Label(text=right_text, font_size=16, size_hint=(None, None), size=(Window.width * 0.3, 50), halign='left', text_size=(Window.width * 0.25, None))
            help_content_layout.add_widget(left_label)
            help_content_layout.add_widget(right_label)

        # Add help content layout to the main layout
        layout.add_widget(help_content_layout)

        # Add the layout to the screen
        self.add_widget(layout)

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
        sm.add_widget(HatiinSaMgaPantigScreen(name='hatiin_sa_mga_pantig'))
        sm.add_widget(HelpScreen(name='help'))
        sm.add_widget(PagpapantigScreen(name='pagpapantig'))
        sm.add_widget(HelpScreen2(name='help2'))
        return sm

# Run the Kivy application
if __name__ == '__main__':
    SignLanguageApp().run()
    """from kivy.app import App

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

    TestApp().run()"""