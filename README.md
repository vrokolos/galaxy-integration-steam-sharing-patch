# galaxy-integration-steam-sharing-patch
Adds steam family sharing support to the Galaxy GOG 2 steam integration plugin

My pull request got rejected because of understandable reasons. I can't stand not having those sweet games on GOG 2 so I remade it into something easier to maintain.
This needs manual patching unfortunately.

# INSTALLATION STEPS

a) Close GOG Galaxy

b) Place **pluginsharing.py** into: **%localappdata%\GOG.com\Galaxy\plugins\installed\steam_ca27391f-2675-49b1-92c0-896d43afa4f8**

c) Edit the **manifest.json** in that folder and replace **plugin.py** with **pluginsharing.py** in the last line

d) Open steam client and add a nickname to each of your friends that are sharing games with you so that it ends with #
  example: Turn **Nick1234** into **Nick1234#** or something similar
  
e) Open GOG Galaxy

If any error occurs please check the file: **C:\ProgramData\GOG.com\Galaxy\logs\plugin-steam-ca27391f-2675-49b1-92c0-896d43afa4f8.log**
