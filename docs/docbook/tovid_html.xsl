<?xml version='1.0'?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fo="http://www.w3.org/1999/XSL/Format" version="1.0">

<!-- Style definitions -->
<!--
<xsl:param name="html.stylesheet">http://tovid.sourceforge.net/tovid_style.css</xsl:param>
-->
<xsl:param name="html.stylesheet">tovid_style.css tovid_print.css</xsl:param>
<xsl:param name="html.stylesheet.type">text/css</xsl:param>

<!-- Chunking (one chunk per chapter, no TOC in chapters) -->
<xsl:param name="chunk.section.depth" select="0"/>
<xsl:param name="section.autolabel" select="1"/>
<xsl:param name="html.cleanup" select="1"/>
<xsl:param name="spacing.paras" select="0"/>
<xsl:param name="make.valid.html" select="1"/>
<xsl:param name="toc.list.type">ul</xsl:param>
<!-- <xsl:param name="generate.toc" select="'book toc'"/> -->
<!-- <xsl:param name="chunker.output.encoding" select="'UTF-8'"/>
<xsl:param name="default.encoding" select="'UTF-8'"/> -->

<!-- Use id as filename -->
<xsl:param name="use.id.as.filename" select="1"/>
<xsl:param name="root.filename" select="toc"/>

<!-- Numbering -->
<xsl:param name="chapter.autolabel" select="0"/>
<xsl:param name="section.autolabel" select="0"/>

<!-- Glossaries -->
<xsl:param name="glossterm.auto.link" select="1"/>
<xsl:param name="glossentry.show.acronym">yes</xsl:param>

<!-- Keep notes and other admonitions from using h3.
     Instead, assume CSS will be defined for note
     (the note block) and note.title (note title block). -->
<xsl:template name="nongraphical.admonition">
  <div class="{name(.)}">
    <xsl:if test="$admon.style">
      <xsl:attribute name="style">
        <xsl:value-of select="$admon.style"/>
      </xsl:attribute>
    </xsl:if>

    <div class="title">
      <xsl:call-template name="anchor"/>
      <xsl:if test="$admon.textlabel != 0 or title">
        <xsl:apply-templates select="." mode="object.title.markup"/>
      </xsl:if>
    </div>

    <xsl:apply-templates/>
  </div>
</xsl:template>

<!-- Use "Previous" instead of "Prev" in navigation header/footer -->
<xsl:param name="local.l10n.xml" select="document('')" />
<l:i18n xmlns:l="http://docbook.sourceforge.net/xmlns/l10n/1.0">
    <l:l10n language="en">
        <l:gentext key="nav-prev" text="Previous"/>
    </l:l10n>
        <l:template name="qandaentry" text="Q:&#160;%n"/>
</l:i18n>

<!-- Unimplemented, but desired: -->
<!-- Keep paragraphs out of list items (li, dd) -->
<!-- Use H1 for chapter headings -->
<!-- Better navigational headers/footers. Include title
     of next/previous in the links to those chapters. Use "Home" before "up", and
     include both in the header as well as the footnote. Eliminate use of tables
     in navigational blocks. -->
<!-- Eliminate some of the redundant empty-div generation -->
<!-- Eliminate the use of tt, i, and b for formatting -->
<!-- <userinput> == <strong> ?!? Get rid of that! -->
<!-- Ugh, and don't get me started on the generated HTML for <qandaset>s
     (as used in the FAQ). Definition terms with no definitions, table-based
     layout, hardly any semantic markup. -->

</xsl:stylesheet>
