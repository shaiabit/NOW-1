# -*- coding: UTF-8 -*-
"""
Commands

Commands describe the input the player can do to the world.

"""
from evennia import gametime
from django.conf import settings
from evennia import utils
from evennia import default_cmds
from evennia import Command as BaseCommand
from evennia.commands.default.muxcommand import MuxCommand, MuxPlayerCommand


class Command(BaseCommand):
    """
    Inherit from this if you want to create your own
    command styles. Note that Evennia's default commands
    use MuxCommand instead (next in this module).

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order:
        - at_pre_command(): If this returns True, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_command(): Extra actions, often things done after
            every command, like prompts.
    """
    # these need to be specified

    key = "MyCommand"
    aliases = []
    locks = "cmd:all()"
    help_category = "General"

    # optional
    # auto_help = False      # uncomment to deactive auto-help for this command.
    # arg_regex = r"\s.*?|$" # optional regex detailing how the part after
    # the cmdname must look to match this command.

    # (we don't implement hook method access() here, you don't need to
    #  modify that unless you want to change how the lock system works
    #  (in that case see evennia.commands.command.Command))

    def at_pre_cmd(self):
        """
        This hook is called before `self.parse()` on all commands.
        """
        pass

    def parse(self):
        """
        This method is called by the `cmdhandler` once the command name
        has been identified. It creates a new set of member variables
        that can be later accessed from `self.func()` (see below).

        The following variables are available to us:
           # class variables:

           self.key - the name of this command ('mycommand')
           self.aliases - the aliases of this cmd ('mycmd','myc')
           self.locks - lock string for this command ("cmd:all()")
           self.help_category - overall category of command ("General")

           # added at run-time by `cmdhandler`:

           self.caller - the object calling this command
           self.cmdstring - the actual command name used to call this
                            (this allows you to know which alias was used,
                             for example)
           self.args - the raw input; everything following `self.cmdstring`.
           self.cmdset - the `cmdset` from which this command was picked. Not
                         often used (useful for commands like `help` or to
                         list all available commands etc).
           self.obj - the object on which this command was defined. It is often
                         the same as `self.caller`.
        """
        pass

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the `cmdhandler` right after `self.parser()` finishes, and so has access
        to all the variables defined therein.
        """
        self.caller.msg('Command "%s" called!' % self.cmdstring)

    def at_post_cmd(self):
        """
        This hook is called after `self.func()`.
        """
        pass


class MuxCommand(default_cmds.MuxCommand):
    """
    This sets up the basis for Evennia's 'MUX-like' command style.
    The idea is that most other Mux-related commands should
    just inherit from this and don't have to implement parsing of
    their own unless they do something particularly advanced.

    A MUXCommand command understands the following possible syntax:

        name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]

    The `name[ with several words]` part is already dealt with by the
    `cmdhandler` at this point, and stored in `self.cmdname`. The rest is stored
    in `self.args`.

    The MuxCommand parser breaks `self.args` into its constituents and stores them
    in the following variables:
        self.switches = optional list of /switches (without the /).
        self.raw = This is the raw argument input, including switches.
        self.args = This is re-defined to be everything *except* the switches.
        self.lhs = Everything to the left of `=` (lhs:'left-hand side'). If
                     no `=` is found, this is identical to `self.args`.
        self.rhs: Everything to the right of `=` (rhs:'right-hand side').
                    If no `=` is found, this is `None`.
        self.lhslist - `self.lhs` split into a list by comma.
        self.rhslist - list of `self.rhs` split into a list by comma.
        self.arglist = list of space-separated args (including `=` if it exists).

    All args and list members are stripped of excess whitespace around the
    strings, but case is preserved.
    """
    player_caller = True

    def at_pre_cmd(self):
        """
        This hook is called before self.parse() on all commands
        """
        pass

    def parse(self):
        """
        This method is called by the cmdhandler once the command name
        has been identified. It creates a new set of member variables
        that can be later accessed from self.func()
        """
        super(MuxCommand, self).parse()

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the `cmdhandler` right after `self.parser()` finishes, and so has access
        to all the variables defined therein.
        """
        super(MuxCommand, self).func()

    def at_post_cmd(self):
        """
        This hook is called after the command has finished executing
        (after self.func()).
        """
        char = self.character
        here = char.location if char else None
        who = self.player.key if self.player else '-visitor-'
        print('%s> %s%s' % (who, self.cmdstring, self.raw))
        if here:
            if char.db.settings and 'broadcast command' in char.db.settings and char.db.settings['broadcast command']:
                here.msg_contents('|r(|n%s%s|n|r)|n' % (self.cmdstring, self.raw))


class MuxPlayerCommand(MuxCommand):
    """
    This is an on-Player version of the MuxCommand. Since these commands sit
    on Players rather than on Characters/Objects, we need to check
    this in the parser.
    Player commands are available also when puppeting a Character, it's
    just that they are applied with a lower priority and are always
    available, also when disconnected from a character (i.e. "ooc").
    This class makes sure that caller is always a Player object, while
    creating a new property "character" that is set only if a
    character is actually attached to this Player and Session.
    """
    def parse(self):
        """
        We run the parent parser as usual, then fix the result
        """
        super(MuxPlayerCommand, self).parse()

        if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
            self.character = self.caller  # caller is an Object/Character
            self.caller = self.caller.player
        elif utils.inherits_from(self.caller, "evennia.players.players.DefaultPlayer"):
            self.character = self.caller.get_puppet(self.session)  # caller was already a Player
        else:
            self.character = None
