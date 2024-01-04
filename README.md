# Mc-PlayTime-Mac

This is a simple python script made to check all the logs files on some minecraft launchers.
It currently works on:

<table>
<tr>
        <th>Supported Launchers</th>
        <th>Supported Clients</th>
        <th>Require Time</th>
</tr>
<tr><td>
        
| Launcher  | Supported |
| ------- | :-------: |
| Minecraft Launcher | :white_check_mark: |
| Tlauncher Legacy   | :white_check_mark: |
| Tlauncher   | :white_check_mark: |
| GDLauncher   | :white_check_mark: |

</td><td>
    
| Client | Supported |
| ------- | :-------: |
| Lunar Client   | :white_check_mark: |
| Badlion Client| :white_check_mark: |
| Labymod | :x: |

</td><td>
    
| Client/Launcher | UnSupported |
| ------- | :-------: |
| Feather Client| :white_check_mark: |
| MultiMC   | :white_check_mark: |
| ATLauncher   |  :white_check_mark: |
| Prism Launcher   | :white_check_mark:  |
| Modrinth   | :white_check_mark: |
| CourseForge   | :white_check_mark: |

</td></tr>
</table>

Check the [Soon](/soon.md) page to understand more.

> [!Note]
> More Launcher will be working pretty soon!

---

## How to use

> [!IMPORTANT]
> Python is required to use this [python installer](https://www.python.org/downloads/)

Clone repo:

```sh
git clone https://github.com/cranci1/Mc-PlayTime-Mac
```

Navige to the directory:

```sh
cd Mc-PlayTime-Mac
```

Install the requirements:

```sh
pip install -r requirements.txt
```

Run the script:

```sh
python3 mc-time.py
```
---
## Custom Path

To use a custom path you just need to find the path to a log folder. (The name doesn't have to be logs/log) It only requires that the folder needs to have files with .log.gz extension.
