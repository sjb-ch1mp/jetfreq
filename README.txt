________     _____________                   
______(_)______  /___  __/_________________ _
_____  /_  _ \  __/_  /_ __  ___/  _ \  __ `/
____  / /  __/ /_ _  __/ _  /   /  __/ /_/ / 
___  /  \___/\__/ /_/    /_/    \___/\__, /  
/___/                                  /_/   

Author: 

sjb-ch1mp

Description:

jetfreq.py uses the Carbon Black Response API to search for all instances of a given process and conduct frequency analysis on its associated
events (by default modloads only). It can also be run in 'by_modload' mode in which a given modload is searched for and all processes that
spawn it are returned.

Installation:

1. cd /path/to/install/folder
2. git clone https://github.com/sjb-ch1mp/jetfreq.git
3. cd jetfreq
4. vim jetfreq.py
	a. Change the shebang line to point to your desired python executable:
		i. 	'#!/path/to/python'
5. vim /conf/jetfreq.cfg 
	a. Change the SERVER and KEY fields to your server hostname and API token
		i. 	'SERVER=your.server.hostname'
		ii.	'KEY=your_user_api_token'
6. chmod +x jetfreq.py

Usage:

by_process => './jetfreq.py <search_name> [-U <username> -H <hostname> -s <start_time> -n <sample_size> -t <threshold> -vrfcdxw]'
by_modload => './jetfreq.py <search_name> -m [-U <username> -H <hostname> -s <start_time> -n <sample_size> -t <threshold> -vw]'
show_help  => './jetfreq.py -h'

Parameters:

PARAMETER	|PRESENCE	|VALUE		|DEFAULT	|DESCRIPTION
----------------------------------------------------------------------------
search_name 	|Required	|		|None		|The name of the process or modload
-U		|Optional	|username	|None		|Filter results by <username>
-H		|Optional	|hostname	|None		|Filter results by <hostname>
-s		|Optional	|start_time	|-72h		|Get all results with a start time >= <start_time>
-n 		|Optional	|sample_size	|20		|Get first <sample_size> results only
-t		|Optional	|threshold	|100		|Show those events that occur in <= <threshold>% processes
		|		|		|		|Show those processes that spawn <= <threshold>% modloads
-w 		|Optional	|		|False		|Write results to CSV file (Default is to stdout)
-v		|Optional	|		|False		|Execute jetfreq.py in debug mode
-r		|Optional	|		|False		|Include regmods in results
-f		|Optional	|		|False		|Include filemods in results
-c		|Optional	|		|False		|Include childprocs in results
-d		|Optional	|		|False		|Include netconns in results
-x		|Optional	|		|False		|Include crossprocs in results
-m 		|Optional	|		|False		|Execute jetfreq.py in by_modload mode
-h		|Optional	|		|False		|Show help (this)
