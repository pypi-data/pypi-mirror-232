This library does several things.

Like:-
- Playing video on youtube
- Prompting an input from user via GUI
- Taking the input in '*' format via GUI
- Changing Mouse position
- Moving the mouse
- Making the mouse click on screen
- Speaking the text
- Recognizing the voice
- Changing the voice of the spoken text
- Creating a Calculator with GUI (with one command)
- Solving any expressiong
- Displaying an error message
- Displaying info

For Example:
1) Playing a video:

import mkwhatkit

mkwhatkit.play("Video name")

2) Prompting via GUI:

import mkwhatkit

a = mkwhatkit.prompt("Enter :")

3) Prompting the text hidden:

import mkwhatkit

a = mkwhatkit.password("Enter :")

4) Changing Mouse Position:

import mkwhatkit

mkwhatkit.move_mouse(100,100)

5) Making the mouse click:

import mkwhatkit

# mkwhatkit.click(x,y,clicks,interval,button)
mkwhatkit.click(100,100,1,0,'left')

6) Speaking a set of String :

import mkwhatkit

# mkwhatkit.speak(text)
mkwhatkit.speak("hello")

7) Taking input from the voice:

import mkwhatkit

text = mkwhatkit.recognize_speech()

8) The voice of the spoken text could be changed :

import mkwhatkit

a = mkwhatkit.speak_voices()
# speak_voices contains two voices : a male & a female voice
# male voice is on 0 index
# male voice is default set on the speak() function.
# female voice is on 1 index
voice = a[1]
mkwhatkit.set_voice(voice)

9) Creating a calculator :

import mkwhatkit

mkwhatkit.create_tk_calculator()

10) Solving any expression :

import mkwhatkit

answer = mkwhatkit.calculate("1000*50")
# any expression could be added to solve (without variables) in str format.

11) Displaying an error message:

import mkwhatkit

mkwhatkit.error("Text")

12) Displaying info:

import mkwhatkit

mkwhatkit.info("Text")

=======================================================================================================================================================================================