# Nov 2014, juammpatronics

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
# THIS SOFTWARE.

from urllib2 import urlopen
from HTMLParser import HTMLParser
import re, getopt, sys, os
from multiprocessing import Pool

def show_help():
  print "getfiles -e extension -n nthreads url"

class GetExtensionFiles(HTMLParser):
  def __init__(self,extension = '.'):
    """ Per default, it retrieves all links """
    HTMLParser.__init__(self)
    self.extension = re.compile(''.join([extension,"$"]))
    self.links = []

  def handle_starttag(self, tag, attrs):
    if re.match('a',tag):
      for (name,value) in attrs:
        if name == 'href' and self.extension.search(value):
          self.links.append(value)

options, remainder = getopt.getopt(sys.argv[1:],'e:n:d:h',
                      ['extensions=','nagents=','folder=','help'])

nagents = 2
folder = os.getcwd() + os.pathsep
for opt,arg in options:
  if opt in ('-e','--extensions'):
    extensions = arg
    if  len(extensions.strip()) == 0:
      print "Not a valid extension"
      sys.exit(1)

  if opt in ('-h','--help'):
    show_help()
    sys.exit(0)

  if opt in ('-n','--nagents'):
    try:
      nagents = int(arg)   # number of simultaneous downloads
    except ValueError:
      print "Not a valid number of agents ", nagents
      sys.exit(1)

  if opt in ('-d','--folder'):
    folder = arg if arg.endswith(os.pathsep) else arg + os.pathsep
    if not os.path.isdir(folder):
      print folder, " is not a valid folder name"
      sys.exit(1)


if not extensions:
  print "Missing extension"
  show_help()
  sys.exit(1)

if not remainder:
  print "Missing input arguments"
  show_help()
  sys.exit(1)

# gzfiles = GetExtensionFiles("gz")
# page = urlopen('http://www.x.org/releases/X11R7.7/src/everything/')

def download_link(url):
  fname = url.split('/')[-1]
  f = urlopen(url)
  with open(folder + fname,'wb') as fh:
    fh.write(f.read())

getlinks = GetExtensionFiles(extensions)
for address in remainder:
  page = urlopen(address)
  getlinks.feed(''.join(page.readlines()))
  page.close()
  if not getlinks.links:
    print "Could not find any link in ", address, "matching ", extensions

  pool = Pool(nagents)
  pool.map_async(download_link,map(
    lambda url: address+url if not re.match('^http',url) else url,
    getlinks.links))
  pool.close()
  pool.join()
