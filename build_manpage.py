# -*- coding: utf-8 -*-

"""build_manpage command -- Generate man page from setup()"""

"""python setup.py build_manpage --output=bla.txt
   --parser=scripts.pwman3:parser_optios
"""

import datetime
from distutils.command.build import build
from distutils.core import Command
from distutils.errors import DistutilsOptionError
import optparse
import argparse

class build_manpage(Command):
    """-O bla.1 --parser pwman:parser_options"""
    description = 'Generate man page from setup().'

    user_options = [
        ('output=', 'O', 'output file'),
        ('parser=', None, 'module path to optparser (e.g. mymod:func'),
        ]

    def initialize_options(self):
        self.output = None
        self.parser = None

    def finalize_options(self):
        if self.output is None:
            raise DistutilsOptionError('\'output\' option is required')
        if self.parser is None:
            raise DistutilsOptionError('\'parser\' option is required')
        mod_name, func_name = self.parser.split(':')
        fromlist = mod_name.split('.')
        try:
            mod = __import__(mod_name, fromlist=fromlist)
            self._parser = getattr(mod, func_name)()
        except ImportError, err:
            raise
        self._parser.formatter = ManPageFormatter()
        self._parser.formatter.set_parser(self._parser)
        self.announce('Writing man page %s' % self.output)
        self._today = datetime.date.today()

    def _markup(self, txt):
        return txt.replace('-', '\\-')

    def _write_header(self):
        appname = self.distribution.get_name()
        ret = []
        ret.append('.TH %s 1 %s\n' % (self._markup(appname),
                                      self._today.strftime('%Y\\-%m\\-%d')))
        description = self.distribution.get_description()
        if description:
            name = self._markup('%s - %s' % (self._markup(appname),
                                             description.splitlines()[0]))
        else:
            name = self._markup(appname)
        ret.append('.SH NAME\n%s\n' % name)

        if isinstance(self._parser, argparse.ArgumentParser):
            self._parser.prog = self.distribution.get_name()
            synopsis = self._parser.format_usage().split(':',1)[1]
        else:
            synopsis = self._parser.get_usage()
        if synopsis:
            synopsis = synopsis.replace('%s ' % appname, '')
            ret.append('.SH SYNOPSIS\n.B %s\n%s\n' % (self._markup(appname),
                                                      synopsis))
        long_desc = self.distribution.get_long_description()
        if long_desc:
            ret.append('.SH DESCRIPTION\n%s\n' % self._markup(long_desc))
        return ''.join(ret)

    def _write_options(self):
        ret = ['.SH OPTIONS\n']
        ret.append(self._parser.format_option_help())
        return ''.join(ret)

    def _write_footer(self):
        ret = []
        appname = self.distribution.get_name()
        author = '%s <%s>' % (self.distribution.get_author(),
                              self.distribution.get_author_email())
        ret.append(('.SH AUTHORS\n.B %s\nwas written by %s.\n'
                    % (self._markup(appname), self._markup(author))))
        homepage = self.distribution.get_url()
        ret.append(('.SH DISTRIBUTION\nThe latest version of %s may '
                    'be downloaded from\n'
                    '.UR %s\n.UE\n'
                    % (self._markup(appname), self._markup(homepage),)))
        return ''.join(ret)

    def run(self):
        manpage = []
        manpage.append(self._write_header())
        manpage.append(self._write_options())
        manpage.append(self._write_footer())
        stream = open(self.output, 'w')
        stream.write(''.join(manpage))
        stream.close()


class ManPageArgFormatter(argparse.HelpFormatter):
    pass

class ManPageFormatter(optparse.HelpFormatter):

    def __init__(self,
                 indent_increment=2,
                 max_help_position=24,
                 width=None,
                 short_first=1):

        # should be replace with super ?
        optparse.HelpFormatter.__init__(self, indent_increment,
                                        max_help_position, width, short_first)

        # argparse.HelpFormatter(indent_increment, max_help_position, width,)
        # no such option in argparse?                         short_first=1)

    def _markup(self, txt):
        return txt.replace('-', '\\-')

    def format_usage(self, usage):
        return self._markup(usage)

    def format_heading(self, heading):
        if self.level == 0:
            return ''
        return '.TP\n%s\n' % self._markup(heading.upper())

    def format_option(self, option):
        result = []
        opts = self.option_strings[option]
        result.append('.TP\n.B %s\n' % self._markup(opts))
        if option.help:
            help_text = '%s\n' % self._markup(self.expand_default(option))
            result.append(help_text)
        return ''.join(result)


#build.sub_commands.append(('build_manpage', None))

