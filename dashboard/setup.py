from cx_Freeze import setup, Executable

# Replace 'your_script.py' with the name of your Tkinter script
setup(
    name="Demo",
    version="0.1",
    description="Your App Description",
    executables=[Executable("dashboard.py", base="Win32GUI")],
)
