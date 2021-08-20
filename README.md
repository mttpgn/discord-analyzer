# Discord-Analyzer

Discord-Analyzer is a dataset generator which can monitor instant messages, 
online chatrooms, or large, synchronous group chats for pre-defined keywords.

Discord-Analyzer enables the collection of word frequency statistics from 
chat applications lacking any direct read-operation API (such as Discord). 
Discord-Analyzer uses image processing to read the text contents of chats 
displayed from the screen disaply output of either a webapp or standalone 
desktop application. The detected words feed into a database, which, over 
time, forms a dataset. Statistical gleanings, such as frequently discussed 
words or phrases over various time horizons, become derivable as discord-
analyzer runs over time.

A word whitelist limits the noise from the word-to-image detection (which is 
done by pytesseract). This requires knowing beforehand the words to find.

The application has been designed for AWS infrastructure. Setup instructions 
below. 


## Setting up the AWS instance

Create new AmazonOS instance with 4GB Ram. For storage, T3 is cheaper than T2.
Chat rooms oriented around timezones-specific activity can contain irrelevant
chatter during off-hours (or simply go silent). Limiting data collection to 
specific hours can be advantageous. Discord-analyzer expects hour-based 
execution limitations in its own configurations. 

Using AWS complements this feature with it ability to bring instances up and
down at specific times. 

Amazon's [documentation](https://aws.amazon.com/premiumsupport/knowledge-center/start-stop-lambda-cloudwatch/) 
gives an overview of taking an instance up and down at times which can be set 
to just before discord-analyzer's activation time and just after discord-
analyzer's deactivation time. 

Modify the steps in the above AWS guide just so: Rather than the two lambda 
functions of `StartEC2Instance` and `StopEC2Instance`, name the two lambda 
functions `StartEC2Instance` and a `HibernateEC2Instance`. The hibernation
function can look like this:

```python
import boto3

instances = ['i-06069d3e1487166ec','i-046f8447f362a966e','i-072ba2ddc23921d1d']
region = 'us-east-2'

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name=region)
    ec2.stop_instances(InstanceIds=instances, Hibernate=True)
    print( 'hibernated your instances: ' + str(instances))
```

