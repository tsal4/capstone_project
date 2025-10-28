from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

#pip install Kivy

class Alfred(App):
    def build(self):
        self.window = GridLayout()
        #add widgets to window
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        #image widget
        self.window.add_widget(Image(source="C:\\Users\\steph\\Downloads\\AlfredLogo.png"))
        
        #Label Widget
        self.greeting = Label(
                            text = "Welcome, ask a question below!",
                            font_size = 25,
                            color ="0099FF"
                             )
        self.window.add_widget(self.greeting)
        #User input widget
        self.user = TextInput(

                        padding_y = (20,20),
                        size_hint = (1,0.5)
        )


        self.window.add_widget(self.user)
        #Button Widget
        self.button = Button(text = "Enter",
                             size_hint = (1,0.5),
                             bold = True,
                             background_color = "#0099FF",
                             background_normal = ""
                             
                             )
        #Microphone Button
        self.mic_button = Button(text= "Mic", size_hint = (None, None), size = (50,50)
                                )
        self.window.add_widget(self.mic_button)


        self.button.bind(on_press= self.callback)
        self.window.add_widget(self.button)

        return self.window

    def callback(self, event):
        self.greeting.text = "Hello " + self.user.text



if __name__ == "__main__":
    Alfred().run()