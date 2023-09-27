import os
import re
import time
import unicodedata
import requests
import notebook_path

from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from IPython.display import display, clear_output, Javascript
from ipywidgets import widgets
from ipylab import JupyterFrontEnd


def strip_accents(s):
    """remove accents from string"""
    umlautfree = (
        s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    )
    umlautfree = umlautfree.replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue")
    result = "".join(
        c
        for c in unicodedata.normalize("NFD", umlautfree)
        if unicodedata.category(c) != "Mn" and (c.isalnum() or c == "-" or c == " ")
    )
    return result


@dataclass
class Text:
    label1: str
    text_placeholder: str
    button_edit_tooltip: str
    label2: str
    label2_error: str
    label3: str
    button_submit_description: str
    button_submit_progress1: str
    button_submit_progress2: str
    button_submit_success: str
    button_submit_error: str
    name_cell_text: str


@dataclass
class Lang:
    de: Text | None
    en: Text | None


en = Text(
    label1="<h3>Please enter your first- and lastname and hit ENTER (not CTRL+ENTER)</h3>",
    text_placeholder="Type your first and last name here",
    button_edit_tooltip="Edit Name",
    label2=(
        "<h4>Your name without problematic characters for file names</h4>"
        "<p><b style='color: #307fc1'>{}</b></p>"
    ),
    label2_error="<b style='color:red'>You need to enter your Name before hitting ENTER!</b>",
    label3=(
        "<h3>Are you ready to submit this notebook?</h3>"
        "<p>You can edit your name by clicking the edit button alongside the textbox for your name.</p>"
        "<h4>If your name is correct and you want to submit this notebook, press the button below.</h4>"
    ),
    button_submit_description="Save and Submit Exam",
    button_submit_progress1="Saving the Notebook... (1/2)",
    button_submit_progress2="Submitting the Notebook... (2/2)",
    button_submit_success="Notebook successfully saved and submitted.",
    button_submit_error="An Error occured!",
    name_cell_text="# Name: {name}\n<small id='submission'>Submitted at: {time}</small>",  # no " in this string!!!
)

de = Text(
    label1="<h3>Geben Sie Ihren Vor- und Nachnamen ein und drücken Sie dann die ENTER-Taste (nicht STRG+ENTER)</h3>",
    text_placeholder="Vor- und Nachname",
    button_edit_tooltip="Edit Name",
    label2=(
        "<h4>Ihr Name ohne problematische Zeichen für Dateinamen</h4>"
        "<p><b style='color: #307fc1'>{}</b></p>"
    ),
    label2_error="<b style='color:red'>Sie müssen Ihren Vor- und Nachnamen angeben bevor Sie ENTER drücken!</b>",
    label3=(
        "<h3>Sind Sie bereit, Ihr Notebook abzugeben?</h3>"
        "<p>Sie können Ihren Namen noch editieren, wenn Sie den Editier Knopf neben dem Eingabefeld drücken.</p>"
        "<h4>Ist Ihr Vor- und Nachname korrekt und sind Sie bereit, dass Notbook abzugeben, dann drücken Sie "
        "bitte den Abgabe Knopf unten.</h4>"
    ),
    button_submit_description="Speichern und Abgeben",
    button_submit_progress1="Das Notebook speichern... (1/2)",
    button_submit_progress2="Das Notebook abgeben... (2/2)",
    button_submit_success="Das Notebook wurde erfolgreich gespeichert und abgegeben.",
    button_submit_error="Es ist ein Fehler bei der Abgabe aufgetreten!",
    name_cell_text="# Name: {name}\n<small id='submission'>Abgegeben am: {time}</small>",  # no " in this string!!!
)

lang = Lang(en=en, de=de)


class ExamType(str, Enum):
    Exam: str = "exam"
    TestExam: str = "testexam"


