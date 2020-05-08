# MassDNS 0.3 (experimental)
## A high-performance DNS stub resolver

MassDNS is a simple high-performance DNS stub resolver targetting those who seek to resolve a massive amount of domain
names in the order of millions or even billions. Without special configuration, MassDNS is capable of resolving over
350,000 names per second using publicly available resolvers.

## Major changes
This version of MassDNS is currently experimental. In order to speed up the resolving process, the `ldns` dependency has
been replaced by a custom stack-based DNS implementation (which currently only supports the text representation of the
most common DNS records). Furthermore, epoll has been introduced in order to lighten CPU usage when operating with a low
concurrency which may have broken compatibility with some platforms. In case of bugs, please create an issue and
[switch to the more mature version 0.2](https://github.com/blechschmidt/massdns/tree/v0.2).

Also note that the command line interface has changed slightly due to criticism of the output complexity. Additionally,
the default values of the `-s` and `-i` parameters have been changed. The repository structure has been changed as well.

## Contributors
* [Quirin Scheitle](https://github.com/quirins), [Technical University of Munich](https://www.net.in.tum.de/members/scheitle/)

## Compilation
Clone the git repository and `cd` into the project root folder. Then run `make` to build from source.
If you are not on Linux, run `make nolinux`. On Windows, the `Cygwin` packages `gcc-core`, `git` and `make` are required.

## Usage
```
Usage: ./bin/massdns [options] [domainlist]
  -b  --bindto           Bind to IP address and port. (Default: 0.0.0.0:0)
      --busy-poll        Use busy-wait polling instead of epoll.
  -c  --resolve-count    Number of resolves for a name before giving up. (Default: 50)
      --drop-group       Group to drop privileges to when running as root. (Default: nogroup)
      --drop-user        User to drop privileges to when running as root. (Default: nobody)
      --flush            Flush the output file whenever a response was received.
  -h  --help             Show this help.
  -i  --interval         Interval in milliseconds to wait between multiple resolves of the same
                         domain. (Default: 500)
  -l  --error-log        Error log file path. (Default: /dev/stderr)
      --norecurse        Use non-recursive queries. Useful for DNS cache snooping.
  -o  --output           Flags for output formatting.
      --predictable      Use resolvers incrementally. Useful for resolver tests.
      --processes        Number of processes to be used for resolving. (Default: 1)
  -q  --quiet            Quiet mode.
      --rcvbuf           Size of the receive buffer in bytes.
      --retry            Unacceptable DNS response codes. (Default: REFUSED)
  -r  --resolvers        Text file containing DNS resolvers.
      --root             Do not drop privileges when running as root. Not recommended.
  -s  --hashmap-size     Number of concurrent lookups. (Default: 10000)
      --sndbuf           Size of the send buffer in bytes.
      --status-format    Format for real-time status updates, json or ansi (Default: ansi)
      --sticky           Do not switch the resolver when retrying.
      --socket-count     Socket count per process. (Default: 1)
  -t  --type             Record type to be resolved. (Default: A)
      --verify-ip        Verify IP addresses of incoming replies.
  -w  --outfile          Write to the specified output file instead of standard output.

Output flags:
  S - simple text output
  F - full text output
  B - binary output
  J - ndjson output

Advanced flags for the simple output mode:
  d - Include records from the additional section.
  i - Indent any reply record.
  l - Separate replies using a line feed.
  m - Only output reply records that match the question name.
  n - Include records from the answer section.
  q - Print the question.
  r - Prepend resolver IP address, Unix timestamp and return code to the question line.
  s - Separate packet sections using a line feed.
  t - Include TTL and record class within the output.
  u - Include records from the authority section.
```

This overview may be incomplete. For more options, especially concerning output formatting, use `--help`.

### Example
Resolve all AAAA records from domains within domains.txt using the resolvers within `resolvers.txt` in `lists` and
store the results within results.txt:
```
$ ./bin/massdns -r lists/resolvers.txt -t AAAA domains.txt > results.txt
```

This is equivalent to:
```
$ ./bin/massdns -r lists/resolvers.txt -t AAAA -w results.txt domains.txt
```

#### Example output
By default, MassDNS will output response packets in text format which looks similar to the following:
```
;; Server: 77.41.229.2:53
;; Size: 93
;; Unix time: 1513458347
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 51298
;; flags: qr rd ra ; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 0

;; QUESTION SECTION:
example.com. IN A

;; ANSWER SECTION:
example.com. 45929 IN A 93.184.216.34

;; AUTHORITY SECTION:
example.com. 24852 IN NS b.iana-servers.net.
example.com. 24852 IN NS a.iana-servers.net.
```

The resolver IP address is included in order to make it easier for you to filter the output in case you detect that some resolvers produce bad results.

### Resolving
The repository includes the file `resolvers.txt` consisting of a filtered subset of the resolvers provided by the [subbrute project](https://github.com/TheRook/subbrute).
Please note that the usage of MassDNS may cause a significant load on the used resolvers and result in abuse complaints being sent to your ISP.
Also note that the provided resolvers are not guaranteed to be trustworthy. The resolver list is currently outdated with a large share of resolvers being dysfunctional.

MassDNS's DNS implementation is currently very sporadic and only supports the most common records. You are welcome to help changing this by collaborating.

#### PTR records
MassDNS includes a Python script allowing you to resolve all IPv4 PTR records by printing their respective queries to the standard output.
```
$ ./scripts/ptr.py | ./bin/massdns -r lists/resolvers.txt -t PTR -w ptr.txt
```
Please note that the labels within `in-addr.arpa` are reversed. In order to resolve the domain name of `1.2.3.4`, MassDNS expects `4.3.2.1.in-addr.arpa` as input query name.
As a consequence, the Python script does not resolve the records in an ascending order which is an advantage because sudden heavy spikes at the name servers of IPv4 subnets are avoided.

#### Reconnaissance by brute-forcing subdomains
**Perform reconnaissance scans responsibly and adjust the `-s` parameter to not overwhelm authoritative name servers.**

Similar to [subbrute](https://github.com/TheRook/subbrute), MassDNS allows you to brute force subdomains using the included `subbrute.py` script:
```
$ ./scripts/subbrute.py lists/names.txt example.com | ./bin/massdns -r lists/resolvers.txt -t A -o S -w results.txt
```

As an additional method of reconnaissance, the `ct.py` script extracts subdomains from certificate transparency logs by scraping the data from [crt.sh](https://crt.sh):
```
$ ./scripts/ct.py example.com | ./bin/massdns -r lists/resolvers.txt -t A -o S -w results.txt
```

The files `names.txt` and `names_small.txt`, which have been copied from the [subbrute project](https://github.com/TheRook/subbrute), contain names of commonly used subdomains. Also consider using [Jason Haddix' subdomain compilation](https://gist.github.com/jhaddix/86a06c5dc309d08580a018c66354a056/raw/f58e82c9abfa46a932eb92edbe6b18214141439b/all.txt) with over 1,000,000 names.

## Screenshots
![Screenshot](https://www.cysec.biz/projects/massdns/screenshots/screenshot2.png)

## Security
MassDNS does not require root privileges and will therefore drop privileges to the user called "nobody" by default when being run as root.
If the user "nobody" does not exist, MassDNS will refuse execution. In this case, it is recommended to run MassDNS as another non-privileged user.
The privilege drop can be circumvented using the `--root` argument which is not recommended.
Also note that other branches than master should not be used in production at all.

## Practical considerations
### Performance tuning
MassDNS is a simple single-threaded application designed for scenarios in which the network is the bottleneck. It is designed to be run on servers with high upload and download bandwidths. Internally, MassDNS makes use of a hash map which controls the concurrency of lookups. Setting the size parameter `-s` hence allows you to control the lookup rate. If you are experiencing performance issues, try adjusting the `-s` parameter in order to obtain a better success rate.

### Rate limiting evasion
In case rate limiting by IPv6 resolvers is a problem, have a look at the [freebind](https://github.com/blechschmidt/freebind) project including `packetrand`, which will cause each packet to be sent from a different IPv6 address from a routed prefix.

### Result authenticity
If the authenticity of results is highly essential, you should not rely on the included resolver list. Instead, set up a local [unbound](https://www.unbound.net/) resolver and supply MassDNS with its IP address. In case you are using MassDNS as a reconnaissance tool, you may wish to run it with the default resolver list first and re-run it on the found names with a list of trusted resolvers in order to eliminate false positives.

## Todo
- Prevent flooding resolvers which are employing rate limits or refusing resolves after some time
- Implement bandwidth limits
- Employ cross-resolver checks to detect DNS poisoning and DNS spam (e.g. [Level 3 DNS hijacking](https://web.archive.org/web/20140302064622/http://james.bertelson.me/blog/2014/01/level-3-are-now-hijacking-failed-dns-requests-for-ad-revenue-on-4-2-2-x/))
- Add wildcard detection for reconnaissance
- Improve reconnaissance reliability by adding a mode which re-resolves found domains through a list of trusted (local) resolvers in order to eliminate false positives
- Detect optimal concurrency automatically
- Parse the command line properly and allow the usage/combination of short options without spaces
