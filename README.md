# Monte Carlo for Event Scheduling

A couple of years ago, while I was teaching, I wrote some software to try and
schedule lab sessions for 100 second-year students at Swansea University, with
 various constraints.
Previously this was done by shuffling around boxes in Excel until they fit. 
I was sure that a computer could do better in less time.

If you ignore the many hours I spend writing the software, I was right about 
the time it would take. Sadly I never managed to get better than "about as 
good" as could be managed by hand. However, other huge improvements were 
achieved: including personalised schedules, rather than having to read through 
an intricate table, and assessment barcodes so that three separate cover 
sheets were no longer needed.

This was my first "big" project in Python, so please forgive the poor 
structure. I'm releasing it:

* in case any part of it is useful to anyone, 
  although the scheduling algorithm isn't great and a lot of the things it 
  does are very bespoke to Swansea's requirements;
* in the spirit of open development - if I can release code I'm not proud of,
  then I am less hypocritical encouraging others to do the same;
* in case anyone wants to improve it, since it is still in active use in
  Swansea.

## What it does

* Takes in a list of students, who are divided into 'pairs' and 'cohorts'
* Takes in four lists of barcodes for assessment points throughout the year
* Uses a Monte Carlo/Simulated Annealing-style algorithm to assign
  activities to assign a range of available activities to pairs, with certain
  constraints. Unfortunately these are hard-coded in one way or another
* Attempts to optimise the schedule to minimise "unpleasantness"
* Generates personalised timetable cover sheets for each student, including
  their name, pair number, cohort, experiment listings, and barcodes for
  assessment points.
* Generates a summary page of how many of each experiment are due to occur
  on any given week, allowing the lab techs to avoid wasting time setting up 
  unnecessary kit.
* Generate mark sheets allowing markers to easily identify students whose work 
  they need to mark.
* Identifies students' preferred language and generates their timetable using 
  this language. This is done in a fairly extensible way, although not using 
  any standard internationalisation libraries.

## How to get it working

Set up a virtualenv running Python 3.5+ (older versions will probably work, 
but I've not tested them). Then use `pip install -r requirements.txt` to 
install the prerequisites.

To generate cover sheets with the Swansea University branding, you need to 
have appropriate fonts in the same directory as the code. I can't stick these 
on GitHub, so you'll have to find them yourself. The files you'll need are:

* `Cosmos-Light.ttf`
* `Futura-Book.ttf`
* `Futura-Heavy.ttf`

There's a small FontForge script in the repository that will convert .otf 
fonts to .ttf, since I only had these fonts in .otf format. Alternatively 
you can comment out the font load lines and replace all other font references 
so that it uses a font you do have instead.

## How to use it

You will need five or six files in the repository directory:

* `students.csv`: A CSV file containing columns: index, student ID, surname, 
  first name, pair number, language code (this format can be obtained by 
  massaging the result of copying/pasting the module listing from the 
  SU Intranet into Excel; in principle it could be scripted); and/or
* `pairs.csv`: a CSV file in the above format but anonymised to have pair 
  number instead of student number, and blank entries for name
* `barcodesAB.csv`, `barcodes1.csv`, `barcodesCD.csv`, `barcodes2.csv`: 
  whitespace-delimited files containing two columns: student number, and 
  barcode, for the assessment points mid-semester 1, end of semester 1, 
  mid-semester 2, and end of semester 2, respectively. (This is the format 
  generated by the SU College of Science Intranet.)

Some parameters are hard coded, including the number of pairs and the 
split of pairs into cohorts. The experiment list is also hard coded.

To generate a timetable, run `python generate_timetable.py new`. This can 
be done even before you have a student list to generate against, although 
the cover sheet generation will fail. This is useful because it sometimes
takes a few attempts and some massaging of parameters to get the algorithm 
to converge on a real solution. 

(I have been known to on occasion manually read in the database at this 
point and switch some experiments around to reduce the unpleasantness in
a way the algorithm for some reason couldn't spot.)

Once the student list is available, then a fresh set of cover sheets can 
be generated using `python generate_timetable.py`. The anonymised versions 
are obtained using `python generate_timetable.py anon`.

The experiment count listing for the technical staff can be generated using 
`python print_week_list.py`.

Mark sheets are generated for the entire year by running 
`python print_mark_sheet.py 1+2`. The `1+2` can be changed to only
print the mark sheet for a single semester if so desired.

There are also some ancillary files from when I have needed to print out
a set of barcode stickers (because the barcode export wasn't ready in time
for the initial printing), and print marking lists for an individual week
for the whole group (rather than a single marker for a year/semester). These
are not up to date, but might be useful in some circumstances.