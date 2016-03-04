# Thesaurus Query/Replacement Plugin

This is a plugin for user to lookup synonyms of any word under cursor and
replace it with an user chosen synonym. It also accept word covered in visual
mode or manual input. But for the latter two cases, auto-replacement function
isn't activated by default.

![](https://github.com/ron89/thesaurus_query.vim/raw/master/synonym_candidate.png)

Two backends are used for this plugin, they function independently.

*   **Online query backend** querys from [Thesaurus.com](http://thesaurus.com/) for
    synonym, so internet connection is required for this backend's
    functionality.

*   **Local query backend** querys from `mthesaur.txt`. For this backend to work,
    be sure to download the file from
    [gutenberg.org](http://www.gutenberg.org/files/3202/files/) and place
    it under "~/.vim/thesaurus". If you place the file elsewhere, change
    global variable |g:thesaurus_query#mthesaur_file| to
    point to the file you downloaded, eg. put the following line
    `let g:thesaurus_query#mthesaurus="~/.config/nvim/thesaurus/mthesaur.txt"`
    into your `.vimrc` file if your `mthesaur.txt` is placed in folder
    "~/.config/nvim/thesaurus/".

**By default, online query backend will be used first(higher priority).** So
it'll still work properly if user neglects configuring for `mthesaur.txt`, as
long as internet is available.

To ensure the best user experience, **the backend that reports error during
query will have its priority lowered.**

## Motivation

After searching on Github for quite a while, I realized that comparing to
emacs, very few vim plugins for thesaurus query is satisfactory. Among the
plugins I tried, the most functional one was the one created by [Anton
Beloglazov](https://github.com/beloglazov/vim-online-thesaurus).
However, even his plugin doesn't support word replacement functionality. On top
of that, since his code relies heavily on vim script and regexp, to expand its
functionality is really difficult.

![](https://github.com/ron89/thesaurus_query.vim/raw/master/split_window.png)

So I decided to create another thesaurus query plugin built upon python
backend. Currently the performance is similar to Anton's plugin, and the only
additional functionality is under-cursor word replacement. But due to Python's
programmability, it should be easy for me to add more functions if requested.


## Installation

Use your plugin manager of choice.

- [Pathogen](https://github.com/tpope/vim-pathogen)
  - `git clone https://github.com/ron89/thesaurus_query.vim ~/.vim/bundle/thesaurus_query.vim`
- [Vundle](https://github.com/gmarik/vundle)
  - Add `Bundle 'ron89/thesaurus_query.vim '` to .vimrc
  - Run `:BundleInstall`
- [NeoBundle](https://github.com/Shougo/neobundle.vim)
  - Add `NeoBundle 'ron89/thesaurus_query.vim'` to .vimrc
  - Run `:NeoBundleInstall`
- [vim-plug](https://github.com/junegunn/vim-plug)
  - Add `Plug 'ron89/thesaurus_query.vim'` to .vimrc
  - Run `:PlugInstall`


## Usage

By default, ThesaurusQueryReplaceCurrentWord is mapped to `<LocalLeader>cs`.

```
    nnoremap <LocalLeader>cs :ThesaurusQueryReplaceCurrentWord<CR>
```

This routine check the synonyms of  the word under cursor and replace it with
the candidate chosen by user. The corresponding non-replacing routine is
defined as `ThesaurusQueryLookupCurrentWord`. User may choose to use it if you
prefer the split buffer display of result over the word replacement routine.

Another might-be-useful routine is the one to look up for words covered in
visual mode,

```
    vnoremap <LocalLeader>cs y:Thesaurus <C-r>"<CR>
```

this routine don't offer replacement by default. Because my current replacement
script is a simple one liner, it couldn't deal with many flexible situations as
yet.

## Configuration

### for Local Query Backend

Online query backend will work without any configuration. However, if user want
to use `mthesaur.txt` for local thesaurus query independent from internet use,
you will need to download `mthesaur.txt`(around 24MB) file from
[gutenberg.org](http://www.gutenberg.org/files/3202/files/), and place it under
folder "~/.vim/thesaurus". If user place the file elsewhere, be sure to let
this plugin know the location of your `mthesaur.txt` file by adding the line

```
    let g:thesaurus_query#mthesaurus="/directory/to/your/mthesaur.txt
```

into your `.vimrc`.

### Truncate query result in candidate window

Synonym replacing interface(shown in first screenshot) is the key feature of
this plugin. I will make my best effort to make sure it work sensibly. If user
has any complain about the current layout or otherwise, please draft an issue
to let me know. Currently, I have drafted two variables to help reducing the
candidate list when the number of synonym is too overwhelming.

![](https://github.com/ron89/thesaurus_query.vim/raw/master/synonym_candidate_truncate.png)

#### Synonym group truncate
Synonyms are grouped by definitions. If there are too many groups to your
liking, you may reduce the number of groups shown to `3` by setting

```
    g:thesaurus_query#truncation_on_definition_num = 3.
```

#### Synonym list truncate
Sometimes synonyms in a single group is also too long to choose from, in this
case, to reduce the number of synonym shown in each group to no more than
`200`, you can set

```
    g:thesaurus_query#truncation_on_syno_list_size = 200
```

Know that if query result is truncated by your rule, and you want to browse
through the result being truncated, you can still access the complete synonym
list by typing `A<Enter>` in your input prompt.

**Notice** Due to current lack of user feedback, and that I do not want to
arbitrarily make up truncation threshold that may damage user experience, both
truncation methods are inactive unless variables stated above are set
explicitly by user.

## TODO List

1. Add option to truncate the synonym list when its length is over a certain
   threashhold(need more feedback to decide parameters).
