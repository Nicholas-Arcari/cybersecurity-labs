# Imposta logwatch

Comando:

```Bash
sudo apt install logwatch
```

Una volta installato configura il tuo logwatch:

```Bash
sudo nano /usr/share/logwatch/default.conf/logwatch.conf
```

Il file risultante deve essere qualcosa del genere:
```Bash
########################################################
# This was written and is maintained by:
#    Kirk Bauer <kirk@kaybee.org>
#
# Please send all comments, suggestions, bug reports,
#    etc, to kirk@kaybee.org.
#
########################################################

# This file lists the default values of the variables, unless
# it is listed as an example, in which case it merely illustrates
# one possible option.
#
# The preferred way of changing a variable is not by changing
# this file.  Rather, you can override the variable by re-assigning
# it locally.  The default location for this override file is
# /etc/logwatch/conf/logwatch.conf
#
# You can override many of these variables on the command line.

# Comments are indicated by the '#' character.  Any characters after
# that are ignored, even if not on the first column.

# Variables are in the format of <name> = <value>.  Whitespace at the
# beginning and end of the lines is removed.  Whitespace before and after
# the = sign is removed.  Both names and values are case insensitive,
# except when indicated.

# For all these variables, only literal strings are allowed.  That is,
# variables cannot be used to set the value.

# Here are the synonyms that can be used for any variable that expects
# one of these values:
# Yes = True  = On  = 1
# No  = False = Off = 0

# You can override the default temp directory (/tmp) here
TmpDir = /var/cache/logwatch

# To format using HTML use Format = html
Format = text
# For HTML output, this variable sets the maximum line length:
# HTML_Wrap = 80

# The default, Encode = none, is the same as Encode = 8bit.
# To make Base64 [aka uuencode] use Encode = base64
# You can also specify 'Encode = 7bit', but only if all text is ASCII only.
Encode = none

# Input Encoding
# Logwatch assumes that the input is in UTF-8 encoding.  Defining CharEncoding
# will use iconv to convert text to the UTF-8 encoding.  Set CharEncoding
# to an empty string to use the default current locale.  If set to a valid
# encoding, the input characters are converted to UTF-8, discarding any
# illegal characters.  Valid encodings are as used by the iconv program,
# and `iconv -l` lists valid character set encodings.
# Setting CharEncoding to UTF-8 simply discards illegal UTF-8 characters.
# CharEncoding = ""

# Output/Format Options
# By default Logwatch will print to stdout in text with no encoding.
# To make email Default set Output = mail to save to file set Output = file
Output = stdout

# If Output is set to "file", a filename must be provided for the
# Filename variable.  The results will be saved to this file.
# The value of this variable is case-sensitive.  For example,
Filename = "/tmp/Logwatch"

# Default person to mail reports to.  Can be a local account or a
# complete email address.  Variable Output should be set to mail, or
# --output mail should be passed on command line to enable mail feature.
# If the environmental variable MAILTO is set, it becomes the default.
# This value is case-sensitive.
MailTo = <tuo_indirizzo_mail>

# When using the mail feature, the subject can be set to a literal string.
# The default is an empty string:
# Subject = ""
# Using the default of an empty string will cause the equivalent of the
# following string to be used: "Logwatch for $(hostname) ($(uname -s))"
# But because only a literal string is allowed in the configuration file,
# no variables may be passed in the string.
# For example:
# Subject = "Logwatch from ExampleHostname"
# The subject can also be set with the command switch --subject, which also
# allows shell decoding of variables.

# When using option --multiemail, it is possible to specify a different
# email recipient per host processed.  For example, to send the report
# for hostname host1 to user@example.com, use:
#Mailto_host1 = user@example.com
# Multiple recipients can be specified by separating them with a space.

# Default person to mail reports from.  Can be a local account or a
# complete email address.
MailFrom = Logwatch

# Use archives?  If set to 'Yes', the archives of logfiles
# (i.e. /var/log/messages.1 or /var/log/messages.1.gz) will
# be searched in addition to the /var/log/messages file.
# This usually will not do much if your range is set to just
# 'Yesterday' or 'Today'... it is probably best used with Range = All
# By default this is now set to Yes.
# Archives = Yes

# The default time range for the report...
# The current choices are All, Today, Yesterday
Range = yesterday

# The default detail level for the report.
# This can either be Low, Med, High or a number.
# Low is a synonym for 0, Med is 5, and High is 10.
Detail = Low


# The 'Service' option expects either the name of a filter
# (in /usr/share/logwatch/scripts/services/*) or 'All'.
# It indicates the default service(s) to report on.  This should be
# left as All for most systems.
Service = All
# You can also disable certain services (when specifying all)
Service = "-zz-network"     # Prevents execution of zz-network service, which
                            # prints useful network configuration info.
Service = "-zz-sys"         # Prevents execution of zz-sys service, which
                            # prints useful system configuration info.
Service = "-eximstats"      # Prevents execution of eximstats service, which
                            # is a wrapper for the eximstats program.
# Because the above sets "All" as the default, and disables certain
# services, you can also set the Service variable to an empty string
# in your local logwatch.conf (by default, under /etc/logwatch/conf).
# That resets the setting of Service, after which you can assign to it
# specific services that you want executed.

# The following are more examples of using the Service variable:
# If you only cared about FTP messages, you could use these 2 lines
# instead of the above:
# Service = ftpd-messages   # Processes ftpd messages in /var/log/messages
# Service = ftpd-xferlog    # Processes ftpd messages in /var/log/xferlog
# Maybe you only wanted reports on PAM messages, then you would use:
# Service = pam_pwdb        # PAM_pwdb messages - usually quite a bit
# Service = pam             # General PAM messages... usually not many

# You can also choose to use the 'LogFile' option.  This will cause
# logwatch to only analyze that one logfile.  For example:
# LogFile = messages
# will process /var/log/messages.  This will run all the filters that
# process that logfile.  This option is probably not too useful, except
# for debugging.  Each service lists its own Logfile options.

# By default we assume that all Unix systems have sendmail or a sendmail-like MTA.
# The mailer code prints a header with To: From: and Subject:.
# At this point you can change the mailer to anything that can handle this output
# stream.
# TODO test variables in the mailer string to see if the To/From/Subject can be set
# From here with out breaking anything. This would allow mail/mailx/nail etc..... -mgt
# This value is case-sensitive.
# mailer = "/usr/sbin/sendmail -t"

# With this option set to a comma separated list of hostnames, only log entries
# for these particular hosts will be processed.  This can allow a log host to
# process only its own logs, or Logwatch can be run once per a set of hosts
# included in the logfiles.  The hostnames are case-sensitive.
# Example: HostLimit = hosta,hostb,myhost
#
# The default is to report on all log entries, regardless of its source host.
# Note that some logfiles do not include host information and will not be
# influenced by this setting.

# Default Log Directory
# All log files are assumed to be given relative to the LogDir directory.
# Multiple LogDir statements are possible.  Additional configuration variables
# to set particular directories follow, so LogDir need not be set.
# This value is case-sensitive.
# For example:
# LogDir = /var/log
#
# By default /var/adm is searched after LogDir.
# AppendVarAdmToLogDirs = 1
#
# By default /var/log is to be searched after LogDir and /var/adm/ .
# AppendVarLogToLogDirs = 1
#
# The current working directory can be searched after the above.  Not set by
# default.
# AppendCWDToLogDirs = 0

# Logwatch can decompress log files (often the case for archived log files -
# that is, older log files rotated and compressed.
# The following variables set the default compression programs:
# PathTozcat = "zcat"
# PathTobzcat = "bzcat"
# PathToxzcat = "zxcat"

# vi: shiftwidth=3 tabstop=3 et
```

Dopo aver salvato il file puoi eseguire logwatch manualmente per generare un report con il comando:
```Bash
sudo logwatch --detail high --mailto <tuo_indirizzo_mail>
```

- Perché farlo?

Nessuno ha tempo di leggere 10.000 righe di log grezzi ogni giorno

- Cosa accade dopo?

Ricevi una email o un report giornaliero che riassume solo le cose importanti (es. "5 tentativi di login falliti", "spazio disco al 90%")

- Cosa rischi se non lo fai?

"Log fatigue": ignori i log perché sono troppi, perdendoti l'unico avviso critico nascosto nel rumore