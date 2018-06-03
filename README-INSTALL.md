# Installation

## Important

You should use ByePass with the latest build of John the Ripper. You may use ByePass with the
default version of JTR, but many formats and rules will not work. The default version of JTR
does not include these features.

## Setup - Video Tutorials

Video tutorials that explain how to install John the Ripper and ByePass are 
available at the following links. For written instructions, refer to the next section.

* [How to Install John the Ripper (YouTube)](https://www.youtube.com/watch?v=7R10QN_uCh0)
* [How to Install ByePass Automated Password Auditor](https://www.youtube.com/watch?v=aQwoJh6cyH8)

If you need help installing VMware, VirtualBox and/or Kali Linux, please see the video 
tutorials in the following playlist

[Complete Guide to ByePass](https://www.youtube.com/playlist?list=PLZOToVAK85Mqfcbufx1_lQHZ4pltV8nAm)

## Setup - Written Instructions

#### Step 1: Install John the Ripper

A video tutorial is available on the webpwnized YouTube channel at the following link.

[How to Install John the Ripper (YouTube)](https://www.youtube.com/watch?v=7R10QN_uCh0)

#### Step 2: Change into desired directory, clone the project and decompress passwords-hailmary.txt.zip

**Example:**

    cd /opt
    git clone https://github.com/webpwnized/byepass.git
    cd bypass/passwords
    cat passwords-hailmary-1.txt.zip passwords-hailmary-2.txt.zip passwords-hailmary-3.txt.zip > passwords-hailmary.txt.zip
    unzip passwords-hailmary.txt.zip
    cd ..

#### Step 3: Verify config.py is properly configured 

##### NOTE: Read and understand the important note above labeled "Important"

Assuming John the Ripper is installed in the /opt directory, the values should be the following:

    JTR_EXECUTABLE_FILE_PATH = "/opt/JohnTheRipper/run/john"
    JTR_POT_FILE_PATH = "/opt/JohnTheRipper/run/john.pot"

**JTR_EXECUTABLE_FILE_PATH**: Filepath to the john executable. If john is
 compiled natively, this path is usually <install directory>/JohnTheRipper/run/john.

**JTR_POT_FILE_PATH**: Filepath of the john.pot file. If john is
 compiled natively, this path is usually <install directory>/JohnTheRipper/run/john.

If unsure of location of the John the Ripper executable and pot file, try 

    which john
    locate john.pot

**Example:**

if locate finds john installed in the following

    which john
    /opt/JohnTheRipper/run/john

    locate john.pot
    /opt/JohnTheRipper/run/john.pot

Then the config.py should contain the following

    JTR_EXECUTABLE_FILE_PATH = "/opt/JohnTheRipper/run/john"
    JTR_POT_FILE_PATH = "/opt/JohnTheRipper/run/john.pot"

#### Step 4: Tell john the location of byepass's word mangling rules 

The rule are located in <byepass directory>/rules/byepass.conf. To
tell john the location, add the following line to john.conf.

    .include "<location of bypass>/byepass/rules/byepass.conf"
    .include "<location of bypass>/byepass/rules/OneRuleToRuleThemAll.rule"
    .include "<location of bypass>/byepass/rules/Best126.rule"

where "location of bypass" is the location that byepass is installed.
For example, if byepass is installed in /opt, add the following line
into john.conf

    .include "/opt/byepass/rules/byepass.conf"
    .include "/opt/byepass/rules/OneRuleToRuleThemAll.rule"
    .include "/opt/byepass/rules/Best126.rule"

**Tips**: 
* To find a good location in john.conf to place the line, search
for ".include" and place the new include line near other include lines.
* The gedit
editor is easy to use.