[Hibernation must be enabled](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Hibernate.html#hibernating-prerequisites) at the time the EC2 is created.

Add your EC2 instance id's into the lambda functions you created. 

In cloudwatch, ensure the lambda functions are scheduled to run at the times 
you want them: [https://console.aws.amazon.com/cloudwatch/]

## Preparing the EC2 Desktop Environment

Each of your EC2 instances needs a GUI installed. 

For the most part, 
[Amazon's guide](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-linux-2-install-gui/) 
works well. The steps below are simplified from that page.

```bash
sudo yum update

reboot

sudo amazon-linux-extras install mate-desktop1.x

sudo bash -c 'echo PREFERRED=/usr/bin/mate-session > /etc/sysconfig/desktop'

echo "/usr/bin/mate-session" > ~/.Xclients && chmod +x ~/.Xclients

sudo yum install tigervnc-server

vncpasswd

sudo cp /lib/systemd/system/vncserver@.service /etc/systemd/system/vncserver@.service

sudo sed -i 's/$USER/ec2-user/' /etc/systemd/system/vncserver@.service

sudo systemctl daemon-reload

sudo systemctl enable vncserver@:1

sudo systemctl start vncserver@:1
```

## Connect to the GUI using the VNC

1.    Install the TigerVNC software on your local computer, if it's not already installed. TigerVNC is available for Linux, Windows, and macOS. See the TigerVNC website to access the download.

2.    On your local computer, use SSH to connect to your instance while creating a tunnel to forward all traffic on local port 5901/TCP (VNC) to the instance's VNC server:

Connect to your instance using SSH.

Use the -L parameter to enable port forwarding. Replace PEM_FILE with your private key, and INSTANCE_IP with your instance's public or private IP, as appropriate.

```bash
ssh -L 5901:localhost:5901 -i $PEM_FILE ec2-user@$INSTANCE_IP
```

Open the connection.

3.    Open the VNC Client on your local computer. When asked for the VNC server hostname, enter localhost:1 and then connect to it.

4.    Enter the VNC password you set up in step 2 of the Install TigerVNC section. If an alert appears stating that the connection isn't secure, disregard it. Although VNC data is unencrypted by default, you're accessing the VNC server using an encrypted SSH tunnel.

Your MATE desktop environment appears.



## Install Firefox

1.    Download [the latest Firefox version](https://www.mozilla.org/en-US/firefox/all/#product-desktop-esr)
for Linux 64-bit to your local computer.

2.    After downloading Firefox, copy the file to your instance.
```bash
scp -i ~/.ssh/AWS_Ubuntu_SSH_Key.pem ~/Downloads/firefox-78.7.0esr.tar.bz2 ec2-user@$(m=$INSTANCE_NAME && aws ec2 describe-instances | grep -B30 $m | grep PublicDns | cut -d\" -f4):/tmp
```

3.    Extract the file contents. The command below indicates that the file is in the ec2-user's home directory. Change the path and the Firefox version as needed.
```bash
tar jxf ~/firefox-xx.y.tar.bz2 -C ~/
```

4.    Using vim or your favorite editor, create a desktop icon. Create the 
file `~/Desktop/Firefox.desktop` with the contents as shown in the following 
example.
```
[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Icon=/home/ec2-user/firefox/browser/chrome/icons/default/default128.png
Icon[en_US]=/home/ec2-user/firefox/browser/chrome/icons/default/default128.png
Name[en_US]=Firefox
Exec=/home/ec2-user/firefox/firefox
Comment[en_US]=Firefox web browser
Name=Firefox
Comment=Firefox web browser
GenericName[en_US.UTF-8]=Firefox web browser
Categories=Network;WebBrowser;
```
5.    Use the desktop icon you created in step 4 to launch Firefox.




## Troubleshooting

In some cases the following command may be necessary when the VNC
connection cannot establish normally, for whatever reason:
```bash
rm /tmp/.X11-unix/X1 
```


## Additional packages

Discord-analyzer depends on these additional system preparations:

```bash
yum install python3-devel python3-tkinter python-pip

pip3 install --user ipython 
sudo amazon-linux-extras install epel
sudo yum install glibc imlib2 libpng tesseract python-virtualenv gcc
sudo vim /etc/yum/pluginconf.d/priorities.conf # set enabled=0

virtualenv --no-site-packages da # (Short for discord analyzer)
cd da && source bin/activate cd ..
pip3 install -r requirements.txt --user
mkdir log
mkdir screenshots
sudo timedatectl set-timezone "America/New_York"

wget -c http://packages.psychotic.ninja/7/base/x86_64/RPMS/scrot-0.8-12.el7.psychotic.x86_64.rpm
wget -c http://packages.psychotic.ninja/7/base/x86_64/RPMS/giblib-1.2.4-22.el7.psychotic.x86_64.rpm

sudo rpm -Uvh *psychotic*rpm
```


## Installing Discord via Snap

You may have better success using the Discord webapp than the Discord desktop 
app. The Discord desktop application will at some point require an update, 
and block use of the app until the new version is detected. Successfully 
updating to newer version is not always smooth or easy though. Hence, skipping 
this section is recommended (use the previously installed Firefox instead). 
Nevertheless, these steps, adapted from [here](https://www.bonusbits.com/wiki/HowTo:Install_Snap_on_Amazon_Linux_Workspace),
may be followed for those who wish.

```bash
tag_version=v0.1.0 && \
rpm_version=2.36.3-0 && \
wget https://github.com/albuild/snap/releases/download/${tag_version}/snap-confine-${rpm_version}.amzn2.x86_64.rpm -P $HOME/Downloads && \
wget https://github.com/albuild/snap/releases/download/${tag_version}/snapd-${rpm_version}.amzn2.x86_64.rpm -P $HOME/Downloads && \
sudo yum -y install $HOME/Downloads/snap-confine-${rpm_version}.amzn2.x86_64.rpm $HOME/Downloads/snapd-${rpm_version}.amzn2.x86_64.rpm && \
sudo systemctl enable --now snapd.socket


snap install discord
```

## Discord customizations

Because discord-analyzer works by reading the visual output to the screen, 
it can be deployed to scrape any chat application auto-scrolling chat 
application. 

For Discord, some (optional) optimizing customizations in the Settings:

* Turn off direct messages
* Appearance -> Light mode
* Appearance -> Zoom level -> 125
* Text and Image -> Do not automatically play gifs
* Text and Image -> Do not show emoji reactions


## Database setup
For each chat channel you wish to monitor, set up one table as follows:

```sql
CREATE TABLE public.mychannel
(
    id serial NOT NULL,
    word character(25) COLLATE pg_catalog."default" NOT NULL,
    msg_text character(999) COLLATE pg_catalog."default" NOT NULL,
    msg_timestamp timestamp without time zone,
    CONSTRAINT mychannel_so_pkey PRIMARY KEY (id)
);
```


## Pre-Configurations
You must create your own configurations file. Expected `.ini` 
file syntax is that of [ConfigParser](https://wiki.python.org/moin/ConfigParserExamples).

Repeat these config file creation steps to make one config file for each chat 
room/discord channel you wish to monitor. 


### Common
Create a section header `[COMMON]` above these fields:

#### `exten`
*A period (.) followed by text*. File extension for screenshot filenames.

#### `all_hours_flag`
*Capitalized word False or True*. If True, ignores the `hour_begin` and 
`hour_finish` properties.

#### `hour_begin`
*Integer*. The hour of day to activate chat monitoring. Minute granularity not 
supported. Relies on whatever timezone is set by `timedatectl`.

#### `hour_finish`
*Integer*. The hour of day to deactivate chat monitoring. Minute granularity 
not supported. Relies on whatever timezone is set by `timedatectl`.


### Database
Create a section header `[POSTGRES_DATABASE]` above these fields:

#### `pg_db_name`
*Text*. Your database name

#### `pg_db_instance`
*Text*. Your database host.

#### `pg_db_hostname`
*FQDN*. Your database's fully qualified domain name.

#### `pg_db_port`
*Integer*. Your database's listening port.

#### `pg_db_username`
*Text*. The username to connect to your database.

#### `pg_db_password`
*Text*. The password to connect to your database.


### Channel
Create a section header `[CHANNEL]` above these fields:

#### `pg_tableName`
*Text*. Each channel being monitored will correspond to one table within a 
single database shared across all records.

#### `discord_name`
*Text*. The name of the discord server.

#### `channel_name`
*Text*. The name of the discord channel.

#### `dup_chk_window`
*Integer*. Estimated length of time in seconds that a single line of chat 
text stays on-screen. A reasonable default here is `4`.


### Environment
Create a section header `[ENVIRONMENT]` above these fields:

#### `projroot`
*Absolute filepath*. The filesystem location from which discord-analyzer 
shuold run.

#### `ss_location`
*Filepath*. Ideally, but not necessarily, a subdirectory of `projroot` for
temporarily storing the last screenshot of the chat. Automatically cleaned
up after each parsing.

#### `logfile`
*Filepath*. A subdirectory within `projroot` storing logs.

Note: Daily-period log purges and rotations are baked-in to the application 
to prevent storage overflows. Settings for this task have not been linked to 
configurable settings.


### Data
Create a section header `[DATA]` above these fields:

#### `tickerlisturl`
*URL*. This list is pulled once per day. If any words on this list are found 
in a parsed message, that message will be written to the database. The 
purpose of requiring this list is to prevent the captured wordless images, 
read in as pure garbage letter-combinations, from populating the dataset.

Note: Depending on your use case, this list of words can often end up being 
updated so frequently that if it were sourced simply from a static config 
file within the repo, all the updates can pollute your commit history with 
trivial changes. The setting is designed to take a URL so that the wordlist 
can be modified as often as needed without requiring an application deploy.

A good example of what to put here might be the raw URL of a github gist.

#### `blacklisturl`
*URL*. Optional field. The list at this URL will be set-subtracted from the 
list pulled from `tickerlisturl`.


### Desktop
Populating this section requires a little calculation using `pyautgui`. 
The values should only need to be discovered once-- then can be used over 
and over for each host. These steps for finding the values below assume 
the chat application from which you want to record is open and running on 
the GUI of your EC2 host. References to the mouse cursor refer to that of 
your open VNC session.

Create a section header `[DESKTOP]` above these fields:

#### `ss_top`
*Integer*. To find this value, position your mouse cursor in the upper left 
corner of the area on your screen where the text portion of chat messages is 
visible. Then, from a terminal, run the following command:

```python
python3 -W ignore -c "import pyautogui as g; print(g.position()[1])"
```
Record the result as the value.

#### `ss_left`
*Integer*. To find this value, position your mouse cursor in the upper left 
corner of the area on your screen where the text portion of chat messages is 
visible. Then, from a terminal, run the following command:

```python
python3 -W ignore -c "import pyautogui as g; print(g.position()[0])"
```
Record the result as the value.

#### `ss_width`
*Integer*. To find this value, position your mouse cursor in the lower right 
corner of the area on your screen where the text portion of chat messages is 
visible. Then, from a terminal, run the following command:

```python
python3 -W ignore -c "import pyautogui as g; print(g.position()[0])"
```
Subtract the value previously stored as `ss_left` from the result to get this 
value.

#### `ss_height`
*Integer*. To find this value, position your mouse cursor in the lower right 
corner of the area on your screen where the text portion of chat messages is 
visible. Then, from a terminal, run the following command:

```python
python3 -W ignore -c "import pyautogui as g; print(g.position()[1])"
```
Subtract the value previously stored as `ss_top` from the result to get this 
value.

#### `x_home`
*Integer*. To find this value, position your mouse cursor outside of the 
area to be screenshot. Then, from a terminal, run the following command:

```python
python3 -W ignore -c "import pyautogui as g; print(g.position()[0])"
```
Record the result as this value.

#### `y_home`
*Integer*. To find this value, position your mouse cursor outside of the 
area to be screenshot. Then, from a terminal, run the following command:

```python
python3 -W ignore -c "import pyautogui as g; print(g.position()[1])"
```
Record the result as this value.



# Execution
From an open VNC session, run `./discord_extractor.py cfgs/config.ini`. 
Close the VNC session. During off hours, your EC2 instance will hibernate. 
When your instance starts back, your program will resume without needing 
any manual intervention.

## Viewing results

You can modify the query below to view the most popular words discussed 
during any period of time you specify.

```sql
-- See the most popular words of this week                                                                    
select 
    word, 
    count(word)
from mychannel 
where msg_timestamp > (
    now() - interval '1' week
)
group by word 
order by count desc;

```


