# Audio Metadata Shuttle

This project is probably redundant as always. Nothing is original in these days. Anyway, hear me out.

## The Situation

In this day and age i am one of those weirdos that actually listen to music that lives in things called *music files* on my hard disk. And by hard disk i mean solid state drives. Anyway. As of now i own like 3 Laptops, two stationary PCs (of which one is technically is not mine) on which i occasionally listen to music. There are also two other mobile devices we call for simplicity sake "phones". All those devices have some amount of music files that are sometimes filtered, sometimes only contain a selection of certain albums or even songs.

Long story short, i recently discovered that the metatag of all those files are ugly, not very accurate and it looks bad when you try to actually filter for something. Now i am lazy, i don't want to go ahead and and update all those files by hand. But there is one big help, every single file comes from the same source.  A huge repository on my local NAS.

Therefore all files should be in itself the same as i haven't changed them for years.

## What i want to do

A program that carries its own database of known files, gets deployed on any one system, crawls a music folder and updates the meta data according to its own database. It uses a set of hashes to identify the files and do its thing so i can edit the files at one place and deploy the changes at another.

