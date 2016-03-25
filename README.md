# Thesaurus Query/Replacement Plugin

This is a plugin for user to *lookup* synonyms of any word under cursor and
*replace it* with an user chosen synonym. It also accepts word/phrases covered in
visual mode or manual input. But for the latter two cases, auto-replacement
function isn't activated by default, and the result will be displayed in
a split buffer.

![](http://i.imgur.com/LJpdBwD.png)

Three backends are used for this plugin, they function independently.

* **thesaurus\_com** queries from [Thesaurus.com](http://thesaurus.com/) for
  synonym, so internet connection is required for this backend's functionality.
  The returned synonym list from this source has very high quality. But since
  `thesaurus.com` didn't actually provide official API. The functionality of
  this backend might fail when the website changes its design.
* **datamuse\_com** queries from [datamuse.com](http://www.datamuse.com) using
  its officially provided API. The returned synonym list is usually quite
  relavant with reasonable quality. But the synonyms list tend to be short, so
  it might leave out some less-frequently-used synonyms. 
* **mthesaur\_txt** queries from local `mthesaur.txt`. It is an useful option
  when you don't have any internet access at all. For this backend to work, be
  sure to download the file from
  [gutenberg.org](http://www.gutenberg.org/files/3202/files/) and place it
  under "~/.vim/thesaurus". If you place the file elsewhere, change global
  variable |g:thesaurus_query#mthesaur_file| to point to the file you
  downloaded, eg. put the following line `let
  g:thesaurus_query#mthesaurus="~/.config/nvim/thesaurus/mthesaur.txt"` into
  your `.vimrc` file if your `mthesaur.txt` is placed in folder
  "~/.config/nvim/thesaurus/".

**By default, The sequence of query is thesaurus\_com -> datamuse\_com ->
mthesaur\_txt** Next query will be conducted only when the previous query
return empty sysnonym list. You may remove unwanted backend or lower their
priority by removing them/putting them on latter position in variable
`g:thesaurus_query#enabled_backends`. Its default is
    g:thesaurus_query#enabled_backends=["thesaurus_com","datamuse_com","mthesaur_txt"]


To ensure the best user experience, **the backend that reports error during
query will have its priority automatically lowered.** If user want to restore originally defined priority, simply invoke command
    :ThesaurusQueryReset

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

By default, command `:ThesaurusQueryReplaceCurrentWord` is mapped to
`<LocalLeader>cs`.

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

![](http://i.imgur.com/1nBNcoL.png)

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
   threshold(need more feedback to decide parameters).
2. Add more thesaurus source and try to parallelize the query process with
   a timeout limit.
3. Implement algorithm to make synonym candidates in a same form(tense,
   plurality, etc.). This could take a while... :-|
