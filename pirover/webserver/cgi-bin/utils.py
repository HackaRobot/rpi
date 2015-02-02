#! /usr/pkg/bin/python

###############################################################################
def print_html_header():
    print "Content-Type: text/html"     # HTML is following
    print """
<style>
  body {background-color:lightgrey}
  h1   {color:blue}
  p    { color:green; font-size:200% }
  input {font-face:'Comic Sans MS';
            font-size: larger;
            color: teal;
            background-color: #FFFFC0;
            border: 3pt ridge lightgrey;
        }
    textarea {
        font-size: larger
    }

</style>
"""

################################################################################
def print_html_form(trimval=0, duration=5, ipaddr="0.0.0.0"):
    html = """
<form method="post" action="click.cgi" enctype="multipart/form-data">
    <p>
        Trim: Left<input type="range" name="trim" value="{0}" min="-10" max="10"/>Right<br/>
        <textarea rows="4" cols="10" name="txtcmds" placeholder="Rover Commands"></textarea> </br>
        <input type="submit" name="click" value="Go"/>
    </p>
    <p>
        Enter commands above or click buttons below: <br/>
        Duration: 
        <input type="text"
            name="duration"
            value="{1}"
            size="10" maxlength="10" />
    <br/>
    <input type="submit" name="click" value="Left"/>
    <input type="submit" name="click" value="Forward"/>
    <input type="submit" name="click" value="Right"/>
    <input type="submit" name="click" value="Back"/>
    <br/>
</p>
    <input type="submit" name="click" value="Snap"/>
    <input type="hidden" name="ipaddr" value="{2}"/>
</form>

<img src="image.cgi"></img>
    </body>
</html>
"""
    print html.format(trimval, duration, ipaddr)



