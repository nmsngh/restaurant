# Restaurant Ambience Tracker
## How to test this project?
All of the steps below can also be seen in the demo [video](https://youtu.be/LW6-wGfNgYI).

1. Download pre-build ADN-AE from release page \
   (Due to capacity issues, the Unity Project (ADN-AE) was unable to upload all files. Check the core code in Assets/Script)
2. Change the first line of the config.ini file to the IP of your current system
3. Download acmecse.
4. `~/.local/bin/acmecse --textui --config=in.ini` in IN-AE path.
5. `~/.local/bin/acmecse --textui --config=mn.ini` in MN-AE path.
6. `python3 mn-ae.py` in MN-AE.py
7. Execute ADN-AE/IoT.exe
8. `python3 run.py` in IN-AE path.
9. Now you can access webpage in localhost:18080.
  (Admin id : `C97f3b907ae2f8f9709f527a143156247f2d43f4c97c26ddde57cd06ebdbc21c9`, password : `password`)
