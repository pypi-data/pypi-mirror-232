\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{fhgtechdoku}[2012/07/27 class file ``fhgtechdoku'' for technical documentation]

\newif\ifpdfOut\pdfOutfalse
\ifx\pdfoutput\undefined
  \pdfOutfalse
\else\ifcase\pdfoutput
  \pdfOutfalse
\else
  \pdfOuttrue
\fi\fi


\newif\ifFTDbetter
\newif\FTDbetterfalse
\DeclareOption{better}{\FTDbettertrue}

\newif\ifFTDnicer
\newif\FTDnicerfalse
\DeclareOption{nicer}{\FTDnicertrue}

\newif\ifFTDuglier
\newif\FTDnicerfalse
\DeclareOption{uglier}{\FTDugliertrue}

\def\setFhgErzeugt#1{\def\fhg@L@erzeugt{#1}}
\setFhgErzeugt{???}


\def\fhg@select@german{
	\setFhgErzeugt{Erzeugt:}
}

\def\fhg@select@english{
	\setFhgErzeugt{Created:}
}

\DeclareOption*{
	\ifcsname fhg@select@\CurrentOption\endcsname\csname fhg@select@\CurrentOption\endcsname\fi
	\PassOptionsToClass{\CurrentOption}{scrartcl}
}

\ProcessOptions

\LoadClass[fontsize=10bp,parskip=full,captions=nooneline]{scrartcl}

\RequirePackage{babel}

\RequirePackage[left=22.5mm,textwidth=131.75mm,top=26.5mm,bottom=1.4in,footskip=0.69in,ignoreheadfoot]{geometry} % paper size

\RequirePackage[T1]{fontenc}

%fonts
\usepackage[scaled=1.0]{frutiger}
\pdfmapfile{+pfr.map}

\renewcommand{\familydefault}{\sfdefault}
\fontfamily{\familydefault}

\def\ltseries{\fontseries{l}\selectfont}
\def\ebseries{\fontseries{eb}\selectfont}

% nicht noetig? schadet aber nix
\def\normalsize{\fontsize{10bp}{12bp}\selectfont}

\DeclareTextFontCommand{\textlt}{\ltseries}
\DeclareTextFontCommand{\texteb}{\ebseries}

\def\seriesdefault{l}



\RequirePackage{eso-pic}
\RequirePackage[24hr]{datetime}
\RequirePackage{isodate}
\RequirePackage{lastpage} % get number of pages
\RequirePackage{ragged2e} % make 
\RequirePackage{microtype}

\RequirePackage{dashbox}
\RequirePackage{dashrule}

% some usefull packages
\RequirePackage{graphicx} % for embedding graphics, rotating, ...
\RequirePackage{overpic}  % put text (or other stuff) over graphics

\RequirePackage{fhginstitutes} % definitions for different institues

% for positioning the Institute logo
\RequirePackage[absolute]{textpos}
\setlength{\TPHorizModule}{1mm}
\setlength{\TPVertModule}{\TPHorizModule}

\RaggedRight % make text ragged right with hyphenation
%\raggedright % make text ragged right -- no hyphenation



