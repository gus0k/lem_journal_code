#!/bin/sh

echo "$PWD"

rsync --exclude-from=.rsyncignore -a --progress "$PWD" dkiedanski@lame23.enst.fr:/home/infres/dkiedanski/
