# Language Forms Application

This project is related to the implementation of the Language Form Application, which helps us to learn English as an assistant.
## Instruction

1. Install [Python](https://www.python.org/).

Windows: 
2. Install [Language Forms Application](https://github.com/yasharsajadi/languageformsapplication)
```
pip install -i https://test.pypi.org/simple/ languageformsapplication
```
Linux: 
2. Install [Language Forms Application](https://github.com/yasharsajadi/languageformsapplication)
```
pip3 install -i https://test.pypi.org/simple/ languageformsapplication
```

## Usage
**To use in Windows or use a bat file with the following content:**
**Or use the exe in the path of the package installation file.**
**Speaker**
‍‍‍```
:: Batch File
@echo off

echo import SpeakerForm>> "%~dp0%SpeakerApplication.pyw"

echo app = SpeakerForm.App()>> "%~dp0%SpeakerApplication.pyw"
echo app.mainloop()>> "%~dp0%SpeakerApplication.pyw"

start pythonw "%~dp0%SpeakerApplication.pyw"

timeout /T 1
del /f "%~dp0%SpeakerApplication.pyw"
```
*[execution file]*()

**Learn More**
[Speaker Module](https://youtu.be/XFSc0TirtGM)

