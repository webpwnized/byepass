# ByePass

### Automate password cracking attempts

# Installation

## Important

You should use ByePass with the latest build of John the Ripper. You may use ByePass with the default version of JTR, but many formats and rules will not work. The default version of JTR does not include these features.

## Setup - Video Tutorials

Video tutorials that explain how to install John the Ripper and ByePass are available at the following links. For written instructions, refer to the next section.

- [How to Install John the Ripper (YouTube)](https://www.youtube.com/watch?v=7R10QN_uCh0)
- [How to Install ByePass Automated Password Auditor](https://www.youtube.com/watch?v=aQwoJh6cyH8)

If you need help installing VMware, VirtualBox, and/or Kali Linux, please see the video tutorials in the following playlist:

- [Complete Guide to ByePass](https://www.youtube.com/playlist?list=PLZOToVAK85Mqfcbufx1_lQHZ4pltV8nAm)

## Setup - Written Instructions

### Step 1: Install John the Ripper

A video tutorial is available on the webpwnized YouTube channel:

- [How to Install John the Ripper (YouTube)](https://www.youtube.com/watch?v=7R10QN_uCh0)

### Step 2: Clone the project and run the setup script

Example:

```bash
cd /opt
git clone https://github.com/webpwnized/byepass.git
cd byepass
./scripts/setup.sh
```

This script will:

- Reconstruct the `passwords-hailmary.txt` wordlist from five compressed `.zip` parts
- Unzip each practice hash file in `data/hashes/` from its `.txt.zip` archive
- Display the number of lines and size of each unpacked `.txt` file

### Step 3: Verify `config.py` is properly configured

> **NOTE:** Read and understand the important note above labeled "Important"

Assuming John the Ripper is installed in the `/opt` directory, your values in `config.py` should look like:

```python
JTR_EXECUTABLE_FILE_PATH = "/opt/JohnTheRipper/run/john"
JTR_POT_FILE_PATH = "/opt/JohnTheRipper/run/john.pot"
```

- `JTR_EXECUTABLE_FILE_PATH`: Filepath to the `john` executable. If John is compiled natively, this path is usually `<install directory>/JohnTheRipper/run/john`.
- `JTR_POT_FILE_PATH`: Filepath to the `john.pot` file. If John is compiled natively, this path is usually `<install directory>/JohnTheRipper/run/john.pot`.

If unsure where these are located, try:

```bash
which john
locate john.pot
```

Example:

```bash
which john
/opt/JohnTheRipper/run/john

locate john.pot
/opt/JohnTheRipper/run/john.pot
```

Then `config.py` should contain:

```python
JTR_EXECUTABLE_FILE_PATH = "/opt/JohnTheRipper/run/john"
JTR_POT_FILE_PATH = "/opt/JohnTheRipper/run/john.pot"
```

### Step 4: Tell John where to find ByePass's word mangling rules

The rules are located in `<byepass directory>/res/rules`. To include them in John, add the following lines to your `john.conf` file:

```
.include "<location of byepass>/res/rules/byepass.conf"
.include "<location of byepass>/res/rules/OneRuleToRuleThemAll.rule"
.include "<location of byepass>/res/rules/Best126.rule"
```

Example:

If ByePass is installed in `/opt/byepass`, add:

```
.include "/opt/byepass/res/rules/byepass.conf"
.include "/opt/byepass/res/rules/OneRuleToRuleThemAll.rule"
.include "/opt/byepass/res/rules/Best126.rule"
```

**Tips:**
- Search `john.conf` for other `.include` lines and add these nearby
- Use `gedit` or your preferred text editor:

```bash
gedit /opt/JohnTheRipper/run/john.conf
```
