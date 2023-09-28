import os
from functools import lru_cache


class Color:
    @staticmethod
    def get_color(color_code: str) -> str:

        return f"\033[{color_code}m"
    BLACK = get_color('30')
    RED = get_color("31")
    GREEN = get_color("32")
    YELLOW = get_color("33")
    BLUE = get_color("34")
    MAGENTA = get_color("35")
    CYAN = get_color("36")
    WHITE = get_color("37")
    RESET = get_color("0")



class BackgroundColor:
    
    @staticmethod
    def get_color(color_code: str) -> str:
        return f"\033[{color_code}m"
    
    BG_BLACK = get_color('40')
    BG_RED = get_color('41')
    BG_GREEN = get_color('42')
    BG_YELLOW = get_color('43')
    BG_BLUE = get_color('44')
    BG_MAGENTA = get_color('45')
    BG_CYAN = get_color('46')
    BG_WHITE = get_color('47')
    RESET = get_color('0')
    
class _Box:
    def __init__(self, Width: int=56):
        self.Width = Width
        StrWidth = "─" * Width
        _Box.UW = f"╭{StrWidth}╮\n"
        _Box.DW = f"╰{StrWidth}╯\n"
    # TODO: Here make a function that can rescale UW, DW 
    ############CHARACTERS############
    URC: str = "╮" # Up Right Conner
    ULC: str = "╭" # Up Left Conner
    DRC: str = "╯" # Down Right Conner
    DLC: str = "╰" # Down Left Conner
    DC: str = "─"  # Dash Character
    UC: str = "│"  # Upward Character
    SPACE:str = " " # Space
    UW: str = "╭────────────────────────────────────────────────────────╮\n" # Upward Wall
    DW: str = "╰────────────────────────────────────────────────────────╯\n" # Upward Wall
    ##################################
    
    
    
    
    
    
    def PrintEmptyRow(self) -> str:
            return f"{_Box.UC}{_Box.SPACE * self.Width}{_Box.UC}\n"
    
    
    

    
#           The main idea
#   1. make a array [].  ✅
#   2. then add text into arrays with a function [AddText("Text", line_number, isInverted)].✅
#   3. then using a empty list, add those text into the empty function making 
#      the data for the whole box. ✅
#   4. and decode them and make it into a string ready to be printed. ✅

# More TODO: Remove that paradox with the Draw instalization (atlest try) ✅, 


'''
TODO: 1. Upgrade DrawBoz class so that the Size can be customizable and text placement (center, right, left) ✅
TODO: 2. Make all the customizable ascpects into a array. ✅
TODO: 3. Go to a Psychiatrist and get a brain scan to check how stupid I am ❌
'''

class DrawBoz:


    def __init__(self, Array: list, Height: int=12, Width: int=56):  
        self.Height = Height
        self.Width = Width  
        self.InputArray = Array
        self.CompleteArray = ["null"] * self.Height
    
    @staticmethod
    def AddText(Text: str, LineNumber: int=0,position: int=1 ,TextColour: Color=Color.RESET, TextBackgroundColor: BackgroundColor=BackgroundColor.RESET) -> list: # should only be used in Array varible
        isColored = True
        text = Text
        text = f"{TextColour}{TextBackgroundColor}{text}{BackgroundColor.RESET}"
        
        if TextColour == Color.RESET and TextBackgroundColor == BackgroundColor.RESET:
            isColored = False
            
        return [text, LineNumber, position, isColored]
    
                
    @lru_cache(maxsize=128)
    def RenderString(self) -> str:  
        # Just prepares Adds Line data into CompleteArray
        for text, LineNumber, isInverted, isColored in self.InputArray:
            if 0 <= LineNumber < len(self.CompleteArray):
                self.CompleteArray[LineNumber] = [text, LineNumber, isInverted, isColored]
        
        
        
        
        BoxClass = _Box(self.Width) 
        OutputString = "" 
        OutputString += _Box.UW 
        
        for i in range(len(self.CompleteArray)): 
            
            if isinstance(self.CompleteArray[i], list) and int(self.CompleteArray[i][2]) > 2:
                raise ValueError("Position Value is Invaild, It should be 0 (right), 1 (center) or 2 (left)")
            
            
            if self.CompleteArray[i] == "null":
                OutputString += _Box.PrintEmptyRow(BoxClass) 
            # Code to handle Rendering Text
            
            # Print at Right Side
            elif isinstance(self.CompleteArray[i], list) and i == self.CompleteArray.index(self.CompleteArray[i]) and self.CompleteArray[i][3] == False and self.CompleteArray[i][2] == 0:
                OutputString += f"{BoxClass.UC} {(self.CompleteArray[i][0])}{'‎' * (self.Width - 6)}{BoxClass.UC}\n"
                
            elif isinstance(self.CompleteArray[i], list) and i == self.CompleteArray.index(self.CompleteArray[i]) and self.CompleteArray[i][3] == True and self.CompleteArray[i][2] == 0:
                OutputString += f"{BoxClass.UC} {(self.CompleteArray[i][0])}{'‎' * (self.Width - 6)}{BoxClass.UC}\n"
                
            # Print at Center
            
            elif isinstance(self.CompleteArray[i], list) and i == self.CompleteArray.index(self.CompleteArray[i]) and self.CompleteArray[i][3] == False and self.CompleteArray[i][2] == 1:
                OutputString += f"{BoxClass.UC}{(self.CompleteArray[i][0]).center(self.Width + 12)}{BoxClass.UC}\n"
                
            elif isinstance(self.CompleteArray[i], list) and i == self.CompleteArray.index(self.CompleteArray[i]) and self.CompleteArray[i][3] == True and self.CompleteArray[i][2] == 1:
                OutputString += f"{BoxClass.UC}{(self.CompleteArray[i][0]).center(self.Width + 14)}{BoxClass.UC}\n"
                
            # Print at Left Side
            
            elif isinstance(self.CompleteArray[i], list) and i == self.CompleteArray.index(self.CompleteArray[i]) and self.CompleteArray[i][3] == False and self.CompleteArray[i][2] == 2:
                OutputString += f"{BoxClass.UC}{'‎' * (self.Width - 6)}{(self.CompleteArray[i][0])} {BoxClass.UC}\n"
                
            elif isinstance(self.CompleteArray[i], list) and i == self.CompleteArray.index(self.CompleteArray[i]) and self.CompleteArray[i][3] == True and self.CompleteArray[i][2] == 2:
                OutputString += f"{BoxClass.UC}{'‎' * (self.Width - 6)}{(self.CompleteArray[i][0])} {BoxClass.UC}\n"
            
            
            
        OutputString += _Box.DW 
        self.RenderString.cache_clear()
        return OutputString
