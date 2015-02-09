# vim: set ts=8 sts=8 sw=8 ft=make:

.POSIX:

# Suffix rules
.SUFFIXES:
.SUFFIXES: \
	.c .C .cc .cxx .cpp .o .so .bin \
	.txt .adoc .asciidoc .docbook \
	.md .mkd .markdown \
	.html .tex .pdf

# Defaults
CP=          cp
RM=          rm
ASCIIDOC=    asciidoc
A2X=         a2x
MARKDOWN=    markdown
DBLATEX=     dblatex
PANDOC=      pandoc

# Eqivalent extensions
.C.cpp:
	$(CP) "$<" "$@"
.cc.cpp:
	$(CP) "$<" "$@"
.cxx.cpp:
	$(CP) "$<" "$@"
.txt.asciidoc:
	$(CP) "$<" "$@"
.adoc.asciidoc:
	$(CP) "$<" "$@"
.markdown.md:
	$(CP) "$<" "$@"
.mkd.md:
	$(CP) "$<" "$@"

.c.o:
	$(CC) -c $(CPPFLAGS) $(CFLAGS) "$<" -o "$@"
.c.bin:
	$(CC) $(CPPFLAGS) $(CFLAGS) "$<" -o "$@" $(LDFLAGS)

.cpp.o:
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) "$<" -o "$@"
.cpp.bin:
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) "$<" -o "$@" $(LDFLAGS)

.md.html:
	$(MARKDOWN) $(MARKDOWN_FLAGS) < "$<" > "$@"


USE_A2X=     no

ASCIIDOC_HTML_COMMAND=       $(ASCIIDOC_HTML_COMMAND_$(USE_A2X))
ASCIIDOC_HTML_COMMAND_yes=   \
	$(A2X) -L -f xhtml $(A2X_FLAGS) "$<"
ASCIIDOC_HTML_COMMAND_no=    \
	$(ASCIIDOC) $(ASCIIDOC_FLAGS) -o "$@" "$<"

ASCIIDOC_HTML_COMMAND_true=  $(ASCIIDOC_HTML_COMMAND_yes)
ASCIIDOC_HTML_COMMAND_false= $(ASCIIDOC_HTML_COMMAND_no)
ASCIIDOC_HTML_COMMAND_1=     $(ASCIIDOC_HTML_COMMAND_yes)
ASCIIDOC_HTML_COMMAND_0=     $(ASCIIDOC_HTML_COMMAND_no)

.asciidoc.html:
	$(ASCIIDOC_HTML_COMMAND)

ASCIIDOC_PDF_FONT=           AR PL UMing TW
ASCIIDOC_PDF_COMMAND=        $(ASCIIDOC_PDF_COMMAND_$(USE_A2X))
ASCIIDOC_PDF_COMMAND_yes=   \
	( echo '<?xml version="1.0" encoding="iso-8859-1"?>';         \
	  echo '<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">'; \
	  echo '  <xsl:param name="xetex.font">';                     \
	  echo '    <xsl:text>\usepackage{fontspec}';                 \
	  echo '    </xsl:text>';                                     \
	  echo '    <xsl:text>\usepackage{xeCJK}';                    \
	  echo '    </xsl:text>';                                     \
	  echo '    <xsl:text>\setCJKmainfont{$(ASCIIDOC_PDF_FONT)}'; \
	  echo '    </xsl:text>';                                     \
	  echo '    <xsl:text>\XeTeXlinebreaklocale "zh"';            \
	  echo '    </xsl:text>';                                     \
	  echo '  </xsl:param>';                                      \
	  echo '</xsl:stylesheet>'; ) > "$<-chinese.xsl" &&           \
	$(A2X) -L -f pdf --dblatex-opts="-b xetex -P doc.publisher.show=0 -p $<-chinese.xsl $(DBLATEX_FLAGS)" $(A2X_FLAGS) "$<" && \
	$(RM) "$<-chinese.xsl"
ASCIIDOC_PDF_COMMAND_no=    \
	( echo '\usepackage{fontspec}';                                  \
	  echo '\usepackage{xeCJK}';                                     \
	  echo '\setCJKmainfont{$(ASCIIDOC_PDF_FONT)}';                  \
	  echo '\XeTeXlinebreaklocale "zh"'; ) > "$<-chinese.tex" &&     \
	$(ASCIIDOC) -b docbook $(ASCIIDOC_FLAGS) -o "$<.docbook" "$<" && \
	$(PANDOC) -f docbook -t latex --latex-engine=xelatex             \
	  -H "$<-chinese.tex" $(PANDOC_FLAGS) -o "$@" "$<.docbook" &&    \
	$(RM) "$<-chinese.tex" "$<.docbook"

ASCIIDOC_PDF_COMMAND_true=   $(ASCIIDOC_PDF_COMMAND_yes)
ASCIIDOC_PDF_COMMAND_false=  $(ASCIIDOC_PDF_COMMAND_no)
ASCIIDOC_PDF_COMMAND_1=      $(ASCIIDOC_PDF_COMMAND_yes)
ASCIIDOC_PDF_COMMAND_0=      $(ASCIIDOC_PDF_COMMAND_no)

.asciidoc.pdf:
	$(ASCIIDOC_PDF_COMMAND)
.asciidoc.tex:
	$(ASCIIDOC_PDF_COMMAND)
