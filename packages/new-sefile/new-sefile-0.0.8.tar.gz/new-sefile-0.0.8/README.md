# Sefile CLI

![SEFILE_v1](https://github.com/Kolong-Meja/search-cli/assets/90602095/579d3cd7-6e68-451f-8c1f-575d8059ef5f)

Sefile CLI is a personal project created by Faisal Ramadhan or myself. This project was built using the Python programming language. At the time of its creation, this CLI was only useful for finding the desired file according to the initial directory, but over time I started adding several new commands, such as Create, Read, Write and Delete. All of these commands have their own purpose and function.

## Installation

You can install this cli from https://pypi.org/project/new-sefile/ or you can just type in command into your terminal like below:

```bash
python3 -m pip install new-sefile
```

Enjoy your exploration on my CLI tool!

> **Warning**
This project does not support yet for Windows and Mac operating system.

## Requirements

Each project must have additional modules or packages for ease of project creation. I myself use a lot of packages to make this CLI. The modules or packages list that I use is:

* **typing**

> [!NOTE] 
> if you want more information about this library, see https://docs.python.org/3/library/typing.html

* **fnmatch**

> [!NOTE]
> if you want more information about this library, see https://docs.python.org/3/library/fnmatch.html

* **logging**

> [!NOTE]
> if you want more information about this library, see https://docs.python.org/3/howto/logging.html

* **os**

Info: > if you want more information about this library, see https://docs.python.org/3/library/os.html

* **pathlib**

> [!NOTE] 
> if you want more information about this library, see https://docs.python.org/3/library/pathlib.html

* **typer**

Installation:
```bash
python -m pip install "typer[all]"
```
> [!NOTE] 
> if you want more information about this library, see https://typer.tiangolo.com/tutorial/first-steps/

* **rich**

> [!WARNING]
> If you do **pip install "typer[all]"** before, then you don't have to install the rich module.

Installation:
```bash
python -m pip install rich
```
> [!NOTE] 
> If you want more information about this library, see https://rich.readthedocs.io/en/stable/introduction.html

* **termcolor**

Installation: 
```bash
python -m pip install termcolor
```

> [!NOTE] 
> if you want more information about this library, see https://github.com/termcolor/termcolor

* **npyscreen**

Installation: 
```bash
python -m pip install npyscreen
```

> [!NOTE]
> if you want more information about this library, see https://npyscreen.readthedocs.io/introduction.html

* **ascii-magic**

Installation: 
```bash
python -m pip install ascii-magic
```

> [!NOTE]
> if you want more information about this library, see https://pypi.org/project/ascii-magic/

* **colorama**

Installation: 
```bash
python -m pip install colorama
```

> [!NOTE]
> if you want more information about this library, see https://pypi.org/project/colorama/

* **Pillow**

Installation: 
```bash
python -m pip install Pillow
```

> [!NOTE]
> if you want more information about this library, see https://pillow.readthedocs.io/en/stable/

* **art**

Installation:
```bash
python -m pip install art
```

> [!NOTE]
> if you want more information about this library, see https://www.ascii-art.site/

## How to use it

It's quite easy, you just need to enter the command **sefile --help**, then you get the output like this:

![Screenshot from 2023-09-25 18-04-19](https://github.com/Kolong-Meja/search-cli/assets/90602095/d6fb2031-6c3c-4a78-84c8-58ee026e7448)

### How to show CLI version?

```bash
sefile --version
```

or

```bash
sefile -v
```

### How to find a file?

```bash
sefile find example.txt
```

or

> [!NOTE] 
> You can specify the initial directory path to find the file you want.

```bash
sefile find example.txt /home/yourname/Documents
```

At first I created this based only on the filename, but eventually I added new flag options, namely --startswith and --endswith.

* **--startswith** flag is useful for searching files with your own custom prefix. Usage examples:

> [!NOTE] 
> **--startswith** flag has been set as **is_eager=True**, meaning this parameter will be executed and the main parameter will be overridden.

```bash
sefile find --startswith=main
```

When you do this, the system will automatically look for files with a certain (in this case **main**) prefix from each directory or sub-directory that matches the initial directory.

* **--endswith** flag is useful for searching files with your own custome prefix. Usage examples:

> [!NOTE] 
> **--endswith** flag has been set as **is_eager=True**, meaning this parameter will be executed and the main parameter will be overridden.

```bash
sefile find --endswith=.py
```

This flag has same functional as **--startswith** flag, but search file by the end name of the file that match with your custome prefix.

### How to create a file?

```bash
sefile create example.txt
```
> [!NOTE] 
> Default directory set as **/home/username**

or 

```bash
sefile create example.txt /home/username/Documents
```

The system will automatically create a file with a certain file type (according to the type you add at the end of the file) in the directory you enter.

> [!NOTE]
> In newest update, there's one Options called **--auto**. This useful for you if you too lazy for creating simple project. **Remember** this Options, will create **Python, Javascript, or Go** depends on your choice. You can detected it from your **home** directory.

To run **--auto** Options, you just simply write it in your terminal like this below:

```bash
sefile create --auto
```

![Screenshot from 2023-09-25 18-05-02](https://github.com/Kolong-Meja/search-cli/assets/90602095/a42f5fe5-d51b-49e4-839f-92fae0aff8f2)

### How to read a file?

```bash
sefile read example.py /home
```

or

* **--read-type** flag is especially useful for reading files of a certain type. Default file typer set as **text** or **.txt**. Example of the output:

**Example 1**:

Do this command in your terminal:

```bash
sefile read example.py /home --read-type=python
```

And you get a result like this in your terminal (**NOTE**: This is just example)

```python
# example.py

def my_func() -> None:
    print("Hello World!")
```

**Example 2**:

Do this command in terminal:

```bash
sefile read example.py /home --read-type=go
```

And you get a result like this in your terminal (**NOTE**: This is just example)

```go
// main.go

func playingPythagoras(altitude, base, hypotenus float64) {
	if altitude == 0.0 {
		formula := math.Pow(hypotenus, 2.0) - math.Pow(base, 2.0)
		fmt.Printf("altitude = %.1f² - %.1f²", hypotenus, base)
		fmt.Printf("Result = %.1f", math.Round(formula))
	} else if base == 0.0 {
		formula := math.Pow(hypotenus, 2.0) - math.Pow(altitude, 2.0)
		fmt.Printf("base = %.1f² - %.1f²", hypotenus, altitude)
		fmt.Printf("Result = %.1f", math.Round(formula))
	} else {
		formula := math.Pow(altitude, 2.0) + math.Pow(base, 2.0)
		fmt.Printf("hypotenus = %.1f² + %.1f²", altitude, base)
		fmt.Printf("\nResult = %.1f", math.Round(formula))
	}
}
```
> [!NOTE] 
> this is just an example, the output will vary depending on the type of file you entered and the program in the file you entered

### How to delete a file?

```bash
sefile delete example.py /home
```

You can add the path as you wish, but make sure that the files you delete are in your destination directory.

### How to write a file?

```bash
sefile write
```

And you get this layer of nice UI

![Screenshot from 2023-09-25 18-05-15](https://github.com/Kolong-Meja/search-cli/assets/90602095/85b9d585-8f73-4b59-9a1f-d84e2b5083fb)

> [!NOTE]
> you need specifiy the Filename and Path first, before you do code or creating text.

So this write command, doesn't need ARGS at all, you just input command in your terminal above, and you can do code in your terminal.

**INFORMATION**:

So if you notice, theres is **'EXIT'** button and **'SAVE'** button right? the functionality of these 2(two) button are same as **'EXIT'** button and **'SAVE'** button in your code editor. 

You can exit whatever you want, but you can't save the code if you not input value in **'Filename'** and **'Folder Path'**. So be careful when you use this. 

## Keep in mind

This program is only useful for **find, create, read, write and delete**. Apart from that, I have nothing to add. I personally will only focus on the main command program, because there are still many things that can be updated in the future.
