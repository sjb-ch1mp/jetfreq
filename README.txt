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

Usage:

by_process => 'python jetfreq.py <search_name> [-u <username> -s <start_time> -w <output_file> -n <sample_size> -t <threshold> -vrfcdx]'
by_modload => 'python jetfreq.py <search_name> -m [-u <username> -s <start_time> -w <output_file> -n <sample_size> -t <threshold> -v]'
show_help  => 'python jetfreq.py -h'

Parameters:

PARAMETER       |PRESENCE       |VALUE          |DEFAULT        |DESCRIPTION
----------------------------------------------------------------------------
search_name     |Required       |               |None           |The name of the process or modload
-u              |Optional       |username       |None           |Filter results by <username>
-s              |Optional       |start_time     |-72h           |Get all results with a start time >= <start_time>
-w              |Optional       |output_file    |stdout         |Write results to <output_file>
-n              |Optional       |sample_size    |20             |Get first <sample_size> results only
-t              |Optional       |threshold      |100            |Show those events that occur in <= <threshold>% processes
                |               |               |               |Show those processes that spawn <= <threshold>% modloads
-v              |Optional       |               |False          |Execute jetfreq.py in debug mode
-r              |Optional       |               |False          |Include regmods in results
-f              |Optional       |               |False          |Include filemods in results
-c              |Optional       |               |False          |Include childprocs in results
-d              |Optional       |               |False          |Include netconns in results
-x              |Optional       |               |False          |Include crossprocs in results
-m              |Optional       |               |False          |Execute jetfreq.py in by_modload mode
-h              |Optional       |               |False          |Show help (this)
