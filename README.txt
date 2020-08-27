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
events. It can also be run in 'Event Mode' to search for a given event type (e.g. modload, regmod) and conduct frequency analysis on the processes that
access it. Running jetfreq.py in 'Compare Mode' allows users to compare a target sample with a representative sample that has been saved in the
./samples directory.

Usage:

By Process Mode : './jetfreq.py [--by-process] <search_name> -m|r|f|c|d|x [{-u|-U} <username> {-h|-H} <hostname> -s <start_time> -n <sample_size> {-t|-T} <threshold> -wvko]'
By Event Mode : './jetfreq.py --by-event -m|r|f|c|d <search_name> [{-u|-U} <username> {-h|-H} <hostname> -s <start_time> -n <sample_size> {-t|-T} <threshold> -vwko]'
Compare Processes : './jetfreq.py --compare-process <search_name> -i <sample_file> -m|r|f|c|d|x [{-u|-U} <username> {-h|-H} <hostname> -s <start_time> -n <sample_size> {-t|-T} <threshold> -wvko]'
Compare Events : './jetfreq.py --compare-event -m|r|f|c|d <search_name> -i <sample_file> [{-u|-U} <username> {-h|-H} <hostname> -s <start_time> -n <sample_size> {-t|-T} <threshold> -vwko]'
Show Help : './jetfreq.py --help'

Parameters:

:: Mandatory
search_name : The name of the process or modload

:: Modes
--by-process : Search for given process (default mode).
--by-event : Search for a given event, e.g. modload, regmod, netconn
--compare-process : Compare a representative by-process sample with a target by-process sample
--compare-event : Compare a representative by-event sample with a target by-event sample
--help : Show help (this)

:: With Value
-u : Filter results by <username>
-U : Exclude all results from <username>
-h : Filter results by <hostname>
-H : Exclude all results from <hostname>
-s : Get all results with a start time >= <s> (default = '-672h')
-n : Get first <n> results only (default = '50')
-t : Include events that occur in <= <threshold>% processes (default = '100')
-T : Include events that occur in >= <threshold>% processes (default = '0')
-i : Import <sample_file> to compare to target sample

:: Boolean
-w : Write results to CSV file (./samples)
-v : Verbose
-r : Include regmods in results (--by-process) | Search for regmod (--by-event)
-f : Include filemods in results (--by-process) | Search for filemod (--by-event)
-c : Include childprocs in results (--by-process) | Search for childproc (--by-event)
-d : Include netconns in results (--by-process) | Search for netconn (--by-event)
-x : Include crossprocs in results (--by-process only)
-m : Include modloads in results (--by-process) | Search for modload (--by-event)
-k : Truncates any directory path with greater than 4 levels to 4, or registry key paths with greater than 6 levels to 6.
-o : Homogenize directory and regkey paths, e.g. 'C:\user\mr_fluffy\...' -> 'C:\user\<USER>\...'

File name syntax:

--by-process : ./samples/process/<datetime>_s-<search-name>_e-<event-types>_n-<sample-size>_t-<upper_threshold>_T-<lower_threshold>[_u-<username>_h-<hostname>].csv
--by-event : ./samples/event/<datetime>_s-<search-name>_e-<event-type>_n-<sample-size>_t-<upper_threshold>_T-<lower_threshold>[_u-<username>_h-<hostname>].csv
--compare-process : ./samples/process/diff/<datetime>_s-<search-name>_e-<event-types>_n-<sample-size>_t-<upper_threshold>_T-<lower_threshold>[_u-<username>_h-<hostname>]_i-<sample-file-datetime>.csv
--compare-event : ./samples/event/diff/<datetime>_s-<search-name>_e-<event-type>_n-<sample-size>_t-<upper_threshold>_T-<lower_threshold>[_u-<username>_h-<hostname>]_i-<sample-file-datetime>.csv
