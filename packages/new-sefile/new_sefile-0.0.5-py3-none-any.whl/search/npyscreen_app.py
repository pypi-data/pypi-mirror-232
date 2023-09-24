# search/npyscreen_app.py

import npyscreen
import curses
import pathlib
import os
from search.callbacks import _some_log

# write your custom code editor here 
class CodeEditorApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.appTheme = npyscreen.setTheme(CustomTheme)
        self.addForm("MAIN", CodeEditor, name="Code Editor V1")

# test creating custom theme
class CustomTheme(npyscreen.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'CYAN_BLACK',
        'FORMDEFAULT' : 'YELLOW_BLACK',
        'NO_EDIT'     : 'GREEN_BLACK',
        'STANDOUT'    : 'CYAN_BLACK',
        'CURSOR'      : 'WHITE_BLACK',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL'       : 'GREEN_BLACK',
        'LABELBOLD'   : 'WHITE_BLACK',
        'CONTROL'     : 'GREEN_BLACK',
        'IMPORTANT'   : 'GREEN_BLACK',
        'SAFE'        : 'GREEN_BLACK',
        'WARNING'     : 'YELLOW_BLACK',
        'DANGER'      : 'RED_BLACK',
        'CRITICAL'    : 'BLACK_RED',
        'GOOD'        : 'GREEN_BLACK',
        'GOODHL'      : 'GREEN_BLACK',
        'VERYGOOD'    : 'BLACK_GREEN',
        'CAUTION'     : 'YELLOW_BLACK',
        'CAUTIONHL'   : 'BLACK_YELLOW',
    }

# define our action form
class CodeEditor(npyscreen.ActionForm):
    # define custom button text
    OK_BUTTON_TEXT = "SAVE"
    CANCEL_BUTTON_TEXT = "EXIT"

    def draw_title_and_help(self):
        if self.name:
            title = self.name[:(self.columns-4)]
            title = ' ' + str(title) + ' '
            if isinstance(title, bytes):
                title = title.decode('utf-8', 'replace')
            self.add_line(0,58, 
                title, 
                self.make_attributes_list(title, curses.A_BOLD),
                self.columns-4
                )

    def create(self):
        self.filename = self.add(
            npyscreen.TitleFilename,
            begin_entry_at=18,
            name="Filename      :",
            relx=3,
            rely=2,
            )
        self.path = self.add(
            npyscreen.TitleText,
            begin_entry_at=18,
            name="Folder Path   :",
            relx=3, 
            rely=4,
            editable=True
            )
        self.code = self.add(
            npyscreen.MultiLineEdit,
            relx=2, 
            rely=6,
            editable=True,
            scroll_exit=True,
            )
    
    # add method for condition where user pick 'SAVE' button
    def on_ok(self):
        # raise error if filename not include file type
        if self.filename.value.find(".") == -1:
            raise ValueError(f"'filename' needs file type at the end, file: {self.filename.value}")
        
        # define path
        curr_path = pathlib.Path(self.path.value)
        if curr_path.is_dir():
            real_path = os.path.join(curr_path, self.filename.value)
            if not self.filename.value or self.path.value:
                raise _some_log.error_log(ValueError, message="Filename and Path required!")
            else:
                if os.path.exists(real_path):
                    raise _some_log.error_log(FileExistsError, f"File exists: {real_path}")
                else:
                    if self.filename.value.endswith('.txt'):
                        with open(os.path.join(self.path.value, self.filename.value), "a+") as file:
                            file.seek(0)
                            is_content_exist = file.read()

                            if is_content_exist:
                                file.write("\n"+self.code.value)
                            else:
                                file.write(self.code.value)
                            file.close()
                    else:
                        with open(os.path.join(self.path.value, self.filename.value), 'a+') as file:
                            file.seek(0)
                            is_code_exist = file.read()
                            
                            if is_code_exist:
                                file.write("\n\n"+self.code.value)
                            else:
                                file.write(f"# {self.filename.value}\n\n"+self.code.value)
                            file.close()
        self.parentApp.setNextForm(None)
    
    # add method for condition where user pick 'EXIT' button
    def on_cancel(self):
        self.parentApp.setNextForm(None)
