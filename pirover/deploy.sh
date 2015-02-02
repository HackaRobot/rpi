#!/bin/sh

# Helper script to deploy cgi scripts and HTML file.

DEPLOYDIR=/www/pirover
SRCDIR=.
PYTHON=`which python`

mkdir -p $DEPLOYDIR/cgi-bin/archive
chmod -R a+x $DEPLOYDIR/

deploy_cgi() {
    SRCFILE=$1
    DSTFILE=$2
    sed -e "
    1c\\
#!$PYTHON
    " < $SRCFILE > $DSTFILE
    chmod a+x $DSTFILE
}

deploy_cgi $SRCDIR/webserver/cgi-bin/click.cgi  $DEPLOYDIR/cgi-bin/click.cgi
deploy_cgi $SRCDIR/webserver/cgi-bin/upload.cgi  $DEPLOYDIR/cgi-bin/upload.cgi
deploy_cgi $SRCDIR/webserver/cgi-bin/image.cgi  $DEPLOYDIR/cgi-bin/image.cgi
cp -p $SRCDIR/webserver/index.html $DEPLOYDIR/
cp -p $SRCDIR/webserver/server.py $DEPLOYDIR/
cp -p $SRCDIR/webserver/view.html $DEPLOYDIR/
cp -p $SRCDIR/webserver/cgi-bin/pymjpeg.py $DEPLOYDIR/cgi-bin/
cp -p $SRCDIR/webserver/cgi-bin/utils.py $DEPLOYDIR/cgi-bin/
chmod -R a+r $DEPLOYDIR/