\def\setinstitute#1{%
	\ifcsname fhg@IAl #1\endcsname
		\edef\fhg@institut{\csname fhg@IAl #1\endcsname}
		\edef\fhg@institutshort{\csname fhg@IAk #1\endcsname}
		\ifcsname fhg@ILogo60 #1\endcsname
			\setlogo{\includegraphics{\csname fhg@ILogo60 #1\endcsname}}
		\else
			\setlogo{}
		\fi
	\else
		\ClassError{fhgtechdoku}{unknown acronym for an FhG institute: #1}{use a known acronym like IIS or use \backslashchar setinstitute{full name}{short name}}
	\fi
}


\newlength{\fulltextwidth}
\setlength\fulltextwidth{177mm}

\newenvironment{fullwidth}{\setlength{\textwidth}{177mm}}{\par}


\def\settitle{\@ifnextchar[{\fhg@settitlei}{\fhg@settitle}}
\def\fhg@settitle#1{\fhg@settitlei[#1]{#1}}
\def\fhg@settitlei[#1]#2{\def\fhg@theshorttitle{#1}\def\fhg@thetitle{#2}}

\def\setsubtitle#1{\def\fhg@thesubtitle{#1}}
\def\setauthor#1{\def\fhg@theauthor{#1}}
\def\setpartnerlogo#1{\def\fhg@partnerlogo{\includegraphics[width=30mm,height=15mm,keepaspectratio]{#1}}}
\def\setpartner#1{\def\fhg@partner{#1}}
\def\setlogo#1{\def\fhg@instituteLogo{#1}}

\def\fhg@partner{}

\def\fhg@titleFont#1{{\fontsize{24bp}{28bp}\fontseries{b}\selectfont\textls[50]{#1}}}
\def\fhg@subtitleFont#1{{\fontsize{24bp}{28bp}\fontseries{l}\selectfont #1}}
\def\fhg@institutFont#1{{\fontsize{8bp}{12bp}\fontseries{b}\selectfont\textls[150]{#1}}}
\def\fhg@zusammenarbeitFont#1{{\fontsize{8bp}{12bp}\fontseries{eb}\selectfont\textls[125]{\MakeUppercase{#1}}}}
\def\fhg@footerFont#1{{\fontsize{8bp}{11bp}\fontseries{l}\selectfont{#1}}}

%%% pagestyle for title page %%%

\def\ps@fhgiistitle{\ps@empty\ClearShipoutPicture%
\AddToShipoutPicture{
\AtPageUpperLeft{
\put(\LenToUnit{129.5mm},\LenToUnit{-16.5mm}){%
\raisebox{-\height}{\fhg@instituteLogo}}%
\put(\LenToUnit{22.5mm},\LenToUnit{-51.9mm}){\parbox[t]{\fulltextwidth}{\raggedright\fhg@institutFont{\MakeUppercase\fhg@institut}}}%
\put(\LenToUnit{22.5mm},\LenToUnit{-106.9mm}){\parbox[t]{\fulltextwidth}{\raggedright\fhg@titleFont{\MakeUppercase\fhg@thetitle}}}%
\put(\LenToUnit{22.5mm},\LenToUnit{-119.6mm}){\parbox[t]{\fulltextwidth}{\raggedright\fhg@subtitleFont{\fhg@thesubtitle}}}%
\ifdefined\fhg@partnerlogo%
\put(\LenToUnit{142.5mm},\LenToUnit{-246.5mm}){\hdashrule[12bp-0.35bp][c]{57mm}{0.7bp}{3bp 2bp}}
\put(\LenToUnit{142.5mm},\LenToUnit{-246.5mm}){\fhg@zusammenarbeitFont{In Zusammenarbeit mit}}
\put(\LenToUnit{142.5mm},\LenToUnit{-267.8mm}){\makebox(\LenToUnit{30mm},\LenToUnit{15mm})[tl]{\fhg@partnerlogo}}%
\fi%
}}}

%%% pagestyle for inner title page, partner logo removed %%%

\def\ps@fhgiisinnertitlenopartner{\ps@empty\ClearShipoutPicture%
\AddToShipoutPicture{
\AtPageUpperLeft{
\put(\LenToUnit{22.5mm},\LenToUnit{-106.9mm}){\color[gray]{0.4}{\parbox[t]{\fulltextwidth}{\raggedright\fhg@titleFont{\MakeUppercase\fhg@thetitle}}}}%
\put(\LenToUnit{22.5mm},\LenToUnit{-119.6mm}){\color[gray]{0.4}{\parbox[t]{\fulltextwidth}{\raggedright\fhg@subtitleFont{\fhg@thesubtitle}}}}%
}}}

%%% pagestyle for inner title page %%%

\def\ps@fhgiisinnertitle{\ps@fhgiisinnertitlenopartner%
\ifdefined\fhg@partnerlogo%
\AddToShipoutPicture{
\AtPageUpperLeft{
\put(\LenToUnit{142.5mm},\LenToUnit{-246.5mm}){\hdashrule[12bp-0.35bp]{57mm}{0.7bp}{3bp 2bp}}
\put(\LenToUnit{142.5mm},\LenToUnit{-246.5mm}){\fhg@zusammenarbeitFont{In Zusammenarbeit mit}}
\put(\LenToUnit{142.5mm},\LenToUnit{-267.8mm}){\makebox(\LenToUnit{30mm},\LenToUnit{15mm})[tl]{\fhg@partnerlogo}}%
}}\fi%
}

%%% pagestyle for normal pages %%%

\newsavebox{\fhg@columntitleBox}

\def\ps@fhgiispage{\ps@empty\ClearShipoutPicture%
\AddToShipoutPicture{
\AtPageUpperLeft{
\put(\LenToUnit{16mm},\LenToUnit{-272.1mm}){\rotatebox[origin=Bl]{90}{\raisebox{0pt}[0pt][0pt]{\tiny\jobname{} -- \fhg@L@erzeugt {\isodate\today} \currenttime}}}
\put(\LenToUnit{158.25mm},\LenToUnit{-26.5mm}){
\parbox[t]{41.25mm}{\fontsize{8bp}{12bp}\fontseries{m}\selectfont%
\hdashrule[0bp-0.175bp]{41.25mm}{0.35bp}{3bp 2bp}\\
{\rightmark}\\%
\raisebox{7.2pt}[4.8bp][0pt]{\hdashrule[0bp]{41.25mm}{0.35bp}{3bp 2bp}}}}%
\put(\LenToUnit{22.75mm},\LenToUnit{-272.1mm}){
\parbox[t]{\fulltextwidth}{\fhg@footerFont{%
\hdashrule[0bp-0.25bp]{\fulltextwidth}{0.5bp}{}\\
\parbox[t]{41.25mm}{\fhg@institutshort}%
\hfill    
\parbox[t]{41.25mm}{\fhg@theshorttitle}%
\hfill    
\parbox[t]{41.25mm}{\fhg@partner}%
\hfill    
\parbox[t]{41.25mm}{\raggedleft\thepage}%
}}}}}%
\let\@mkboth\markboth%
\def\sectionmark##1{\markright{##1}}
}

%%% pagestyle for normal empty %%%

\def\ps@fhgiisempty{\ps@empty\ClearShipoutPicture}


\ifFTDnicer
%\setkomafont{section}{\LARGE\mdseries}
%\setkomafont{subsection}{\normalsize\bfseries}
%\setkomafont{caption}{\fontsize{8bp}{10bp}\fontseries{l}\selectfont}
%\setkomafont{captionlabel}{\bfseries}
\else
\setcounter{secnumdepth}{4}
\setkomafont{section}{\fontsize{14bp}{17.5bp}\fontseries{b}\selectfont}
\setkomafont{subsection}{\fontsize{14bp}{17.5bp}\fontseries{l}\selectfont}
\setkomafont{subsubsection}{\fontsize{10bp}{12bp}\fontseries{b}\selectfont}
\setkomafont{paragraph}{\fontsize{10bp}{12bp}\fontseries{b}\selectfont}
\setkomafont{caption}{\fontsize{8bp}{12bp}\fontseries{l}\selectfont}
\setkomafont{captionlabel}{\ebseries}
\fi

% make section ragged right
\renewcommand{\raggedsection}{\raggedright}

\ifFTDuglier
\def\othersectionlevelsformat#1#2#3{\raisebox{\baselineskip}{\makebox[0pt][l]{#3\autodot}}}
\fi

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\def\maketitlepage{\pagestyle{fhgiistitle}\leavevmode\newpage\pagestyle{fhgiispage}}

\newenvironment{innertitlepage}[1][p]{%
\ifx#1n\pagestyle{fhgiisinnertitlenopartner}%
\else\pagestyle{fhgiisinnertitle}%
\fi\vglue300bp}{\leavevmode\newpage\pagestyle{fhgiispage}}%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\newif\iffhgc@ptionedframed\fhgc@ptionedframedfalse

\fhgc@ptionedframedfalse%

\newbox\fhgc@ptionedContentBox

\def\fhgcaptioned#1#2{%
	\fhgc@ptionedframedfalse%
	\@ifnextchar[{\fhgc@ptioned@{#1}{#2}}{\fhgc@ptioned{#1}{#2}}%
}

\def\ffhgcaptioned#1#2{%
	\fhgc@ptionedframedtrue%
	\@ifnextchar[{\fhgc@ptioned@{#1}{#2}}{\fhgc@ptioned{#1}{#2}}%
}

\def\fhgc@ptioned@#1#2[#3]{%
	\def\fhgc@ptionedOptParam{[#3]}%
	\fhgc@ptioned@@{#1}{#2}%
}

\def\fhgc@ptioned{%
	\let\fhgc@ptionedOptParam\relax%
	\fhgc@ptioned@@%
}

\def\fhgc@ptioned@@#1#2{
	\def\fhgc@ptionedFloatType{#2}%
	% width
	\def\fhgc@ptionedColumns{#1}%
	\def\fhgc@ptionedWidth{\errormsg{invalid width of #1 columns specified}}%
	\if1#1\def\fhgc@ptionedWidth{41.25mm}\fi%
	\if2#1\def\fhgc@ptionedWidth{86.50mm}\fi%
	\if3#1\def\fhgc@ptionedWidth{131.75mm}\fi%
	\if4#1\def\fhgc@ptionedWidth{177.00mm}\fi%
	% label
	\let\fhgc@ptionedLabel\label%
	\let\fhgc@ptionedStoredLabel\relax%
	\def\label##1{\gdef\fhgc@ptionedStoredLabel{\fhgc@ptionedLabel{##1}}}%
	\expandafter\begin\expandafter\fhgc@ptionedFloatType\fhgc@ptionedOptParam%
	% caption
	\let\fhgc@ptionedCaption\caption%
	\def\fhgc@ptionedStoredCaption{}%
	\def\caption{%
		\@dblarg\fhgc@ptionedCaption@%
	}
	% correct vertical spacing
	\setlength{\abovecaptionskip}{0pt}
	\setlength{\belowcaptionskip}{-\dp\strutbox}%
	% do the stuff
	\setlength\@tempdima{\fhgc@ptionedWidth}%
	\iffhgc@ptionedframed%
		\setlength\fboxrule{0.5bp}
		\addtolength\@tempdima{-2\fboxrule}%
		\addtolength\@tempdima{-2\fboxsep}%
	\fi%
	\begin{lrbox}{\fhgc@ptionedContentBox}%
	\begin{minipage}[b]{\@tempdima}%
}

\def\endfhgcaptioned{%
	\removelastskip%
	\end{minipage}%
	\end{lrbox}%
	\iffhgc@ptionedframed%
		\fcolorbox[gray]{0.4}{1.0}{\usebox\fhgc@ptionedContentBox}%
	\else%
		\usebox\fhgc@ptionedContentBox%
	\fi
	\expandafter\if\fhgc@ptionedColumns4%
		\iffhgc@ptionedframed\vspace*{0.5\baselineskip}\else\unskip\vskip-0.5\baselineskip\fi%
		\vskip\z@skip\hskip131.75mm%
	\fi%
	\hglue4mm%
	%\rule{0.5cm}{\ht\fhgc@ptionedContentBox}%
	%\rule[-1\dp\fhgc@ptionedContentBox]{0.5cm}{\dp\fhgc@ptionedContentBox}%
	\parbox[b]{41.25mm}{%
		\fhgc@ptionedCaption[\fhgc@ptionedStoredCaptionShort]{\fhgc@ptionedStoredCaption}%
		\fhgc@ptionedStoredLabel%
	}%
	\end{\fhgc@ptionedFloatType}%
}

\let\endffhgcaptioned\endfhgcaptioned

\def\fhgc@ptionedCaption@[#1]#2{%
	\gdef\fhgc@ptionedStoredCaptionShort{#1}%
	\gdef\fhgc@ptionedStoredCaption{#2}%
}



\setcapindent{0bp}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\def\fhg@tabular@hdline{\noalign{\setlength\@tempdima{\textwidth}\addtolength\@tempdima{2bp}\hdashrule[0bp][x]{\@tempdima}{\arrayrulewidth}{3bp 2bp}\hspace*{-2bp}}}

\AtBeginDocument{%
	\expandafter\let\expandafter\fhg@tabular@\csname tabular*\endcsname%
	\@namedef{tabular*}{%
		\def\arrayrulewidth{0.5bp}%
		\let\hdline=\fhg@tabular@hdline%
		\fhg@tabular@%
	}%
}

\let\fhg@tabular=\tabular
\def\tabular{%
	\def\arrayrulewidth{0.5bp}%
	\let\hdline=\fhg@tabular@hdline%
	\fhg@tabular%
}

\AfterPackage{tabularx}{%
	\let\fhg@tabularx=\tabularx%
	\def\tabularx{%
		\def\arrayrulewidth{0.5bp}%
		\let\hdline=\fhg@tabular@hdline%
		\fhg@tabularx%
	}%
}

