# backup
A program that backs up files

I made this about a year ago in my spare time, and I finally figured out how to fix it.

It has a few primary functions:
- Backing up files
- Restoring files from backups

It saves files in the `.backup` file if you initalize the program by typing:

  `python3 backup.py backup`
  
In order to view old backups, type:

  `python3 backup.py metaview`
  
and it should show a list of previous backups.

If you need more infomation, type:

  `python3 backup.py help`

In order to install backup, type:

  `sh INSTALL.sh /path/to/exec/backup`
