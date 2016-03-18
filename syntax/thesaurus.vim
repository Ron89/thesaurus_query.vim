" Vim plugin for looking up words in an online thesaurus
" Maintainer:   HE Chong [[chong.he.1989@gmail.com][e-mail]]
" Based on script written by:
" Author:       Anton Beloglazov <http://beloglazov.info/>
" Original idea and code: Nick Coleman <http://www.nickcoleman.org/>

if exists("b:current_syntax")
    finish
endif

" Setup
syntax case match
setlocal iskeyword+=:

" Entry name rules
syntax match thesPartOfSpeech '\v\a{,6}\.'
" syntax match thesMainEntry '"\v\{2,}"' contained
syntax keyword thesDefinition Found_as: nextgroup=thesPartOfSpeech
syntax keyword thesSynonyms Synonyms:
" syntax keyword thesPartOfSpeech noun. pron. verb. adj. adv. prep. conj. interj.

" Entry contents rules
syntax region thesMainWord start=/Main entry:/  end=/$/ contains=CONTAINED keepend

" Highlighting
" hi link thesMainEntry   Keyword
hi link thesDefinition  Keyword
hi link thesSynonyms    Keyword
hi link thesPartOfSpeech Directory
" hi thesMainWord         term=bold cterm=bold gui=bold
" hi thesPartOfSpeech     term=italic cterm=italic gui=italic

let b:current_syntax = "thesaurus"
