%%
%% This is file `bcsj.cls' of which base was
%% generated with the docstrip utility.
%%
%% The original source file is:
%% jclasses.dtx (with options: `article,12pt,yoko')
%% 
%% This class is specially designed for typesetting
%% any article to be published in Bul. Comput. Statist.
%% Jpn. (Keisanki Toukeigaku) by Prof N. Niki, DSc, 
%% Tokyo University of Science in Aug 2013. Some 
%% parameters and definitions inherited their values 
%% from `kt2.sty' (ver 2.1) due to Dr Minami.
%%
\NeedsTeXFormat{pLaTeX2e}
\ProvidesClass{bcsj}
\ProvidesFile{jsize12.clo}
%%  [1998/12/24 v1.1o Standard pLaTeX class]
\newcounter{@paper}
\newif\if@landscape \@landscapefalse
\newcommand{\@ptsize}{}
\newif\if@restonecol
\newif\if@titlepage
\@titlepagefalse
\hour\time \divide\hour by 60\relax
\@tempcnta\hour \multiply\@tempcnta 60\relax
\minute\time \advance\minute-\@tempcnta
\newif\if@stysize \@stysizefalse
\newif\if@enablejfam \@enablejfamtrue
%\DeclareOption{a4paper}
  \setcounter{@paper}{1}%
  \setlength\paperheight {297mm}%
  \setlength\paperwidth  {210mm}
%\DeclareOption{12pt}
  \renewcommand{\@ptsize}{2}
%\DeclareOption{twoside}
  \@twosidetrue
%\DeclareOption{twocolumn}
  \@twocolumntrue
%\DeclareOption{notitlepage}
  \@titlepagefalse
\DeclareOption{draft}{\setlength\overfullrule{5pt}}
\DeclareOption{final}{\setlength\overfullrule{0pt}}
\ExecuteOptions{final}
\newif\ifbcs@header
\DeclareOption{noheader}{\bcs@headerfalse}
\DeclareOption{header}{\bcs@headertrue}
\ExecuteOptions{header}
\newif\ifbcs@natbib
\DeclareOption{nonatbib}{\bcs@natbibfalse}
\DeclareOption{natbib}{\bcs@natbibtrue}
\ExecuteOptions{natbib}
\ProcessOptions\relax
%
\input{jsize1\@ptsize.clo}
\renewcommand{\normalsize}{%
    \@setfontsize\normalsize\@xiipt{16.5}%
  \abovedisplayskip 12\p@ \@plus3\p@ \@minus7\p@
  \abovedisplayshortskip \z@ \@plus3\p@
  \belowdisplayshortskip 6.5\p@ \@plus3.5\p@ \@minus3\p@
   \belowdisplayskip \abovedisplayskip
   \let\@listi\@listI}
\normalsize
\setbox0\hbox{\char\euc"A1A1}%
\setlength\Cht{\ht0}
\setlength\Cdp{\dp0}
\setlength\Cwd{\wd0}
\setlength\Cvs{\baselineskip}
\setlength\Chs{\wd0}
\renewcommand{\small}{%
  \@setfontsize\small\@xipt{13.6}%
  \abovedisplayskip 11\p@ \@plus3\p@ \@minus6\p@
  \abovedisplayshortskip \z@ \@plus3\p@
  \belowdisplayshortskip 6.5\p@ \@plus3.5\p@ \@minus3\p@
  \def\@listi{\leftmargin\leftmargini
              \topsep 9\p@ \@plus3\p@ \@minus5\p@
              \parsep 4.5\p@ \@plus2\p@ \@minus\p@
              \itemsep \parsep}%
  \belowdisplayskip \abovedisplayskip}
\renewcommand{\footnotesize}{%
  \@setfontsize\footnotesize\@xpt\@xiipt
  \abovedisplayskip 10\p@ \@plus2\p@ \@minus5\p@
  \abovedisplayshortskip \z@ \@plus3\p@
  \belowdisplayshortskip 6\p@ \@plus3\p@ \@minus3\p@
  \def\@listi{\leftmargin\leftmargini
              \topsep 6\p@ \@plus2\p@ \@minus2\p@
              \parsep 3\p@ \@plus2\p@ \@minus\p@
              \itemsep \parsep}%
  \belowdisplayskip \abovedisplayskip}
\renewcommand{\scriptsize}{\@setfontsize\scriptsize\@viiipt{9.5}}
\renewcommand{\tiny}{\@setfontsize\tiny\@vipt\@viipt}
\renewcommand{\large}{\@setfontsize\large\@xivpt{21}}
\renewcommand{\Large}{\@setfontsize\Large\@xviipt{25}}
\renewcommand{\LARGE}{\@setfontsize\LARGE\@xxpt{28}}
\renewcommand{\huge}{\@setfontsize\huge\@xxvpt{33}}
\let\Huge=\huge
%
\kanjiskip=-1pt plus .3pt minus .2pt
\xkanjiskip=0pt plus .6pt minus .6pt
%
\setlength\columnsep{8mm}
%
\setlength\columnseprule{0\p@}
\setlength\lineskip{1\p@}
\setlength\normallineskip{1\p@}
\renewcommand{\baselinestretch}{1.125}
\setlength\parskip{0\p@ \@plus \p@}
\setlength\parindent{1\Cwd}
\setlength\smallskipamount{3\p@ \@plus 1\p@ \@minus 1\p@}
\setlength\medskipamount{6\p@ \@plus 2\p@ \@minus 2\p@}
\setlength\bigskipamount{12\p@ \@plus 4\p@ \@minus 4\p@}
\@lowpenalty   51
\@medpenalty  151
\@highpenalty 301
\setlength\headheight{0\p@}
\setlength\headsep{25\p@}
\setlength\topskip{1\Cht}
\setlength\footskip{30\p@}
%
\setlength\maxdepth{.5\topskip}
%
\setlength\textwidth{172mm}
\@settopoint\textwidth
%
\setlength\@tempdima{\paperwidth}
\addtolength\@tempdima{-\textwidth}
\setlength\oddsidemargin{0.5\@tempdima}
\addtolength\oddsidemargin{-1in}
\@settopoint\oddsidemargin
%
\setlength\evensidemargin{\oddsidemargin}
\@settopoint\evensidemargin
%
\setlength\textheight{250mm}
\@settopoint\textheight
%
\setlength\@tempdima{\paperheight}
\addtolength\@tempdima{-\textheight}
\setlength\topmargin{0.5\@tempdima}
\addtolength\topmargin{-1.35in}
\@settopoint\topmargin
%
\setlength\marginparsep{10\p@}
\setlength\marginparpush{7\p@}
%
\setlength\marginparwidth{2in}
\@settopoint\marginparwidth
%
\setlength\footnotesep{8.4\p@}
\setlength{\skip\footins}{10.8\p@ \@plus 4\p@ \@minus 2\p@}
\setlength\floatsep    {14\p@ \@plus 2\p@ \@minus 4\p@}
\setlength\textfloatsep{20\p@ \@plus 2\p@ \@minus 4\p@}
\setlength\intextsep   {14\p@ \@plus 4\p@ \@minus 4\p@}
\setlength\dblfloatsep    {14\p@ \@plus 2\p@ \@minus 4\p@}
\setlength\dbltextfloatsep{20\p@ \@plus 2\p@ \@minus 4\p@}
\setlength\@fptop{0\p@ \@plus 1fil}
\setlength\@fpsep{10\p@ \@plus 2fil}
\setlength\@fpbot{0\p@ \@plus 1fil}
\setlength\@dblfptop{0\p@ \@plus 1fil}
\setlength\@dblfpsep{10\p@ \@plus 2fil}
\setlength\@dblfpbot{0\p@ \@plus 1fil}
\setcounter{topnumber}{2}
\setcounter{bottomnumber}{1}
\setcounter{totalnumber}{3}
\setcounter{dbltopnumber}{2}
\renewcommand{\topfraction}{.7}
\renewcommand{\bottomfraction}{.3}
\renewcommand{\textfraction}{.2}
\renewcommand{\floatpagefraction}{.5}
\renewcommand{\dbltopfraction}{.7}
\renewcommand{\dblfloatpagefraction}{.5}
%
\def\ps@plain{\let\@mkboth\@gobbletwo
   \let\ps@jpl@in\ps@plain
   \let\@oddhead\@empty
   \def\@oddfoot{\reset@font\hfil%
      {\bfseries--}\,\thepage\,{\bfseries--}\hfil}%
   \let\@evenhead\@empty
   \let\@evenfoot\@oddfoot}
\let\ps@jpl@in\ps@plain
%
\newenvironment{titlepage}
    {%
      \if@twocolumn
        \@restonecoltrue\onecolumn
      \else
        \@restonecolfalse\newpage
      \fi
      \thispagestyle{empty}%
      \setcounter{page}\@ne
    }%
    {\if@restonecol\twocolumn \else \newpage \fi
     \if@twoside\else
        \setcounter{page}\@ne
     \fi
    }
\newcommand\p@thanks[1]{\footnotemark
  \protected@xdef\@thanks{\@thanks
    \protect{\noindent$\m@th^\thefootnote$~#1\protect\par}}}
\newcommand{\maketitle}{\par
  \begingroup
    \renewcommand{\thefootnote}{\fnsymbol{footnote}}%
    \def\@makefnmark{\hbox{\ifydir $\m@th^{\@thefnmark}$
      \else\hbox{\yoko$\m@th^{\@thefnmark}$}\fi}}%
    \long\def\@makefntext##1{\parindent 1em\noindent
       \hbox to1.8em{\hss$\m@th^{\@thefnmark}$}##1}%
    \twocolumn[\@maketitle]%
    \thispagestyle{jpl@in}\@thanks
  \endgroup
  \setcounter{footnote}{0}%
  \global\let\thanks\relax
  \global\let\maketitle\relax
  \global\let\p@thanks\relax
  \global\let\@thanks\@empty
  \global\let\@author\@empty
  \global\let\@date\@empty
  \global\let\@title\@empty
  \global\let\title\relax
  \global\let\author\relax
  \global\let\date\relax
  \global\let\and\relax
}
\def\@maketitle{%
  \newpage\null\noindent\label{bcs@fp}%
  \ifbcs@header{\footnotesize\noindent 計算機統計学\\
   {\bfseries\bcs@vol}(\bcs@num),\,%
   \pageref{bcs@fp}--\@ifundefined{bcs@lp}{\pageref{bcs@lp}}{\bcs@lp}%
   \,(\bcs@year)\\
   \par\vskip -2\baselineskip}\else \vskip-4em\fi
  \vskip 2em%
  \begin{center}%
  \let\footnote\thanks
    {\huge\bfseries \@title \par}%
    \vskip 1.5em%
    {\large
      \lineskip .5em%
       \begin{tabular}[t]{@{}c@{}}%
        \@author
       \end{tabular}
     \par}%
  \end{center}%
  \par\vskip 1.5em%
}
%
\newenvironment{abstract}{%
  \begin{center}{\bfseries\abstractname}\end{center}
  \unskip\vspace{0.25\Cht}\par}{\relax}
%
\setcounter{secnumdepth}{3}
\newcounter{part}
\newcounter{section}
\newcounter{subsection}[section]
\newcounter{subsubsection}[subsection]
\newcounter{paragraph}[subsubsection]
\newcounter{subparagraph}[paragraph]
\renewcommand{\thepart}{\@Roman\c@part}
\renewcommand{\thesection}{\@arabic\c@section.}
\renewcommand{\thesubsection}{\thesection\@arabic\c@subsection}
\renewcommand{\thesubsubsection}{%
   \thesubsection.\@arabic\c@subsubsection}
\renewcommand{\theparagraph}{%
   \thesubsubsection.\@arabic\c@paragraph}
\renewcommand{\thesubparagraph}{%
   \theparagraph.\@arabic\c@subparagraph}
%
\newcommand{\section}{\@startsection{section}{1}{\z@}%
   {1.\Cvs \@plus.5\Cdp \@minus.2\Cdp}%
   {.125\Cvs \@plus.13\Cdp}%
   {\gdef\@currentlabel{%
      \ifin@ppendix\@Alph\c@section\else\@arabic\c@section\fi}%
    \reset@font\normalsize\bfseries}}
\newcommand{\subsection}{\@startsection{subsection}{2}{\z@}%
   {1.\Cvs \@plus.5\Cdp \@minus.2\Cdp}%
   {.125\Cvs \@plus.13\Cdp}%
   {\reset@font\normalsize\bfseries}}
\newcommand{\subsubsection}{\@startsection{subsubsection}{3}{\z@}%
   {1.\Cvs \@plus.5\Cdp \@minus.2\Cdp}%
   {.125\Cvs \@plus.13\Cdp}%
   {\reset@font\normalsize\bfseries}}
\newcommand{\paragraph}{\@startsection{paragraph}{4}{\z@}%
   {1.25ex \@plus 1ex \@minus .2ex}%
   {-1em}%
   {\reset@font\normalsize\bfseries}}
\newcommand{\subparagraph}{\@startsection{subparagraph}{5}{\z@}%
   {1.25ex \@plus 1ex \@minus .2ex}%
   {-1em}%
   {\reset@font\normalsize\bfseries}}
\newif\ifin@ppendix\in@ppendixfalse
\newcommand{\appendix}{\par\in@ppendixtrue
  \setcounter{section}{0}%
  \setcounter{subsection}{0}%
  \renewcommand{\thesection}{\@Alph\c@section.}}
%
\setlength\leftmargini {2.5em}
\setlength\leftmarginii{2.2em}
\setlength\leftmarginiii{1.87em}
\setlength\leftmarginiv{1.7em}
\setlength\leftmarginv {1em}
\setlength\leftmarginvi{1em}
%
\setlength  \labelsep  {.5em}
\setlength  \labelwidth{\leftmargini}
\addtolength\labelwidth{-\labelsep}
\@beginparpenalty -\@lowpenalty
\@endparpenalty   -\@lowpenalty
\@itempenalty     -\@lowpenalty
\setlength\partopsep{3\p@ \@plus 2\p@ \@minus 2\p@}
%
\def\@listi{\leftmargin\leftmargini
  \parsep 5\p@  \@plus2.5\p@ \@minus\p@
  \topsep 10\p@ \@plus4\p@   \@minus6\p@
  \itemsep5\p@  \@plus2.5\p@ \@minus\p@}
\let\@listI\@listi
\@listi
\def\@listii{\leftmargin\leftmarginii
   \labelwidth\leftmarginii \advance\labelwidth-\labelsep
   \topsep  5\p@   \@plus2.5\p@ \@minus\p@
   \parsep  2.5\p@ \@plus\p@  \@minus\p@
   \itemsep\parsep}
\def\@listiii{\leftmargin\leftmarginiii
   \labelwidth\leftmarginiii \advance\labelwidth-\labelsep
   \topsep 2.5\p@\@plus\p@\@minus\p@
   \parsep\z@
   \partopsep \p@ \@plus\z@ \@minus\p@
   \itemsep\topsep}
\def\@listiv {\leftmargin\leftmarginiv
              \labelwidth\leftmarginiv
              \advance\labelwidth-\labelsep}
\def\@listv  {\leftmargin\leftmarginv
              \labelwidth\leftmarginv
              \advance\labelwidth-\labelsep}
\def\@listvi {\leftmargin\leftmarginvi
              \labelwidth\leftmarginvi
              \advance\labelwidth-\labelsep}
%
\renewcommand{\theenumi}{\@arabic\c@enumi}
\renewcommand{\theenumii}{\@alph\c@enumii}
\renewcommand{\theenumiii}{\@roman\c@enumiii}
\renewcommand{\theenumiv}{\@Alph\c@enumiv}
\newcommand{\labelenumi}{\theenumi.}
\newcommand{\labelenumii}{(\theenumii)}
\newcommand{\labelenumiii}{\theenumiii.}
\newcommand{\labelenumiv}{\theenumiv.}
\renewcommand{\p@enumii}{\theenumi}
\renewcommand{\p@enumiii}{\theenumi(\theenumii)}
\renewcommand{\p@enumiv}{\p@enumiii\theenumiii}
%
\renewenvironment{enumerate}
  {\ifnum \@enumdepth >3\relax\@toodeep\else
   \advance\@enumdepth\@ne
   \edef\@enumctr{enum\romannumeral\the\@enumdepth}%
   \list{\csname label\@enumctr\endcsname}{%
         \ifnum \@listdepth=\@ne \topsep.5\normalbaselineskip
           \else\topsep\z@\fi
         \parskip\z@ \itemsep\z@ \parsep\z@
         \labelwidth1zw \labelsep.3zw
         \ifnum \@enumdepth=\@ne \leftmargin1zw\relax
           \else\leftmargin\leftskip\fi
         \advance\leftmargin 1zw
         \usecounter{\@enumctr}%
         \def\makelabel##1{\hss\llap{##1}}}%
   \fi}{\endlist}
%
\newcommand{\labelitemi}{\textbullet}
\newcommand{\labelitemii}{\textbullet}
\newcommand{\labelitemiii}{\textasteriskcentered}
\newcommand{\labelitemiv}{\textperiodcentered}
%
\renewenvironment{itemize}
  {\ifnum \@itemdepth >3\relax\@toodeep\else
   \advance\@itemdepth\@ne
   \edef\@itemitem{labelitem\romannumeral\the\@itemdepth}%
   \expandafter
   \list{\csname \@itemitem\endcsname}{%
      \iftdir
         \ifnum \@listdepth=\@ne \topsep.5\normalbaselineskip
           \else\topsep\z@\fi
         \parskip\z@ \itemsep\z@ \parsep\z@
         \labelwidth1zw \labelsep.3zw
         \ifnum \@itemdepth =\@ne \leftmargin1zw\relax
           \else\leftmargin\leftskip\fi
         \advance\leftmargin 1zw
      \fi
         \def\makelabel##1{\hss\llap{##1}}}%
   \fi}{\endlist}
\newenvironment{description}
  {\list{}{\labelwidth\z@ \itemindent-\leftmargin
   \iftdir
     \leftmargin\leftskip \advance\leftmargin3\Cwd
     \rightmargin\rightskip
     \labelsep=1zw \itemsep\z@
     \listparindent\z@ \topskip\z@ \parskip\z@ \partopsep\z@
   \fi
           \let\makelabel\descriptionlabel}}{\endlist}
\newcommand{\descriptionlabel}[1]{%
   \hspace\labelsep\normalfont\bfseries #1}
%
\newenvironment{verse}
  {\let\\\@centercr
   \list{}{\itemsep\z@ \itemindent -1.5em%
           \listparindent\itemindent
           \rightmargin\leftmargin \advance\leftmargin 1.5em}%
           \item\relax}{\endlist}
\newenvironment{quotation}
  {\list{}{\listparindent 1.5em%
           \itemindent\listparindent
           \rightmargin\leftmargin
           \parsep\z@ \@plus\p@}%
           \item\relax}{\endlist}
\newenvironment{quote}
  {\list{}{\rightmargin\leftmargin}%
           \item\relax}{\endlist}
%
\newcounter{figure}
\renewcommand{\thefigure}{\@arabic\c@figure}
\def\fps@figure{tbp}
\def\ftype@figure{1}
\def\ext@figure{lof}
\def\fnum@figure{\figurename~\thefigure}
\newenvironment{figure}
               {\@float{figure}}
               {\end@float}
\newenvironment{figure*}
               {\@dblfloat{figure}}
               {\end@dblfloat}
\newcounter{table}
\renewcommand{\thetable}{\@arabic\c@table}
\def\fps@table{tbp}
\def\ftype@table{2}
\def\ext@table{lot}
\def\fnum@table{\tablename~\thetable}
\newenvironment{table}
               {\@float{table}}
               {\end@float}
\newenvironment{table*}
               {\@dblfloat{table}}
               {\end@dblfloat}
\newlength\abovecaptionskip
\newlength\belowcaptionskip
\setlength\abovecaptionskip{10\p@}
\setlength\belowcaptionskip{0\p@}
\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip
  \iftdir\sbox\@tempboxa{#1\hskip1zw#2}%
    \else\sbox\@tempboxa{#1: #2}%
  \fi
  \ifdim \wd\@tempboxa >\hsize
    \iftdir #1\hskip1zw#2\relax\par
      \else #1: #2\relax\par\fi
  \else
    \global \@minipagefalse
    \hbox to\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip}
%
\setlength\arraycolsep{5\p@}
\setlength\tabcolsep{6\p@}
\setlength\arrayrulewidth{.4\p@}
\setlength\doublerulesep{2\p@}
\setlength\tabbingsep{\labelsep}
\skip\@mpfootins = \skip\footins
\setlength\fboxsep{3\p@}
\setlength\fboxrule{.4\p@}
%
\renewcommand{\theequation}{\@arabic\c@section.\@arabic\c@equation}
%
\if@enablejfam
  \DeclareSymbolFont{mincho}{JY1}{mc}{m}{n}
  \DeclareSymbolFontAlphabet{\mathmc}{mincho}
  \SetSymbolFont{mincho}{bold}{JY1}{gt}{m}{n}
  \DeclareMathAlphabet{\mathgt}{JY1}{gt}{m}{n}
  \reDeclareMathAlphabet{\mathrm}{\@mathrm}{\@mathmc}
  \reDeclareMathAlphabet{\mathbf}{\@mathbf}{\@mathgt}
  \jfam\symmincho
\else
  \DeclareRobustCommand{\mathmc}{%
    \@latex@error{Command \noexpand\mathmc invalid with\space
       `disablejfam' class option.}\@eha
  }
  \DeclareRobustCommand{\mathgt}{%
    \@latex@error{Command \noexpand\mathgt invalid with\space
       `disablejfam' class option.}\@eha
  }
\fi
\DeclareOldFontCommand{\mc}{\normalfont\mcfamily}{\mathmc}
\DeclareOldFontCommand{\gt}{\normalfont\gtfamily}{\mathgt}
\DeclareOldFontCommand{\rm}{\normalfont\rmfamily}{\mathrm}
\DeclareOldFontCommand{\sf}{\normalfont\sffamily}{\mathsf}
\DeclareOldFontCommand{\tt}{\normalfont\ttfamily}{\mathtt}
\DeclareOldFontCommand{\bf}{\normalfont\bfseries}{\mathbf}
\DeclareOldFontCommand{\it}{\normalfont\itshape}{\mathit}
\DeclareOldFontCommand{\sl}{\normalfont\slshape}{\@nomath\sl}
\DeclareOldFontCommand{\sc}{\normalfont\scshape}{\@nomath\sc}
\DeclareRobustCommand*{\cal}{\@fontswitch\relax\mathcal}
\DeclareRobustCommand*{\mit}{\@fontswitch\relax\mathnormal}
%
\setcounter{tocdepth}{3}
\newcommand{\@pnumwidth}{1.55em}
\newcommand{\@tocrmarg}{2.55em}
\newcommand{\@dotsep}{4.5}
\newdimen\toclineskip
\setlength\toclineskip{\z@}
\newdimen\@lnumwidth
\def\numberline#1{\hbox to\@lnumwidth{#1\hfil}}
\def\@dottedtocline#1#2#3#4#5{\ifnum #1>\c@tocdepth \else
  \vskip\toclineskip \@plus.2\p@
  {\leftskip #2\relax \rightskip \@tocrmarg \parfillskip -\rightskip
    \parindent #2\relax\@afterindenttrue
   \interlinepenalty\@M
   \leavevmode
   \@lnumwidth #3\relax
   \advance\leftskip \@lnumwidth \hbox{}\hskip -\leftskip
    {#4}\nobreak\leaders\hbox{$\m@th \mkern \@dotsep mu.\mkern \@dotsep
       mu$}\hfill \nobreak\hbox to\@pnumwidth{%
         \hss\reset@font\rmfamily \normalcolor #5}\par}\fi}
\def\addcontentsline#1#2#3{%
  \protected@write\@auxout
    {\let\label\@gobble \let\index\@gobble \let\glossary\@gobble
\@temptokena{\thepage}}%
    {\string\@writefile{#1}%
       {\protect\contentsline{#2}{#3}{\the\@temptokena}}}%
}
\newcommand{\tableofcontents}{%
  \section*{\contentsname
    \@mkboth{\contentsname}{\contentsname}%
  }\@starttoc{toc}%
}
\newcommand*{\l@part}[2]{%
  \ifnum \c@tocdepth >-2\relax
    \addpenalty{\@secpenalty}%
    \addvspace{2.25em \@plus\p@}%
    \begingroup
    \parindent\z@\rightskip\@pnumwidth
    \parfillskip-\@pnumwidth
    {\leavevmode\large\bfseries
     \setlength\@lnumwidth{4zw}%
     #1\hfil\nobreak
     \hbox to\@pnumwidth{\hss#2}}\par
    \nobreak
    \if@compatibility
    \global\@nobreaktrue
    \everypar{\global\@nobreakfalse\everypar{}}%
    \fi
     \endgroup
  \fi}
\newcommand*{\l@section}[2]{%
  \ifnum \c@tocdepth >\z@
    \addpenalty{\@secpenalty}%
    \addvspace{1.0em \@plus\p@}%
    \begingroup
      \parindent\z@ \rightskip\@pnumwidth \parfillskip-\rightskip
      \leavevmode\bfseries
      \setlength\@lnumwidth{1.5em}%
      \advance\leftskip\@lnumwidth \hskip-\leftskip
      #1\nobreak\hfil\nobreak\hbox to\@pnumwidth{\hss#2}\par
    \endgroup
  \fi}
\newcommand*{\l@subsection}   {\@dottedtocline{2}{1.5em}{2.3em}}
\newcommand*{\l@subsubsection}{\@dottedtocline{3}{3.8em}{3.2em}}
\newcommand*{\l@paragraph}    {\@dottedtocline{4}{7.0em}{4.1em}}
\newcommand*{\l@subparagraph} {\@dottedtocline{5}{10em}{5em}}
%
\newcommand{\listoffigures}{%
    \section*{\listfigurename
  \@mkboth{\listfigurename}{\listfigurename}}%
  \@starttoc{lof}%
}
\newcommand*{\l@figure}{\@dottedtocline{1}{1.5em}{2.3em}}
\newcommand{\listoftables}{%
    \section*{\listtablename
  \@mkboth{\listtablename}{\listtablename}}%
  \@starttoc{lot}%
}
\let\l@table\l@figure
%
\newdimen\bibindent
\setlength\bibindent{1.5em}
\newcommand{\newblock}{\hskip .11em\@plus.33em\@minus.07em}
%
\newenvironment{theindex}
  {\if@twocolumn\@restonecolfalse\else\@restonecoltrue\fi
   \columnseprule\z@ \columnsep 35\p@
   \twocolumn[\section*{\indexname}]%
   \@mkboth{\indexname}{\indexname}%
   \thispagestyle{jpl@in}\parindent\z@
   \parskip\z@ \@plus .3\p@\relax
   \let\item\@idxitem}
  {\if@restonecol\onecolumn\else\clearpage\fi}
\newcommand{\@idxitem}{\par\hangindent 40\p@}
\newcommand{\subitem}{\@idxitem \hspace*{20\p@}}
\newcommand{\subsubitem}{\@idxitem \hspace*{30\p@}}
\newcommand{\indexspace}{\par\vskip10\p@ \@plus5\p@ \@minus3\p@\relax}
%
\renewcommand{\footnoterule}{%
  \kern-3\p@
  \hrule width .4\columnwidth
  \kern 2.6\p@}
\newcommand\@makefntext[1]{\parindent 1em
  \noindent\hbox to 1.8em{\hss\@makefnmark}#1}
%
\newif\if西暦 \西暦false
\def\西暦{\西暦true}
\def\和暦{\西暦false}
\newcount\heisei \heisei\year \advance\heisei-1988\relax
\def\today{{%
  \iftdir
    \if西暦
      \kansuji\number\year 年
      \kansuji\number\month 月
      \kansuji\number\day 日
    \else
      平成\ifnum\heisei=1 元年\else\kansuji\number\heisei 年\fi
      \kansuji\number\month 月
      \kansuji\number\day 日
    \fi
  \else
    \if西暦
      \number\year~年
      \number\month~月
      \number\day~日
    \else
      平成\ifnum\heisei=1 元年\else\number\heisei~年\fi
      \number\month~月
      \number\day~日
    \fi
  \fi}}
\newcommand{\prepartname}{第}
\newcommand{\postpartname}{部}
\newcommand{\contentsname}{目\ \ 次}
\newcommand{\listfigurename}{図 目 次}
\newcommand{\listtablename}{表 目 次}
\newcommand{\refname}{参考文献}
\newcommand{\indexname}{索\ \ 引}
\newcommand{\figurename}{図}
\newcommand{\tablename}{表}
\newcommand{\appendixname}{付録}
\newcommand{\abstractname}{要\ \ 旨}
\newcommand{\ackname}{謝\ \ 辞}
\pagestyle{plain}
\pagenumbering{arabic}
\raggedbottom
\twocolumn
\sloppy
\@mparswitchtrue
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\renewcommand\eqnarray{%
  \stepcounter{equation}\def\@currentlabel{\p@equation \theequation }
  \global\@eqnswtrue\m@th \global\@eqcnt\z@
  \tabskip \@centering \let\\\@eqncr 
  $$\everycr{}\halign to\displaywidth \bgroup 
    \hskip\@centering $\displaystyle\tabskip\z@skip{##}$%
    \@eqnsel &\global\@eqcnt\@ne \hskip\arraycolsep \hfil${##}$\hfil &%
    \global \@eqcnt \tw@ \hskip\arraycolsep $\displaystyle {##}$\hfil 
    \tabskip\@centering &\global\@eqcnt\thr@@\hb@xt@\z@\bgroup
      \hss ##\egroup\tabskip\z@skip\cr}
%
\newcommand{\setIssue}[3]{%
  \gdef\bcs@vol{#1}\gdef\bcs@num{#2}\gdef\bcs@year{#3}}
\newcommand{\setPage}[1]{\setcounter{page}{#1}%
  \@ifnextchar[{\setPageAux}{\relax}}
\def\setPageAux[#1]{\gdef\bcs@lp{#1}}
\newcommand{\setHistory}[1]{%
  \gdef\bcs@history{(Received: #1)}
  \@ifnextchar[{\setHistoryAux{#1}}{\relax}}
\def\setHistoryAux#1[#2]{%
  \gdef\bcs@history{(Received: #1;~ Revised: #2)}}
\setIssue{xx}{x}{20xx}
\setPage{1}
%
\newcommand{\affil}{\@ifnextchar[{\affilAux}{\thanks}}
\def\affilAux[#1]{\protect\rlap{#1}\thanks}
\newcommand{\poaddr}[1]{\bcs@nl 〒#1}
\newcommand{\phone}[1]{(Tel: #1)}
\newcommand{\email}[1]{, Email: {\tt #1}}
\newcommand{\bcs@and}{\@ifnextchar[{\andAux}%
   {\andAux[\hskip-0.75em\@plus.17fil]}}
\def\andAux[#1]{\end{tabular}\,\, #1~\begin{tabular}[t]{c}}
\let\and\bcs@and
%
\newcounter{bcs@fn}
\renewcommand{\@fnsymbol}[1]{\ifcase#1\or *\or *\!*\or *\!*\!*\or 
   \dagger\or \dagger\!\dagger\or\dagger\!\dagger\!\dagger\or
   \ddagger\or \ddagger\!\ddagger\or \ddagger\!\ddagger\!\ddagger 
   \else\@ctrerr\fi\relax}
\def\sameaffil{\@ifnextchar[{\@sameaffil}{\@sameaffil[-1]}}
\def\@sameaffil[#1]{\setcounter{bcs@fn}{\c@footnote}%
   \addtocounter{footnote}{#1}\footnotemark
   \setcounter{footnote}{\c@bcs@fn}}
\let\same\sameaffil
%
\let\bcs@enddocument\enddocument
\renewcommand{\enddocument}{\label{bcs@lp}\bcs@enddocument}
%%%%
% One column Footnote in twocolumns
\newdimen\@prefoot
\renewcommand\@makecol{
  \if@twocolumn 
    \ifvoid\footins 
    \else
      \if@firstcolumn
        \global\@prefoot=\@colht
        \global\advance\@colht-\dp\footins
        \global\advance\@colht-\ht\footins
      \fi
    \fi
    \setbox\@outputbox\box\@cclv
  \else
    \ifvoid\footins \setbox\@outputbox\box\@cclv
    \else\setbox\@outputbox
      \vbox{\boxmaxdepth \maxdepth
      \unvbox\@cclv\vskip\skip\footins\footnoterule\unvbox\footins}
    \fi
  \fi
  \xdef\@freelist{\@freelist\@midlist}\gdef\@midlist{}\@combinefloats
  \setbox\@outputbox\vbox to\@colht{\boxmaxdepth\maxdepth
    \@texttop\dimen128=\dp\@outputbox\unvbox\@outputbox
    \vskip-\dimen128\@textbottom}%
  \global\maxdepth\@maxdepth}
\renewcommand\@outputdblcol{%
  \if@firstcolumn \global\@firstcolumnfalse
    \global\setbox\@leftcolumn\box\@outputbox
  \else \global\@firstcolumntrue
    \setbox\@outputbox\vbox{\hbox to\textwidth{\hbox to\columnwidth
      {\box\@leftcolumn \hss}\hfil \vrule width\columnseprule\hfil
       \hbox to\columnwidth{\box\@outputbox \hss}}
    \ifvoid\footins 
    \else \vskip \skip\footins \footnoterule \unvbox\footins 
    \fi}
    \@combinedblfloats
    \@outputpage \begingroup \@dblfloatplacement \@startdblcolumn
    \@whilesw\if@fcolmade \fi{\@outputpage\@startdblcolumn}\endgroup
  \fi}
% Footnote columnwidth -> textwidth
\long\def\@footnotetext#1{
  \hsize\textwidth
  \insert\footins{\footnotesize
  \interlinepenalty\interfootnotelinepenalty
  \splittopskip\footnotesep
  \splitmaxdepth \dp\strutbox \floatingpenalty \@MM
  \hsize\textwidth \@parboxrestore
  \edef\@currentlabel{\csname p@footnote\endcsname\@thefnmark}%
  \@makefntext{\rule{\z@}{\footnotesep}\ignorespaces #1\strut}}
  \hsize\columnwidth}
% Footnote Indent
\long\def\@makefntext#1{\parindent 1em\noindent
  \hbox to 1em{\hss$^{\@thefnmark}$~}%
  \@tempdima\textwidth\advance\@tempdima-2.5em\parbox[t]{\@tempdima}{#1}}
% Full textwidth footnote line
\renewcommand\footnoterule{\kern-3\p@
  \hrule width \textwidth \kern 2.6\p@} % the \hrule is .4pt high
%%%%
\newcommand\bcs@title[1]{\gdef\bcsb@title{#1}}
\newcommand\bcs@author[1]{\let\nl\break\gdef\bcsb@author{#1}}
\newcommand\bcs@keyword[1]{\gdef\bcsb@keyword{#1}}
% for compatibility
\let\etitle\bcs@title
\let\etitles\bcs@title
\let\eauthor\bcs@author
\let\keyword\bcs@keyword
%
\newenvironment{eabstract}
{\pagebreak\onecolumn
  \begingroup
  \let\thanks\footnote
  \def\thefootnote{\fnsymbol{footnote}}
  \def\@makefnmark{\hbox to 0pt{${}^{\@thefnmark}$\hss}}
  \newpage
  \quotation
  \setcounter{footnote}{0}
  \global\@topnum\z@ \@emaketitle \thispagestyle{plain}%
  \endgroup
  \setcounter{footnote}{0}
  \parindent1.5em}
{\par\vskip\baselineskip
  \@ifundefined{bcsb@keyword}{\relax}
    {{\bf Key words:} \bcsb@keyword}
  \endquotation}
%
\newcommand{\@emaketitle}{\par\null
 \let\affil\bcs@affil
 \let\and\bcs@and
 \vskip2em\parindent0pt%\hskip-1em 
 \begin{center}
  {\Large\bfseries\bcsb@title}
  \par\vskip1.5em 
  {\large\lineskip.5em
   \begin{tabular}[t]{c}\bcsb@author
   \end{tabular}\par}
  \@ifundefined{bcs@history}{\relax}
    {\par\vskip1em{\small\bcs@history}}
  \vskip1em{\small\bcsb@affil\par} 
 \end{center}
 \par\vskip 1.5em}
%
\newcommand{\bcs@affil}{\@ifnextchar[{\bcs@affilOpt}{\bcs@affilAux}}
\def\bcs@affilOpt[#1]{\rlap{#1}\bcs@affilAux}
\newcommand{\bcs@affilAux}[1]{\footnotemark\begingroup
  \def\protect{\noexpand\protect\noexpand}%
  \xdef\bcsb@affil{\bcsb@affil\protect\par${}^{\fnsymbol{footnote}}$\,#1}
  \endgroup}
\newcommand{\bcsb@affil}{}
\newcommand{\bcs@nl}{\newline\hspace{1.85em}}
\let\nl\bcs@nl
%
\newenvironment{acknowledgement}{%
  \section*{\hfill\ackname\hfill\hfill}}{\relax}
%
\ifbcs@natbib % natbib
  \newenvironment{thebibliography}[1]{\relax}{\relax}
  \usepackage{natbib}
  \long\def\bibsection{%
    \begin{center}\bfseries\refname~\end{center}%
    \unskip\vspace{-0.75\Cht}
    \gdef\baselinestretch{1}}
  \setlength{\bibsep}{0.1\Cht}
  \let\cite=\citep
\else % nonatbib
  \newenvironment{thebibliography}[1]
    {\section*{\refname\@mkboth{\refname}{\refname}}%
     \list{\@biblabel{\@arabic\c@enumiv}}%
        {\settowidth\labelwidth{\@biblabel{#1}}%
         \leftmargin\labelwidth
         \advance\leftmargin\labelsep
         \@openbib@code
         \usecounter{enumiv}%
         \let\p@enumiv\@empty
         \renewcommand\theenumiv{\@arabic\c@enumiv}}%
     \sloppy
     \clubpenalty4000
     \@clubpenalty\clubpenalty
     \widowpenalty4000%
     \sfcode`\.\@m}
    {\def\@noitemerr
      {\@latex@warning{Empty `thebibliography' environment}}%
     \endlist}
  \let\@openbib@code\@empty
\fi
\let\noheader\relax
%
\tolerance=3000
\endinput
%%
%% End of file `bcsj.cls'.
