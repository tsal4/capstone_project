from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
import threading
from kivy.clock import Clock

from Root import guibackend

class Alfred(App):
    def build(self):
        self.window = GridLayout()
        #add widgets to window
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        #image widget
        self.window.add_widget(Image(source="AlfredLogo.png"))    
        
        #Label Widget
        self.greeting = Label(
                            text = "Welcome, ask a question!",
                            font_size = 25,
                            color ="white"
                             )
        self.window.add_widget(self.greeting)


        

        
        #Button Widget
        self.button = Button(text = "Press to Speak",
                             size_hint = (1,0.5), 
                             bold = True,
                             background_color = "#0099FF",
                             background_normal = ""
                             
                             )
        self.button.bind(on_press= self.activateAlfred)
        self.window.add_widget(self.button)
        return self.window

    #When the button is pressed it will listen and print out "Listening for wake word"
    def activateAlfred(self, instance):
        self.greeting.text = "Listening..."
        threading.Thread(target=self.alfredThread).start()

    def alfredThread(self):
        try:
#Prevent the Gui from freezing, run root4.py on another thread and update it to this main thread of the GUI
            user_text, alfred_response = guibackend()
            Clock.schedule_once(lambda dt: self.update_text(user_text, alfred_response))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(str(e)))

    def update_text(self, user_text, response):
        self.greeting.text= f"You said: {user_text}\n\n Alfred: {response}"

    def error(self, msg):
        self.greeting.text = f"Error: {msg}"
   
if __name__ == "__main__":
    Alfred().run()
    







#If needed, extra code for labels and loading screen


#Microphone Button
        #self.mic_button = Button(text= "Mic", size_hint = (None,None), size = (100,50), background_color = "#B700FF"
                                #)
        #Horizontal Layout for Buttons
        #horizontal_layout = BoxLayout(orientation='horizontal', spacing=20, padding=20)

       # horizontal_layout.add_widget(self.mic_button)
        #horizontal_layout.add_widget(self.button)

        #self.window.add_widget(horizontal_layout)


    #def callback(self, event):
       # self.greeting.text = "Loading ..."
       # threading.Thread(target=self.long).start()

   # def long(self):
       # time.sleep(.5)  #only simulating a task, replace with function later

       # Clock.schedule_once(self.update_greeting)

   # def update_greeting(self, event):
       # self.greeting.text = "Hello "




       #self.question = Label(
                            #text = "You: This is where the User will have their response",
                           # font_size = 25,
                           # color ="white"
                          #   )
        
        #self.window.add_widget(self.question)
 
        #User input widget
        #self.user = TextInput(

            #            padding_y = (20,20),
           #             size_hint = (1,0.5)
       # )

       # self.window.add_widget(self.user)