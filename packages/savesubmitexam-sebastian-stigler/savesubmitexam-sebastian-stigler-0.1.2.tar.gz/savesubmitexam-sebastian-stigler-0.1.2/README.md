[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/savesubmitexam-sebastian-stigler.svg)](https://pypi.org/project/savesubmitexam-sebastian-stigler/)

# SaveSubmitExam

> Widget generator for exam submission via ExamUploader in
> [tljh](https://tljh.jupyter.org/en/latest/index.html) (The Littlest
> JupyterHub) Version 1.0.0

## Installation

From the webapp of [tljh](https://tljh.jupyter.org/en/latest/index.html)
as an admin user. Open a Terminal and type:

``` {.}
sudo -E /opt/tljh/user/pip install savesubmitexam-sebastian-stigler
```

Check if ``ipylab`` is available on the webapp. If it is not installed, install it in the
[tljh](https://tljh.jupyter.org/en/latest/index.html) user environment.

Make sure you also install
[ExamUploader](https://pypi.org/project/examuploader-sebastian-stigler/)
on your [tljh](https://tljh.jupyter.org/en/latest/index.html) server.

## Usage

Put the following line in **the last cell** of your exam notebook:

``` {.}
from savesubmitexam import SaveSubmit
SaveSubmit().run_<lang>_<examtype>_<course>()
```

Where

-   `<lang>` is either `de` for german or `en` for english,
-   `<exam_type>` is either `testexam` or `exam` and
-   `<course>` is the name of the course from the
    [config.yaml]{.title-ref} of ExamUploader.

Please use in the `<course>` underscores wherever you used hyphens in
the `config.yaml` file.

### Example:

You want the german form for a testexam for the course 23w-python101,
then you call:

``` {.}
SaveSubmit().run_de_testexam_23w_python101()
```

## Note

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see <https://pyscaffold.org/>.
