# Build it, Break it, Fix it (BiBiFi 2014)

* Submission by KnightSec
* *Coder:* Grant Hernandez
* *QA:* Ditmar Wendt, Alex Lynch

This submission was a great exercise in safely applying AES and HMAC
implementations to create a "secure" file container. At the time, it was
probably the most complete Python project I had written. This definitely taught
me that although Python is easy to write, the lack of a static type system
could seriously compromise the reliability of a program if care was not taken.

Although this program uses off-the-shelf cryptographic implementations, it should be considered as "rolling your own crypto" as the guarantees of the file container have not been formally verified in any way. There may be mistakes or ommissions that could lead to the compromise of the container.

For more information on the 2014 contest, [read this recap by Michael Hicks](http://www.pl-enthusiast.net/2014/10/08/bibifi-contest/).

## Architecture
* **Language:** Python
* **Security model:** Fully encrypted event transactions with an HMAC for authentication and integrity checking

## Log Append
Dedicated log writing application. Unseals the log file, writes an event record, reseals.

## Log Read
Dedicated reader application. Unseals the log file, performs some query on the event records, reseals.
