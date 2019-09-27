# Multi-Language Thesaurus Query/Replacement Plugin

[![Join the chat at https://gitter.im/Ron89/thesaurus_query.vim](https://badges.gitter.im/Ron89/thesaurus_query.vim.svg)](https://gitter.im/Ron89/thesaurus_query.vim?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This is a plugin for user to **lookup** synonyms of any word under cursor or
phrase covered in visual mode, and **replace it** with an user chosen synonym.
It also accepts word/phrases from manual input for synonym checkup.

**Notice:** Currently this plugin Supports only English (en), Chinese (cn), 
French (fr), Russian (ru) and German (de) thesaurus query. If you want to use the 
plugin for other languages, or if you're not satisfied with the performance of 
current backends and know of some online synonym services that I can integrate 
into the plugin, please come and post an issue with your suggestion.

This plugin is written in Python. So **+Python or +Python3 version of Vim is
required**.

![](http://i.imgur.com/3QXxUp7.gif)

## What's new

Deleted `thesaurus_com` backend due to the legal warning from Thesaurus.com on
the upstream package [thesarus](https://github.com/Manwholikespie/thesaurus).
For existing users that still have `thesaurus_com` explicitly enabled, the
backend now always return exception. For English users, currently the highest
quality source is either the OpenOffice Thesaurus source or mthesaur.txt. I am sorry for any inconvenience caused.

-------

Added two new French backend based on [synonymo.fr](http://www.synonymo.fr/)
and [cnrtl.fr](https://cnrtl.fr/). To activate them, add `fr` to variable
`g:tq_language` and `synonymo_fr` and/or `cnrtl_fr` to `g:tq_enabled_backends`.

-------

Added new German backend based on
[openthesaurus.de](https://www.openthesaurus.de/about/api#json). This
thesaurus backend is one of the German default backends. To activate it, add
`de` to variable `g:tq_language`. Also, if you have manual specification for
`g:tq_enabled_backends`, be sure to add `openthesaurus_de` to your backend
list.

-------

Added new Russian backend based
on [yarn-synsets.csv](http://russianword.net/yarn-synsets.csv). To use, add
`yarn_synsets` to Vim variable `g:tq_enabled_backends`, e.g.

```vim
let g:tq_enabled_backends=["yarn_synsets", "openoffice_en", "mthesaur_txt"]
```

also, add `ru` to variable `g:tq_language` and make sure that either
`yarn-synsets.csv` in downloaded to `~/.vim/thesaurus` or where variable
`g:tq_yarn_synsets_file` points at.

-------

A new variable is designed to force use certain version of Python, e.g.

```vim
let g:tq_python_version = 2
```
will force Plugin to use Python2 no matter if Python3 is supported.

## Installation

Use your plugin manager of choice.

- [Pathogen](https://github.com/tpope/vim-pathogen)
  - `git clone https://github.com/ron89/thesaurus_query.vim ~/.vim/bundle/thesaurus_query.vim`
- [Vundle](https://github.com/gmarik/vundle)
  - Add `Bundle 'ron89/thesaurus_query.vim'` to `.vimrc`
  - Run `:BundleInstall`
- [NeoBundle](https://github.com/Shougo/neobundle.vim)
  - Add `NeoBundle 'ron89/thesaurus_query.vim'` to `.vimrc`
  - Run `:NeoBundleInstall`
- [vim-plug](https://github.com/junegunn/vim-plug)
  - Add `Plug 'ron89/thesaurus_query.vim'` to `.vimrc`
  - Run `:PlugInstall`


## Usage

By default, command `:ThesaurusQueryReplaceCurrentWord` is mapped to
`<Leader>cs`.

```vim
nnoremap <Leader>cs :ThesaurusQueryReplaceCurrentWord<CR>
```

This routine check the synonyms of the word under cursor and replace it with
the candidate chosen by user. The corresponding non-replacing routine is
defined as `ThesaurusQueryLookupCurrentWord`. User may choose to use it if you
prefer the split buffer display of result over the word replacement routine.

----------------

Another might-be-useful routine is the one to query synonym for and replace
a multi-word phrase covered in visual mode, using the same key mapping
`<Leader>cs`

```vim
vnoremap <Leader>cs y:ThesaurusQueryReplace <C-r>"<CR>
```

The phrase covered in visual mode can be in a same line, or wrapped in two or
more lines.

---------------

Also, this plugin support Vim's builtin `completefunc` insert mode autocomplete
function. To invoke it, use keybinding `ctrl-x ctrl-u` in insert mode. This
function resembles Vim's own thesaurus checking function, but using online
resources for matchings.

---------------

Finally, this plugin support thesaurus checkup for manually input through
command mode command `:Thesaurus`.

```vim
:Thesaurus your phrase
```

## Configuration

### Description for backends and their setup

To ensure stability of the plugin's functionality, under the hood, this plugin
uses multiple backends sequentially to query for a synonym. Backends function
independently, hence the plugin will be functional as long as one of the these
backends is behaving properly.

* **openoffice\_en** queries from local thesaurus database provided by
  OpenOffice. It is an useful option when you don't have any internet access at
  all. If you are using Linux and has installed OpenOffice from official repo,
  you should have index file `th_en_US_v2.idx` and database
  file`th_en_US_v2.dat` in `/usr/share/myspell/dicts`, and this plugin should
  work outright. But if not, you can download the thesaurus data from [this
  link](https://www.openoffice.org/lingucomponent/MyThes-1.zip). You may then
  manually inform the plugin of the downloaded location on your machine by
  setting variable `g:tq_openoffice_en_file`. Eg, if your indes and database (2
  files) are `~/Downloads/MyThes-1.0/th_en_US_new[.idx,.dat]` then you should
  set your variable by adding `let
  g:tq_openoffice_en_file="~/Downloads/MyThes-1.0/th_en_US_new"` in your
  `.vimrc`.
* **mthesaur\_txt** queries from local `mthesaur.txt`. It is another useful
  option when you don't have any internet access at all. For this backend to
  work, be sure to download the file from
  [gutenberg.org](http://www.gutenberg.org/files/3202/files/) and place it
  under `"~/.vim/thesaurus"`. If you place the file elsewhere, change global
  variable `g:tq_mthesaur_file` to point to the file you
  downloaded, eg. put the following line `let
  g:tq_mthesaur_file="~/.config/nvim/thesaurus/mthesaur.txt"` into
  your `.vimrc` file if your `mthesaur.txt` is placed in folder
  `"~/.config/nvim/thesaurus/"`.
* **datamuse\_com** queries from [datamuse.com](http://www.datamuse.com) using
  its officially provided API. The returned synonym list is usually quite
  relavant with reasonable quality. But the synonyms list tend to be short, so
  it might leave out some less-frequently-used synonyms.
* **cilin\_txt** queries from local `cilin.txt`. It makes use of a Chinese
  thesaurus source "cilin.txt". For this backend to
  work, be sure to download the file from
  [this github
  repo](https://github.com/shijiebei2009/Algorithms/blob/master/src/main/resources/cilin.txt)
  and place it under `"~/.vim/thesaurus"`. If you place the file elsewhere,
  change global variable |g:tq_cilin_txt_file| to point to the file you
  downloaded, eg. put the following line `let
  g:tq_cilin_txt_file="~/.config/nvim/thesaurus/cilin.txt"` into your `.vimrc`
  file if your `cilin.txt` is placed in folder `"~/.config/nvim/thesaurus/"`.
  Note that if you downloaded "cilin.txt" from elsewhere, make sure that your
  source `cilin.txt` is utf-8 encoded. Or the plugin won't function correctly
  with the file.
* **yarn\_synsets** is a *Russian* thesaurus backend. It
  uses [yarn-synsets.csv](http://russianword.net/yarn-synsets.csv) as synonym
  resource, providing a fast responding and decent thesaurus query solution.
  Please place `yarn-synsets.csv` in `~/.vim/thesaurus`, or use variable
  `g:tq_yarn_synsets_file` to indicate the location of `yarn-synsets.csv` in
  your system.
* **jeck\_ru** is a *Russian* thesaurus backend. It queries
  [jeck.ru](http://jeck.ru/tools/SynonymsDictionary) for synonym resources.
  This website didn't provide standard API to use. Hence functionality of this
  backend depends on whether the website owner will change the webpage design.
* **woxikon\_de** is a *German* thesaurus backend. It queries
  [woxikon.de](http://synonyme.woxikon.de/synonyme) for synonym resources. This
  website didn't provide standard API to use. Hence functionality of this
  backend depends on whether the website owner will change the webpage design.
* **openthesaurus\_de** is a *German* thesaurus backend. It queries
  [openthesaurus.de](https://www.openthesaurus.de/about/api#json) for synonym
  resources. This thesaurus backend is one of the German default backends. To
  activate it, add `de` to variable `g:tq_language`. Also, if you have manual
  specification for `g:tq_enabled_backends`, be sure to add `openthesaurus_de`
  to your backend list.
* **cnrtl\_fr** is a *French* thesaurus backend. It queries
  [cnrtl.fr](https://cnrtl.fr/) for synonym resources. This
  website didn't provide standard API to use. Hence functionality of this
  backend depends on whether the website owner will change the webpage design.
  This backend requires `bs4` *BeautifulSoup* dependency.
* **synonymo\_fr** is a *French* thesaurus backend. It queries
  [synonymo.fr](http://www.synonymo.fr/) for synonym resources. This
  website didn't provide standard API to use. Hence functionality of this
  backend depends on whether the website owner will change the webpage design.
  This backend requires `bs4` *BeautifulSoup* dependency.

The thesaurus query plugin will go through the list `g:tq_enabled_backends` in
sequence until a match is found. Unless user explicitly instruct, Next query
will be conducted only when the previous query return empty synonym list or
failed to query. You may remove unwanted backend or lower their priority by
removing them/putting them on latter position in variable
`g:tq_enabled_backends` as following example:

```vim
let g:tq_enabled_backends=["woxikon_de","jeck_ru","openoffice_en","mthesaur_txt"]
let g:tq_enabled_backends=["cilin_txt",
            \"openthesaurus_de",
            \"yarn_synsets",
            \"openoffice_en",
            \"mthesaur_txt",
            \"datamuse_com",]
```

Non-Engligh backends are currently **not activated by
default**, due to the default setting `g:tq_language='en'`. To enable Russian, German, 
or Chinese backend, add 'ru', 'de' or 'cn' to the `tq_language` list:
```vim
let g:tq_language=['en', 'ru', 'de', 'cn']
```
Or if you want to use only German thesaurus engine in specific/current buffer
```vim
let b:tq_language=['de']
```

To ensure the best user experience, **the backend that reports error during
query will have its priority automatically lowered**. If user want to restore
originally defined priority, simply invoke command

```vim
:ThesaurusQueryReset
```

#### Online Backends Timeout Mechanism

Timeout mechanism (configurable with `g:tq_online_backends_timeout`) is added
to all online query backends to reduce query time(in seconds). Default value is
`1.0` (second), so that user using slower internet or having long response time
with certain backend servers could still has reliable performance.  For users
with faster internet, you may want to lower the value (mine is `0.4`).

   ```vim
   let g:tq_online_backends_timeout = 0.4
   ```

**Q:** Why would this help?

**A:** Usually when thesaurus is found, the server respond quickly. However,
when the word is not found, it will take a while before server return 404
error. And our plugin will freeze Vim before the error is returned. By setting
timeout, we may cut the waiting time down and start query from next backend
sooner. So that waiting-time for user can be drastically reduced if set
properly.

**Q:** What does it mean by **long response time to certain servers**

**A:** Depending on where you are, some thesaurus query service might not have
server built up close to you. In this case, the response time between you and
the server might varied greatly. For example, `woxikon_de` might only have
server in Germany. And I am in Singapore. Based on my experience, it might take
`400ms-1.0s` for the server to respond to my request. If I want to use its
service reliably, I might want to set the timeout to `1.0` (second), so that
most of the valid query can yield response before timeout.


### Truncate query result in candidate window

Synonym replacing interface(shown in first screenshot) is the key feature of
this plugin. I will make my best effort to make sure it work sensibly. If user
has any complain about the current layout or otherwise, please draft an issue
to let me know. Currently, I have drafted two variables to help reducing the
candidate list when the number of synonym is too overwhelming.

![](http://i.imgur.com/NTygvav.png)

#### Synonym group truncate
Synonyms are grouped by definitions. If there are too many groups to your
liking, you may reduce the number of groups shown to `3` by setting

```vim
let g:tq_truncation_on_definition_num = 3
```

#### Synonym list truncate
Sometimes synonyms in a single group is also too long to choose from, in this
case, to reduce the number of synonym shown in each group to no more than
`200`, you can set

```vim
let g:tq_truncation_on_syno_list_size = 200
```

Know that if query result is truncated by your rule, and you want to browse
through the result being truncated, you can still access the complete synonym
list by typing `A<Enter>` in your input prompt.

**Notice** Due to current lack of user feedback, and that I do not want to
arbitrarily make up truncation threshold that may damage user experience, both
truncation methods are inactive unless variables stated above are set
explicitly by user.

## Credit

This plugin is functionally based on and extended from the idea behind
[vim-online-thesaurus](http://www.vim.org/scripts/script.php?script_id=4588) by
Anton Beloglazov:

Several key improvements were made comparing to his plugin:
- added synonym replacing mechanism
- added fallback backend to ensure functionality even when server down or lack
  of internet connection.
- added alternative thesaurus sources and switching mechanism
- added multilanguage support. With proper backends, it is possible to extend
  the functionality of this plugin to any western letter based languages.

## TODO List

1. Add more thesaurus source and try to parallelize the query process with
   a timeout limit.
2. Implement algorithm to make synonym candidates in a same form(tense,
   plurality, etc.). This could take a while... :-|
3. Update documentation
