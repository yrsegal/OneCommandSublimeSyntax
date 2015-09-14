# OneCommandSublimeSyntax
A sublime syntax for [the One Command generator](https://github.com/destruc7i0n/OneCommand) by myself and [destruc7i0n](https://github.com/destruc7i0n).

[PackageControl page](https://packagecontrol.io/packages/One%20Command%20Syntax%20Highlighter)

## What it adds

### Commands
#### `minecraft_onecc_instant`
Generates a self-activating one-command contraption from the current file.

#### `minecraft_onecc_manual`
Generates a manually-activated one-command contraption from the current file.

#### `minecraft_sort_selectors`
Sorts any entity/player selector tags within the selection by alphabetical order.

#### `minecraft_onecc_format`
Explodes the commands selected, using `-` syntax to keep them in the same line in the eyes of the generator.

#### `minecraft_onecc_unformat`
Compresses `-` syntax down to normal lines.

---

### Language
#### `source.one_command`
A syntax highlighter for the special syntax accepted by the generator. Uses the file extension `.1cc`.

## The Syntax
Most of the differences between 1CC syntax and regular commands lie in the prepends.  

* `INIT:` as a prepend will make the command only run once, when you run the command.
* `COND:` as a prepend will make the command only run if the previous one was successful. Not recommended to use on the first command, nor the first `INIT:` command.
* `REPEAT:` as a prepend will make the command in a repeating command block. This is included to allow for different-speed clocks, and similar functions.
* `BLOCK:` as a prepend will use the following command (format `minecraft:BLOCKNAME:DATA`) as a normal block instead of a command. This can be used to visually seperate parts of a module; remember that `REPEAT:` must be used afterwards to carry the signal.
* `-` as a prepend will append the current line to the previous one.

There's also the `DEFINE:` syntax, similar to the C `#define` directive. This allows simpler-to-read blocks of code to be written.  
The syntax is `DEFINE: identifier replacewith`. You can then use this by calling out, anywhere in your code, `$identifier`.
