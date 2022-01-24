# Audio Metadata Shuttle

This project is probably redundant as always. Nothing is original in these days. Anyway, hear me out.

## The Situation

In this day and age i am one of those weirdos that actually listen to music that lives in things called *music files* on my hard disk. And by hard disk i mean solid state drives. Anyway. As of now i own like 3 Laptops, two stationary PCs (of which one is technically is not mine) on which i occasionally listen to music. There are also two other mobile devices we call for simplicity sake "phones". All those devices have some amount of music files that are sometimes filtered, sometimes only contain a selection of certain albums or even songs.

Long story short, i recently discovered that the metatag of all those files are ugly, not very accurate and it looks bad when you try to actually filter for something. Now i am lazy, i don't want to go ahead and and update all those files by hand. But there is one big help, every single file comes from the same source.  A huge repository on my local NAS.

Therefore all files should be in itself the same as i haven't changed them for years.

## What i want to do

A program that carries its own database of known files, gets deployed on any one system, crawls a music folder and updates the meta data according to its own database. It uses a set of hashes to identify the files and do its thing so i can edit the files at one place and deploy the changes at another.

## Captains Log aka. Problems 

*22.01.2022* - Open Waters

Once more i picked up this project and fiddled a bit around. I forget where i left oft the last time i was here but it is clear that i haven't done a lot for the task at hand. This isnt surprising as the most important thing of this program stand and fall with a usable interface and not programming ingenuity. I spend some time to get some algorithms going that display a table in a console which works somewhat okay but has its caveats.

I researched a bit how exactly different audio files save their meta data and as far as i can see they all change some variable or fixed part in the file itself. This isnt surprising as i rarely see other files coming in tandem when getting an mp3. What is annoying is that i cannot just go 25000 Bytes into the file and take an hash of the first  500 Bytes and be done. (Although this method could work in a bit more complex way). For my personal files i know that they all derive from the same source, its not like i got the same album from two sources, i am happy enough when i get the stuff once. Anyway, this means i can probably just save all meta data and if there are some old files that are changed in some way i just need a function to reassign them again to a known pattern.

The general design idea is as follows: the portable database contains a master definition of song meta data and everything else are just pattern variations. When landing on a new system we check every file for a 100% Match in five or six properties and if there are files left we offer to check for lesser matches. There is some though of doing fuzzy string comparison but i know nothing about that, also it might get a bit slow. On the other hand, a few minutes of processing seem no like no biggie.