class GenericSaveSubmitExam:
    def __init__(self, text: Text = en):
        try:
            self.login_name = os.getlogin()
        except OSError:
            if "JUPYTERHUB_USER" in os.environ and os.environ["JUPYTERHUB_USER"]:
                self.login_name = os.environ["JUPYTERHUB_USER"]
            elif "USER" in os.environ and os.environ["USER"]:
                self.login_name = os.environ["USER"]
            else:
                self.login_name = "user"
        self.student_name = ""
        self.js = ""
        self.text = text

    def build_notebook_prefix(self):
        student_name = self.student_name.title().replace(" ", "").replace("_", "")
        return "_".join(("Submission", self.login_name, strip_accents(student_name)))

    def run(self, course: str, exam_type: ExamType):

        output = widgets.Output(layout={"border": "1px solid black", "padding": "10px"})

        label1 = widgets.HTML(value=self.text.label1)

        text = widgets.Text(
            value=self.student_name,
            placeholder=self.text.text_placeholder,
            disabled=False,
            layout=widgets.Layout(width="auto"),
        )

        button_edit = widgets.Button(
            tooltip=self.text.button_edit_tooltip,
            button_style="warning",
            icon="edit",
            disabled=True,
            layout=widgets.Layout(width="40px"),
        )

        text_edit_button = widgets.GridBox(
            [text],
            layout=widgets.Layout(grid_template_columns="auto auto"),
        )

        label2 = widgets.HTML(value=self.text.label2.format(self.student_name))
        label3 = widgets.HTML(value=self.text.label3)

        layout = widgets.Layout(width="auto", height="40px")  # set width and height
        button_submit = widgets.Button(
            description=self.text.button_submit_description,
            icon="download",
            button_style="info",
            display="flex",
            flex_flow="column",
            align_items="stretch",
            layout=layout,
        )

        jump_mark = widgets.HTML(value="<div id='jump_mark'></div>")

        def do_jump(mark: str):
            return Javascript(
                """
            document.getElementById("%s").scrollIntoView(
              { behavior: "smooth", block: "end", inline: "nearest" }
            );"""
                % (mark)
            )

        def on_name_changed(change):
            self.student_name = strip_accents(change["new"])
            notebook_name = self.build_notebook_prefix()
            # self.js = js_rename_save_notebook(notebook_name)
            label2.value = self.text.label2.format(self.student_name)

        def on_submit_text(instance):
            if strip_accents(text.value.strip()) == "":
                label2.value = self.text.label2_error
                return
            text.disabled = True
            button_edit.disabled = False
            text_edit_button.children = text, button_edit
            with output:
                display(label3, button_submit, jump_mark, do_jump("jump_mark"))

        def on_edit(edit=None):
            output.clear_output()
            text.disabled = False
            button_edit.disabled = True
            text_edit_button.children = (text,)
            with output:
                display(label1, text_edit_button, label2)
            text.focus()

        def check_notebook(current_file: str, name_cell_text: str) -> bool:
            with open(current_file) as nb:
                content = nb.read()
            matchlines = name_cell_text.split("\n")
            return all(content.find(line) != -1 for line in matchlines)

        def save_notebook(app: JupyterFrontEnd, current_filename: str):
            before_state = os.stat(current_filename)
            time.sleep(0.1)
            app.commands.execute("docmanager:save")
            while before_state == os.stat(current_filename):
                time.sleep(0.1)

        def insert_name_cell(app: JupyterFrontEnd, name_cell_text: str):
            app.commands.execute("notebook:move-cursor-down")
            # app.commands.execute('notebook:delete-cell')
            app.commands.execute("notebook:insert-cell-below")
            app.commands.execute("notebook:change-cell-to-markdown")
            app.commands.execute("notebook:replace-selection", {"text": name_cell_text})
            app.commands.execute("notebook:run-cell")

        def on_submit_exam(instance):
            button_submit.disabled = True
            button_submit.icon = "spinner spin"
            button_submit.description = self.text.button_submit_progress1
            clear_output()

            app = JupyterFrontEnd()
            name_cell_text = self.text.name_cell_text.format(
                name=text.value, time=datetime.now().strftime("%Y%m%dT%H%M%S")
            )

            insert_name_cell(app, name_cell_text)

            current_filename = (
                notebook_path.get_notebook_path()
            )  # os.environ.get('JPY_SESSION_NAME')
            while not check_notebook(current_filename, name_cell_text):
                save_notebook(app, current_filename)
                time.sleep(0.1)

            time.sleep(1)
            button_submit.description = self.text.button_submit_progress2

            headers = {
                "x-course": course,
                "x-student": self.login_name,
                "x-exam-type": exam_type.value,
            }
            submit_filename = (
                f"{self.build_notebook_prefix()}_{os.path.basename(current_filename)}"
            )
            files = [("file", (submit_filename, open(current_filename, "rb")))]
            res = requests.post(
                url="http://127.0.0.1:8000/api/upload", headers=headers, files=files
            )
            time.sleep(1)
            if res.status_code == 200:
                button_submit.description = self.text.button_submit_success
                button_submit.icon = "check"
                button_submit.button_style = "success"
            else:
                button_submit.description = self.text.button_submit_error
                button_submit.icon = "skull"
                button_submit.button_style = "danger"
                with output:
                    display(widgets.HTML(value=f"<b style='color:red'>{res.text}</b>"))

            display(do_jump("submission"))

        text.observe(on_name_changed, names="value")
        text.on_submit(on_submit_text)
        button_edit.on_click(on_edit)
        button_submit.on_click(on_submit_exam)

        clear_output()
        display(output)
        on_edit()


class SaveSubmit:
    """Run the submission form
    =======================

        SaveSubmit().run_<lang>_<exam_type>_<course>()

    Where

    * <lang> is either ``de`` for german or ``en`` for english,
    * <exam_type> is either ``testexam`` or ``exam`` and
    * <course> is the name of the course from the `config.yaml` of
      ExamUploader.

    Please use in the <course> underscores wherever you used hyphens in
    the ``config.yaml`` file.

    Example:
    --------

    You want the german form for a testexam for the course 23w-python101,
    then you call:

        SaveSubmit().run_de_testexam_23w_python101()
    ----------------------------------------------------------------------
    """

    def __getattr__(self, name):
        pattern = re.compile(
            r"^run_(?P<lang>de|en)_(?P<exam_type>testexam|exam)_(?P<course>[a-z0-9_]+)$"
        )
        parsed = pattern.match(name)
        print(repr(parsed))
        if parsed is None:
            raise AttributeError(
                f"Xtype object '{self.__class__.name}' has no attribute '{name}'"
            )
        lng, exam_type, course = parsed.groups()
        course = course.replace("_", "-")
        return lambda: GenericSaveSubmitExam(text=getattr(lang, lng)).run(
            course, ExamType(exam_type)
        )
