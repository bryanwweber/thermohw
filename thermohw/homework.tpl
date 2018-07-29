% Default to the notebook output style
((* if not cell_style is defined *))
    ((* set cell_style = 'style_ipython.tplx' *))
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

((( super() )))
((* endblock commands *))

% Render markdown but remove figure environment
((* block markdowncell scoped *))
    ((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown-implicit_figures', 'latex') )))
((* endblock markdowncell *))
