# Mc-PlayTime-Mac

This is a simple python script made to check all the logs files on some minecraft launchers, to get the Total playtime on that launcher (Soon will have a 'All' option to check all launchers).
<br>
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
| Tlauncher   | :white_check_mark: |
| Tlauncher Legacy   | :white_check_mark: |
| GDLauncher   | :white_check_mark: |
| Prism Launcher   | :white_check_mark:  |
| MultiMC   | :white_check_mark: |
| Modrinth   | :white_check_mark: |

</td><td>
    
| Client | Supported |
| ------- | :-------: |
| Lunar Client   | :white_check_mark: |
| Badlion Client| :white_check_mark: |
| Labymod | :white_check_mark: |

</td><td>
    
| Client/Launcher | Supported |
| ------- | :-------: |
| Feather Client| :x: |
| ATLauncher   |  :x: |
| CourseForge   | :x: |

</td></tr>
</table>

Check the [Soon](/soon.md) page to understand more about the unsupported launcher/clients.
<br>
Labymod and tlauncher use the normal directory of minecraft logs.

> [!Note]
> More Launcher will be working pretty soon! And if i miss any launcher please let me know!

---

## How to use

> [!IMPORTANT]
> Python is required to run this file. Install this: [python installer](https://www.python.org/downloads/)

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
