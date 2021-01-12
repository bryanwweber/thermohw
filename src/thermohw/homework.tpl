% Default to the notebook output style
((* if not cell_style is defined *))
    ((* set cell_style = 'style_jupyter.tplx' *))
((* endif *))

% Inherit from the specified cell style.
((* extends cell_style *))


%===============================================================================
% Latex Article
%===============================================================================

((* block docclass *))
\documentclass[11pt]{article}
((* endblock docclass *))

% Remove maketitle
((* block maketitle *))((* endblock maketitle *))

((* block commands *))
% Remove section numbering
\setcounter{secnumdepth}{0}

% Set up boxes for success/warning/info
% The boxes match the Bootstrap alert classes
% https://getbootstrap.com/docs/4.1/components/alerts/
\newtcolorbox{successbox}{colback=green!5!white, colframe=green!75!black}
\newtcolorbox{primarybox}{colback=blue!5!white, colframe=blue!75!black}
\newtcolorbox{secondarybox}{colback=gray!5!white, colframe=gray!75!black}
\newtcolorbox{warningbox}{colback=yellow!5!white, colframe=yellow!75!black}
\newtcolorbox{dangerbox}{colback=red!5!white, colframe=red!75!black}
\newtcolorbox{infobox}{colback=teal!5!white, colframe=teal!75!black}

((( super() )))
((* endblock commands *))

% Render markdown but remove figure environment and convert
% appropriate divs to boxes
((* block markdowncell scoped *))
    ((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown-implicit_figures+tex_math_double_backslash', 'json') | convert_div('latex') | convert_raw_html('latex') | resolve_references | convert_pandoc('json', 'latex'))))
((* endblock markdowncell *))
