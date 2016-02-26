# Thesaurus Query/Replacement Plugin

This is a plugin for user to lookup synonyms of any word under cursor and
replace it with an user chosen synonym. It also accept word covered in visual
mode or manual input. But for the latter two cases, auto-replacement function
isn't activated by default. 

Default source of synonyms is [Thesaurus.com](http://thesaurus.com/), so
internet connection is required for it's functionality.


## Motivation 

After searching on Github for quite a while, I realized that comparing to
emacs, very few vim plugins for thesaurus query is satisfactory. Among the
plugins I tried, the most functional one was the one created by [Anton
Beloglazov](https://github.com/beloglazov/vim-online-thesaurus/blob/master/plugin/online-thesaurus.vim).
However, even his plugin doesn't support word replacement functionality. On top
of that, since his code relies heavily on vim script and regexp, to expand its
functionality is really difficult.

So I decided to create another thesautus query plugin built upon python
backend. Currently the performance is similar to Anton's plugin, and the only
additional functionality is under-cursor word replacement. But due to Python's
programmability, it should be easy for me to add more functions if requested.


## Installation

Use your plugin manager of choice.

- [Pathogen](https://github.com/tpope/vim-pathogen)
  - `git clone https://github.com/ron89/thesaurus_query.vim ~/.vim/bundle/thesaurus_query.vim`
- [Vundle](https://github.com/gmarik/vundle)
  - Add `Bundle 'https://github.com/ron89/thesaurus_query.vim '` to .vimrc
  - Run `:BundleInstall`
- [NeoBundle](https://github.com/Shougo/neobundle.vim)
  - Add `NeoBundle 'https://github.com/ron89/thesaurus_query.vim'` to .vimrc
  - Run `:NeoBundleInstall`
- [vim-plug](https://github.com/junegunn/vim-plug)
  - Add `Plug 'https://github.com/ron89/thesaurus_query.vim'` to .vimrc
  - Run `:PlugInstall`


## Customization

By default, ThesaurusQueryReplaceCurrentWord is mapped to `<LocalLeader>cs`.

    nnoremap <unique> <LocalLeader>cs :ThesaurusQueryReplaceCurrentWord<CR>

This routine check the synonyms of  the word under cursor and replace it with
the candidate chosen by user. The corresponsing non-replacing routine is
defined as `ThesaurusQueryLookupCurrentWord`. User may choose to use it if you
prefer the split buffer display of result over the word replacement routine.

Another might be useful routine is to look up for words covereded in visual
mode, this routine don't offer replacement by default.

    vnoremap <unique> <LocalLeader>cs y:Thesaurus <C-r>"<CR>

