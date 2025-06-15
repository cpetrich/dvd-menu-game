# Stars of Skistua
A DVD menu game that challenges you to find three stars on the playground of "Skistua" kindergarden.

The game can be played on any device that can play DVDs and show menus, including
a venerable DVD player, or
a video player on desktop, laptop, or mobile, such as [VLC media player](https://www.videolan.org/vlc/).

The ISO image file [``dvd_stjerner_231014.iso``](https://drive.google.com/file/d/1pmniI_VgP61LEuj4KDtMpiBAE43Bcg33/view?usp=sharing) can be downloaded from [Google Drive](https://drive.google.com/file/d/1pmniI_VgP61LEuj4KDtMpiBAE43Bcg33/view?usp=sharing) (945 MB).

## Getting Started
* **With physical DVD**: Download the ISO image and burn to DVD (Windows: right-click .iso image file and select "Burn disc image"), then play in a DVD player or app on PC/Mac/Linux.
* **Without physical DVD**: Download the ISO image, start the DVD player app and open the .iso image file.

![DVD Cover](/assets/view_cover_640px.png)

## About the Game
The goal is to find and capture three stars that are randomly placed across 14 places on the playground. Each find is rewarded with a little star animation.

Stars tend to be somewhat close to one another, so a reasonable strategy is to keep looking in the proximinity of a discovered star.

If the player takes many steps without capturing a star then a smiley will appear. Once the smiley is captured, pointers are given to the closest star. The pointers are active until the next star is captured.

Smiley and stars do not need to be captured when they are first encountered.

Where available, selecting the arrow pointing straight down will lead back to the previously visited place.

![Example menu with discovered star and arrows](/assets/menu_with_star_640px.png)

### Menu Options
There are two "menus". They can be entered with dedicated buttons on the DVD remote, or somewhere in the menu system of the app where they are probably called "Main menu", "Title menu", or "Chapter menu".
One menu is the start screen that allows to start a new game. The other menu has two menu options: one to request a smiley at the current place, and the other to toggle the transition videos off and on. Also, the "resume"
button on a remote control should work in the latter menu. In case somebody wonders, "innstillinger" is Norwegian for "settings".

![Screenshot of menu titled "innstillinger"](/assets/view_toggle_640px.png)

## Known Limitations
The game does not disable buttons that should not be pushed. For example, one can bring the game into an undefined state by pushing the "skip chapter" button too many times. Strange behavior or a blue screen with the words "eject disc" are
signs that the game is in an undefined state. The best way to get the game back into a defined state is by ejecting the DVD and re-inserting it.

## If it looks odd on a conventional TV
If the view is distorted, check that the **DVD player outputs a 16:9 image in NTSC** to the TV, and that the **TV expects an image in 16:9 aspect ratio**. All modern TVs can deal with NTSC signals but DVD players sold outside North America may try to convert NTSC content to PAL. This is not an issue when played on an App.

## License
The game (.iso) is distributed under the CC BY 4.0 licence. This means that it can be used, copied, and shared without restrictions. The code in this repository comes with the MIT license. Author: Chris Petrich, 2023.

## Acknowledgements
The creation of this game relied primarily on [DVDAuthor](https://dvdauthor.sourceforge.net/), on [FFmpeg](https://ffmpeg.org/), and the DVD resources listed in the DVDAuthor [GitHub repository](https://github.com/ldo/dvdauthor/), specifically http://www.mpucoder.com/DVD/ and http://en.wikibooks.org/wiki/Inside_DVD-Video.

## Creation of the Game
In 2023 I considered DVDs a great medium to watch movies because I was able to watch them without computer or mobile device. As I was browsing through menus I thought it would be neat to re-purpose the DVD concept to make a game. So, completely underestimating the amount of time this would take me I discovered the fabulous ``DVDAuthor`` and learned to write [``.xml`` definition files](/processed/06_dvd.xml) to create DVDs with it. I think it took me about 3 weeks to make the game in June 2023. I would estimate that adding one node to the game will take approximately 2 hours for recording and (mostly) processing the videos (i.e., creating views of the node with directional buttons coming from all possible directions, and generating movies of the transition from any view to any possible destination). Hence, re-making this game with 14 nodes, even with all scripts and pipeline in place, would probably take a few days. I found that dedicated DVD players were not in common use anymore after I was done. Feeling that I was 10 years late to the game, I do not think that there is much value documenting in detail how to create a DVD menu game. Suffice to say, the scripts are in ``/src``, where one can see that a surprising amount of effort had to be used to generate the movie files for the menus themselves. The [last script](/src/06_create_dvdauthor_DVD_xml.py) generates the ``.xml`` file with the structure of the DVD (titles, chapters) and the code defining how to jump between them. A DVD menu game can be extremely space-inefficient. For each node and view a large number of menu movies has to be generated: one with only directional arrows, one with a star, one with a smiley, and one for each possible combination of star-hints (e.g. 15 menu movies for a view with four onward paths). Hence, a node with four exit paths needs 72 menu movies. There are a few places where the DVD specification limits the number of something to 99, so structuring this to be usable in a DVD player requires some thought. I did not upload the source ``.mp4`` files since they take up about 3 GB and I do not expect may people to seriously want to set up this pipeline and put the scripts to use. However, I hope you will enjoy the ISO image that came out of it.
